#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "CRGameMode.h"
#include "CRChapterSaveGame.generated.h"

/** Chapter01 values only. No world objects, timers, animation state or delegates. */
UCLASS()
class CINDERRELAY_API UCRChapterSaveGame : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY(SaveGame) int32 SchemaVersion = 1;
    UPROPERTY(SaveGame) FName ChapterId = TEXT("CH01_DeadStation");
    UPROPERTY(SaveGame) FName CheckpointId = TEXT("CP00_START_YARD");
    UPROPERTY(SaveGame) int32 TargetZone = 0;
    UPROPERTY(SaveGame) int64 SaveGeneration = 1;
    UPROPERTY(SaveGame) ECRObjective CurrentObjective = ECRObjective::ReachWorkshop;
    UPROPERTY(SaveGame) float PlayerHealth = 100;
    UPROPERTY(SaveGame) int32 MagazineAmmo = 5;
    UPROPERTY(SaveGame) int32 ReserveAmmo = 25;
    UPROPERTY(SaveGame) TArray<FName> DefeatedEnemyIds;
    UPROPERTY(SaveGame) TArray<FName> CollectedPickupIds;
    UPROPERTY(SaveGame) bool SurveyOpticCollected = false;
    UPROPERTY(SaveGame) FName SurveyOpticSourceId;
    UPROPERTY(SaveGame) bool SurveyUpgradeApplied = false;
    UPROPERTY(SaveGame) TArray<FName> ClaimedStoryBeatIds;
    UPROPERTY(SaveGame) uint32 PayloadChecksum = 0;

    void Seal();
    bool Validate(FString& Reason) const;
    static int32 CheckpointZone(FName Id);
    static bool ObjectiveAllowsCheckpoint(FName Id, ECRObjective Objective);
private:
    uint32 ComputeChecksum() const;
};
