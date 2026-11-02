#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRCheckpointRoute.generated.h"
class ACRCharacter;
class ACRPlayerController;
class ACRChapterStreamingController;
class UInputAction;
/** Bounded Development acceptance route using existing Enhanced Input actions and native maps. */
UCLASS(NotBlueprintable, Transient)
class ACRCheckpointRoute : public AActor
{
    GENERATED_BODY()
public:
    ACRCheckpointRoute();
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float Delta) override;
private:
#if !UE_BUILD_SHIPPING
    TWeakObjectPtr<ACRCharacter> Player;
    TWeakObjectPtr<ACRPlayerController> PC;
    TWeakObjectPtr<ACRChapterStreamingController> Streaming;
    FString Stage = TEXT("menu"), AfterWalk;
    TArray<FVector2D> Waypoints;
    int32 Route = 0, SlideEdgeCase=0;
    bool bSlideEdges=false;
    bool bGateCheck=false;
    int32 GateCheckStep=0;
    double GateCheckAt=0;
    float GatePausedWorldTime=0;
    FTransform GatePausedPose;
    void TickGateCheck();
    FVector SlideEdgeOrigin=FVector::ZeroVector;
    TWeakObjectPtr<AActor> SlideObstacle;
    AActor* SlideBlock(FVector Position,FVector Size);
    void FinishSlideEdge();
    bool bFinished = false, bPauseChecked = false, bHeld = false, bLifecycle = false;
    double Started = 0, StageStarted = 0, LastShot = 0, PausedAt = 0;
    float PausedPosition = 0;
    void Next(const FString& Name);
    void Walk(TArray<FVector2D> Points, const FString& After);
    void Inject(const UInputAction* Action, float Value = 1);
    bool Interact(AActor* Actor, const FVector& Point);
    void Check(bool Condition, const TCHAR* Message);
    void Finish(bool Success, const FString& Message);
    void Travel(bool Continue, int32 NextJourney);
    void Record(float Delta);
#endif
};
