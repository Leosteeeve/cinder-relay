#include "CRHUDWidget.h"
#include "CRPlayerController.h"
#include "CRCharacter.h"
#include "CRWeaponComponent.h"
#include "CRWeaponViewComponent.h"
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
	PromptText->SetAutoWrapText(true);
	auto* PromptSlot = Root->AddChildToCanvas(PromptText); PromptSlot->SetAnchors(FAnchors(.18f,1.f,.82f,1.f)); PromptSlot->SetOffsets(FMargin(0,-118,0,64));
	StreamingText = MakeText(TEXT("StreamingStatus"), TEXT(""), 18, Amber);
	auto* StreamingSlot = Root->AddChildToCanvas(StreamingText); StreamingSlot->SetPosition(FVector2D(36, 150)); StreamingSlot->SetAutoSize(true);
	CheckpointText = MakeText(TEXT("CheckpointStatus"), TEXT(""), 18, Amber);
	auto* CheckpointSlot = Root->AddChildToCanvas(CheckpointText); CheckpointSlot->SetPosition(FVector2D(36, 182)); CheckpointSlot->SetAutoSize(true);
	CombatText=MakeText(TEXT("Combat"),TEXT("ROOK-5"),22,Amber);
	auto* CombatSlot=Root->AddChildToCanvas(CombatText); CombatSlot->SetAnchors(FAnchors(1,1)); CombatSlot->SetAlignment(FVector2D(1,1)); CombatSlot->SetPosition(FVector2D(-36,-80)); CombatSlot->SetAutoSize(true);
	DamageBorder=WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(),TEXT("DamageTint"));
	DamageBorder->SetBrushColor(FLinearColor(.8f,.025f,.01f,.22f)); DamageBorder->SetVisibility(ESlateVisibility::HitTestInvisible); DamageBorder->SetRenderOpacity(0);
	auto* DamageSlot=Root->AddChildToCanvas(DamageBorder); DamageSlot->SetAnchors(FAnchors(0,0,1,1)); DamageSlot->SetOffsets(FMargin(0));
	UTextBlock* Controls = MakeText(TEXT("Controls"), TEXT("WASD Move   Shift Sprint   Ctrl Crouch/Slide   Space Jump   LMB Fire   RMB Aim   R Reload   E Interact   Esc Pause"), 14, FLinearColor(0.8f, 0.85f, 0.88f));
	ControlsText=Controls;
	SubtitleText=MakeText(TEXT("Subtitle"),TEXT(""),22,FLinearColor::White);
	SubtitleText->SetJustification(ETextJustify::Center); SubtitleText->SetAutoWrapText(true);
	auto* SubSlot=Root->AddChildToCanvas(SubtitleText); SubSlot->SetAnchors(FAnchors(.15f,1.f,.85f,1.f)); SubSlot->SetOffsets(FMargin(0,-230,0,92));
	Controls->SetAutoWrapText(true);
	auto* ControlsSlot = Root->AddChildToCanvas(Controls); ControlsSlot->SetAnchors(FAnchors(0,1,1,1)); ControlsSlot->SetOffsets(FMargin(36,-62,36,40));
	UTextBlock* Reticle = MakeText(TEXT("Reticle"), TEXT("+"), 18, FLinearColor::White);
	ReticleText=Reticle;
	HitText=MakeText(TEXT("ConfirmedHit"),TEXT("x"),24,FLinearColor::White);
	auto* HitSlot=Root->AddChildToCanvas(HitText); HitSlot->SetAnchors(FAnchors(.5f)); HitSlot->SetAlignment(FVector2D(.5f)); HitSlot->SetAutoSize(true); HitText->SetRenderOpacity(0);
	auto* ReticleSlot = Root->AddChildToCanvas(Reticle); ReticleSlot->SetAnchors(FAnchors(0.5f)); ReticleSlot->SetAlignment(FVector2D(0.5f)); ReticleSlot->SetAutoSize(true);
	MenuBackdrop = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("MenuBackdrop"));
	MenuBackdrop->SetBrushColor(FLinearColor(0.015f, 0.025f, 0.035f, 0.96f));
	MenuBackdrop->SetHorizontalAlignment(HAlign_Center); MenuBackdrop->SetVerticalAlignment(VAlign_Center);
	auto* MenuSlot = Root->AddChildToCanvas(MenuBackdrop); MenuSlot->SetAnchors(FAnchors(0, 0, 1, 1)); MenuSlot->SetOffsets(FMargin(0)); MenuSlot->SetZOrder(10);
	UVerticalBox* Menu = WidgetTree->ConstructWidget<UVerticalBox>(); MenuBackdrop->SetContent(Menu);
	MenuTitle = MakeText(TEXT("MenuTitle"), TEXT("PAUSED"), 38, Amber); MenuTitle->SetJustification(ETextJustify::Center);
	Menu->AddChildToVerticalBox(MenuTitle)->SetPadding(FMargin(16));
	MenuBody = MakeText(TEXT("MenuBody"), TEXT(""), 22, FLinearColor::White); MenuBody->SetJustification(ETextJustify::Center);
	MenuBody->SetWrapTextAt(650);
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
	ContinueButton = MakeButton(TEXT("Continue"), TEXT("Continue from Checkpoint")); ContinueButton->OnClicked.AddDynamic(this, &UCRHUDWidget::ContinueClicked);
	RestartButton = MakeButton(TEXT("Restart"), TEXT("Restart Chapter")); RestartButton->OnClicked.AddDynamic(this, &UCRHUDWidget::RestartClicked);
	MakeButton(TEXT("Exit"), TEXT("Exit Game"))->OnClicked.AddDynamic(this, &UCRHUDWidget::ExitClicked);
	SaveStatusText = MakeText(TEXT("SaveAvailability"), TEXT(""), 16, FLinearColor(.8f,.85f,.88f));
	SaveStatusText->SetWrapTextAt(650); SaveStatusText->SetJustification(ETextJustify::Center);
	Menu->AddChildToVerticalBox(SaveStatusText)->SetPadding(FMargin(12));
	MenuBackdrop->SetVisibility(ESlateVisibility::Collapsed);
}

