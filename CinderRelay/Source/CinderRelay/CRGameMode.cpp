#include "CRGameMode.h"
#include "CRChapterMechanics.h"
#include "CRCharacter.h"
#include "CRPlayerController.h"
#include "CRChapterStreamingController.h"
#include "CRStreamingAcceptance.h"
#include "CRCombatAcceptance.h"
#include "CRCombatRoute.h"
#include "CRInterfaceAcceptance.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "CRChapterSaveGame.h"
#include "CRCheckpointRoute.h"
#include "CRChapterSaveSubsystem.h"
#include "CRCheckpoint.h"
#include "CRHealthComponent.h"
#include "CRWeaponComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/GameInstance.h"

void ACRGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
	Super::InitGame(MapName, Options, ErrorMessage);
	BootstrapStarted = FPlatformTime::Seconds();
	bUseCheckpoints = MapName.EndsWith(TEXT("L_CH01_Persistent"));
#if !UE_BUILD_SHIPPING
	bLegacyAcceptance = FParse::Param(FCommandLine::Get(), TEXT("CRStreamAcceptance")) || FParse::Param(FCommandLine::Get(), TEXT("CRCombatCheck"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CRWeaponCheck")) || FParse::Param(FCommandLine::Get(), TEXT("CRRestorationCheck"));
#endif
	if (auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>())
	{
		RunEpoch = Store->BeginRun();
		UCRChapterSaveGame* Snapshot = nullptr;
		const bool Intent = Store->ConsumeTravelIntent(Snapshot);
		bStartupMenu = bUseCheckpoints && !Intent && !bLegacyAcceptance;
		if (Snapshot)
		{
			if (RestoreSession(*Snapshot)) { RestoreSnapshot = Snapshot; StartingCheckpoint = Snapshot->CheckpointId; PassedCheckpoint = Snapshot->TargetZone; }
			else { bStartupMenu = true; UE_LOG(LogTemp, Error, TEXT("CR04_RESTORE Invalid travel snapshot; player remains held")); }
		}
		Store->OnWritten.AddUObject(this, &ACRGameMode::CheckpointWritten);
	}
	UE_LOG(LogTemp, Display, TEXT("CR04_RESTORE Bootstrap checkpoint=%s zone=%d objective=%d restored=%d menu=%d epoch=%llu"), *StartingCheckpoint.ToString(), GetStartingZone(), int32(Objective), RestoreSnapshot != nullptr, bStartupMenu, RunEpoch);
}
int32 ACRGameMode::GetStartingZone() const { return UCRChapterSaveGame::CheckpointZone(StartingCheckpoint); }
bool ACRGameMode::HasPassedCheckpoint(FName Id) const { return bLegacyAcceptance || UCRChapterSaveGame::CheckpointZone(Id) <= PassedCheckpoint; }
bool ACRGameMode::RequestCheckpoint(const ACRCheckpoint& Anchor, ACRCharacter& Player)
{
	auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
	auto* PC = Cast<ACRPlayerController>(Player.GetController()); FString Reason;
	const int32 Zone = UCRChapterSaveGame::CheckpointZone(Anchor.CheckpointId);
	if (!bBootstrapReady || bLegacyAcceptance || Zone < 0 || HasPassedCheckpoint(Anchor.CheckpointId) || !Store || !PC || Store->IsBusy()
		|| PC->bPrototypePaused || PC->IsAssembling() || Player.Health->IsDead() || !Player.GetCharacterMovement()->IsMovingOnGround()
		|| Player.Weapon->State != ECRWeaponState::Ready || GetWorld()->GetTimeSeconds() - Player.Health->GetLastDamageTime() < 2
		|| !UCRChapterSaveGame::ObjectiveAllowsCheckpoint(Anchor.CheckpointId, Objective) || !Anchor.ValidateSpawn(Reason)) return false;
	// New Game and Restart preserve an existing disk checkpoint until a later natural checkpoint.
	if (Zone == 0 && !Store->AreSlotsMissing()) { PassedCheckpoint = 0; return true; }
	auto* Snapshot = NewObject<UCRChapterSaveGame>(this); CaptureSession(*Snapshot);
	Snapshot->CheckpointId = Anchor.CheckpointId; Snapshot->TargetZone = Zone;
	Snapshot->PlayerHealth = Player.Health->Health; Snapshot->MagazineAmmo = Player.Weapon->Magazine; Snapshot->ReserveAmmo = Player.Weapon->Reserve;
	Snapshot->Seal();
	return Store->RequestWrite(*Snapshot, RunEpoch);
}
void ACRGameMode::CheckpointWritten(const UCRChapterSaveGame* Save, bool Success, uint64 Epoch)
{
	if (Epoch != RunEpoch || !Save) return;
	if (Success) PassedCheckpoint = FMath::Max(PassedCheckpoint, Save->TargetZone);
	if (auto* PC = Cast<ACRPlayerController>(GetWorld()->GetFirstPlayerController()))
		PC->ShowCheckpointFeedback(Success ? TEXT("CHECKPOINT SAVED") : TEXT("CHECKPOINT UNAVAILABLE — previous checkpoint retained. Re-enter to retry."));
}
void ACRGameMode::EndPlay(const EEndPlayReason::Type Reason)
{
	if (auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>()) Store->OnWritten.RemoveAll(this);
	Super::EndPlay(Reason);
}

void ACRGameMode::CaptureSession(UCRChapterSaveGame& S) const
{
	S.CurrentObjective = Objective; S.DefeatedEnemyIds = DefeatedEnemies.Array(); S.CollectedPickupIds = CollectedPickups.Array();
	S.SurveyOpticCollected = bSurveyOptic; S.SurveyOpticSourceId = SurveyOpticSource; S.SurveyUpgradeApplied = bSurveyUpgrade;
	S.ClaimedStoryBeatIds = StoryBeats.Array();
}
bool ACRGameMode::RestoreSession(const UCRChapterSaveGame& S)
{
	FString Reason; if (!S.Validate(Reason)) return false;
	// CP00 rolls the opening back. Later checkpoints reconstruct a clear return route
	// for existing schema1 saves, including runs that originally used the east walk.
	bYardHoistPowered = S.TargetZone >= 1;
	DiagnosticStep=0; RelayServiceStep=0; bAccessStopped=false; bUseIronSights=false;
	Objective = S.CurrentObjective; DefeatedEnemies.Reset(); CollectedPickups.Reset(); StoryBeats.Reset();
	for (FName Id : S.DefeatedEnemyIds) DefeatedEnemies.Add(Id);
	for (FName Id : S.CollectedPickupIds) CollectedPickups.Add(Id);
	for (FName Id : S.ClaimedStoryBeatIds) StoryBeats.Add(Id);
	bSurveyOptic = S.SurveyOpticCollected; SurveyOpticSource = S.SurveyOpticSourceId; bSurveyUpgrade = S.SurveyUpgradeApplied;
	// Bootstrap runs before streamed BeginPlay. Do not broadcast objective progression or replay story.
	return true;
}

bool ACRGameMode::TryCollectSurveyOptic(FName SourceId)
{
	if (bSurveyOptic || SourceId.IsNone()) return false;
	bSurveyOptic = true; SurveyOpticSource = SourceId;
	UE_LOG(LogTemp, Display, TEXT("CR03_SALVAGE CR03_SurveyOptic source=%s"), *SourceId.ToString());
	OnRestorationChanged.Broadcast(); return true;
}
bool ACRGameMode::TryApplySurveyUpgrade()
{
	if (!bSurveyOptic || bSurveyUpgrade) return false;
	bSurveyUpgrade = true;
	UE_LOG(LogTemp, Display, TEXT("CR03_UPGRADE CR03_Rook5_SurveyOptic applied"));
	OnRestorationChanged.Broadcast(); return true;
}

bool ACRGameMode::SelectSurveyOptic(bool Active)
{
	if (!bSurveyUpgrade || IsSurveyOpticActive() == Active) return false;
	bUseIronSights = !Active;
	OnRestorationChanged.Broadcast();
	return true;
}

ACRGameMode::ACRGameMode()
{
	DefaultPawnClass = ACRCharacter::StaticClass();
	PlayerControllerClass = ACRPlayerController::StaticClass();
}

void ACRGameMode::RegisterYardHoist()
{
	if (bHasYardHoist) return;
	bHasYardHoist = true;
	OnMaintenanceChanged.Broadcast();
}

bool ACRGameMode::PowerYardHoist()
{
	if (bYardHoistPowered) return false;
	bYardHoistPowered = true;
	OnMaintenanceChanged.Broadcast();
	return true;
}

void ACRGameMode::RegisterWorkshopDiagnostic()
{
	if (bWorkshopDiagnostic) return;
	bWorkshopDiagnostic = true;
	OnMaintenanceChanged.Broadcast();
}

void ACRGameMode::RegisterAccessMachinery()
{
	if (bAccessMachinery) return;
	bAccessMachinery = true;
	OnMaintenanceChanged.Broadcast();
}

void ACRGameMode::RegisterRelayService()
{
	if (bRelayService) return;
	bRelayService = true;
	OnMaintenanceChanged.Broadcast();
}

bool ACRGameMode::TryRelayServiceStep(int32 Step)
{
	if (!bRelayService || Objective != ECRObjective::RestorePower || Step != RelayServiceStep || Step >= 2)
		return false;
	++RelayServiceStep;
	OnMaintenanceChanged.Broadcast();
	UE_LOG(LogTemp, Display, TEXT("CR06_EXPANSION RelayService=%d"), RelayServiceStep);
	return true;
}

bool ACRGameMode::TryDiagnosticStep(int32 Step)
{
	if(Objective != ECRObjective::FindModule || !bWorkshopDiagnostic) return false;
	const int32 Next = CRChapterMechanics::DiagnosticStep(DiagnosticStep, Step);
	if(Next == DiagnosticStep) return false;
	DiagnosticStep=Next; OnMaintenanceChanged.Broadcast();
	UE_LOG(LogTemp, Display, TEXT("CR06_MAINTENANCE Diagnostic=%d"), DiagnosticStep);
	return true;
}
void ACRGameMode::StopAccessMachinery()
{
	if(!bAccessMachinery || bAccessStopped || !IsRelayServiceReady() || Objective != ECRObjective::RestorePower) return;
	bAccessStopped=true; OnMaintenanceChanged.Broadcast();
	UE_LOG(LogTemp, Display, TEXT("CR06_MAINTENANCE AccessStopped"));
}

void ACRGameMode::HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer)
{
	for (TActorIterator<ACRChapterStreamingController> It(GetWorld()); It; ++It)
	{
		WaitingPlayer = NewPlayer;
		UE_LOG(LogTemp, Display, TEXT("CR_STREAM StartupPlayerHeld checkpoint=%s"), *StartingCheckpoint.ToString());
		ReleaseStartingPlayer(); return;
	}
	Super::HandleStartingNewPlayer_Implementation(NewPlayer);
}

