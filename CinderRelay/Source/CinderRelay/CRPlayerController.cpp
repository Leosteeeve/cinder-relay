#include "CRPlayerController.h"
#include "CRCharacter.h"
#include "CRHealthComponent.h"
#include "CRWeaponComponent.h"
#include "CRHUDWidget.h"
#include "Camera/PlayerCameraManager.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "InputCoreTypes.h"
#include "Components/InputComponent.h"
#include "Engine/World.h"
#include "CRChapterStreamingController.h"
#include "EngineUtils.h"
#include "CRWorkbench.h"
#include "TimerManager.h"

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
	InputComponent->BindKey(EKeys::F5, IE_Pressed, this, &ACRPlayerController::RetryStreaming);
	InputComponent->BindKey(EKeys::Tab, IE_Pressed, this, &ACRPlayerController::SkipAssembly);
}

void ACRPlayerController::SetStreamingStatus(const FText& Text) { if (HUD) HUD->SetStreamingStatus(Text); }
void ACRPlayerController::RetryStreaming()
{
	for (TActorIterator<ACRChapterStreamingController> It(GetWorld()); It; ++It) { It->RetryFailedLoads(); break; }
}

void ACRPlayerController::OnPossess(APawn* InPawn)
{
	Super::OnPossess(InPawn);
	BindPawn();
}

void ACRPlayerController::BindPawn()
{
	if (ObservedPawn.IsValid())
	{
		ObservedPawn->OnPromptChanged.RemoveDynamic(this, &ACRPlayerController::PromptChanged);
		ObservedPawn->Health->OnHealthChanged.RemoveDynamic(this, &ACRPlayerController::HealthChanged);
		ObservedPawn->Weapon->OnChanged.RemoveDynamic(this, &ACRPlayerController::RefreshCombat);
		ObservedPawn->Weapon->OnShot.RemoveDynamic(this, &ACRPlayerController::ShotFeedback);
	}
	ObservedPawn = Cast<ACRCharacter>(GetPawn());
	if (ObservedPawn.IsValid())
	{
		ObservedPawn->OnPromptChanged.AddDynamic(this, &ACRPlayerController::PromptChanged);
		ObservedPawn->Health->OnHealthChanged.AddDynamic(this, &ACRPlayerController::HealthChanged);
		ObservedPawn->Weapon->OnChanged.AddDynamic(this, &ACRPlayerController::RefreshCombat);
		ObservedPawn->Weapon->OnShot.AddDynamic(this, &ACRPlayerController::ShotFeedback);
	}
	RefreshCombat();
}

void ACRPlayerController::RefreshCombat()
{
	if (HUD && ObservedPawn.IsValid()) HUD->SetCombat(ObservedPawn->Health->Health, ObservedPawn->Weapon->Magazine, ObservedPawn->Weapon->Reserve, ObservedPawn->Weapon->State==ECRWeaponState::Reloading);
}
void ACRPlayerController::HealthChanged(float,float Damage) { RefreshCombat(); if (HUD && Damage>0) HUD->DamageFeedback(); }
void ACRPlayerController::ShotFeedback(FVector,bool Hit,bool) { if (HUD) HUD->ShotFeedback(Hit); }
void ACRPlayerController::PlayerDefeated() { AbortAssembly(); bPrototypeDefeated=true; ApplyPause(true); }

void ACRPlayerController::ObjectiveChanged(ECRObjective Objective)
{
	if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>())
	{
		if(Objective==ECRObjective::FindModule && G->ClaimStoryBeat(TEXT("CR03_WorkshopDiscovery")))
			ShowSubtitle(FText::FromString(TEXT("ELIAS: A calibration bench. I can still put this place to use.")));
		if(Objective==ECRObjective::InvestigateSignal && G->ClaimStoryBeat(TEXT("CR03_RelayEcho")))
			ShowSubtitle(FText::FromString(TEXT("[A broken carrier tone returns.]\nELIAS: Something on the other end is still listening.")));
	}
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
	HUD->SetMenu(bPrototypePaused, bPrototypeEnded, bPrototypeDefeated);
	RefreshCombat();
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

void ACRPlayerController::TogglePrototypePause() { if (!bPrototypeEnded && !bPrototypeDefeated) ApplyPause(!bPrototypePaused); }
void ACRPlayerController::ResumePrototype() { if (!bPrototypeEnded && !bPrototypeDefeated) ApplyPause(false); }
void ACRPlayerController::RestartPrototype()
{
	AbortAssembly();
	ApplyPause(false);
	UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
}
void ACRPlayerController::ExitPrototype() { AbortAssembly(); UKismetSystemLibrary::QuitGame(this, this, EQuitPreference::Quit, false); }
void ACRPlayerController::SetAssembly(ACRWorkbench* Workbench)
{ ActiveWorkbench=Workbench; if(HUD) HUD->SetAssembly(Workbench!=nullptr); }
void ACRPlayerController::SkipAssembly()
{ if(!bPrototypePaused && ActiveWorkbench.IsValid()) ActiveWorkbench->Skip(); }
void ACRPlayerController::AbortAssembly()
{ if(ActiveWorkbench.IsValid()) ActiveWorkbench->Abort(); }
void ACRPlayerController::ShowSubtitle(const FText& Text,float Seconds)
{
	if(!HUD) return; HUD->SetSubtitle(Text);
	GetWorldTimerManager().SetTimer(SubtitleTimer,FTimerDelegate::CreateWeakLambda(this,[this](){ if(HUD) HUD->SetSubtitle(FText::GetEmpty()); }),Seconds,false);
}
void ACRPlayerController::EndPlay(const EEndPlayReason::Type Reason)
{ AbortAssembly(); GetWorldTimerManager().ClearTimer(SubtitleTimer); Super::EndPlay(Reason); }
