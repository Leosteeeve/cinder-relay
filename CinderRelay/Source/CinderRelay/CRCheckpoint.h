#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRCheckpoint.generated.h"
class UBoxComponent;
class UArrowComponent;
class ACRCharacter;

/** Three persistent, stable chapter anchors. Geometry remains owned by native sublevels. */
UCLASS()
class CINDERRELAY_API ACRCheckpoint : public AActor
{
    GENERATED_BODY()
public:
    ACRCheckpoint();
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Checkpoint") FName CheckpointId;
    UPROPERTY(VisibleAnywhere, Category="Checkpoint") TObjectPtr<UBoxComponent> Trigger;
    UPROPERTY(VisibleAnywhere, Category="Checkpoint") TObjectPtr<UArrowComponent> Facing;
    bool ValidateSpawn(FString& Reason) const;
    void BeginCheckpointAttempt(ACRCharacter& Player);
    UFUNCTION(CallInEditor, BlueprintCallable, Category="Checkpoint") bool SnapToSafeFloor();
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UFUNCTION() void Enter(UPrimitiveComponent* Overlapped, AActor* Other, UPrimitiveComponent* OtherComponent, int32 BodyIndex, bool FromSweep, const FHitResult& Hit);
    void TryCheckpoint();
    TWeakObjectPtr<ACRCharacter> Candidate;
    FTimerHandle RetryTimer;
    double AttemptStarted = 0;
};
