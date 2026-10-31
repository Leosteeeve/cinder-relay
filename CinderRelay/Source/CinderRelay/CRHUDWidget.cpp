#include "CRHUDWidget.h"
#include "CRPlayerController.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "InputCoreTypes.h"

void UCRHUDWidget::NativeOnInitialized()
{
	Super::NativeOnInitialized();
	SetIsFocusable(true);
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("HUDRoot"));
	WidgetTree->RootWidget = Root;
	auto MakeText = [this](const TCHAR* Name, const FString& Text, int32 Size, FLinearColor Color)
	{
		UTextBlock* Block = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), FName(Name));
		Block->SetText(FText::FromString(Text));
		FSlateFontInfo Font = Block->GetFont(); Font.Size = Size; Block->SetFont(Font);
		Block->SetColorAndOpacity(FSlateColor(Color));
		Block->SetShadowOffset(FVector2D(1.f, 2.f));
		Block->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.9f));
		return Block;
	};
	const FLinearColor Amber(1.f, 0.62f, 0.2f);
	UTextBlock* Chapter = MakeText(TEXT("Chapter"), TEXT("CINDER RELAY  /  THE DEAD STATION"), 18, Amber);
	auto* ChapterSlot = Root->AddChildToCanvas(Chapter); ChapterSlot->SetPosition(FVector2D(36, 28)); ChapterSlot->SetAutoSize(true);
	ObjectiveText = MakeText(TEXT("Objective"), TEXT(""), 24, FLinearColor::White);
	ObjectiveText->SetAutoWrapText(true);
	auto* ObjectiveSlot = Root->AddChildToCanvas(ObjectiveText); ObjectiveSlot->SetPosition(FVector2D(36, 64)); ObjectiveSlot->SetSize(FVector2D(670, 90));
	PromptText = MakeText(TEXT("Prompt"), TEXT(""), 22, Amber);
	PromptText->SetJustification(ETextJustify::Center);
	auto* PromptSlot = Root->AddChildToCanvas(PromptText); PromptSlot->SetAnchors(FAnchors(0.5f, 1.f)); PromptSlot->SetAlignment(FVector2D(0.5f, 1.f)); PromptSlot->SetPosition(FVector2D(0, -82)); PromptSlot->SetAutoSize(true);
	StreamingText = MakeText(TEXT("StreamingStatus"), TEXT(""), 18, Amber);
	auto* StreamingSlot = Root->AddChildToCanvas(StreamingText); StreamingSlot->SetPosition(FVector2D(36, 150)); StreamingSlot->SetAutoSize(true);
	CombatText=MakeText(TEXT("Combat"),TEXT("ROOK-5"),22,Amber);
	auto* CombatSlot=Root->AddChildToCanvas(CombatText); CombatSlot->SetAnchors(FAnchors(1,1)); CombatSlot->SetAlignment(FVector2D(1,1)); CombatSlot->SetPosition(FVector2D(-36,-56)); CombatSlot->SetAutoSize(true);
	DamageBorder=WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(),TEXT("DamageTint"));
	DamageBorder->SetBrushColor(FLinearColor(.8f,.025f,.01f,.22f)); DamageBorder->SetVisibility(ESlateVisibility::HitTestInvisible); DamageBorder->SetRenderOpacity(0);
	auto* DamageSlot=Root->AddChildToCanvas(DamageBorder); DamageSlot->SetAnchors(FAnchors(0,0,1,1)); DamageSlot->SetOffsets(FMargin(0));
	UTextBlock* Controls = MakeText(TEXT("Controls"), TEXT("WASD Move   Shift Sprint   Ctrl Crouch   Space Jump   LMB Fire   RMB Aim   R Reload   E Interact   Esc Pause"), 14, FLinearColor(0.8f, 0.85f, 0.88f));
	auto* ControlsSlot = Root->AddChildToCanvas(Controls); ControlsSlot->SetAnchors(FAnchors(0.f, 1.f)); ControlsSlot->SetAlignment(FVector2D(0.f, 1.f)); ControlsSlot->SetPosition(FVector2D(36, -26)); ControlsSlot->SetAutoSize(true);
	UTextBlock* Reticle = MakeText(TEXT("Reticle"), TEXT("+"), 18, FLinearColor::White);
	ReticleText=Reticle;
	auto* ReticleSlot = Root->AddChildToCanvas(Reticle); ReticleSlot->SetAnchors(FAnchors(0.5f)); ReticleSlot->SetAlignment(FVector2D(0.5f)); ReticleSlot->SetAutoSize(true);
	MenuBackdrop = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("MenuBackdrop"));
	MenuBackdrop->SetBrushColor(FLinearColor(0.015f, 0.025f, 0.035f, 0.96f));
	MenuBackdrop->SetHorizontalAlignment(HAlign_Center); MenuBackdrop->SetVerticalAlignment(VAlign_Center);
	auto* MenuSlot = Root->AddChildToCanvas(MenuBackdrop); MenuSlot->SetAnchors(FAnchors(0, 0, 1, 1)); MenuSlot->SetOffsets(FMargin(0)); MenuSlot->SetZOrder(10);
	UVerticalBox* Menu = WidgetTree->ConstructWidget<UVerticalBox>(); MenuBackdrop->SetContent(Menu);
	MenuTitle = MakeText(TEXT("MenuTitle"), TEXT("PAUSED"), 38, Amber); MenuTitle->SetJustification(ETextJustify::Center);
	Menu->AddChildToVerticalBox(MenuTitle)->SetPadding(FMargin(16));
	MenuBody = MakeText(TEXT("MenuBody"), TEXT(""), 22, FLinearColor::White); MenuBody->SetJustification(ETextJustify::Center);
	Menu->AddChildToVerticalBox(MenuBody)->SetPadding(FMargin(12, 12, 12, 30));
	auto MakeButton = [this, Menu, &MakeText](const TCHAR* Name, const FString& Label)
	{
		UButton* Button = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), FName(Name));
		UTextBlock* LabelBlock = MakeText(*(FString(Name) + TEXT("Label")), Label, 22, FLinearColor::White);
		LabelBlock->SetJustification(ETextJustify::Center); Button->SetContent(LabelBlock);
		Menu->AddChildToVerticalBox(Button)->SetPadding(FMargin(18, 8));
		return Button;
	};
	ResumeButton = MakeButton(TEXT("Resume"), TEXT("Resume")); ResumeButton->OnClicked.AddDynamic(this, &UCRHUDWidget::ResumeClicked);
	MakeButton(TEXT("Restart"), TEXT("Restart prototype"))->OnClicked.AddDynamic(this, &UCRHUDWidget::RestartClicked);
	MakeButton(TEXT("Exit"), TEXT("Exit prototype"))->OnClicked.AddDynamic(this, &UCRHUDWidget::ExitClicked);
	MenuBackdrop->SetVisibility(ESlateVisibility::Collapsed);
}