void UCRHUDWidget::SetObjective(const FText& Text) { if (ObjectiveText) ObjectiveText->SetText(Text); }
void UCRHUDWidget::SetSubtitle(const FText& Text) { if(SubtitleText) SubtitleText->SetText(Text); }
void UCRHUDWidget::SetAssembly(bool Active)
{
	for(UTextBlock* T : {ObjectiveText.Get(),PromptText.Get(),CombatText.Get(),ReticleText.Get(),HitText.Get()})
		if(T) T->SetVisibility(Active?ESlateVisibility::Collapsed:ESlateVisibility::HitTestInvisible);
	if(ControlsText) ControlsText->SetText(FText::FromString(Active?TEXT("SURVEY OPTIC CALIBRATION     Tab Skip & apply upgrade     Esc Pause"):TEXT("WASD Move   Shift Sprint   Ctrl Crouch/Slide   Space Jump   LMB Fire   RMB Aim   R Reload   E Interact   Esc Pause")));
}
void UCRHUDWidget::SetPrompt(const FText& Text) { if (PromptText) PromptText->SetText(Text); }
void UCRHUDWidget::SetStreamingStatus(const FText& Text) { if (StreamingText && !StreamingText->GetText().EqualTo(Text)) StreamingText->SetText(Text); }
void UCRHUDWidget::SetMenu(bool bVisible, bool bEnded, bool bDefeated)
{
	if (!MenuBackdrop) return;
	MenuBackdrop->SetVisibility(bVisible ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
	ResumeButton->SetVisibility(bEnded || bDefeated ? ESlateVisibility::Collapsed : ESlateVisibility::Visible);
	MenuTitle->SetText(FText::FromString(bDefeated ? TEXT("ELIAS HAS FALLEN") : bEnded ? TEXT("MERIDIAN NETWORK") : TEXT("PAUSED")));
	MenuBody->SetText(FText::FromString(bDefeated ? TEXT("Recover from the last saved checkpoint, or restart the chapter.") : bEnded ? TEXT("CONNECTION RESTORED\n\nEnd of The Dead Station prototype") : TEXT("The Dead Station\nEsc or Resume to continue")));
}
void UCRHUDWidget::SetCheckpointStatus(const FText& Text) { if (CheckpointText) CheckpointText->SetText(Text); }
void UCRHUDWidget::SetRecoveryMenu(bool Startup, bool Defeated, bool CanResume, bool CanContinue, const FString& Status)
{
	if (!ContinueButton) return;
	ContinueButton->SetIsEnabled(CanContinue);
	if (auto* Label = Cast<UTextBlock>(ContinueButton->GetContent())) Label->SetText(FText::FromString(Defeated ? TEXT("Retry from Last Checkpoint") : TEXT("Continue from Checkpoint")));
	if (auto* Label = Cast<UTextBlock>(RestartButton->GetContent())) Label->SetText(FText::FromString(Startup ? TEXT("New Game") : TEXT("Restart Chapter")));
	ResumeButton->SetVisibility(CanResume && !Startup ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
	SaveStatusText->SetText(FText::FromString(Status));
	if (Startup) { MenuTitle->SetText(FText::FromString(TEXT("CINDER RELAY"))); MenuBody->SetText(FText::FromString(TEXT("THE DEAD STATION\nNew Game preserves the existing checkpoint until you reach a new one."))); }
}
void UCRHUDWidget::SetCombat(float Health,int32 Magazine,int32 Reserve,bool Reloading)
{
	if (CombatText) CombatText->SetText(FText::FromString(FString::Printf(TEXT("HEALTH %03.0f    ROOK-5  %d / %d%s"),Health,Magazine,Reserve,Reloading?TEXT("   RELOADING"):TEXT(""))));
}
void UCRHUDWidget::ShotFeedback(bool) { ShotPulse=.12f; }
void UCRHUDWidget::HitFeedback(bool Killed) { HitPulse=Killed?.36f:.18f; bKillFeedback=Killed; }
void UCRHUDWidget::DamageFeedback() { HurtPulse=.4f; }
void UCRHUDWidget::NativeTick(const FGeometry& Geometry,float Delta)
{
	Super::NativeTick(Geometry,Delta);
	ShotPulse=FMath::Max(0.f,ShotPulse-Delta); HitPulse=FMath::Max(0.f,HitPulse-Delta); HurtPulse=FMath::Max(0.f,HurtPulse-Delta);
	if(ReticleText) ReticleText->SetRenderScale(FVector2D(1+ShotPulse*2));
	if(HitText) { HitText->SetRenderOpacity(FMath::Clamp(HitPulse*10.f,0.f,1.f)); HitText->SetColorAndOpacity(FSlateColor(bKillFeedback?FLinearColor(1,.45f,.18f):FLinearColor(.9f,.92f,.88f))); HitText->SetRenderScale(FVector2D(bKillFeedback?1.2f:1.f)); }
	if(ReticleText) if(const auto* Pawn=Cast<ACRCharacter>(GetOwningPlayerPawn()))
		ReticleText->SetRenderOpacity(Pawn->Weapon && Pawn->Weapon->bAiming && Pawn->WeaponView && Pawn->WeaponView->HasImportedAppearance()?0.f:1.f);
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
void UCRHUDWidget::ContinueClicked() { if (auto* PC = Cast<ACRPlayerController>(GetOwningPlayer())) PC->ContinueCheckpoint(); }
