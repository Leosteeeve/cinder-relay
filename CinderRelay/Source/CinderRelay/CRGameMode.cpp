#include "CRGameMode.h"
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

ACRGameMode::ACRGameMode()
{
	DefaultPawnClass = ACRCharacter::StaticClass();
	PlayerControllerClass = ACRPlayerController::StaticClass();
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
	case ECRObjective::ReachWorkshop: return NSLOCTEXT("Cinder", "Reach", "Reach the maintenance workshop.");
	case ECRObjective::FindModule: return NSLOCTEXT("Cinder", "Module", "Find a functional power module.");
	case ECRObjective::RestorePower: return NSLOCTEXT("Cinder", "Power", "Restore power to Relay Nine.");
	case ECRObjective::InvestigateSignal: return NSLOCTEXT("Cinder", "Signal", "Investigate the restored signal.");
	default: return NSLOCTEXT("Cinder", "Complete", "Connection restored.");
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