bool ACRGameMode::ReleaseStartingPlayer()
{
	if (bBootstrapReady) return true;
	if (!WaitingPlayer.IsValid() || bStartupMenu) return false;
	for (TActorIterator<ACRChapterStreamingController> It(GetWorld()); It; ++It) if (!It->IsZoneReady(GetStartingZone())) return false;
	ACRCheckpoint* Anchor = nullptr;
	for (TActorIterator<ACRCheckpoint> It(GetWorld()); It; ++It) if (It->CheckpointId == StartingCheckpoint)
	{
		if (Anchor) { UE_LOG(LogTemp, Error, TEXT("CR04_RESTORE Duplicate anchor %s"), *StartingCheckpoint.ToString()); return false; }
		Anchor = *It;
	}
	FString Reason;
	if (!Anchor || !Anchor->ValidateSpawn(Reason))
	{
		if (!Anchor) Reason = TEXT("Checkpoint anchor missing");
		if (LastBootstrapFailure != Reason) { LastBootstrapFailure = Reason; UE_LOG(LogTemp, Error, TEXT("CR04_RESTORE Held: %s"), *Reason); }
		if (auto* PC = Cast<ACRPlayerController>(WaitingPlayer.Get())) PC->ShowCheckpointFeedback(TEXT("CHECKPOINT UNAVAILABLE — unsafe anchor. Esc for recovery options."));
		return false;
	}
	APlayerController* Controller = WaitingPlayer.Get();
	RestartPlayerAtTransform(Controller, Anchor->GetActorTransform());
	auto* Player = Cast<ACRCharacter>(Controller->GetPawn());
	if (!Player) return false;
	if (RestoreSnapshot && (!Player->Health->RestoreCheckpointHealth(RestoreSnapshot->PlayerHealth) || !Player->Weapon->RestoreCheckpointAmmo(RestoreSnapshot->MagazineAmmo, RestoreSnapshot->ReserveAmmo)))
	{ Player->Destroy(); UE_LOG(LogTemp, Error, TEXT("CR04_RESTORE Player component values rejected")); return false; }
	bBootstrapReady = true; WaitingPlayer.Reset();
	// Spawn overlap precedes Possess in native RestartPlayerAtTransform. Explicitly arm
	// the same bounded stable-state check after possession, so a fresh CP00 is not missed.
	if (GetStartingZone() == 0) Anchor->BeginCheckpointAttempt(*Player);
	if (auto* PC = Cast<ACRPlayerController>(Controller)) { PC->RefreshHUD(); if (RestoreSnapshot) PC->ShowCheckpointFeedback(TEXT("CHECKPOINT RESTORED")); }
	UE_LOG(LogTemp, Display, TEXT("CR04_RESTORE SafeControl checkpoint=%s zone=%d objective=%d health=%.1f magazine=%d reserve=%d upgrade=%d reconstruction_ms=%.3f position=%s"),
		*StartingCheckpoint.ToString(), GetStartingZone(), int32(Objective), Player->Health->Health, Player->Weapon->Magazine, Player->Weapon->Reserve, HasSurveyUpgrade(), (FPlatformTime::Seconds()-BootstrapStarted)*1000, *Player->GetActorLocation().ToString());
	RestoreSnapshot = nullptr;
	return true;
}

