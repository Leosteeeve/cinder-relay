#include "CRHUDWidget.h"
#include "CRInterfaceLayout.h"
#include "CRPlayerController.h"
#include "CRAudioSettingsSubsystem.h"
#include "CRGameMode.h"
#include "CREchoChapter.h"
#include "CRChapterSaveSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/TextBlock.h"
#include "Components/Border.h"
#include "Components/ButtonSlot.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/Slider.h"
#include "Components/ProgressBar.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/CanvasPanel.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/SizeBox.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Engine/Texture2D.h"
#include "Engine/GameInstance.h"
#include "GameFramework/GameUserSettings.h"
#include "Engine/World.h"
#include "Brushes/SlateColorBrush.h"
#include "InputCoreTypes.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
namespace
{
FLinearColor Amber()
{
    return FLinearColor::FromSRGBColor(FColor(201, 149, 83));
}
FLinearColor White()
{
    return FLinearColor::FromSRGBColor(FColor(232, 227, 216));
}
FLinearColor Cyan()
{
    return FLinearColor::FromSRGBColor(FColor(119, 182, 176));
}
FButtonStyle Style(bool Focus)
{
    FButtonStyle S;
    S.SetNormal(FSlateColorBrush(FLinearColor::FromSRGBColor(Focus ? FColor(72, 62, 44) : FColor(27, 41, 45))))
        .SetHovered(FSlateColorBrush(FLinearColor::FromSRGBColor(FColor(61, 73, 68))))
        .SetPressed(FSlateColorBrush(FLinearColor::FromSRGBColor(FColor(80, 66, 47))))
        .SetDisabled(FSlateColorBrush(FLinearColor::FromSRGBColor(FColor(21, 32, 35))))
        .SetNormalPadding(FMargin(23, 10))
        .SetPressedPadding(FMargin(23, 11, 23, 9));
    return S;
}
int32 TaskArea(const UWorld* World)
{
    const auto* Chapter = World ? World->GetAuthGameMode<ACRGameMode>() : nullptr;
    if (!Chapter) return INDEX_NONE;
    switch (Chapter->GetObjective())
    {
    case ECRObjective::ReachWorkshop: return 0;
    case ECRObjective::FindModule: return 1;
    case ECRObjective::RestorePower:
    case ECRObjective::InvestigateSignal:
    case ECRObjective::Complete: return 2;
    }
    return INDEX_NONE;
}
const TCHAR* const TaskAreas[] = {TEXT("RAIL YARD"), TEXT("WORKSHOP"), TEXT("RELAY BUNKER")};
const TArray<FName> Groups = {TEXT("Master"), TEXT("SFX"), TEXT("Ambience"), TEXT("UI"), TEXT("Voice")};
} // namespace
void UCRInterfaceAction::Configure(UCRHUDWidget *W, int32 Id)
{
    Owner = W;
    Action = Id;
    InitIsFocusable(false);
    OnClicked.AddDynamic(this, &UCRInterfaceAction::Activated);
    OnHovered.AddDynamic(this, &UCRInterfaceAction::Hovered);
}
void UCRInterfaceAction::Activated()
{
    if (Owner.IsValid())
        Owner->HandleAction(Action);
}
void UCRInterfaceAction::Hovered()
{
    if (Owner.IsValid())
        Owner->PlayInterfaceSound(TEXT("UISelect"));
}
UTextBlock *UCRHUDWidget::Text(FName N) const
{
    return WidgetTree ? Cast<UTextBlock>(WidgetTree->FindWidget(N)) : nullptr;
}
void UCRHUDWidget::Put(FName N, const FText &V)
{
    if (auto *T = Text(N); T && !T->GetText().EqualTo(V))
        T->SetText(V);
}
void UCRHUDWidget::Put(FName N, const FString &V)
{
    Put(N, FText::FromString(V));
}
void UCRHUDWidget::Visibility(FName N, bool V)
{
    if (auto *W = WidgetTree->FindWidget(N))
        W->SetVisibility(V ? (Cast<UButton>(W) ? ESlateVisibility::Visible : ESlateVisibility::SelfHitTestInvisible)
                           : ESlateVisibility::Collapsed);
}
void UCRHUDWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    SetIsFocusable(true);
    if (!WidgetTree->RootWidget)
        CRInterfaceLayout::Build(WidgetTree, BodyFont, TitleFont, TEXT("HUDRoot"));
    CRInterfaceLayout::ApplyChapterLayout(WidgetTree, BodyFont, TitleFont);
    for (const auto& Row : {TPair<FName, float>(TEXT("StreamingStatus"), 198.f),
                           TPair<FName, float>(TEXT("CheckpointStatus"), 234.f),
                           TPair<FName, float>(TEXT("EventNotice"), 290.f)})
    {
        if (auto *Label = Text(Row.Key))
            if (auto *CanvasSlot = Cast<UCanvasPanelSlot>(Label->Slot))
                CanvasSlot->SetPosition(FVector2D(40.f, Row.Value));
    }
    auto B = [this](const TCHAR *N)
    {
        auto *W = Cast<UButton>(WidgetTree->FindWidget(N));
        if (W)
        {
            W->IsFocusable = false;
            W->SetStyle(Style(false));
            W->OnHovered.AddDynamic(this, &UCRHUDWidget::MenuHovered);
            if (auto* Label = W->GetContent())
                if (auto* Slot = Cast<UButtonSlot>(Label->Slot)) Slot->SetHorizontalAlignment(HAlign_Left);
        }
        return W;
    };
    if (auto *W = B(TEXT("Resume")))
        W->OnClicked.AddDynamic(this, &UCRHUDWidget::ResumeClicked);
    if (auto *W = B(TEXT("Continue")))
        W->OnClicked.AddDynamic(this, &UCRHUDWidget::ContinueClicked);
    if (auto *W = B(TEXT("Restart")))
        W->OnClicked.AddDynamic(this, &UCRHUDWidget::RestartClicked);
    if (auto *W = B(TEXT("Settings")))
        W->OnClicked.AddDynamic(this, &UCRHUDWidget::SettingsClicked);
    if (auto *W = B(TEXT("Credits")))
        W->OnClicked.AddDynamic(this, &UCRHUDWidget::CreditsClicked);
    if (auto *W = B(TEXT("Exit")))
        W->OnClicked.AddDynamic(this, &UCRHUDWidget::ExitClicked);
    if (auto *W = B(TEXT("PackClose")))
        W->OnClicked.AddDynamic(this, &UCRHUDWidget::PackCloseClicked);
    if (auto *Content = Cast<UCanvasPanel>(WidgetTree->FindWidget(TEXT("MenuContent"))))
    {
        auto *Guide = WidgetTree->ConstructWidget<UCRInterfaceAction>(UCRInterfaceAction::StaticClass(), TEXT("FieldGuide"));
        Guide->Configure(this, 104);
        Guide->SetStyle(Style(false));
        auto *Label = WidgetTree->ConstructWidget<UTextBlock>();
        Label->SetText(NSLOCTEXT("Cinder", "FieldGuideButton", "F1   Field Guide"));
        Label->SetFont(FSlateFontInfo(BodyFont, 22));
        Label->SetColorAndOpacity(White());
        Guide->SetContent(Label);
        auto *GuideSlot = Content->AddChildToCanvas(Guide);
        GuideSlot->SetAnchors(FAnchors(1, 1));
        GuideSlot->SetAlignment(FVector2D(1, 1));
        GuideSlot->SetPosition(FVector2D(-48, -44));
        GuideSlot->SetSize(FVector2D(248, 56));
        auto* Chapters = WidgetTree->ConstructWidget<UCRInterfaceAction>(UCRInterfaceAction::StaticClass(), TEXT("Chapters"));
        Chapters->Configure(this, 108);
        Chapters->SetStyle(Style(false));
        auto* Caption = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("ChaptersLabel"));
        Caption->SetFont(FSlateFontInfo(BodyFont, 24));
        Caption->SetColorAndOpacity(White());
        Chapters->SetContent(Caption);
        auto* ChapterSlot = Content->AddChildToCanvas(Chapters);
        ChapterSlot->SetAnchors(FAnchors(1, 1));
        ChapterSlot->SetAlignment(FVector2D(1, 1));
        ChapterSlot->SetPosition(FVector2D(-48,-115));
        ChapterSlot->SetSize(FVector2D(420,64));
        auto* ReturnLog = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("EchoReturnLog"));
        ReturnLog->SetText(FText::FromString(TEXT("The first pulse faded at the river.\nA second came back on the far aerial.\n\nRelay Nine now has a route across the water.")));
        ReturnLog->SetFont(FSlateFontInfo(BodyFont, 28));
        ReturnLog->SetColorAndOpacity(White());
        ReturnLog->SetAutoWrapText(true);
        auto* LogSlot = Content->AddChildToCanvas(ReturnLog);
        LogSlot->SetAnchors(FAnchors(.53f,.27f,.94f,.70f));
        LogSlot->SetOffsets(FMargin(0));
        ReturnLog->SetVisibility(ESlateVisibility::Collapsed);
    }
    TArray<FSoftObjectPath> Icons;
    for (const TCHAR *N : {TEXT("Rook"), TEXT("Optic"), TEXT("Ammo"), TEXT("PowerModule")})
        Icons.Add(FSoftObjectPath(
            FString::Printf(TEXT("/Game/Generated/Phase055/Interface/Textures/T_CR055_Icon%s.T_CR055_Icon%s"), N, N)));
    const FSoftObjectPath MarkPath(
        TEXT("/Game/Generated/Phase055/Interface/Textures/T_CR055_RelayMark.T_CR055_RelayMark"));
    Icons.Add(MarkPath);
    IconLoad = UAssetManager::GetStreamableManager().RequestAsyncLoad(
        Icons, FStreamableDelegate::CreateWeakLambda(
                   this,
                   [this, MarkPath]()
                   {
                       if (auto *Mark = Cast<UImage>(WidgetTree->FindWidget(TEXT("RelayMark"))))
                           Mark->SetBrushFromTexture(Cast<UTexture2D>(MarkPath.ResolveObject()));
                       if (bPack)
                           RefreshFieldPack();
                   }));
    for (const TCHAR *N :
         {TEXT("MenuBackdrop"), TEXT("ModalPanel"), TEXT("SubtitlePanel"), TEXT("AssemblyHelp"), TEXT("PackPanel")})
        Visibility(N, false);
    for (const TCHAR *N : {TEXT("ConfirmedHit"), TEXT("DamageTint")})
        if (auto *W = WidgetTree->FindWidget(N))
            W->SetRenderOpacity(0);
}
void UCRHUDWidget::NativeDestruct()
{
    if (TitleLoad)
    {
        TitleLoad->CancelHandle();
        TitleLoad.Reset();
    }
    if (IconLoad)
    {
        IconLoad->CancelHandle();
        IconLoad.Reset();
    }
    Super::NativeDestruct();
}
void UCRHUDWidget::SetObjectiveExpanded(bool Expanded)
{
    Visibility(TEXT("ObjectiveHint"), Expanded && bObjectiveHasHint);
    const float Height = Expanded && bObjectiveHasHint ? 156.f : 98.f;
    for (const TCHAR *Name : {TEXT("ObjectivePanel"), TEXT("ObjectiveRail")})
    {
        if (auto *Widget = WidgetTree->FindWidget(Name))
        {
            if (auto *CanvasSlot = Cast<UCanvasPanelSlot>(Widget->Slot))
                CanvasSlot->SetSize(FVector2D(CanvasSlot->GetSize().X, Height));
        }
    }
    if (auto *Objective = Text(TEXT("Objective")))
    {
        if (auto *CanvasSlot = Cast<UCanvasPanelSlot>(Objective->Slot))
        {
            CanvasSlot->SetPosition(FVector2D(23.f, 41.f));
            CanvasSlot->SetSize(FVector2D(568.f, 52.f));
        }
    }
    if (auto *Panel = WidgetTree->FindWidget(TEXT("ObjectivePanel")))
        Panel->SetRenderOpacity(Expanded ? 1.f : .91f);
}
void UCRHUDWidget::SetObjective(const FText &V, bool Notify)
{
    if (FullObjective.EqualTo(V))
        return;
    bool Changed = !FullObjective.IsEmpty();
    FullObjective = V;
    ObjectiveAge = 7.f;
    FString Primary = V.ToString(), Hint;
    int32 BreakAt;
    if (Primary.FindChar(TEXT('\n'), BreakAt))
    {
        Hint = Primary.Mid(BreakAt + 1).TrimStartAndEnd();
        Primary.LeftInline(BreakAt);
    }
    bObjectiveHasHint = !Hint.IsEmpty();
    Put(TEXT("Objective"), Primary);
    Put(TEXT("ObjectiveHint"), Hint);
    const int32 Area = TaskArea(GetWorld());
    Put(TEXT("ObjectiveLabel"), UCREchoChapter::IsEchoWorld(GetWorld()) ? FString(TEXT("TASK   /   ECHO CROSSING")) : Area == INDEX_NONE ? FString(TEXT("CURRENT TASK"))
        : FString::Printf(TEXT("TASK   /   %s"), TaskAreas[Area]));
    SetObjectiveExpanded(true);
    if (Changed && Notify)
    {
        PlayInterfaceSound(TEXT("Confirm"));
    }
}
void UCRHUDWidget::SetPrompt(const FText &V)
{
    Put(TEXT("Prompt"), V);
}
void UCRHUDWidget::SetStreamingStatus(const FText &V)
{
    Put(TEXT("StreamingStatus"), V);
}
void UCRHUDWidget::SetSubtitle(const FText &V)
{
    Put(TEXT("Subtitle"), V);
    Visibility(TEXT("SubtitlePanel"), !V.IsEmpty() && !bMenu && !bPack);
}
void UCRHUDWidget::SetAssembly(bool V, bool Iron)
{
    bAssembly = V;
    Put(TEXT("AssemblyHelp"), Iron ? TEXT("IRON SIGHT SERVICE    Tab Skip & select    Esc Pause")
                                   : TEXT("SURVEY OPTIC FITTING    Tab Skip & apply    Esc Pause"));
    Visibility(TEXT("AssemblyHelp"), V);
    Visibility(TEXT("GameplayLayer"), !V && !bMenu && !bPack);
}
void UCRHUDWidget::SetMenu(bool V, bool End, bool Dead)
{
    bool Changed = bMenu != V || bEnded != End || bDefeated != Dead;
    bMenu = V;
    bEnded = End;
    bDefeated = Dead;
    Visibility(TEXT("MenuBackdrop"), V && !bPack);
    Visibility(TEXT("GameplayLayer"), !V && !bAssembly && !bPack);
    if (auto *T = Text(TEXT("Subtitle")))
        Visibility(TEXT("SubtitlePanel"), !V && !bPack && !T->GetText().IsEmpty());
    if (!V && !bPack && ModalKind)
        CloseModal();
    if (!bStartup)
    {
        const bool Echo = UCREchoChapter::IsEchoWorld(GetWorld());
        Put(TEXT("MenuTitle"), Dead ? TEXT("ELIAS HAS FALLEN") : End ? (Echo ? TEXT("ECHO\nCROSSING") : TEXT("MERIDIAN NETWORK")) : TEXT("PAUSED"));
        Put(TEXT("MenuBody"), End    ? (Echo ? TEXT("RETURN PATH CONFIRMED") : TEXT("CONNECTION RESTORED"))
                              : Dead ? TEXT("Recover from the last saved checkpoint.")
                                     : Echo ? TEXT("ECHO CROSSING") : TEXT("THE DEAD STATION"));
        Put(TEXT("ChapterKicker"), Echo ? TEXT("CHAPTER 02") : TEXT("CHAPTER 01"));
    }
    Visibility(TEXT("Resume"), V && !End && !Dead);
    Visibility(TEXT("FieldGuide"), !End && !Dead);
    Visibility(TEXT("Chapters"), V && !Dead);
    Visibility(TEXT("EchoReturnLog"), V && End && UCREchoChapter::IsEchoWorld(GetWorld()));
    if (Changed && V && !ModalKind)
        RefreshNavigation();
}
void UCRHUDWidget::SetRecoveryMenu(bool Startup, bool Dead, bool Resume, bool Continue, const FString &Status)
{
    bool Changed = bStartup != Startup;
    bStartup = Startup;
    if (auto *B = Cast<UButton>(WidgetTree->FindWidget(TEXT("Continue"))))
        B->SetIsEnabled(Continue);
    if (auto *L = Text(TEXT("ContinueLabel")))
        L->SetRenderOpacity(Continue ? 1.f : .35f);
    Put(TEXT("ContinueLabel"), Dead ? TEXT("Retry checkpoint") : TEXT("Continue"));
    Put(TEXT("RestartLabel"), Startup ? TEXT("New Game") : TEXT("Restart Chapter"));
    Put(TEXT("SaveAvailability"), Status);
    Visibility(TEXT("Resume"), Resume && !Startup);
    if (Startup)
    {
        Put(TEXT("MenuTitle"), TEXT("CINDER\nRELAY"));
        Put(TEXT("MenuBody"), TEXT("The Dead Station"));
    }
    Visibility(TEXT("TitleStationSection"), Startup);
    Put(TEXT("ChaptersLabel"), bEnded && !UCREchoChapter::IsEchoWorld(GetWorld()) ? TEXT("Next  /  Echo Crossing") : TEXT("Chapters & story"));
    if (Changed)
        RefreshTitleArtwork();
    if (bMenu && !ModalKind && !bPack)
        RefreshNavigation();
}
void UCRHUDWidget::RefreshTitleArtwork()
{
    auto *I = Cast<UImage>(WidgetTree->FindWidget(TEXT("TitleBackground")));
    if (!I)
        return;
    if (!bStartup)
    {
        I->SetBrushFromTexture(nullptr);
        I->SetVisibility(ESlateVisibility::Collapsed);
        if (TitleLoad)
        {
            TitleLoad->CancelHandle();
            TitleLoad.Reset();
        }
        return;
    }
    FSoftObjectPath P(
        TEXT("/Game/Generated/Phase055/Interface/Textures/T_CR055_MenuBackground.T_CR055_MenuBackground"));
    TitleLoad = UAssetManager::GetStreamableManager().RequestAsyncLoad(
        P, FStreamableDelegate::CreateWeakLambda(
               this,
               [this, P]()
               {
                   if (bStartup)
                       if (auto *Art = Cast<UImage>(WidgetTree->FindWidget(TEXT("TitleBackground"))))
                       {
                           Art->SetBrushFromTexture(Cast<UTexture2D>(P.ResolveObject()));
                           Art->SetVisibility(ESlateVisibility::HitTestInvisible);
                       }
               }));
}
void UCRHUDWidget::SetCombat(float H, int32 M, int32 R, bool Reload)
{
    TRACE_CPUPROFILER_EVENT_SCOPE(CR055_HUDUpdate);
    Put(TEXT("HealthValue"), FString::Printf(TEXT("%.0f"), H));
    Put(TEXT("HealthState"), H <= 25 ? TEXT("LOW HEALTH") : TEXT("HEALTH"));
    if (auto *B = Cast<UProgressBar>(WidgetTree->FindWidget(TEXT("HealthBar"))))
    {
        B->SetPercent(H / 100.f);
        B->SetFillColorAndOpacity(H <= 25 ? FLinearColor(.7f, .16f, .10f) : Cyan());
    }
    Put(TEXT("Magazine"), FString::Printf(TEXT("%02d"), M));
    Put(TEXT("Reserve"), FString::Printf(TEXT("/  %02d"), R));
    Put(TEXT("ReloadState"), Reload ? TEXT("RELOADING") : M > 0 ? TEXT("") : R > 0 ? TEXT("R  RELOAD") : TEXT("NO AMMO"));
    if (bHadCombat && bWasReloading && !Reload && H > 0)
        Notice(FText::FromString(TEXT("RELOAD COMPLETE")));
    bWasReloading = Reload;
    bHadCombat = true;
}
void UCRHUDWidget::SetSightState(bool Hide, bool Installed)
{
    if (auto *R = WidgetTree->FindWidget(TEXT("Reticle")))
        R->SetRenderOpacity(Hide ? 0 : 1);
    Put(TEXT("OpticState"), Installed ? TEXT("SURVEY OPTIC") : TEXT("IRON SIGHTS"));
}
void UCRHUDWidget::SetCheckpointStatus(const FText &V)
{
    Put(TEXT("CheckpointStatus"), V);
}
void UCRHUDWidget::Notice(const FText &V)
{
    Put(TEXT("EventNotice"), V);
    NoticeAge = 3;
}
void UCRHUDWidget::ShotFeedback(bool)
{
    ShotPulse = .12f;
    if (auto *W = WidgetTree->FindWidget(TEXT("Reticle")))
        W->SetRenderScale(FVector2D(1.24f));
}
void UCRHUDWidget::HitFeedback(bool K)
{
    HitPulse = K ? .36f : .18f;
    bKilled = K;
    Put(TEXT("ConfirmedHit"), K ? TEXT("x  CONFIRMED") : TEXT("x"));
}
void UCRHUDWidget::DamageFeedback()
{
    HurtPulse = .4f;
}
void UCRHUDWidget::NativeTick(const FGeometry &G, float D)
{
    Super::NativeTick(G, D);
    if (ShotPulse <= 0 && HitPulse <= 0 && HurtPulse <= 0 && ObjectiveAge <= 0 && NoticeAge <= 0)
        return;
    TRACE_CPUPROFILER_EVENT_SCOPE(CR055_HUDTransient);
    if (ShotPulse > 0)
    {
        ShotPulse = FMath::Max(0.f, ShotPulse - D);
        if (auto *W = WidgetTree->FindWidget(TEXT("Reticle")))
            W->SetRenderScale(FVector2D(1 + ShotPulse * 2));
    }
    if (HitPulse > 0)
    {
        HitPulse = FMath::Max(0.f, HitPulse - D);
        if (auto *W = Text(TEXT("ConfirmedHit")))
        {
            W->SetRenderOpacity(FMath::Clamp(HitPulse * 10, 0.f, 1.f));
            W->SetColorAndOpacity(bKilled ? Amber() : White());
        }
    }
    if (HurtPulse > 0)
    {
        HurtPulse = FMath::Max(0.f, HurtPulse - D);
        if (auto *W = WidgetTree->FindWidget(TEXT("DamageTint")))
            W->SetRenderOpacity(HurtPulse / .4f);
    }
    if (!bMenu && !bPack && ObjectiveAge > 0)
    {
        ObjectiveAge = FMath::Max(0.f, ObjectiveAge - D);
        if (ObjectiveAge == 0)
            SetObjectiveExpanded(false);
    }
    if (!bMenu && !bPack && NoticeAge > 0)
    {
        NoticeAge = FMath::Max(0.f, NoticeAge - D);
        if (NoticeAge == 0)
            Put(TEXT("EventNotice"), TEXT(""));
    }
}
void UCRHUDWidget::PlayInterfaceSound(FName Cue)
{
    if (auto *GI = GetGameInstance())
        if (auto *A = GI->GetSubsystem<UCRAudioSettingsSubsystem>())
            A->PlayUI(Cue);
}
void UCRHUDWidget::RefreshNavigation()
{
    MenuNavigation.Reset();
    for (const TCHAR *N :
         {TEXT("Resume"), TEXT("Continue"), TEXT("Restart"), TEXT("Settings"), TEXT("Credits"), TEXT("Exit"), TEXT("FieldGuide"), TEXT("Chapters")})
        if (auto *B = Cast<UButton>(WidgetTree->FindWidget(N));
            B && B->GetIsEnabled() && B->GetVisibility() != ESlateVisibility::Collapsed)
            MenuNavigation.Add(B);
    FocusIndex(FMath::Clamp(Focused, 0, MenuNavigation.Num() - 1));
}
void UCRHUDWidget::FocusIndex(int32 I)
{
    Focused = I;
    for (int32 N = 0; N < MenuNavigation.Num(); ++N)
    {
        MenuNavigation[N]->SetStyle(Style(N == I));
        if (auto *T = Cast<UTextBlock>(MenuNavigation[N]->GetContent()))
            T->SetColorAndOpacity(N == I ? Amber() : White());
    }
}
void UCRHUDWidget::MoveFocus(int32 D)
{
    if (MenuNavigation.Num())
    {
        FocusIndex((Focused + D + MenuNavigation.Num()) % MenuNavigation.Num());
        PlayInterfaceSound(TEXT("UISelect"));
    }
}
void UCRHUDWidget::MenuHovered()
{
    for (int32 Index = 0; Index < MenuNavigation.Num(); ++Index)
        if (MenuNavigation[Index]->IsHovered())
        {
            FocusIndex(Index);
            PlayInterfaceSound(TEXT("UISelect"));
            break;
        }
}
void UCRHUDWidget::BeginModal(const FString &T, const FString &B, int32 K)
{
    ModalKind = K;
    Visibility(TEXT("ModalPanel"), true);
    if (auto *W = WidgetTree->FindWidget(TEXT("MenuBackdrop")))
        W->SetIsEnabled(false);
    Put(TEXT("ModalTitle"), T);
    Put(TEXT("ModalBody"), B);
    if (auto *Body = Text(TEXT("ModalBody")))
        if (auto *BodySlot = Cast<UVerticalBoxSlot>(Body->Slot))
            BodySlot->SetPadding(FMargin(0, 0, 0, K == 6 ? 48.f : 24.f));
    if (auto *Box = Cast<UVerticalBox>(WidgetTree->FindWidget(TEXT("ModalChoices"))))
        Box->ClearChildren();
    MenuNavigation.Reset();
    VolumeSliders.Reset();
    VolumeLabels.Reset();
    Focused = 0;
    VolumeFocus = 0;
    SetKeyboardFocus();
}
UCRInterfaceAction *UCRHUDWidget::AddAction(int32 Id, const FString &Label)
{
    auto *Box = Cast<UVerticalBox>(WidgetTree->FindWidget(TEXT("ModalChoices")));
    if (!Box)
        return nullptr;
    auto *B = WidgetTree->ConstructWidget<UCRInterfaceAction>();
    B->Configure(this, Id);
    B->SetStyle(Style(false));
    auto *T = WidgetTree->ConstructWidget<UTextBlock>();
    T->SetText(FText::FromString(Label));
    T->SetFont(FSlateFontInfo(BodyFont, 24));
    T->SetColorAndOpacity(White());
    B->SetContent(T);
    Box->AddChildToVerticalBox(B)->SetPadding(FMargin(0, 5));
    MenuNavigation.Add(B);
    return B;
}
void UCRHUDWidget::CloseModal()
{
    SaveVolumes();
    ModalKind = 0;
    Visibility(TEXT("ModalPanel"), false);
    if (auto *W = WidgetTree->FindWidget(TEXT("MenuBackdrop")))
        W->SetIsEnabled(true);
    VolumeSliders.Reset();
    VolumeLabels.Reset();
    RefreshNavigation();
    SetKeyboardFocus();
}
bool UCRHUDWidget::HandleBack()
{
    if (bPack)
    {
        if (auto *PC = Cast<ACRPlayerController>(GetOwningPlayer()))
            PC->ToggleFieldPack();
        return true;
    }
    if (ModalKind == 7)
    {
        PlayInterfaceSound(TEXT("UICancel"));
        SettingsClicked();
        return true;
    }
    if (ModalKind)
    {
        PlayInterfaceSound(TEXT("UICancel"));
        CloseModal();
        return true;
    }
    return false;
}

