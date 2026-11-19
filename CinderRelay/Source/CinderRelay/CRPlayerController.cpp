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
#include "CRChapterSaveSubsystem.h"
#include "Engine/GameInstance.h"
#include "CRZonePresentation.h"
#include "CRWeaponViewComponent.h"
#include "CRAudioSettingsSubsystem.h"
#include "CREchoChapter.h"
#include "CRSignalFilm.h"
#include "UObject/ConstructorHelpers.h"

ACRPlayerController::ACRPlayerController()
{
	static ConstructorHelpers::FClassFinder<UCRHUDWidget> AuthoredHUD(TEXT("/Game/Generated/Phase055/Interface/Widgets/WBP_CR_HUDRoot"));
	HUDClass=AuthoredHUD.Succeeded()?AuthoredHUD.Class.Get():UCRHUDWidget::StaticClass();
}

ASpectatorPawn* ACRPlayerController::SpawnSpectatorPawn()
{
	// Native GetPlayerPawn includes spectator pawns. A menu/loading spectator must not
	// fly through unloaded space or override the checkpoint's required initial zone.
	if (const auto* G = GetWorld()->GetAuthGameMode<ACRGameMode>(); G && !G->IsCheckpointReady()) return nullptr;
	return Super::SpawnSpectatorPawn();
}

void ACRPlayerController::BeginPlay()
{
	Super::BeginPlay();
	if (!IsLocalController()) return;
	PlayerCameraManager->ViewPitchMin = -80.f;
	PlayerCameraManager->ViewPitchMax = 80.f;
	if(auto* Audio=GetGameInstance()->GetSubsystem<UCRAudioSettingsSubsystem>())Audio->ApplyMix(GetWorld());
	HUD = CreateWidget<UCRHUDWidget>(this, HUDClass?HUDClass.Get():UCRHUDWidget::StaticClass());
	if (HUD) HUD->AddToViewport();
	if (auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>())
	{
		Mode->OnObjectiveChanged.AddDynamic(this, &ACRPlayerController::ObjectiveChanged);
		Mode->OnRestorationChanged.AddDynamic(this,&ACRPlayerController::RestorationChanged);
		Mode->OnFieldItemsChanged.AddDynamic(this,&ACRPlayerController::FieldItemsChanged);
		Mode->OnMaintenanceChanged.AddDynamic(this, &ACRPlayerController::MaintenanceChanged);
		bLastOptic=Mode->HasSurveyOptic();bLastUpgrade=Mode->HasSurveyUpgrade();
		bStartupMenu = Mode->IsStartupMenu();
	}
	if (auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>()) Store->OnAvailabilityChanged.AddUObject(this, &ACRPlayerController::SaveAvailabilityChanged);
	if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>())
		Echo->OnChanged.AddUObject(this, &ACRPlayerController::EchoUpdated);
	if (auto* Store = GetGameInstance()->GetSubsystem<UCREchoStore>())
		Store->OnAvailabilityChanged.AddUObject(this, &ACRPlayerController::RefreshHUD);
	BindPawn();
	SetInputMode(FInputModeGameOnly());
	bShowMouseCursor = false;
	RefreshHUD();
	if (bStartupMenu) ApplyPause(true);
}

void ACRPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
	// Pause must remain available when the game is paused; movement uses Enhanced Input assets.
	FInputKeyBinding& PauseBinding = InputComponent->BindKey(EKeys::Escape, IE_Pressed, this, &ACRPlayerController::TogglePrototypePause);
	PauseBinding.bExecuteWhenPaused = true;
	InputComponent->BindKey(EKeys::I,IE_Pressed,this,&ACRPlayerController::ToggleFieldPack).bExecuteWhenPaused=true;
	InputComponent->BindKey(EKeys::F5, IE_Pressed, this, &ACRPlayerController::RetryStreaming);
	InputComponent->BindKey(EKeys::Tab, IE_Pressed, this, &ACRPlayerController::SkipAssembly);
	InputComponent->BindKey(EKeys::F1, IE_Pressed, this, &ACRPlayerController::OpenFieldGuide);
	InputComponent->BindKey(EKeys::One, IE_Pressed, this, &ACRPlayerController::SelectIronSights);
}