void ACRGameMode::BeginPlay()
{
	Super::BeginPlay();
#if !UE_BUILD_SHIPPING
	int32 CheckpointRoute = 0;
	FString InterfaceCheck;
	if (FParse::Value(FCommandLine::Get(), TEXT("CR055InterfaceCheck="), InterfaceCheck)) GetWorld()->SpawnActor<ACRInterfaceAcceptance>();
	if (FParse::Value(FCommandLine::Get(), TEXT("CRCheckpointRoute="), CheckpointRoute)) GetWorld()->SpawnActor<ACRCheckpointRoute>();
	if (FParse::Param(FCommandLine::Get(), TEXT("CRStreamAcceptance"))) GetWorld()->SpawnActor<ACRStreamingAcceptance>();
	if (FParse::Param(FCommandLine::Get(), TEXT("CRWeaponCheck"))) GetWorld()->SpawnActor<ACRCombatAcceptance>();
	if (FParse::Param(FCommandLine::Get(), TEXT("CRCombatCheck")) || FParse::Param(FCommandLine::Get(), TEXT("CRRestorationCheck"))) GetWorld()->SpawnActor<ACRCombatRoute>();
#endif
}

FText ACRGameMode::GetObjectiveText() const
{
	switch (Objective)
	{
	case ECRObjective::ReachWorkshop:
		if (!bHasYardHoist) return NSLOCTEXT("Cinder", "ReachLegacyWorkshop", "Follow the rail line to the Workshop.");
		return bYardHoistPowered
			? NSLOCTEXT("Cinder", "YardStoreOpen", "Reach the Workshop shutter.\nThe raised wagon opens the Signal Store route.")
			: NSLOCTEXT("Cinder", "YardShutter", "Reach the Workshop shutter.\nOptional: power the hoist at the yellow booth.");
	case ECRObjective::FindModule:
		if (bWorkshopDiagnostic)
		{
			switch (GetDiagnosticStep())
			{
			case 0: return NSLOCTEXT("Cinder", "RouteSupplyBay", "Bay 01 / Route bench supply\nEnter the signed Module Test Hall.");
			case 1: return NSLOCTEXT("Cinder", "VerifyLoadBay", "Bay 02 / Verify the load\nFollow the blue bay signs.");
			case 2: return NSLOCTEXT("Cinder", "ReleaseCradleBay", "Bay 03 / Release the module cradle\nFollow the blue bay signs.");
			default: break;
			}
		}
		return bWorkshopDiagnostic
			? NSLOCTEXT("Cinder", "CollectModuleViaReturn", "Collect the power module.\nTake the amber return to the bench.")
			: NSLOCTEXT("Cinder", "CollectModule", "Collect the replacement power module.");
	case ECRObjective::RestorePower:
		if (!IsRelayServiceReady())
			return GetRelayServiceStep() == 0
				? NSLOCTEXT("Cinder", "PrimeServiceBus", "A / Prime the auxiliary bus.\nCross the shuttle or use the side walk.")
				: NSLOCTEXT("Cinder", "OpenServiceInterlock", "B / Release the interlock.\nFollow the blue signs past the bus.");
		return IsAccessStopped()
			? NSLOCTEXT("Cinder", "InstallModule", "Install the module at Relay Nine.")
			: NSLOCTEXT("Cinder", "StopShuttle", "Latch the machinery stop.\nTake the amber return to the relay.");
	case ECRObjective::InvestigateSignal: return NSLOCTEXT("Cinder", "ReadSignal", "Inspect the MERIDIAN signal console.");
	default: return NSLOCTEXT("Cinder", "Complete", "Connection restored.");
	}
}