void UCRHUDWidget::ShowFieldGuide(const FText& Objective, const FText& Route)
{
    if (ModalKind == 6)
    {
        PlayInterfaceSound(TEXT("UICancel"));
        CloseModal();
        return;
    }
    if (ModalKind != 0) return;
    if (UCREchoChapter::IsEchoWorld(GetWorld()))
    {
        BeginModal(TEXT("FIELD GUIDE"), TEXT("Chapter 02   /   Echo Crossing"), 6);
        auto* Box = Cast<UVerticalBox>(WidgetTree->FindWidget(TEXT("ModalChoices")));
        if (Box)
        {
            auto* Copy = WidgetTree->ConstructWidget<UTextBlock>();
            Copy->SetText(FText::FromString(Objective.ToString() + TEXT("\n\n") + Route.ToString()));
            Copy->SetWrapTextAt(FMath::Max(280.f, GetCachedGeometry().GetLocalSize().X * .64f));
            Copy->SetFont(FSlateFontInfo(BodyFont, 26));
            Copy->SetColorAndOpacity(White());
            Box->AddChildToVerticalBox(Copy)->SetPadding(FMargin(0,8,0,36));
        }
        AddAction(0,TEXT("Back"));
        FocusIndex(0);
        return;
    }
    const int32 Area = bStartup ? INDEX_NONE : TaskArea(GetWorld());
    BeginModal(TEXT("FIELD GUIDE"), bStartup ? TEXT("Chapter 01   /   The Dead Station")
        : FString::Printf(TEXT("Task area   /   %s"), Area == INDEX_NONE ? TEXT("THE DEAD STATION") : TaskAreas[Area]), 6);
    auto* Choices = Cast<UVerticalBox>(WidgetTree->FindWidget(TEXT("ModalChoices")));
    if (Choices)
    {
        auto* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
        Choices->AddChildToVerticalBox(Row)->SetPadding(FMargin(0, 0, 0, 30));
        auto* Instructions = WidgetTree->ConstructWidget<UVerticalBox>();
        auto* Left = Row->AddChildToHorizontalBox(Instructions);
        Left->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
        Left->SetPadding(FMargin(0, 0, 42, 0));
        auto* References = WidgetTree->ConstructWidget<UVerticalBox>();
        Row->AddChildToHorizontalBox(References)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
        // The scroll panel measures its rows before Slate assigns their final width.
        // Give paragraphs a wrap width during the first layout pass so later rows clear every line.
        const float PanelWidth = GetCachedGeometry().GetLocalSize().X * .8f;
        const float ColumnWidth = FMath::Max(160.f, (PanelWidth - 96.f) * .5f - 42.f);
        auto AddLine = [this, ColumnWidth](UVerticalBox* Box, const FString& Value, int32 Size, FLinearColor Tint, bool Heading, float After)
        {
            auto* Line = WidgetTree->ConstructWidget<UTextBlock>();
            auto Font = Line->GetFont();
            Font.Size = Size;
            if (auto* Face = Heading ? TitleFont.Get() : BodyFont.Get()) Font.FontObject = Face;
            Line->SetFont(Font);
            Line->SetText(FText::FromString(Value));
            Line->SetColorAndOpacity(Tint);
            Line->SetWrapTextAt(ColumnWidth);
            Line->SetAutoWrapText(true);
            Box->AddChildToVerticalBox(Line)->SetPadding(FMargin(0, 0, 0, After));
        };
        if (bStartup)
        {
            AddLine(Instructions, TEXT("THE ROUTE"), 19, Cyan(), false, 10);
            AddLine(Instructions, TEXT("Bring Relay Nine back online."), 37, White(), true, 16);
            AddLine(Instructions, TEXT("Cross the rail yard to the Workshop. Release the replacement module, "
                "then take it below ground to restore the relay."), 23, White(), false, 18);
        }
        else
        {
            AddLine(Instructions, TEXT("CURRENT TASK"), 19, Cyan(), false, 10);
            const FString ObjectiveText = Objective.ToString();
            int32 BreakAt;
            const FString Primary = ObjectiveText.FindChar(TEXT('\n'), BreakAt) ? ObjectiveText.Left(BreakAt) : ObjectiveText;
            AddLine(Instructions, Primary, 37, White(), true, 16);
            AddLine(Instructions, Route.ToString().Replace(TEXT("\n"), TEXT(" ")), 23, White(), false, 18);
        }
        References->AddChildToVerticalBox(CRInterfaceLayout::StationSection(WidgetTree, BodyFont, Area))->SetPadding(FMargin(0, 0, 0, 18));
        const TCHAR* ReferenceTitle = TEXT("YARD APPROACH");
        const TCHAR* ReferenceBody = TEXT("Press E at the yellow booth to raise the wagon. The motor alerts the scouts. "
            "For a quiet route, follow the north track east.");
        if (Area == 1)
        {
            ReferenceTitle = TEXT("AT THE WORKBENCH");
            ReferenceBody = TEXT("Use 1 to service the iron sights. If you have recovered the Survey Optic, "
                "press E at the calibration bench to fit it. Both sight choices are optional.");
        }
        else if (Area == 2)
        {
            ReferenceTitle = TEXT("AT THE CROSSING");
            ReferenceBody = TEXT("The shuttle moves across the main passage. The side service walk lets you cross "
                "on foot throughout the cycle.");
        }
        AddLine(References, ReferenceTitle, 19, Amber(), false, 6);
        AddLine(References, ReferenceBody, 20, White(), false, 12);
        AddLine(Instructions, TEXT("E   Interact      I   Field Pack"), 19, Cyan(), false, 0);
    }
    AddAction(0, TEXT("Back"));
    FocusIndex(0);
}
FReply UCRHUDWidget::NativeOnKeyDown(const FGeometry &G, const FKeyEvent &E)
{
    FKey K = E.GetKey();
    if (K == EKeys::F1 && !bPack && bMenu)
    {
        if (!E.IsRepeat()) if (auto *PC = Cast<ACRPlayerController>(GetOwningPlayer())) PC->OpenFieldGuide();
        return FReply::Handled();
    }
    if (E.IsRepeat() && (K == EKeys::I || K == EKeys::Escape || K == EKeys::Enter))
        return FReply::Handled();
    if (K == EKeys::Escape)
    {
        if (!HandleBack())
            if (auto *PC = Cast<ACRPlayerController>(GetOwningPlayer()))
                PC->TogglePrototypePause();
        return FReply::Handled();
    }
    if (K == EKeys::I && bPack)
    {
        if (auto *PC = Cast<ACRPlayerController>(GetOwningPlayer()))
            PC->ToggleFieldPack();
        return FReply::Handled();
    }
    if (ModalKind == 4 && (K == EKeys::Left || K == EKeys::Right))
    {
        if (VolumeFocus >= Groups.Num())
            return FReply::Handled();
        FName Group = Groups[FMath::Clamp(VolumeFocus, 0, 4)];
        if (auto *S = VolumeSliders.Find(Group))
        {
            float V = FMath::Clamp((*S)->GetValue() + (K == EKeys::Right ? .05f : -.05f), 0.f, 1.f);
            (*S)->SetValue(V);
            ChangeVolume(Group, V);
        }
        return FReply::Handled();
    }
    if (bPack && (K == EKeys::Left || K == EKeys::Right))
    {
        PackCategory = (PackCategory + (K == EKeys::Right ? 1 : 3)) % 4;
        PackSelection = 0;
        RefreshFieldPack();
        PlayInterfaceSound(TEXT("UISelect"));
        return FReply::Handled();
    }
    if (bMenu || bPack)
    {
        if (K == EKeys::Up || K == EKeys::Down || K == EKeys::Tab)
        {
            int32 D = K == EKeys::Up ? -1 : 1;
            if (ModalKind == 4)
            {
                const int32 ChoiceCount = Groups.Num() + MenuNavigation.Num();
                VolumeFocus = (VolumeFocus + D + ChoiceCount) % ChoiceCount;
                FocusIndex(VolumeFocus >= Groups.Num() ? VolumeFocus - Groups.Num() : -1);
                for (auto &Pair : VolumeLabels)
                    Pair.Value->SetColorAndOpacity(Groups.IndexOfByKey(Pair.Key) == VolumeFocus ? Amber() : White());
            }
            else if (bPack)
            {
                if (MenuNavigation.Num() > 0)
                {
                    PackSelection = (PackSelection + D + MenuNavigation.Num()) % MenuNavigation.Num();
                    RefreshFieldPack();
                    if (MenuNavigation.Num() > 1) PlayInterfaceSound(TEXT("UISelect"));
                }
            }
            else
                MoveFocus(D);
            return FReply::Handled();
        }
        if (K == EKeys::Enter || K == EKeys::SpaceBar)
        {
            if ((ModalKind != 4 || VolumeFocus >= Groups.Num()) && MenuNavigation.IsValidIndex(Focused) &&
                MenuNavigation[Focused]->GetIsEnabled())
                MenuNavigation[Focused]->OnClicked.Broadcast();
            return FReply::Handled();
        }
    }
    return Super::NativeOnKeyDown(G, E);
}
void UCRHUDWidget::ResumeClicked()
{
    PlayInterfaceSound(TEXT("UICancel"));
    if (auto *PC = Cast<ACRPlayerController>(GetOwningPlayer()))
        PC->ResumePrototype();
}
void UCRHUDWidget::ContinueClicked()
{
    PlayInterfaceSound(TEXT("UIConfirm"));
    if (bStartup && UCREchoChapter::HasUnfinishedCheckpoint(this))
    {
        const auto* First = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
        if (First && First->HasCheckpoint())
        {
            BeginModal(TEXT("CONTINUE"),TEXT("Both chapters have a saved checkpoint."),10);
            AddAction(110,TEXT("02   Echo Crossing")); AddAction(115,TEXT("01   The Dead Station")); AddAction(0,TEXT("Back"));
            FocusIndex(0);
        }
        else if (auto* PC = Cast<ACRPlayerController>(GetOwningPlayer())) PC->EnterEchoCrossing(true);
        return;
    }
    if (auto *PC = Cast<ACRPlayerController>(GetOwningPlayer()))
        PC->ContinueCheckpoint();
}
void UCRHUDWidget::RestartClicked()
{
    BeginModal(bStartup ? TEXT("START NEW GAME?") : TEXT("RESTART CHAPTER?"),
               UCREchoChapter::IsEchoWorld(GetWorld())
                    ? TEXT("Start again on the west bank. A new crossing checkpoint will replace your current progress.")
                    : TEXT("Your existing checkpoint is kept until you reach a new checkpoint. Unsaved progress returns to the chapter start."),
               1);
    AddAction(100, TEXT("Start chapter"));
    AddAction(0, TEXT("Cancel"));
    FocusIndex(1);
}
void UCRHUDWidget::ExitClicked()
{
    BeginModal(TEXT("EXIT GAME?"), TEXT("Progress after the last saved checkpoint will be lost."), 2);
    AddAction(101, TEXT("Exit Game"));
    AddAction(0, TEXT("Cancel"));
    FocusIndex(1);
}
void UCRHUDWidget::CreditsClicked()
{
    BeginModal(
        TEXT("CREDITS"),
        TEXT("CINDER RELAY / An original independent project\n\nOriginal interface, industrial artwork and sound "
             "design.\nBarlow type family: Jeremy Tribby / SIL OFL 1.1.\nHuman base data: MakeHuman contributors / "
             "CC0.\nUnreal Engine: Epic Games.\n\nNo third-party game artwork, music or voice performances."),
        3);
    AddAction(0, TEXT("Back"));
    FocusIndex(0);
}
void UCRHUDWidget::AddVolume(FName Group)
{
    auto *A = GetGameInstance()->GetSubsystem<UCRAudioSettingsSubsystem>();
    auto *Box = Cast<UVerticalBox>(WidgetTree->FindWidget(TEXT("ModalChoices")));
    if (!A || !Box)
        return;
    auto *Row = WidgetTree->ConstructWidget<UHorizontalBox>();
    auto *T = WidgetTree->ConstructWidget<UTextBlock>();
    T->SetFont(FSlateFontInfo(BodyFont, 22));
    T->SetColorAndOpacity(White());
    auto *Size = WidgetTree->ConstructWidget<USizeBox>();
    Size->SetWidthOverride(230);
    Size->SetContent(T);
    Row->AddChildToHorizontalBox(Size);
    auto *S = WidgetTree->ConstructWidget<USlider>();
    S->IsFocusable = false;
    S->SetMinValue(0);
    S->SetMaxValue(1);
    S->SetStepSize(.05f);
    S->SetValue(A->GetVolume(Group));
    S->SetSliderHandleColor(Amber());
    S->SetSliderBarColor(Cyan());
    Row->AddChildToHorizontalBox(S)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
    Box->AddChildToVerticalBox(Row)->SetPadding(FMargin(0, 12));
    VolumeSliders.Add(Group, S);
    VolumeLabels.Add(Group, T);
    ChangeVolume(Group, S->GetValue());
    if (Group == TEXT("Master"))
        S->OnValueChanged.AddDynamic(this, &UCRHUDWidget::MasterChanged);
    else if (Group == TEXT("SFX"))
        S->OnValueChanged.AddDynamic(this, &UCRHUDWidget::SFXChanged);
    else if (Group == TEXT("Ambience"))
        S->OnValueChanged.AddDynamic(this, &UCRHUDWidget::AmbienceChanged);
    else if (Group == TEXT("UI"))
        S->OnValueChanged.AddDynamic(this, &UCRHUDWidget::UIChanged);
    else
        S->OnValueChanged.AddDynamic(this, &UCRHUDWidget::VoiceChanged);
}
void UCRHUDWidget::SettingsClicked()
{
    BeginModal(TEXT("SETTINGS"),
               TEXT("AUDIO / Changes save when you leave. No music in this chapter.\nUP/DOWN: select  |  LEFT/RIGHT: "
                    "volume  |  ENTER: action"),
               4);
    for (FName G : Groups)
        AddVolume(G);
    AddAction(102, TEXT("Controls / Help"));
    AddAction(0, TEXT("Save & back"));
    AddAction(105, TEXT("Graphics"));
    FocusIndex(-1);
    if (auto *P = VolumeLabels.Find(TEXT("Master")))
        (*P)->SetColorAndOpacity(Amber());
}
void UCRHUDWidget::ShowGraphics()
{
    const auto *Settings = UGameUserSettings::GetGameUserSettings();
    if (!Settings) return;
    const int32 Shadows = Settings->GetShadowQuality();
    const bool IsPreset = Shadows == Settings->GetGlobalIlluminationQuality() && Shadows == Settings->GetReflectionQuality();
    const TCHAR *Current = IsPreset && Shadows == 2 ? TEXT("BALANCED") : IsPreset && Shadows == 3 ? TEXT("EPIC") : TEXT("CUSTOM");
    BeginModal(TEXT("GRAPHICS"), FString::Printf(TEXT("LIGHTING / %s\n\n"
        "Balanced uses High shadows, global illumination and reflections.\n"
        "Epic uses the original Epic settings for those three groups.\n"
        "Both choices keep the current resolution and render scale."), Current), 7);
    AddAction(106, TEXT("Balanced lighting"));
    AddAction(107, TEXT("Epic lighting"));
    AddAction(103, TEXT("Back to settings"));
    FocusIndex(IsPreset && Shadows == 3 ? 1 : 0);
}
void UCRHUDWidget::SetLightingQuality(int32 Quality)
{
    auto *Settings = UGameUserSettings::GetGameUserSettings();
    if (!Settings) return;
    Settings->SetShadowQuality(Quality);
    Settings->SetGlobalIlluminationQuality(Quality);
    Settings->SetReflectionQuality(Quality);
    Settings->ApplyNonResolutionSettings();
    Settings->SaveSettings();
    ShowGraphics();
}
void UCRHUDWidget::ChangeVolume(FName G, float V)
{
    if (auto *A = GetGameInstance()->GetSubsystem<UCRAudioSettingsSubsystem>())
        A->SetVolume(G, V);
    if (auto *T = VolumeLabels.Find(G))
        (*T)->SetText(
            FText::FromString(FString::Printf(TEXT("%s  %d%%"), *G.ToString().ToUpper(), FMath::RoundToInt(V * 100))));
}
void UCRHUDWidget::MasterChanged(float V)
{
    ChangeVolume(TEXT("Master"), V);
}
void UCRHUDWidget::SFXChanged(float V)
{
    ChangeVolume(TEXT("SFX"), V);
}
void UCRHUDWidget::AmbienceChanged(float V)
{
    ChangeVolume(TEXT("Ambience"), V);
}
void UCRHUDWidget::UIChanged(float V)
{
    ChangeVolume(TEXT("UI"), V);
}
void UCRHUDWidget::VoiceChanged(float V)
{
    ChangeVolume(TEXT("Voice"), V);
}
void UCRHUDWidget::SaveVolumes()
{
    if (ModalKind == 4)
        if (auto *A = GetGameInstance()->GetSubsystem<UCRAudioSettingsSubsystem>())
            A->SavePreferences();
}
void UCRHUDWidget::HandleAction(int32 Id)
{
    PlayInterfaceSound(Id == 0 || Id == 103 ? TEXT("UICancel") : TEXT("UIConfirm"));
    if (Id == 0)
    {
        CloseModal();
        return;
    }
    auto *PC = Cast<ACRPlayerController>(GetOwningPlayer());
    if (!PC)
        return;
    if (Id == 100)
    {
        CloseModal();
        PC->RestartPrototype();
    }
    else if (Id == 101)
    {
        SaveVolumes();
        PC->ExitPrototype();
    }
    else if (Id == 102)
    {
        SaveVolumes();
        BeginModal(TEXT("FIELD CONTROLS"),
                   TEXT("MOVE     WASD  Move     Mouse  Look     Space  Jump\n"
                        "               Shift  Sprint     Ctrl  Crouch or slide while sprinting\n\n"
                        "ROOK-5     LMB  Fire     RMB  Aim     R  Reload\n\n"
                        "STATION     E  Operate doors, stations and pickups     F5  Retry a streaming door\n"
                        "                   1  Service irons at the calibration bench     Tab  Skip workbench or ending\n\n"
                        "FIELD     F1  Field Guide     I  Field Pack     Esc  Pause or close"),
                   5);
        AddAction(103, TEXT("Back to settings"));
        FocusIndex(0);
    }
    else if (Id == 104)
        PC->OpenFieldGuide();
    else if (Id == 108) ShowChapterMenu();
    else if (Id == 109) { CloseModal(); PC->EnterEchoCrossing(false); }
    else if (Id == 110) { CloseModal(); PC->EnterEchoCrossing(true); }
    else if (Id == 111 || Id == 112) { CloseModal(); PC->PlayCampaignFilm(Id == 112); }
    else if (Id == 113) { CloseModal(); PC->ReturnToTitle(); }
    else if (Id == 115) { CloseModal(); PC->ContinueCheckpoint(); }
    else if (Id == 114)
    {
        BeginModal(TEXT("RESTART ECHO CROSSING?"), TEXT("Starting from the intake creates a new Chapter 02 checkpoint."), 9);
        AddAction(109,TEXT("Start from the intake")); AddAction(0,TEXT("Cancel")); FocusIndex(1);
    }
    else if (Id == 105)
    {
        SaveVolumes();
        ShowGraphics();
    }
    else if (Id == 106 || Id == 107)
        SetLightingQuality(Id == 106 ? 2 : 3);
    else if (Id == 103)
        SettingsClicked();
    else if (Id >= 200 && Id < 204)
    {
        PackCategory = Id - 200;
        PackSelection = 0;
        RefreshFieldPack();
    }
    else if (Id >= 220 && Id < 230)
    {
        PackSelection = Id - 220;
        RefreshFieldPack();
    }
    else if (Id == 240)
        PC->ToggleFieldPack();
}

