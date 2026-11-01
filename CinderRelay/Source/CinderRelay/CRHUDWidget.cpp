#include "CRHUDWidget.h"
#include "CRInterfaceLayout.h"
#include "CRPlayerController.h"
#include "CRAudioSettingsSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/TextBlock.h"
#include "Components/Border.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/Slider.h"
#include "Components/ProgressBar.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/SizeBox.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Engine/Texture2D.h"
#include "Engine/GameInstance.h"
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
    FSlateBrush N;
    N.DrawAs = ESlateBrushDrawType::Box;
    N.TintColor = Focus ? FLinearColor::FromSRGBColor(FColor(61, 53, 43)) : FLinearColor(.025f, .035f, .038f);
    FSlateBrush H = N;
    H.TintColor = FLinearColor::FromSRGBColor(FColor(54, 64, 61));
    FSlateBrush P = N;
    P.TintColor = FLinearColor::FromSRGBColor(FColor(48, 67, 63));
    FSlateBrush D = N;
    D.TintColor = FLinearColor(.02f, .025f, .025f, .5f);
    S.SetNormal(N)
        .SetHovered(H)
        .SetPressed(P)
        .SetDisabled(D)
        .SetNormalPadding(FMargin(16, 10))
        .SetPressedPadding(FMargin(16, 11, 16, 9));
    return S;
}
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
    auto B = [this](const TCHAR *N)
    {
        auto *W = Cast<UButton>(WidgetTree->FindWidget(N));
        if (W)
        {
            W->IsFocusable = false;
            W->SetStyle(Style(false));
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
    Visibility(TEXT("ObjectiveLabel"), Expanded);
    const float Height = Expanded ? 104.f : 72.f;
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
            CanvasSlot->SetPosition(FVector2D(CanvasSlot->GetPosition().X, Expanded ? 46.f : 8.f));
    }
    if (auto *Panel = WidgetTree->FindWidget(TEXT("ObjectivePanel")))
        Panel->SetRenderOpacity(Expanded ? 1.f : .82f);
}
void UCRHUDWidget::SetObjective(const FText &V)
{
    if (FullObjective.EqualTo(V))
        return;
    bool Changed = !FullObjective.IsEmpty();
    FullObjective = V;
    ObjectiveAge = 4;
    Put(TEXT("Objective"), V);
    SetObjectiveExpanded(true);
    if (Changed)
    {
        Notice(FText::FromString(TEXT("OBJECTIVE UPDATED")));
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
void UCRHUDWidget::SetAssembly(bool V)
{
    bAssembly = V;
    Put(TEXT("AssemblyHelp"), TEXT("SURVEY OPTIC CALIBRATION    Tab Skip & apply    Esc Pause"));
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
        Put(TEXT("MenuTitle"), Dead ? TEXT("ELIAS HAS FALLEN") : End ? TEXT("MERIDIAN NETWORK") : TEXT("PAUSED"));
        Put(TEXT("MenuBody"), End    ? TEXT("CONNECTION RESTORED")
                              : Dead ? TEXT("Recover from the last saved checkpoint.")
                                     : TEXT("THE DEAD STATION"));
    }
    Visibility(TEXT("Resume"), V && !End && !Dead);
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
        Put(TEXT("MenuBody"), TEXT("THE LAST SIGNAL"));
    }
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
    Put(TEXT("HealthValue"), FString::Printf(TEXT("%03.0f"), H));
    Put(TEXT("HealthState"), H <= 25 ? TEXT("LOW HEALTH") : TEXT("HEALTH"));
    if (auto *B = Cast<UProgressBar>(WidgetTree->FindWidget(TEXT("HealthBar"))))
    {
        B->SetPercent(H / 100.f);
        B->SetFillColorAndOpacity(H <= 25 ? FLinearColor(.7f, .16f, .10f) : Cyan());
    }
    Put(TEXT("Magazine"), FString::Printf(TEXT("%02d"), M));
    Put(TEXT("Reserve"), FString::Printf(TEXT("/  %02d"), R));
    Put(TEXT("ReloadState"), Reload ? TEXT("RELOADING") : M == 0 ? TEXT("R  RELOAD") : TEXT(""));
    if (bHadCombat && bWasReloading && !Reload && H > 0)
        Notice(FText::FromString(TEXT("RELOAD COMPLETE")));
    bWasReloading = Reload;
    bHadCombat = true;
}
void UCRHUDWidget::SetSightState(bool Hide, bool Installed)
{
    if (auto *R = WidgetTree->FindWidget(TEXT("Reticle")))
        R->SetRenderOpacity(Hide ? 0 : 1);
    Put(TEXT("OpticState"), Installed ? TEXT("SURVEY OPTIC") : TEXT(""));
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
         {TEXT("Resume"), TEXT("Continue"), TEXT("Restart"), TEXT("Settings"), TEXT("Credits"), TEXT("Exit")})
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
void UCRHUDWidget::BeginModal(const FString &T, const FString &B, int32 K)
{
    ModalKind = K;
    Visibility(TEXT("ModalPanel"), true);
    if (auto *W = WidgetTree->FindWidget(TEXT("MenuBackdrop")))
        W->SetIsEnabled(false);
    Put(TEXT("ModalTitle"), T);
    Put(TEXT("ModalBody"), B);
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
    if (ModalKind)
    {
        PlayInterfaceSound(TEXT("UICancel"));
        CloseModal();
        return true;
    }
    return false;
}
FReply UCRHUDWidget::NativeOnKeyDown(const FGeometry &G, const FKeyEvent &E)
{
    FKey K = E.GetKey();
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
        return FReply::Handled();
    }
    if (bMenu || bPack)
    {
        if (K == EKeys::Up || K == EKeys::Down || K == EKeys::Tab)
        {
            int32 D = K == EKeys::Up ? -1 : 1;
            if (ModalKind == 4)
            {
                VolumeFocus = (VolumeFocus + D + 7) % 7;
                FocusIndex(VolumeFocus >= 5 ? VolumeFocus - 5 : -1);
                for (auto &Pair : VolumeLabels)
                    Pair.Value->SetColorAndOpacity(Groups.IndexOfByKey(Pair.Key) == VolumeFocus ? Amber() : White());
            }
            else if (bPack)
            {
                if (MenuNavigation.Num() > 0)
                {
                    PackSelection = (PackSelection + D + MenuNavigation.Num()) % MenuNavigation.Num();
                    RefreshFieldPack();
                }
            }
            else
                MoveFocus(D);
            return FReply::Handled();
        }
        if (K == EKeys::Enter || K == EKeys::SpaceBar)
        {
            if ((ModalKind != 4 || VolumeFocus >= 5) && MenuNavigation.IsValidIndex(Focused) &&
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
    if (auto *PC = Cast<ACRPlayerController>(GetOwningPlayer()))
        PC->ContinueCheckpoint();
}
void UCRHUDWidget::RestartClicked()
{
    BeginModal(bStartup ? TEXT("START NEW GAME?") : TEXT("RESTART CHAPTER?"),
               TEXT("Your existing checkpoint is kept until you reach a new checkpoint. Unsaved progress returns to "
                    "the chapter start."),
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
    FocusIndex(-1);
    if (auto *P = VolumeLabels.Find(TEXT("Master")))
        (*P)->SetColorAndOpacity(Amber());
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
    PlayInterfaceSound(TEXT("UIConfirm"));
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
                   TEXT("W A S D  Move  /  Mouse  Look\nShift  Sprint  /  Ctrl  Crouch or grounded sprint slide\nSpace "
                        " Jump  /  E  Interact\nLMB  Fire  /  RMB  Aim  /  R  Reload\nI  Field Pack  /  Esc  Pause or "
                        "close\nTab  Skip workbench / ending  /  F5  Retry streaming\n\nField Pack pauses the world "
                        "and reload.\nUnavailable during assembly and ending."),
                   5);
        AddAction(103, TEXT("Back to settings"));
        FocusIndex(0);
    }
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

FReply UCRHUDWidget::NativeOnPreviewKeyDown(const FGeometry &G, const FKeyEvent &E)
{
    return NativeOnKeyDown(G, E);
}

void UCRHUDWidget::PackCloseClicked()
{
    if (auto *PC = Cast<ACRPlayerController>(GetOwningPlayer()))
        PC->ToggleFieldPack();
}
