#include "CRInterfaceLayout.h"

#include "Blueprint/WidgetTree.h"
#include "Brushes/SlateColorBrush.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/ProgressBar.h"
#include "Components/ScrollBox.h"
#include "Components/SizeBox.h"
#include "Components/ScaleBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/Font.h"
#include "Engine/FontFace.h"
#include "UObject/UnrealType.h"
#if WITH_EDITOR
#include "WidgetBlueprint.h"
#endif

namespace
{
    FLinearColor Color(const TCHAR* Hex) { return FLinearColor(FColor::FromHex(Hex)); }
    const FLinearColor Deep = Color(TEXT("0B1012"));
    const FLinearColor Steel = Color(TEXT("151B1D"));
    const FLinearColor White = Color(TEXT("E8E3D8"));
    const FLinearColor Amber = Color(TEXT("C99553"));
    const FLinearColor Cyan = Color(TEXT("77B6B0"));
    const FLinearColor Olive = Color(TEXT("8E978B"));

    UWidgetTree* DesignerTree(UObject* Blueprint)
    {
        if (!Blueprint) return nullptr;
        if (const FObjectPropertyBase* Property = FindFProperty<FObjectPropertyBase>(Blueprint->GetClass(), TEXT("WidgetTree")))
            return Cast<UWidgetTree>(Property->GetObjectPropertyValue_InContainer(Blueprint));
        return FindObject<UWidgetTree>(Blueprint, TEXT("WidgetTree"));
    }

    struct FLayout
    {
        UWidgetTree* Tree;
        UObject* Body;
        UObject* Title;

        template <typename T> T* Make(const TCHAR* Name)
        {
            T* Widget = Tree->ConstructWidget<T>(T::StaticClass(), FName(Name));
            // Named widgets remain available in the Designer and to the existing event router.
            Widget->bIsVariable = true;
            return Widget;
        }

        UTextBlock* Text(const TCHAR* Name, const TCHAR* Value, int32 Size, FLinearColor Tint = White, bool Heading = false)
        {
            UTextBlock* W = Make<UTextBlock>(Name);
            W->SetText(FText::FromString(Value));
            FSlateFontInfo Font = W->GetFont();
            Font.Size = Size;
            if (UObject* Asset = Heading ? Title : Body) { Font.FontObject = Asset; Font.TypefaceFontName = TEXT("Regular"); }
            W->SetFont(Font);
            W->SetColorAndOpacity(FSlateColor(Tint));
            W->SetShadowColorAndOpacity(FLinearColor(0, 0, 0, .65f));
            W->SetShadowOffset(FVector2D(0, 1));
            W->SetVisibility(ESlateVisibility::HitTestInvisible);
            return W;
        }

        UCanvasPanelSlot* Place(UCanvasPanel* Parent, UWidget* W, FVector2D Position, FVector2D Size,
            FAnchors Anchor = FAnchors(0), FVector2D Align = FVector2D::ZeroVector, int32 Z = 0)
        {
            UCanvasPanelSlot* Slot = Parent->AddChildToCanvas(W);
            Slot->SetAnchors(Anchor); Slot->SetAlignment(Align); Slot->SetPosition(Position); Slot->SetSize(Size); Slot->SetZOrder(Z);
            return Slot;
        }

        void Stretch(UCanvasPanel* Parent, UWidget* W, int32 Z = 0)
        {
            UCanvasPanelSlot* Slot = Parent->AddChildToCanvas(W);
            Slot->SetAnchors(FAnchors(0, 0, 1, 1)); Slot->SetOffsets(FMargin(0)); Slot->SetZOrder(Z);
        }

        UBorder* Panel(const TCHAR* Name, FLinearColor Tint = Deep)
        {
            UBorder* B = Make<UBorder>(Name); B->SetBrushColor(Tint); B->SetPadding(FMargin(0));
            B->SetVisibility(ESlateVisibility::SelfHitTestInvisible); return B;
        }