void ACRPlayerController::OpenFieldGuide()
{
	if (!HUD || bFieldPackOpen || IsAssembling() || ActiveEnding.IsValid() || bPrototypeEnded || bPrototypeDefeated) return;
	if (!bStartupMenu && !bPrototypePaused)
	{
		if (!ObservedPawn.IsValid()) return;
		ApplyPause(true);
	}
	const auto* Chapter = GetWorld()->GetAuthGameMode<ACRGameMode>();
	if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>(); Echo && UCREchoChapter::IsEchoWorld(GetWorld()))
		HUD->ShowFieldGuide(Echo->GetObjectiveText(), Echo->GetGuideText());
	else if (Chapter) HUD->ShowFieldGuide(Chapter->GetObjectiveText(), Chapter->GetObjectiveGuide());
}

void ACRPlayerController::SelectIronSights()
{
	if (!bPrototypePaused && !ActiveEnding.IsValid() && ObservedPawn.IsValid()) ObservedPawn->TryServiceIronSights();
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
		ObservedPawn->Weapon->OnImpact.RemoveDynamic(this, &ACRPlayerController::ConfirmedImpact);
	}
	ObservedPawn = Cast<ACRCharacter>(GetPawn());
	if (ObservedPawn.IsValid())
	{
		if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>(); UCREchoChapter::IsEchoWorld(GetWorld()) && Echo && !Echo->IsStarted() && !bEchoInputHeld)
		{
			bEchoInputHeld = true;
			SetIgnoreMoveInput(true);
			SetIgnoreLookInput(true);
			ObservedPawn->Weapon->SetPresentationLocked(true);
		}
		ObservedPawn->OnPromptChanged.AddDynamic(this, &ACRPlayerController::PromptChanged);
		ObservedPawn->Health->OnHealthChanged.AddDynamic(this, &ACRPlayerController::HealthChanged);
		ObservedPawn->Weapon->OnChanged.AddDynamic(this, &ACRPlayerController::RefreshCombat);
		ObservedPawn->Weapon->OnShot.AddDynamic(this, &ACRPlayerController::ShotFeedback);
		ObservedPawn->Weapon->OnImpact.AddDynamic(this, &ACRPlayerController::ConfirmedImpact);
	}
	RefreshCombat();
	if(HUD && ObservedPawn.IsValid() && !bOpeningShown)
	{
		bOpeningShown=true;
		if(UCREchoChapter::IsEchoWorld(GetWorld()))
			ShowSubtitle(FText::FromString(TEXT("ECHO CROSSING\nELIAS: The line comes ashore here. I'll take a reading at the intake.")),5.f);
		else if(const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>(); G && G->GetObjective()==ECRObjective::ReachWorkshop)
			ShowSubtitle(FText::FromString(TEXT("THE DEAD STATION / 2118\nELIAS: Workshop lights. There may be a way to bring the relay back.")),6.f);
	}
}

void ACRPlayerController::RefreshCombat()
{
	if (HUD && ObservedPawn.IsValid()) HUD->SetCombat(ObservedPawn->Health->Health, ObservedPawn->Weapon->Magazine, ObservedPawn->Weapon->Reserve, ObservedPawn->Weapon->State==ECRWeaponState::Reloading);
	if(HUD&&ObservedPawn.IsValid())
	{
		const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
		HUD->SetSightState(ObservedPawn->Weapon->bAiming&&ObservedPawn->WeaponView&&ObservedPawn->WeaponView->HasImportedAppearance(),G&&G->IsSurveyOpticActive());
		if(bFieldPackOpen)HUD->RefreshFieldPack();
	}
}
void ACRPlayerController::HealthChanged(float,float Damage) { RefreshCombat(); if (HUD && Damage>0) HUD->DamageFeedback(); }
void ACRPlayerController::ShotFeedback(FVector,bool Hit,bool) { if (HUD) HUD->ShotFeedback(Hit); }
void ACRPlayerController::ConfirmedImpact(FVector,FVector,ECRImpactKind Kind) { if(HUD && Kind!=ECRImpactKind::Surface) HUD->HitFeedback(Kind==ECRImpactKind::EnemyKill); }
void ACRPlayerController::PlayerDefeated() { CloseFieldPackForTravel(); AbortAssembly(); if(ActiveEnding.IsValid()) ActiveEnding->AbortPresentation(); ActiveEnding.Reset(); bPrototypeDefeated=true; ApplyPause(true); }

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
		for(TActorIterator<ACRZonePresentation> It(GetWorld()); It; ++It)
			if(It->BeginEnding(this)) { ActiveEnding=*It; RefreshHUD(); return; }
		FinishChapterPresentation();
	}
	RefreshHUD();
}

