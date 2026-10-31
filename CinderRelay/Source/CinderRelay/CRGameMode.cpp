#include "CRGameMode.h"
#include "CRCharacter.h"
#include "CRPlayerController.h"

ACRGameMode::ACRGameMode()
{
	DefaultPawnClass = ACRCharacter::StaticClass();
	PlayerControllerClass = ACRPlayerController::StaticClass();
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