        UButton* Button(const TCHAR* Name, const TCHAR* Label)
        {
            UButton* B = Make<UButton>(Name);
            FButtonStyle Style;
            Style.SetNormal(FSlateColorBrush(Steel));
            Style.SetHovered(FSlateColorBrush(Color(TEXT("303B39"))));
            Style.SetPressed(FSlateColorBrush(Color(TEXT("6A5032"))));
            Style.SetDisabled(FSlateColorBrush(Color(TEXT("101617"))));
            Style.SetNormalForeground(FSlateColor(White));
            Style.SetHoveredForeground(FSlateColor(White));
            Style.SetPressedForeground(FSlateColor(Amber));
            Style.SetDisabledForeground(FSlateColor(Color(TEXT("59615C"))));
            Style.SetNormalPadding(FMargin(24, 10)); Style.SetPressedPadding(FMargin(26, 11, 22, 9));
            B->SetStyle(Style); // Native UButton is keyboard-focusable by default.
            UTextBlock* T = Text(*(FString(Name) + TEXT("Label")), Label, 26);
            B->SetContent(T); return B;
        }

        void Health(UCanvasPanel* Gameplay)
        {
            UBorder* B = Panel(TEXT("HealthPanel"));
            Place(Gameplay, B, FVector2D(48, -48), FVector2D(252, 112), FAnchors(0, 1), FVector2D(0, 1));
            UCanvasPanel* C = Make<UCanvasPanel>(TEXT("HealthLayout")); B->SetContent(C);
            Place(C, Text(TEXT("HealthState"), TEXT("VITALS"), 17, Olive), FVector2D(24, 14), FVector2D(204, 24));
            Place(C, Text(TEXT("HealthValue"), TEXT("100"), 36, White, true), FVector2D(24, 40), FVector2D(170, 48));
            UProgressBar* Bar = Make<UProgressBar>(TEXT("HealthBar")); Bar->SetPercent(1); Bar->SetFillColorAndOpacity(Cyan);
            FProgressBarStyle Style; Style.SetBackgroundImage(FSlateColorBrush(Color(TEXT("34423D"))));
            Style.SetFillImage(FSlateColorBrush(FLinearColor::White)); Bar->SetWidgetStyle(Style);
            Bar->SetVisibility(ESlateVisibility::HitTestInvisible);
            Place(C, Bar, FVector2D(24, 92), FVector2D(204, 5));
        }

        void Weapon(UCanvasPanel* Gameplay)
        {
            UBorder* B = Panel(TEXT("WeaponPanel"));
            Place(Gameplay, B, FVector2D(-48, -48), FVector2D(264, 134), FAnchors(1, 1), FVector2D(1, 1));
            UCanvasPanel* C = Make<UCanvasPanel>(TEXT("WeaponLayout")); B->SetContent(C);
            Place(C, Text(TEXT("WeaponLabel"), TEXT("ROOK-5"), 18, Olive), FVector2D(24, 12), FVector2D(148, 24));
            Place(C, Text(TEXT("Magazine"), TEXT("05"), 56, White, true), FVector2D(24, 39), FVector2D(100, 64));
            Place(C, Text(TEXT("Reserve"), TEXT("/ 25"), 28, Olive), FVector2D(132, 61), FVector2D(108, 40));
            Place(C, Text(TEXT("ReloadState"), TEXT(""), 18, Amber), FVector2D(24, 108), FVector2D(216, 24));
            UTextBlock* Optic = Text(TEXT("OpticState"), TEXT(""), 16, Cyan); Optic->SetJustification(ETextJustify::Right);
            Place(C, Optic, FVector2D(24, -30), FVector2D(216, 24));
        }

        void Objective(UCanvasPanel* Gameplay)
        {
            UBorder* B = Panel(TEXT("ObjectivePanel"));
            Place(Gameplay, B, FVector2D(48, 48), FVector2D(660, 104));
            UCanvasPanel* C = Make<UCanvasPanel>(TEXT("ObjectiveLayout")); B->SetContent(C);
            UBorder* Rail = Panel(TEXT("ObjectiveRail"), Amber); Place(C, Rail, FVector2D::ZeroVector, FVector2D(3, 104));
            Place(C, Text(TEXT("ObjectiveLabel"), TEXT("CURRENT OBJECTIVE"), 17, Amber), FVector2D(24, 14), FVector2D(600, 24));
            UTextBlock* T = Text(TEXT("Objective"), TEXT("Reach the maintenance workshop."), 24); T->SetAutoWrapText(true);
            Place(C, T, FVector2D(24, 46), FVector2D(600, 56));
        }