void ACRPlayerController::FinishChapterPresentation()
{
	ActiveEnding.Reset(); bPrototypeEnded=true; ShowSubtitle(FText::GetEmpty(),.1f); ApplyPause(true);
}

void ACRPlayerController::PromptChanged(FText Prompt)
{
	if (HUD) HUD->SetPrompt(bPrototypePaused ? FText::GetEmpty() : Prompt);
}

void ACRPlayerController::MaintenanceChanged()
{
	if (const auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>(); HUD && Mode)
		HUD->SetObjective(Mode->GetObjectiveText(), false);
}

void ACRPlayerController::RefreshHUD()
{
	if (!HUD) return;
	if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>(); Echo && UCREchoChapter::IsEchoWorld(GetWorld()))
	{
		HUD->SetObjective(Echo->GetObjectiveText());
		HUD->SetPrompt(!bPrototypePaused && ObservedPawn.IsValid() ? ObservedPawn->GetCurrentPrompt() : FText::GetEmpty());
		HUD->SetMenu(bPrototypePaused && !bFieldPackOpen, bPrototypeEnded, bPrototypeDefeated);
		auto* Store = GetGameInstance()->GetSubsystem<UCREchoStore>();
		HUD->SetRecoveryMenu(false, bPrototypeDefeated, GetPawn() && !bPrototypeEnded && !bPrototypeDefeated,
			Store && Store->IsReady() && Store->HasUnfinishedCheckpoint() && !Echo->IsSaving(),
			Echo->IsSaving() ? TEXT("Saving crossing checkpoint…") : TEXT(""));
		RefreshCombat();
		return;
	}
	if (const auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>()) HUD->SetObjective(Mode->GetObjectiveText());
	HUD->SetPrompt(!bPrototypePaused && ObservedPawn.IsValid() ? ObservedPawn->GetCurrentPrompt() : FText::GetEmpty());
	HUD->SetMenu(bPrototypePaused&&!bFieldPackOpen, bPrototypeEnded, bPrototypeDefeated);
	if (auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>())
	{
		auto* EchoStore = GetGameInstance()->GetSubsystem<UCREchoStore>();
		const bool HasEcho = bStartupMenu && EchoStore && EchoStore->IsReady() && EchoStore->HasUnfinishedCheckpoint();
		HUD->SetRecoveryMenu(bStartupMenu, bPrototypeDefeated, GetPawn() != nullptr && !bPrototypeEnded && !bPrototypeDefeated,
			HasEcho || (Store->HasCheckpoint() && !Store->IsBusy()), HasEcho ? TEXT("Echo Crossing checkpoint available.") : Store->GetStatus());
	}
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