void UCRHUDWidget::SetObjective(const FText& Text) { if (ObjectiveText) ObjectiveText->SetText(Text); }
void UCRHUDWidget::SetPrompt(const FText& Text) { if (PromptText) PromptText->SetText(Text); }
void UCRHUDWidget::SetStreamingStatus(const FText& Text) { if (StreamingText && !StreamingText->GetText().EqualTo(Text)) StreamingText->SetText(Text); }
void UCRHUDWidget::SetMenu(bool bVisible, bool bEnded, bool bDefeated)
{
	if (!MenuBackdrop) return;
	MenuBackdrop->SetVisibility(bVisible ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
	ResumeButton->SetVisibility(bEnded || bDefeated ? ESlateVisibility::Collapsed : ESlateVisibility::Visible);
	MenuTitle->SetText(FText::FromString(bDefeated ? TEXT("ELIAS HAS FALLEN") : bEnded ? TEXT("MERIDIAN NETWORK") : TEXT("PAUSED")));
	MenuBody->SetText(FText::FromString(bDefeated ? TEXT("Restart to try First Contact again.") : bEnded ? TEXT("CONNECTION RESTORED\n\nEnd of The Dead Station prototype") : TEXT("The Dead Station\nEsc or Resume to continue")));
}
void UCRHUDWidget::SetCombat(float Health,int32 Magazine,int32 Reserve,bool Reloading)
{
	if (CombatText) CombatText->SetText(FText::FromString(FString::Printf(TEXT("HEALTH %03.0f    ROOK-5  %d / %d%s"),Health,Magazine,Reserve,Reloading?TEXT("   RELOADING"):TEXT(""))));
}
void UCRHUDWidget::ShotFeedback(bool Hit) { ShotPulse=.18f; if(Hit) HitPulse=.22f; }
void UCRHUDWidget::DamageFeedback() { HurtPulse=.4f; }
void UCRHUDWidget::NativeTick(const FGeometry& Geometry,float Delta)
{
	Super::NativeTick(Geometry,Delta);
	ShotPulse=FMath::Max(0.f,ShotPulse-Delta); HitPulse=FMath::Max(0.f,HitPulse-Delta); HurtPulse=FMath::Max(0.f,HurtPulse-Delta);
	if (ReticleText) { ReticleText->SetText(FText::FromString(HitPulse>0?TEXT("X"):TEXT("+"))); ReticleText->SetRenderScale(FVector2D(1+ShotPulse*2)); ReticleText->SetColorAndOpacity(FSlateColor(HitPulse>0?FLinearColor(1,.55f,.2f):FLinearColor::White)); }
	if (DamageBorder) DamageBorder->SetRenderOpacity(HurtPulse/.4f);
}
FReply UCRHUDWidget::NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& KeyEvent)
{
	if (KeyEvent.GetKey() == EKeys::Escape)
	{
		if (auto* PC = Cast<ACRPlayerController>(GetOwningPlayer())) PC->TogglePrototypePause();
		return FReply::Handled();
	}
	return Super::NativeOnKeyDown(Geometry, KeyEvent);
}
void UCRHUDWidget::ResumeClicked() { if (auto* PC = Cast<ACRPlayerController>(GetOwningPlayer())) PC->ResumePrototype(); }
void UCRHUDWidget::RestartClicked() { if (auto* PC = Cast<ACRPlayerController>(GetOwningPlayer())) PC->RestartPrototype(); }
void UCRHUDWidget::ExitClicked() { if (auto* PC = Cast<ACRPlayerController>(GetOwningPlayer())) PC->ExitPrototype(); }