        void Gameplay(UCanvasPanel* Root)
        {
            UCanvasPanel* G = Make<UCanvasPanel>(TEXT("GameplayLayer")); G->SetVisibility(ESlateVisibility::SelfHitTestInvisible); Stretch(Root, G);
            Health(G); Weapon(G); Objective(G);
            Place(G, Text(TEXT("StreamingStatus"), TEXT(""), 18, Amber), FVector2D(48, 168), FVector2D(760, 32));
            Place(G, Text(TEXT("CheckpointStatus"), TEXT(""), 20, Cyan), FVector2D(48, 208), FVector2D(760, 56));
            Place(G, Text(TEXT("EventNotice"), TEXT(""), 20, Amber), FVector2D(48, 272), FVector2D(760, 56));
            UTextBlock* R = Text(TEXT("Reticle"), TEXT("+"), 20); R->SetJustification(ETextJustify::Center);
            Place(G, R, FVector2D::ZeroVector, FVector2D(32, 32), FAnchors(.5f), FVector2D(.5f));
            UTextBlock* Hit = Text(TEXT("ConfirmedHit"), TEXT("x"), 26); Hit->SetJustification(ETextJustify::Center); Hit->SetRenderOpacity(0);
            Place(G, Hit, FVector2D::ZeroVector, FVector2D(260, 40), FAnchors(.5f), FVector2D(.5f), 2);
            UTextBlock* Prompt = Text(TEXT("Prompt"), TEXT(""), 23, Amber); Prompt->SetAutoWrapText(true); Prompt->SetJustification(ETextJustify::Center);
            Place(G, Prompt, FVector2D(0, 72), FVector2D(760, 76), FAnchors(.5f), FVector2D(.5f, 0));
            UBorder* Subtitle = Panel(TEXT("SubtitlePanel")); Subtitle->SetPadding(FMargin(24, 14));
            Subtitle->SetVerticalAlignment(VAlign_Center); Subtitle->SetVisibility(ESlateVisibility::Collapsed);
            UCanvasPanelSlot* SubSlot = Root->AddChildToCanvas(Subtitle); SubSlot->SetAnchors(FAnchors(.19f, 1, .81f, 1)); SubSlot->SetOffsets(FMargin(0, -290, 0, 112)); SubSlot->SetZOrder(7);
            UTextBlock* SubText = Text(TEXT("Subtitle"), TEXT(""), 26); SubText->SetAutoWrapText(true); SubText->SetJustification(ETextJustify::Center); Subtitle->SetContent(SubText);
            UTextBlock* Help = Text(TEXT("AssemblyHelp"), TEXT(""), 21, Amber); Help->SetJustification(ETextJustify::Center);
            Place(Root, Help, FVector2D(0, -58), FVector2D(1100, 42), FAnchors(.5f, 1), FVector2D(.5f, 1), 8);
            UBorder* Damage = Panel(TEXT("DamageTint"), FLinearColor(.3f, .012f, .006f, .18f));
            Damage->SetVisibility(ESlateVisibility::HitTestInvisible); Damage->SetRenderOpacity(0); Stretch(G, Damage, 5);
        }