void UCRHUDWidget::ShowChapterMenu()
{
    const bool Echo = UCREchoChapter::IsEchoWorld(GetWorld());
    auto* Store = GetGameInstance()->GetSubsystem<UCREchoStore>();
    BeginModal(TEXT("CHAPTERS & STORY"), TEXT("01   The Dead Station      /      02   Echo Crossing"), 8);
    if (!Echo && Store && Store->IsReady())
    {
        if (Store->HasUnfinishedCheckpoint()) AddAction(110,TEXT("Resume Echo Crossing"));
        AddAction(Store->HasCheckpoint() ? 114 : 109,Store->HasCheckpoint() ? TEXT("Start Echo Crossing from the intake") : TEXT("Begin Echo Crossing"));
    }
    AddAction(111,TEXT("Watch opening   /   The Quieting"));
    AddAction(112,TEXT("Watch recap   /   Relay Nine"));
    if (!bStartup) AddAction(113,TEXT("Return to title"));
    AddAction(0,TEXT("Back"));
    FocusIndex(0);
}

FReply UCRHUDWidget::NativeOnPreviewKeyDown(const FGeometry &G, const FKeyEvent &E)
{
    return NativeOnKeyDown(G, E);
}

void UCRHUDWidget::PackCloseClicked()
{
    if (auto *PC = Cast<ACRPlayerController>(GetOwningPlayer()))
        PC->ToggleFieldPack();
}
