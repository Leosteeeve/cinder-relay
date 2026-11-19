#include "CRHUDWidget.h"
#include "CRFieldPackModel.h"
#include "CRCharacter.h"
#include "CREchoChapter.h"
#include "CRWeaponComponent.h"
#include "Blueprint/WidgetTree.h"
#include "Brushes/SlateColorBrush.h"
#include "Components/ButtonSlot.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/Texture2D.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"

namespace
{
const TCHAR* const Categories[] = {TEXT("Equipment"), TEXT("Supplies"), TEXT("Components"), TEXT("Mission Items")};
FLinearColor PackColor(const TCHAR* Hex) { return FLinearColor::FromSRGBColor(FColor::FromHex(Hex)); }
}

void UCRHUDWidget::SetFieldPack(bool Open)
{
    bPack = Open;
    Visibility(TEXT("PackPanel"), Open);
    Visibility(TEXT("MenuBackdrop"), false);
    Visibility(TEXT("GameplayLayer"), !Open && !bAssembly && !bMenu);
    auto* Subtitle = Text(TEXT("Subtitle"));
    Visibility(TEXT("SubtitlePanel"), !Open && Subtitle && !Subtitle->GetText().IsEmpty());
    if (Open)
    {
        PackCategory = 0;
        PackSelection = 0;
        RefreshFieldPack();
    }
    else MenuNavigation.Reset();
    PlayInterfaceSound(Open ? TEXT("UIConfirm") : TEXT("UICancel"));
}

void UCRHUDWidget::RefreshFieldPack()
{
    if (!bPack) return;
    TRACE_CPUPROFILER_EVENT_SCOPE(CR055_FieldPackUpdate);
    const auto* Player = Cast<ACRCharacter>(GetOwningPlayerPawn());
    const auto* Chapter = GetWorld()->GetAuthGameMode<ACRGameMode>();
    if (!Player || !Chapter) return;
    auto Items = CRFieldPack::Items(CRFieldPack::Read(*Chapter, *Player), PackCategory);
    if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>(); Echo && UCREchoChapter::IsEchoWorld(GetWorld()))
    {
        Put(TEXT("PackChapter"), TEXT("ECHO CROSSING   /   EQUIPMENT"));
        if (PackCategory == 3)
        {
            const bool Strip = Echo->GetStep() >= 2;
            Items = {{TEXT("PowerModule"),TEXT("Archive reference strip"),Strip ? TEXT("COPIED") : TEXT("AT THE ARCHIVE"),
                Strip ? TEXT("Return bearing: 120 degrees. Turn the aerial to match the strip, then use TEST RETURN.") : TEXT("The archive holds the reference for the aerial."),Strip ? 1 : 0}};
            if (Echo->HasFieldLog()) Items.Add({TEXT("PowerModule"),TEXT("Observer's log"),TEXT("RECOVERED"),
                TEXT("The first pulse dies at the river. Record the second return. Recovered at the survey walk overlook."),1});
        }
        if (PackCategory == 1 && !Items.IsEmpty())
            Items[0].Description = FString::Printf(TEXT("Magazine  %02d / 05     Reserve  %02d"), Player->Weapon->Magazine, Player->Weapon->Reserve);
        if (!Chapter->HasSurveyOptic() && (PackCategory == 0 || PackCategory == 2) && !Items.IsEmpty())
            Items.Last().Description = TEXT("The optional optic can be carried here from the Workshop in Chapter 01.");
    }
    if (Items.IsEmpty()) return;
    PackSelection = FMath::Clamp(PackSelection, 0, Items.Num() - 1);
    const auto& Item = Items[PackSelection];
    auto* CategoryList = Cast<UVerticalBox>(WidgetTree->FindWidget(TEXT("PackCategories")));
    auto* ItemList = Cast<UVerticalBox>(WidgetTree->FindWidget(TEXT("PackItems")));
    if (!CategoryList || !ItemList) return;
    CategoryList->ClearChildren();
    ItemList->ClearChildren();
    MenuNavigation.Reset();

    auto AddChoice = [this](UVerticalBox* Box, int32 Id, const FString& Label, bool Selected)
    {
        auto* Button = WidgetTree->ConstructWidget<UCRInterfaceAction>();
        Button->Configure(this, Id);
        FButtonStyle Style;
        Style.SetNormal(FSlateColorBrush(PackColor(Selected ? TEXT("3D514F") : TEXT("1B292D"))))
            .SetHovered(FSlateColorBrush(PackColor(TEXT("425855"))))
            .SetPressed(FSlateColorBrush(PackColor(TEXT("4A4537"))))
            .SetNormalPadding(FMargin(18, 16)).SetPressedPadding(FMargin(18, 17, 18, 15));
        Button->SetStyle(Style);
        auto* LabelWidget = WidgetTree->ConstructWidget<UTextBlock>();
        LabelWidget->SetFont(FSlateFontInfo(BodyFont, 23));
        LabelWidget->SetText(FText::FromString(Selected ? FString(TEXT(">   ")) + Label : Label));
        LabelWidget->SetColorAndOpacity(PackColor(Selected ? TEXT("F0C48A") : TEXT("E8E3D8")));
        LabelWidget->SetAutoWrapText(true);
        Button->SetContent(LabelWidget);
        if (auto* Slot = Cast<UButtonSlot>(LabelWidget->Slot)) Slot->SetHorizontalAlignment(HAlign_Left);
        Box->AddChildToVerticalBox(Button)->SetPadding(FMargin(0, 0, 0, 9));
        return Button;
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Categories); ++Index)
        AddChoice(CategoryList, 200 + Index, Categories[Index], Index == PackCategory);
    for (int32 Index = 0; Index < Items.Num(); ++Index)
        MenuNavigation.Add(AddChoice(ItemList, 220 + Index, Items[Index].Name, Index == PackSelection));
    Focused = PackSelection;
    Put(TEXT("PackDetailTitle"), Item.Name);
    // Quantity here is actual inventory. An installed module stays intelligible
    // after its carried quantity becomes zero, and the ROOK readout owns ammo.
    Put(TEXT("PackDetailState"), PackCategory == 3
        ? FString::Printf(TEXT("%s   /   IN PACK %d"), *Item.State, Item.Quantity) : Item.State);
    Put(TEXT("PackDetailBody"), Item.Description);
    Put(TEXT("PackFooter"), TEXT("LEFT / RIGHT   Category       UP / DOWN   Item       I / ESC   Close"));
    if (auto* Icon = Cast<UImage>(WidgetTree->FindWidget(TEXT("PackIcon"))))
    {
        const FString Name = TEXT("T_CR055_Icon") + Item.Icon.ToString();
        const FSoftObjectPath Path(TEXT("/Game/Generated/Phase055/Interface/Textures/") + Name + TEXT(".") + Name);
        Icon->SetBrushFromTexture(Cast<UTexture2D>(Path.ResolveObject()));
    }
}