        void Menu(UCanvasPanel* Root)
        {
            UCanvasPanel* M = Make<UCanvasPanel>(TEXT("MenuBackdrop")); Stretch(Root, M, 10);
            UBorder* Base = Panel(TEXT("MenuBase"), Deep); Stretch(M, Base);
            UScaleBox* ArtFit = Make<UScaleBox>(TEXT("TitleArtworkFit")); ArtFit->SetStretch(EStretch::ScaleToFill); ArtFit->SetClipping(EWidgetClipping::ClipToBounds); Stretch(M, ArtFit, 1);
            USizeBox* ArtSize = Make<USizeBox>(TEXT("TitleArtworkSize")); ArtSize->SetWidthOverride(1920); ArtSize->SetHeightOverride(1080); ArtFit->AddChild(ArtSize);
            UImage* Background = Make<UImage>(TEXT("TitleBackground")); Background->SetVisibility(ESlateVisibility::Collapsed); ArtSize->AddChild(Background);
            UBorder* Shade = Panel(TEXT("MenuShade"), FLinearColor(Deep.R, Deep.G, Deep.B, .90f));
            UCanvasPanelSlot* ShadeSlot = M->AddChildToCanvas(Shade); ShadeSlot->SetAnchors(FAnchors(0, 0, 0, 1)); ShadeSlot->SetOffsets(FMargin(0, 0, 760, 0)); ShadeSlot->SetZOrder(2);
            UCanvasPanel* Content = Make<UCanvasPanel>(TEXT("MenuContent")); Stretch(M, Content, 3);
            UImage* Mark = Make<UImage>(TEXT("RelayMark")); Mark->SetVisibility(ESlateVisibility::HitTestInvisible); Place(Content, Mark, FVector2D(96, 100), FVector2D(72, 72));
            UTextBlock* TitleBlock = Text(TEXT("MenuTitle"), TEXT("CINDER\nRELAY"), 82, White, true); TitleBlock->SetAutoWrapText(true);
            Place(Content, TitleBlock, FVector2D(96, 192), FVector2D(620, 210));
            UTextBlock* BodyBlock = Text(TEXT("MenuBody"), TEXT("THE LAST SIGNAL"), 24, Amber); BodyBlock->SetAutoWrapText(true);
            Place(Content, BodyBlock, FVector2D(100, 460), FVector2D(580, 58));
            UVerticalBox* Actions = Make<UVerticalBox>(TEXT("MenuActions")); Place(Content, Actions, FVector2D(80, 530), FVector2D(500, 440));
            const TCHAR* Names[] = {TEXT("Resume"), TEXT("Continue"), TEXT("Restart"), TEXT("Settings"), TEXT("Credits"), TEXT("Exit")};
            const TCHAR* Labels[] = {TEXT("Resume"), TEXT("Continue"), TEXT("New Game"), TEXT("Settings"), TEXT("Credits"), TEXT("Exit Game")};
            for (int32 I = 0; I < UE_ARRAY_COUNT(Names); ++I)
            {
                UButton* B = Button(Names[I], Labels[I]);
                UVerticalBoxSlot* Slot = Actions->AddChildToVerticalBox(B); Slot->SetPadding(FMargin(0, 0, 0, 8));
                Slot->SetHorizontalAlignment(HAlign_Fill);
                if (I == 0) B->SetVisibility(ESlateVisibility::Collapsed);
            }
            UTextBlock* Status = Text(TEXT("SaveAvailability"), TEXT("Checking checkpoints..."), 18, Olive); Status->SetAutoWrapText(true);
            Place(Content, Status, FVector2D(96, -42), FVector2D(620, 50), FAnchors(0, 1), FVector2D(0, 1));
            M->SetVisibility(ESlateVisibility::Collapsed);
        }

        void Modal(UCanvasPanel* Root)
        {
            UBorder* PanelWidget = Panel(TEXT("ModalPanel"), Deep); PanelWidget->SetPadding(FMargin(40));
            UCanvasPanelSlot* Slot = Root->AddChildToCanvas(PanelWidget); Slot->SetAnchors(FAnchors(.10f, .07f, .90f, .93f)); Slot->SetOffsets(FMargin(0)); Slot->SetZOrder(20);
            UVerticalBox* Column = Make<UVerticalBox>(TEXT("ModalLayout")); PanelWidget->SetContent(Column);
            UTextBlock* TitleBlock = Text(TEXT("ModalTitle"), TEXT("SETTINGS"), 50, White, true); TitleBlock->SetAutoWrapText(true);
            Column->AddChildToVerticalBox(TitleBlock)->SetPadding(FMargin(0, 0, 0, 20));
            UTextBlock* BodyBlock = Text(TEXT("ModalBody"), TEXT(""), 24, Olive); BodyBlock->SetAutoWrapText(true);
            Column->AddChildToVerticalBox(BodyBlock)->SetPadding(FMargin(0, 0, 0, 24));
            UScrollBox* Scroll = Make<UScrollBox>(TEXT("ModalScroll")); Scroll->SetConsumeMouseWheel(EConsumeMouseWheel::WhenScrollingPossible);
            UVerticalBoxSlot* ScrollSlot = Column->AddChildToVerticalBox(Scroll); ScrollSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
            UVerticalBox* Choices = Make<UVerticalBox>(TEXT("ModalChoices")); Scroll->AddChild(Choices);
            PanelWidget->SetVisibility(ESlateVisibility::Collapsed);
        }

