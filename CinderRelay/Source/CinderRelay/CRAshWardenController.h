#pragma once
#include "CoreMinimal.h"
#include "AIController.h"
#include "Perception/AIPerceptionTypes.h"
#include "CRAshWardenController.generated.h"
class UAIPerceptionComponent;
class UAISenseConfig_Sight;
class UAISenseConfig_Hearing;
class ANavigationData;
class ACRAshWarden;
UENUM(BlueprintType) enum class ECRWardenState:uint8 { WaitingNavigation, Idle, Investigate, Combat, Search, Return, Dead };
UCLASS()
class CINDERRELAY_API ACRAshWardenController : public AAIController
{
    GENERATED_BODY()
public:
    ACRAshWardenController();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UAIPerceptionComponent> Senses;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly) ECRWardenState State=ECRWardenState::WaitingNavigation;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly) bool bNavigationReady=false;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly) bool bSight=false;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly) FVector LastKnown;
    void Decide();
    void Shutdown();
    bool HasAttackLine() const;
#if !UE_BUILD_SHIPPING
    int32 InjectNavigationFailure();
#endif
protected:
    virtual void OnPossess(APawn* InPawn) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void OnMoveCompleted(FAIRequestID RequestID,const FPathFollowingResult& Result) override;
private:
    UPROPERTY() TObjectPtr<UAISenseConfig_Sight> Sight;
    UPROPERTY() TObjectPtr<UAISenseConfig_Hearing> Hearing;
    TWeakObjectPtr<ACRAshWarden> Warden;
    TWeakObjectPtr<AActor> Target;
    FVector Home, MoveGoal;
    FRotator HomeRotation;
    FTimerHandle NavigationTimer;
    double NavStarted=0,LastStimulus=-100,NextAttack=0,NextMove=0,SearchStarted=-1;
    int32 MoveFailures=0;
    bool bStopped=false;
    FRandomStream Accuracy;
    UFUNCTION() void Perceived(AActor* Actor,FAIStimulus Stimulus);
    void CheckNavigation();
    UFUNCTION() void NavigationGenerated(ANavigationData* Data);
    void SetWardenState(ECRWardenState Next);
    void MoveBounded(FVector Goal);
};