void ACRPlayerController::TogglePrototypePause() { if(bFieldPackOpen){ToggleFieldPack();return;} if(HUD&&HUD->HandleBack())return; if (!bStartupMenu && !bPrototypeEnded && !bPrototypeDefeated) ApplyPause(!bPrototypePaused); }
void ACRPlayerController::ResumePrototype() { if(bFieldPackOpen){ToggleFieldPack();return;} if (!bStartupMenu && GetPawn() && !bPrototypeEnded && !bPrototypeDefeated) ApplyPause(false); }
void ACRPlayerController::RestartPrototype()
{
	if (bTravelling || CampaignFilm) return;
	if (UCREchoChapter::IsEchoWorld(GetWorld())) { TravelToEcho(false); return; }
	if (bStartupMenu)
		PresentFilm(false, FSimpleDelegate::CreateUObject(this, &ACRPlayerController::StartFirstChapter));
	else StartFirstChapter();
}
void ACRPlayerController::StartFirstChapter()
{
	if (auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>()) Store->PrepareNewChapter();
	TravelToChapter();
}
void ACRPlayerController::TravelToChapter()
{
	if (bTravelling) return;
	bTravelling=true;
	bPendingContinue = false;
	CloseFieldPackForTravel();
	if(ActiveEnding.IsValid()) ActiveEnding->AbortPresentation(); ActiveEnding.Reset();
	AbortAssembly();
	ApplyPause(false);
	UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
}
void ACRPlayerController::ContinueCheckpoint()
{
	if (bTravelling || CampaignFilm) return;
	if (UCREchoChapter::IsEchoWorld(GetWorld())) { EnterEchoCrossing(true); return; }
	auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
	if (!Store || Store->IsBusy() || bPendingContinue) return;
	bPendingContinue = true;
	if (!Store->ScanSlots()) { bPendingContinue = false; ShowCheckpointFeedback(TEXT("CHECKPOINT UNAVAILABLE — try again after the current write.")); }
}
void ACRPlayerController::SaveAvailabilityChanged()
{
	auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
	RefreshHUD();
	if (!Store || Store->IsBusy() || !bPendingContinue) return;
	bPendingContinue = false;
	if (Store->PrepareContinue()) TravelToChapter();
	else ShowCheckpointFeedback(TEXT("CHECKPOINT UNAVAILABLE — files retained. New Game is available."));
}
void ACRPlayerController::ShowCheckpointFeedback(const FString& Text)
{
	if (!HUD) return;
	HUD->SetCheckpointStatus(FText::FromString(Text));
	if(Text==TEXT("CHECKPOINT SAVED")||Text.StartsWith(TEXT("CHECKPOINT RESTORED")))HUD->PlayInterfaceSound(TEXT("Confirm"));
	GetWorldTimerManager().SetTimer(CheckpointMessageTimer, FTimerDelegate::CreateWeakLambda(this, [this](){ if (HUD) HUD->SetCheckpointStatus(FText::GetEmpty()); }), 5.f, false);
}
void ACRPlayerController::ExitPrototype() { AbortAssembly(); if(ActiveEnding.IsValid()) ActiveEnding->AbortPresentation(); ActiveEnding.Reset(); UKismetSystemLibrary::QuitGame(this, this, EQuitPreference::Quit, false); }
void ACRPlayerController::SetAssembly(ACRWorkbench* Workbench)
{ ActiveWorkbench=Workbench; if(HUD) HUD->SetAssembly(Workbench!=nullptr, Workbench && Workbench->IsIronService()); }
void ACRPlayerController::SkipAssembly()
{ if(!bPrototypePaused) { if(ActiveWorkbench.IsValid()) ActiveWorkbench->Skip(); else if(ActiveEnding.IsValid()) ActiveEnding->SkipEnding(); } }
void ACRPlayerController::AbortAssembly()
{ if(ActiveWorkbench.IsValid()) ActiveWorkbench->Abort(); }
void ACRPlayerController::ShowSubtitle(const FText& Text,float Seconds)
{
	if(!HUD) return; HUD->SetSubtitle(Text);
	GetWorldTimerManager().SetTimer(SubtitleTimer,FTimerDelegate::CreateWeakLambda(this,[this](){ if(HUD) HUD->SetSubtitle(FText::GetEmpty()); }),Seconds,false);
}
void ACRPlayerController::EndPlay(const EEndPlayReason::Type Reason)
{
	if (CampaignFilm) { CampaignFilm->RemoveFromParent(); CampaignFilm=nullptr; }
	if (auto* Store = GetGameInstance()->GetSubsystem<UCREchoStore>()) Store->OnAvailabilityChanged.RemoveAll(this);
	if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>()) Echo->OnChanged.RemoveAll(this);
	CloseFieldPackForTravel();
	if (auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>())
	{
		Mode->OnObjectiveChanged.RemoveDynamic(this, &ACRPlayerController::ObjectiveChanged);
		Mode->OnRestorationChanged.RemoveDynamic(this, &ACRPlayerController::RestorationChanged);
		Mode->OnFieldItemsChanged.RemoveDynamic(this, &ACRPlayerController::FieldItemsChanged);
		Mode->OnMaintenanceChanged.RemoveDynamic(this, &ACRPlayerController::MaintenanceChanged);
	}
	if (HUD) { HUD->RemoveFromParent(); HUD = nullptr; }
	if(ActiveEnding.IsValid()) ActiveEnding->AbortPresentation(); ActiveEnding.Reset();
	if (auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>()) Store->OnAvailabilityChanged.RemoveAll(this);
	AbortAssembly(); GetWorldTimerManager().ClearTimer(SubtitleTimer); GetWorldTimerManager().ClearTimer(CheckpointMessageTimer); Super::EndPlay(Reason);
}