        void FieldPack(UCanvasPanel* Root)
        {
            UBorder* Pack = Panel(TEXT("PackPanel"), FLinearColor(Deep.R, Deep.G, Deep.B, .98f));
            Stretch(Root, Pack, 15);
            UCanvasPanel* C = Make<UCanvasPanel>(TEXT("PackLayout")); Pack->SetContent(C);
            Place(C, Text(TEXT("PackTitle"), TEXT("ELIAS'S FIELD PACK"), 54, White, true), FVector2D(64, 72), FVector2D(1136, 70));
            Place(C, Text(TEXT("PackChapter"), TEXT("FIELD EQUIPMENT / THE DEAD STATION"), 18, Olive), FVector2D(66, 148), FVector2D(800, 30));
            Place(C, Button(TEXT("PackClose"), TEXT("Close")), FVector2D(-64, 80), FVector2D(176, 54), FAnchors(1, 0), FVector2D(1, 0));
            UBorder* Rule = Panel(TEXT("PackRule"), Color(TEXT("3B4545")));
            UCanvasPanelSlot* RuleSlot = C->AddChildToCanvas(Rule); RuleSlot->SetAnchors(FAnchors(0, 0, 1, 0)); RuleSlot->SetOffsets(FMargin(64, 204, 64, 1));
            UVerticalBox* Categories = Make<UVerticalBox>(TEXT("PackCategories"));
            Place(C, Categories, FVector2D(64, 252), FVector2D(272, 520));
            UBorder* Divider = Panel(TEXT("PackDivider"), Color(TEXT("3B4545")));
            UCanvasPanelSlot* DividerSlot = C->AddChildToCanvas(Divider); DividerSlot->SetAnchors(FAnchors(0, 0, 0, 1)); DividerSlot->SetOffsets(FMargin(368, 248, 1, 128));
            Place(C, Text(TEXT("PackItemHeading"), TEXT("ITEMS"), 18, Olive), FVector2D(408, 250), FVector2D(408, 28));
            UVerticalBox* Items = Make<UVerticalBox>(TEXT("PackItems"));
            Place(C, Items, FVector2D(408, 298), FVector2D(408, 600));
            UBorder* Detail = Panel(TEXT("PackDetailPanel"), Steel);
            UCanvasPanelSlot* DetailSlot = C->AddChildToCanvas(Detail); DetailSlot->SetAnchors(FAnchors(.45f, 0, 1, 1)); DetailSlot->SetOffsets(FMargin(0, 248, 64, 128));
            UCanvasPanel* D = Make<UCanvasPanel>(TEXT("PackDetailLayout")); Detail->SetContent(D);
            UTextBlock* TitleBlock = Text(TEXT("PackDetailTitle"), TEXT(""), 48, White, true); TitleBlock->SetAutoWrapText(true);
            Place(D, TitleBlock, FVector2D(40, 32), FVector2D(620, 72));
            UTextBlock* State = Text(TEXT("PackDetailState"), TEXT(""), 18, Cyan);
            Place(D, State, FVector2D(40, 94), FVector2D(900, 32));
            UImage* Icon = Make<UImage>(TEXT("PackIcon")); Icon->SetVisibility(ESlateVisibility::HitTestInvisible);
            Place(D, Icon, FVector2D(0, 150), FVector2D(520, 260), FAnchors(.5f, 0), FVector2D(.5f, 0));
            UTextBlock* BodyBlock = Text(TEXT("PackDetailBody"), TEXT(""), 22); BodyBlock->SetAutoWrapText(true);
            UCanvasPanelSlot* BodySlot = D->AddChildToCanvas(BodyBlock); BodySlot->SetAnchors(FAnchors(0, 0, 1, 1)); BodySlot->SetOffsets(FMargin(40, 430, 40, 24));
            UTextBlock* Footer = Text(TEXT("PackFooter"), TEXT("I / ESC  Close     UP / DOWN  Select     LEFT / RIGHT  Category"), 20, Olive);
            Place(C, Footer, FVector2D(64, -48), FVector2D(1500, 36), FAnchors(0, 1), FVector2D(0, 1));
            Pack->SetVisibility(ESlateVisibility::Collapsed);
        }
    };
}

bool CRInterfaceLayout::Build(UWidgetTree* Tree, UObject* BodyFont, UObject* TitleFont, FName Panel)
{
    if (!Tree || Tree->RootWidget || (Panel != TEXT("HUDRoot") && Panel != TEXT("HUD") && !Panel.IsNone())) return false;
    FLayout Layout{Tree, BodyFont, TitleFont};
    UCanvasPanel* Root = Layout.Make<UCanvasPanel>(TEXT("HUDRoot"));
    Root->SetVisibility(ESlateVisibility::SelfHitTestInvisible); Tree->RootWidget = Root;
    Layout.Gameplay(Root); Layout.Menu(Root); Layout.FieldPack(Root); Layout.Modal(Root);
    return true;
}

