#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRGameMode.h"
#include "CRZonePresentation.generated.h"
class UPointLightComponent;
class ULevelSequence;
class ALevelSequenceActor;
class ACRPlayerController;
class ACRCharacter;
struct FStreamableHandle;
// Bunker-owned cosmetic sequencing. It never changes objectives or persistent IDs.
UCLASS()
class CINDERRELAY_API ACRZonePresentation : public AActor
{
    GENERATED_BODY()
public:
    ACRZonePresentation();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UPointLightComponent> StatusLight;
    UPROPERTY(EditAnywhere, Category="Presentation") TSoftObjectPtr<ULevelSequence> PowerSequence;
    UPROPERTY(EditAnywhere, Category="Presentation") TSoftObjectPtr<ULevelSequence> EndingSequence;
    bool BeginEnding(ACRPlayerController* PlayerController);
    void SkipEnding();
    void AbortPresentation();
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UPROPERTY(Transient) TObjectPtr<ALevelSequenceActor> PlaybackActor;
    TSharedPtr<FStreamableHandle> AssetLoad;
    TWeakObjectPtr<ACRPlayerController> Controller;
    TWeakObjectPtr<ACRCharacter> Player;
    bool bEnding=false, bFinalizing=false, bOwnsInput=false;
    uint32 PlaybackGeneration=0;
    bool Play(ULevelSequence* Sequence);
    void Cleanup();
    void AssetsReady();
    UFUNCTION() void ObjectiveChanged(ECRObjective Objective);
    UFUNCTION() void Finished();
    UFUNCTION() void Stopped();
};
