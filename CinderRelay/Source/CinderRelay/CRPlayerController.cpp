#include "CRPlayerController.h"
#include "CRCharacter.h"
#include "CRHUDWidget.h"
#include "Camera/PlayerCameraManager.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "InputCoreTypes.h"
#include "Components/InputComponent.h"
#include "Engine/World.h"

void ACRPlayerController::BeginPlay()
{
	Super::BeginPlay();
	if (!IsLocalController()) return;
	PlayerCameraManager->ViewPitchMin = -80.f;
	PlayerCameraManager->ViewPitchMax = 80.f;
	HUD = CreateWidget<UCRHUDWidget>(this, UCRHUDWidget::StaticClass());
	if (HUD) HUD->AddToViewport();
	if (auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>())
		Mode->OnObjectiveChanged.AddDynamic(this, &ACRPlayerController::ObjectiveChanged);
	BindPawn();
	SetInputMode(FInputModeGameOnly());
	bShowMouseCursor = false;
	RefreshHUD();
}

void ACRPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
	// Pause must remain available when the game is paused; movement uses Enhanced Input assets.
	FInputKeyBinding& PauseBinding = InputComponent->BindKey(EKeys::Escape, IE_Pressed, this, &ACRPlayerController::TogglePrototypePause);
	PauseBinding.bExecuteWhenPaused = true;
}

void ACRPlayerController::OnPossess(APawn* InPawn)
{
	Super::OnPossess(InPawn);
	BindPawn();
}

void ACRPlayerController::BindPawn()
{
	if (ObservedPawn.IsValid()) ObservedPawn->OnPromptChanged.RemoveDynamic(this, &ACRPlayerController::PromptChanged);
	ObservedPawn = Cast<ACRCharacter>(GetPawn());
	if (ObservedPawn.IsValid()) ObservedPawn->OnPromptChanged.AddDynamic(this, &ACRPlayerController::PromptChanged);
}

void ACRPlayerController::ObjectiveChanged(ECRObjective Objective)
{
	if (Objective == ECRObjective::Complete)
	{
		bPrototypeEnded = true;
		ApplyPause(true);
	}
	RefreshHUD();
}

void ACRPlayerController::PromptChanged(FText Prompt)
{
	if (HUD) HUD->SetPrompt(bPrototypePaused ? FText::GetEmpty() : Prompt);
}

void ACRPlayerController::RefreshHUD()
{
	if (!HUD) return;
	if (const auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>()) HUD->SetObjective(Mode->GetObjectiveText());
	HUD->SetPrompt(!bPrototypePaused && ObservedPawn.IsValid() ? ObservedPawn->GetCurrentPrompt() : FText::GetEmpty());
	HUD->SetMenu(bPrototypePaused, bPrototypeEnded);
}

void ACRPlayerController::ApplyPause(bool bPause)
{
	if (ObservedPawn.IsValid()) ObservedPawn->ClearHeldActions();
	FlushPressedKeys();
	SetPause(bPause);
	bPrototypePaused = bPause;
	bShowMouseCursor = bPause;
	RefreshHUD();
	if (bPause && HUD)
	{
		FInputModeUIOnly Mode;
		Mode.SetWidgetToFocus(HUD->TakeWidget());
		Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		SetInputMode(Mode);
		HUD->SetKeyboardFocus();
	}
	else SetInputMode(FInputModeGameOnly());
}

void ACRPlayerController::TogglePrototypePause() { if (!bPrototypeEnded) ApplyPause(!bPrototypePaused); }
void ACRPlayerController::ResumePrototype() { if (!bPrototypeEnded) ApplyPause(false); }
void ACRPlayerController::RestartPrototype()
{
	ApplyPause(false);
	UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
}
void ACRPlayerController::ExitPrototype() { UKismetSystemLibrary::QuitGame(this, this, EQuitPreference::Quit, false); }
