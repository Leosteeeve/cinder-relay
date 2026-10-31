#include "CRAshWardenController.h"
#include "CRAshWarden.h"
#include "CRCharacter.h"
#include "CRHealthComponent.h"
#include "Perception/AIPerceptionComponent.h"
#include "Perception/AISenseConfig_Sight.h"
#include "Perception/AISenseConfig_Hearing.h"
#include "Perception/AISense_Sight.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "BehaviorTree/BehaviorTree.h"
#include "BrainComponent.h"
#include "NavigationSystem.h"
#include "NavigationData.h"
#include "Navigation/PathFollowingComponent.h"
#include "Kismet/GameplayStatics.h"
#include "TimerManager.h"
#include "Engine/World.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
ACRAshWardenController::ACRAshWardenController()
{
    PrimaryActorTick.bCanEverTick=false;
    Senses=CreateDefaultSubobject<UAIPerceptionComponent>(TEXT("Perception")); SetPerceptionComponent(*Senses);
    Sight=CreateDefaultSubobject<UAISenseConfig_Sight>(TEXT("Sight")); Sight->SightRadius=1500; Sight->LoseSightRadius=1800; Sight->PeripheralVisionAngleDegrees=75; Sight->SetMaxAge(5);
    Sight->DetectionByAffiliation.bDetectEnemies=true; Sight->DetectionByAffiliation.bDetectFriendlies=true; Sight->DetectionByAffiliation.bDetectNeutrals=true;
    Hearing=CreateDefaultSubobject<UAISenseConfig_Hearing>(TEXT("Hearing")); Hearing->HearingRange=2200; Hearing->SetMaxAge(5); Hearing->DetectionByAffiliation=Sight->DetectionByAffiliation;
    Senses->ConfigureSense(*Sight); Senses->ConfigureSense(*Hearing); Senses->SetDominantSense(Sight->GetSenseImplementation());
}
void ACRAshWardenController::OnPossess(APawn* InPawn)
{
    Super::OnPossess(InPawn); Warden=Cast<ACRAshWarden>(InPawn); if(!Warden.IsValid())return;
    Home=InPawn->GetActorLocation(); HomeRotation=InPawn->GetActorRotation(); Accuracy.Initialize(GetTypeHash(Warden->EnemyId));
    Sight->SightRadius=Warden->SightRadius; Sight->LoseSightRadius=Sight->SightRadius+300; Sight->SetMaxAge(FMath::Max(1.f,Warden->MemorySeconds)); Senses->ConfigureSense(*Sight);
    Senses->OnTargetPerceptionUpdated.AddUniqueDynamic(this,&ACRAshWardenController::Perceived);
    Senses->SetSenseEnabled(UAISense_Sight::StaticClass(),false); Senses->SetSenseEnabled(Hearing->GetSenseImplementation(),false);
    if(auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld())) Nav->OnNavigationGenerationFinishedDelegate.AddDynamic(this,&ACRAshWardenController::NavigationGenerated);
    NavStarted=GetWorld()->GetTimeSeconds(); GetWorldTimerManager().SetTimer(NavigationTimer,this,&ACRAshWardenController::CheckNavigation,.5f,true);
}
void ACRAshWardenController::CheckNavigation()
{
    if(bStopped || !Warden.IsValid() || Warden->Health->IsDead())return;
    auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld()); FNavLocation Point;
    if(Nav && !UNavigationSystemV1::IsNavigationBeingBuiltOrLocked(this) && Nav->ProjectPointToNavigation(Warden->GetActorLocation(),Point,FVector(90,90,200)))
    {
        bNavigationReady=true; GetWorldTimerManager().ClearTimer(NavigationTimer);
        Senses->SetSenseEnabled(UAISense_Sight::StaticClass(),true); Senses->SetSenseEnabled(Hearing->GetSenseImplementation(),true);
        if(!Warden->Behavior || !RunBehaviorTree(Warden->Behavior)) { UE_LOG(LogTemp,Error,TEXT("CR_AI MissingBehavior id=%s"),*Warden->EnemyId.ToString()); Shutdown(); return; }
        SetWardenState(ECRWardenState::Idle); UE_LOG(LogTemp,Display,TEXT("CR_AI NavigationReady id=%s"),*Warden->EnemyId.ToString());
    }
    else if(GetWorld()->GetTimeSeconds()-NavStarted>12)
    {
        GetWorldTimerManager().ClearTimer(NavigationTimer);
        UE_LOG(LogTemp,Warning,TEXT("CR_AI NavigationUnavailable id=%s; waiting for native generation event"),*Warden->EnemyId.ToString());
    }
}
void ACRAshWardenController::NavigationGenerated(ANavigationData*)
{
    if(!bNavigationReady&&!bStopped) { NavStarted=GetWorld()->GetTimeSeconds(); GetWorldTimerManager().SetTimer(NavigationTimer,this,&ACRAshWardenController::CheckNavigation,.5f,true); }
}
void ACRAshWardenController::Perceived(AActor* Actor,FAIStimulus Stimulus)
{
    if(bStopped || !bNavigationReady || !Cast<ACRCharacter>(Actor))return;
    auto* H=Actor->FindComponentByClass<UCRHealthComponent>(); if(!H||H->IsDead())return;
    if(Stimulus.Type==UAISense::GetSenseID<UAISense_Sight>())
    {
        bSight=Stimulus.WasSuccessfullySensed();
        if(bSight) { Target=Actor; LastKnown=Stimulus.StimulusLocation; LastStimulus=GetWorld()->GetTimeSeconds(); NextAttack=LastStimulus+.65; MoveFailures=0; SearchStarted=-1; }
        else { LastStimulus=GetWorld()->GetTimeSeconds(); SearchStarted=-1; }
        UE_LOG(LogTemp,Display,TEXT("CR_AI Sight id=%s visible=%d"),*GetNameSafe(GetPawn()),bSight);
    }
    else if(Stimulus.WasSuccessfullySensed()&&!bSight)
    {
        Target=Actor; LastKnown=Stimulus.StimulusLocation; LastStimulus=GetWorld()->GetTimeSeconds(); MoveFailures=0; SearchStarted=-1;
        SetWardenState(ECRWardenState::Investigate);
    }
}
bool ACRAshWardenController::HasAttackLine() const
{
    if(!bSight||!Target.IsValid()||!Warden.IsValid()||Warden->Health->IsDead())return false;
    const auto* H=Target->FindComponentByClass<UCRHealthComponent>(); if(!H||H->IsDead())return false;
    const FVector Start=Warden->GetActorLocation()+FVector(0,0,60),End=Target->GetActorLocation()+FVector(0,0,35);
    FHitResult Hit; FCollisionQueryParams Params(SCENE_QUERY_STAT(CRWardenLOS),false,Warden.Get());
    return FVector::DistSquared(Start,End)<=FMath::Square(Warden->AttackRange) && GetWorld()->LineTraceSingleByChannel(Hit,Start,End,ECC_Visibility,Params) && Hit.GetActor()==Target.Get();
}
void ACRAshWardenController::SetWardenState(ECRWardenState Next)
{
    if(State==Next)return; State=Next;
    if(GetBlackboardComponent())GetBlackboardComponent()->SetValueAsInt(TEXT("State"),int32(State));
    UE_LOG(LogTemp,Display,TEXT("CR_AI State id=%s value=%d"),Warden.IsValid()?*Warden->EnemyId.ToString():TEXT("none"),int32(State));
}
void ACRAshWardenController::MoveBounded(FVector Goal)
{
    const double Now=GetWorld()->GetTimeSeconds();
    if(Now<NextMove||MoveFailures>=2||!Warden.IsValid())return;
    if(GetMoveStatus()==EPathFollowingStatus::Moving && FVector::DistSquared(Goal,MoveGoal)<FMath::Square(150.f))return;
    MoveGoal=Goal; NextMove=Now+1;
    const int32 FailuresBefore=MoveFailures;
    const auto Result=MoveToLocation(Goal,65,true,true,true,false,nullptr,false);
    if(Result==EPathFollowingRequestResult::Failed) { if(MoveFailures==FailuresBefore)++MoveFailures; NextMove=Now+2; UE_LOG(LogTemp,Warning,TEXT("CR_AI MoveFailed id=%s count=%d"),*Warden->EnemyId.ToString(),MoveFailures); }
}
void ACRAshWardenController::OnMoveCompleted(FAIRequestID RequestID,const FPathFollowingResult& Result)
{
    Super::OnMoveCompleted(RequestID,Result);
    if(Result.Code==EPathFollowingResult::Success) { MoveFailures=0; UE_LOG(LogTemp,Display,TEXT("CR_AI MoveCompleted id=%s"),*GetNameSafe(GetPawn())); }
    else if(Result.Code!=EPathFollowingResult::Aborted) { ++MoveFailures; NextMove=GetWorld()->GetTimeSeconds()+2; }
}
void ACRAshWardenController::Decide()
{
    TRACE_CPUPROFILER_EVENT_SCOPE(CR_WardenDecision);
    if(bStopped||!bNavigationReady||!Warden.IsValid()||Warden->Health->IsDead())return;
    const double Now=GetWorld()->GetTimeSeconds();
    if(Target.IsValid()) { const auto* H=Target->FindComponentByClass<UCRHealthComponent>(); if(!H||H->IsDead()) { bSight=false; Target.Reset(); LastStimulus=-100; } }
    if(bSight && Target.IsValid())
    {
        // Perception authorizes tracking; every attack independently verifies real collision LOS.
        if(LineOfSightTo(Target.Get())) { LastKnown=Target->GetActorLocation(); LastStimulus=Now; }
        else { bSight=false; LastStimulus=Now; }
    }
    if(GetBlackboardComponent()) { GetBlackboardComponent()->SetValueAsBool(TEXT("HasSight"),bSight); GetBlackboardComponent()->SetValueAsVector(TEXT("LastKnown"),LastKnown); }
    if(bSight && HasAttackLine())
    {
        SetWardenState(ECRWardenState::Combat); StopMovement(); SetFocus(Target.Get());
        Warden->SetActorRotation(FRotator(0,(LastKnown-Warden->GetActorLocation()).Rotation().Yaw,0));
        if(Now>=NextAttack)
        {
            NextAttack=Now+FMath::Max(.5f,Warden->AttackInterval);
            const FVector Start=Warden->GetActorLocation()+FVector(0,0,60);
            const FVector Direction=Accuracy.VRandCone((Target->GetActorLocation()+FVector(0,0,35)-Start).GetSafeNormal(),FMath::DegreesToRadians(Warden->AccuracyDegrees));
            FHitResult Hit; FCollisionQueryParams Params(SCENE_QUERY_STAT(CRWardenShot),false,Warden.Get());
            if(GetWorld()->LineTraceSingleByChannel(Hit,Start,Start+Direction*Warden->AttackRange,ECC_Visibility,Params) && Hit.GetActor()==Target.Get()) UGameplayStatics::ApplyPointDamage(Target.Get(),Warden->ShotDamage,Direction,Hit,this,Warden.Get(),nullptr);
            Warden->PresentAttack(); UE_LOG(LogTemp,Display,TEXT("CR_AI Attack id=%s hit=%s"),*Warden->EnemyId.ToString(),*GetNameSafe(Hit.GetActor()));
        }
    }
    else if(Target.IsValid() && Now-LastStimulus<FMath::Max(1.f,Warden->MemorySeconds))
    {
        ClearFocus(EAIFocusPriority::Gameplay);
        if(FVector::Dist2D(Warden->GetActorLocation(),LastKnown)>100) { SetWardenState(ECRWardenState::Investigate); MoveBounded(LastKnown); }
        else { SetWardenState(ECRWardenState::Search); StopMovement(); if(SearchStarted<0)SearchStarted=Now; Warden->SetActorRotation(FRotator(0,HomeRotation.Yaw+FMath::Sin((Now-SearchStarted)*1.5)*65,0)); }
    }
    else
    {
        Target.Reset(); bSight=false; ClearFocus(EAIFocusPriority::Gameplay);
        if(State!=ECRWardenState::Return && State!=ECRWardenState::Idle) { MoveFailures=0; NextMove=Now; }
        if(FVector::Dist2D(Warden->GetActorLocation(),Home)>110) { SetWardenState(ECRWardenState::Return); MoveBounded(Home); }
        else { SetWardenState(ECRWardenState::Idle); StopMovement(); Warden->SetActorRotation(HomeRotation); }
    }
}
void ACRAshWardenController::Shutdown()
{
    if(bStopped)return; bStopped=true; bNavigationReady=false; bSight=false; Target.Reset();
    GetWorldTimerManager().ClearTimer(NavigationTimer); StopMovement(); ClearFocus(EAIFocusPriority::Gameplay);
    if(BrainComponent)BrainComponent->StopLogic(TEXT("Dead or unloaded"));
    Senses->OnTargetPerceptionUpdated.RemoveDynamic(this,&ACRAshWardenController::Perceived); Senses->ForgetAll(); Senses->Deactivate();
    if(auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld()))Nav->OnNavigationGenerationFinishedDelegate.RemoveAll(this);
    SetWardenState(ECRWardenState::Dead);
}
void ACRAshWardenController::EndPlay(const EEndPlayReason::Type Reason) { Shutdown(); Super::EndPlay(Reason); }
#if !UE_BUILD_SHIPPING
int32 ACRAshWardenController::InjectNavigationFailure() { MoveBounded(FVector(1000000,1000000,0)); return MoveFailures; }
#endif
