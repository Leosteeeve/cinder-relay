#include "CRHUDWidget.h"
#include "CRFieldPackModel.h"
#include "CRCharacter.h"
#include "CRPlayerController.h"
#include "Blueprint/WidgetTree.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/TextBlock.h"
#include "Components/Image.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Engine/Texture2D.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
namespace {
const TCHAR* Categories[]={TEXT("Equipment"),TEXT("Supplies"),TEXT("Components"),TEXT("Mission Items")};
FLinearColor PackColor(const TCHAR* Hex){return FLinearColor::FromSRGBColor(FColor::FromHex(Hex));}
}
void UCRHUDWidget::SetFieldPack(bool Open)
{
    bPack=Open;Visibility(TEXT("PackPanel"),Open);Visibility(TEXT("MenuBackdrop"),false);
    Visibility(TEXT("GameplayLayer"),!Open&&!bAssembly&&!bMenu);Visibility(TEXT("SubtitlePanel"),!Open&&Text(TEXT("Subtitle"))&&!Text(TEXT("Subtitle"))->GetText().IsEmpty());
    if(Open){PackCategory=0;PackSelection=0;RefreshFieldPack();PlayInterfaceSound(TEXT("UIConfirm"));}
    else {PlayInterfaceSound(TEXT("UICancel"));MenuNavigation.Reset();}
}
void UCRHUDWidget::RefreshFieldPack()
{
    if(!bPack)return;
    TRACE_CPUPROFILER_EVENT_SCOPE(CR055_FieldPackUpdate);
    const auto* P=Cast<ACRCharacter>(GetOwningPlayerPawn());const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();if(!P||!G)return;
    const auto Items=CRFieldPack::Items(CRFieldPack::Read(*G,*P),PackCategory);if(Items.IsEmpty())return;
    PackSelection=FMath::Clamp(PackSelection,0,Items.Num()-1);const auto& Item=Items[PackSelection];
    auto* CatBox=Cast<UVerticalBox>(WidgetTree->FindWidget(TEXT("PackCategories")));auto* ItemBox=Cast<UVerticalBox>(WidgetTree->FindWidget(TEXT("PackItems")));if(!CatBox||!ItemBox)return;
    CatBox->ClearChildren();ItemBox->ClearChildren();MenuNavigation.Reset();
    auto Make=[this](UVerticalBox* Box,int32 Id,const FString& Label,bool Selected)
    {
        auto* B=WidgetTree->ConstructWidget<UCRInterfaceAction>();B->Configure(this,Id);
        FButtonStyle S;FSlateBrush N;N.DrawAs=ESlateBrushDrawType::Box;N.TintColor=PackColor(Selected?TEXT("30413F"):TEXT("182122"));FSlateBrush H=N;H.TintColor=PackColor(TEXT("3E4C46"));S.SetNormal(N).SetHovered(H).SetPressed(H).SetNormalPadding(FMargin(20,18)).SetPressedPadding(FMargin(20,19,20,17));B->SetStyle(S);
        auto* T=WidgetTree->ConstructWidget<UTextBlock>();T->SetText(FText::FromString(Label));T->SetFont(FSlateFontInfo(BodyFont,24));T->SetColorAndOpacity(PackColor(Selected?TEXT("C99553"):TEXT("E8E3D8")));T->SetAutoWrapText(true);B->SetContent(T);Box->AddChildToVerticalBox(B)->SetPadding(FMargin(0,0,0,12));return B;
    };
    for(int32 C=0;C<4;++C)Make(CatBox,200+C,Categories[C],C==PackCategory);
    for(int32 I=0;I<Items.Num();++I)MenuNavigation.Add(Make(ItemBox,220+I,FString::Printf(TEXT("%s\n%s  /  %02d"),*Items[I].Name,*Items[I].State,Items[I].Quantity),I==PackSelection));
    Focused=PackSelection;
    Put(TEXT("PackDetailTitle"),Item.Name);Put(TEXT("PackDetailState"),FString::Printf(TEXT("%s  /  QUANTITY %02d"),*Item.State,Item.Quantity));Put(TEXT("PackDetailBody"),Item.Description);
    Put(TEXT("PackFooter"),TEXT("I / ESC  Close     UP / DOWN  Select     LEFT / RIGHT  Category     ENTER  Inspect"));
    auto* Icon=Cast<UImage>(WidgetTree->FindWidget(TEXT("PackIcon")));
    const FSoftObjectPath IconPath(FString::Printf(TEXT("/Game/Generated/Phase055/Interface/Textures/T_CR055_Icon%s.T_CR055_Icon%s"),*Item.Icon.ToString(),*Item.Icon.ToString()));
    if(Icon){Icon->SetBrushFromTexture(Cast<UTexture2D>(IconPath.ResolveObject()));}
}
