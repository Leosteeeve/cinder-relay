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
	void ReleaseStartingPlayer();
	UFUNCTION(BlueprintPure) bool IsEnemyDefeated(FName Id) const { return DefeatedEnemies.Contains(Id); }
	UFUNCTION(BlueprintCallable) void RecordEnemyDefeated(FName Id) { if(!Id.IsNone()) DefeatedEnemies.Add(Id); }
	UFUNCTION(BlueprintPure) bool IsPickupCollected(FName Id) const { return CollectedPickups.Contains(Id); }
	UFUNCTION(BlueprintCallable) void RecordPickupCollected(FName Id) { if(!Id.IsNone()) CollectedPickups.Add(Id); }
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Chapter|Combat") TSet<FName> DefeatedEnemies;
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Chapter|Combat") TSet<FName> CollectedPickups;
protected:
	virtual void HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer) override;
	virtual void BeginPlay() override;
private:
	TWeakObjectPtr<APlayerController> WaitingPlayer;
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Chapter", meta=(AllowPrivateAccess="true"))
	ECRObjective Objective = ECRObjective::ReachWorkshop;
};