FText ACRGameMode::GetObjectiveGuide() const
{
	switch (Objective)
	{
	case ECRObjective::ReachWorkshop:
		if (!bHasYardHoist) return NSLOCTEXT("Cinder", "GuideLegacyWorkshop", "Follow the tracks east to the Workshop. Take cover along the way.");
		return bYardHoistPowered
			? NSLOCTEXT("Cinder", "GuideRaisedWagon", "Cross under the raised wagon for the Signal Store.\nLeave the apron by its east gate, then use E at the Workshop shutter.")
			: NSLOCTEXT("Cinder", "GuideYardHoist", "The yellow booth powers the wagon lift. The noise carries across the yard.\nFor a quiet approach, follow the north track east to the Workshop.");
	case ECRObjective::FindModule:
		if (GetDiagnosticStep() == 0 && bWorkshopDiagnostic)
			return NSLOCTEXT("Cinder", "GuideBay01", "Look for MODULE TEST HALL on the south side of the Workshop.\nOperate the console beneath the Bay 01 sign.");
		if (!IsModuleReleased())
			return NSLOCTEXT("Cinder", "GuideNextBay", "Follow the blue bay signs through the raised safety gate.\nThe bay numbers follow the order of the module test.");
		return NSLOCTEXT("Cinder", "GuideModule", "Use the open crosswalk or follow the amber lane back to the bench.\nCollect the module. Servicing the sights is optional.");
	case ECRObjective::RestorePower:
		if (!IsRelayServiceReady())
			return GetRelayServiceStep() == 0
				? NSLOCTEXT("Cinder", "GuideBus", "Go down the ramp and cross via the shuttle or side walk.\nLook for AUXILIARY SERVICE on the far side and operate A.")
				: NSLOCTEXT("Cinder", "GuideInterlock", "Go around the bus equipment wall on the right.\nContinue through the opening marked B. Look for the amber return.");
		if (!IsAccessStopped())
			return NSLOCTEXT("Cinder", "GuideStop", "Cross through the open interlock to the amber return walk.\nLatch the stop in the main chamber, then fit the module.");
		return NSLOCTEXT("Cinder", "GuideInstall", "Use E at the orange Relay Nine terminal to fit the power module.");
	case ECRObjective::InvestigateSignal:
		return NSLOCTEXT("Cinder", "GuideSignal", "Use E at the cyan console in front of the large carrier meter.\nWatch the needle for the returning signal.");
	default:
		return FText::GetEmpty();
	}
}

bool ACRGameMode::TryAdvance(ECRObjective Expected)
{
	if (Objective != Expected || Objective == ECRObjective::Complete) return false;
	Objective = static_cast<ECRObjective>(static_cast<uint8>(Objective) + 1);
	UE_LOG(LogTemp, Display, TEXT("CR_OBJECTIVE %d"), static_cast<int32>(Objective));
	OnObjectiveChanged.Broadcast(Objective);
	return true;
}
