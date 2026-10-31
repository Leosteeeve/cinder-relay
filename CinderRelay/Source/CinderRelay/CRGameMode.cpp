#include "CRGameMode.h"
#include "CRCharacter.h"
#include "CRPlayerController.h"
#include "CRChapterStreamingController.h"
#include "CRStreamingAcceptance.h"
#include "CRCombatAcceptance.h"
#include "CRCombatRoute.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

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
		if (!It->IsZoneReady(0))
		{
			WaitingPlayer = NewPlayer;
			UE_LOG(LogTemp, Display, TEXT("CR_STREAM StartupPlayerHeld"));
			return;
		}
		break;
	}
	Super::HandleStartingNewPlayer_Implementation(NewPlayer);
}

void ACRGameMode::ReleaseStartingPlayer()
{
	if (WaitingPlayer.IsValid())
	{
		APlayerController* Player = WaitingPlayer.Get(); WaitingPlayer.Reset();
		Super::HandleStartingNewPlayer_Implementation(Player);
		UE_LOG(LogTemp, Display, TEXT("CR_STREAM StartupPlayerReleased"));
	}
}

void ACRGameMode::BeginPlay()
{
	Super::BeginPlay();
#if !UE_BUILD_SHIPPING
	if (FParse::Param(FCommandLine::Get(), TEXT("CRStreamAcceptance"))) GetWorld()->SpawnActor<ACRStreamingAcceptance>();
	if (FParse::Param(FCommandLine::Get(), TEXT("CRWeaponCheck"))) GetWorld()->SpawnActor<ACRCombatAcceptance>();
	if (FParse::Param(FCommandLine::Get(), TEXT("CRCombatCheck"))) GetWorld()->SpawnActor<ACRCombatRoute>();
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