bool UCRInterfaceLibrary::BuildDesignerLayout(UObject* Blueprint, UObject* BodyFont, UObject* TitleFont, FName Panel)
{
#if WITH_EDITOR
    UWidgetTree* Tree = DesignerTree(Blueprint);
    if (!Tree || Tree->RootWidget) return false; // Never rebuild over authored Designer changes.
    Blueprint->Modify(); Tree->Modify();
    if (!CRInterfaceLayout::Build(Tree, BodyFont, TitleFont, Panel)) return false;
    Blueprint->MarkPackageDirty(); return true;
#else
    return false;
#endif
}

bool UCRInterfaceLibrary::UpgradeDesignerArtworkAspect(UObject* Blueprint)
{
#if WITH_EDITOR
    UWidgetTree* Tree=DesignerTree(Blueprint);
    auto* WidgetBP=Cast<UWidgetBlueprint>(Blueprint);
    if(!Tree || !WidgetBP) return false;
    auto Register=[WidgetBP](FName Name)
    { if(!WidgetBP->WidgetVariableNameToGuidMap.Contains(Name)) WidgetBP->OnVariableAdded(Name); };
    if(Tree->FindWidget(TEXT("TitleArtworkFit")))
    { Register(TEXT("TitleArtworkFit")); Register(TEXT("TitleArtworkSize")); return true; }
    auto* Art=Cast<UImage>(Tree->FindWidget(TEXT("TitleBackground")));
    auto* Parent=Art?Cast<UCanvasPanel>(Art->GetParent()):nullptr;
    auto* OldSlot=Art?Cast<UCanvasPanelSlot>(Art->Slot):nullptr;
    if(!Parent || !OldSlot) return false;
    const FAnchorData Layout=OldSlot->GetLayout(); const int32 Z=OldSlot->GetZOrder();
    Blueprint->Modify(); Tree->Modify(); Parent->Modify(); Art->Modify();
    Art->RemoveFromParent();
    auto* Fit=Tree->ConstructWidget<UScaleBox>(UScaleBox::StaticClass(),TEXT("TitleArtworkFit"));
    Fit->SetStretch(EStretch::ScaleToFill); Fit->SetClipping(EWidgetClipping::ClipToBounds);
    auto* Slot=Parent->AddChildToCanvas(Fit); Slot->SetLayout(Layout); Slot->SetZOrder(Z);
    auto* Size=Tree->ConstructWidget<USizeBox>(USizeBox::StaticClass(),TEXT("TitleArtworkSize"));
    Size->SetWidthOverride(1920); Size->SetHeightOverride(1080); Fit->AddChild(Size); Size->AddChild(Art);
    Register(Fit->GetFName()); Register(Size->GetFName());
    Blueprint->MarkPackageDirty(); return true;
#else
    return false;
#endif
}

bool UCRInterfaceLibrary::ConfigureCompositeFont(UObject* Font, UObject* FontFace)
{
#if WITH_EDITOR
    UFont* Target = Cast<UFont>(Font);
    UFontFace* Face = Cast<UFontFace>(FontFace);
    if (!Target || !Face) return false;
    Target->Modify(); Target->FontCacheType = EFontCacheType::Runtime;
    Target->RuntimeFontSource = ERuntimeFontSource::Asset;
    FCompositeFont& Composite = Target->GetMutableInternalCompositeFont();
    Composite.DefaultTypeface.Fonts.Reset();
    FTypefaceEntry& Entry = Composite.DefaultTypeface.Fonts.AddDefaulted_GetRef();
    Entry.Name = TEXT("Regular"); Entry.Font = FFontData(Face);
    Composite.MakeDirty(); Target->PostEditChange(); Target->MarkPackageDirty(); return true;
#else
    return false;
#endif
}

TArray<FName> UCRInterfaceLibrary::GetDesignerWidgetNames(UObject* Blueprint)
{
    TArray<FName> Names;
#if WITH_EDITOR
    if (const UWidgetTree* Tree = DesignerTree(Blueprint))
        Tree->ForEachWidget([&Names](UWidget* Widget) { Names.Add(Widget->GetFName()); });
#endif
    return Names;
}
