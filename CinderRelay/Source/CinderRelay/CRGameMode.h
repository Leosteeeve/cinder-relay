#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "CRGameMode.generated.h"

UENUM(BlueprintType)
enum class ECRObjective : uint8
{
	ReachWorkshop, FindModule, RestorePower, InvestigateSignal, Complete
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FCRObjectiveChanged, ECRObjective, Objective);

/** One chapter-local state, intentionally not a quest framework. */
UCLASS()
class CINDERRELAY_API ACRGameMode : public AGameModeBase
{
	GENERATED_BODY()
public:
	ACRGameMode();
	UPROPERTY(BlueprintAssignable) FCRObjectiveChanged OnObjectiveChanged;
	UFUNCTION(BlueprintPure) ECRObjective GetObjective() const { return Objective; }
	UFUNCTION(BlueprintPure) FText GetObjectiveText() const;
	bool TryAdvance(ECRObjective Expected);
private:
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Chapter", meta=(AllowPrivateAccess="true"))
	ECRObjective Objective = ECRObjective::ReachWorkshop;
};
