#include "CRCheckpoint.h"
#include "CRChapterSaveGame.h"
#include "CRChapterStreamingController.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "CRPlayerController.h"
#include "Components/BoxComponent.h"
#include "Components/ArrowComponent.h"
#include "Engine/LevelStreaming.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "TimerManager.h"

ACRCheckpoint::ACRCheckpoint()
{
    PrimaryActorTick.bCanEverTick = false;
    Trigger = CreateDefaultSubobject<UBoxComponent>(TEXT("CheckpointRange")); SetRootComponent(Trigger);
    Trigger->SetBoxExtent(FVector(150, 390, 150)); Trigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Trigger->SetCollisionResponseToAllChannels(ECR_Ignore); Trigger->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
    Trigger->SetGenerateOverlapEvents(true);
    Facing = CreateDefaultSubobject<UArrowComponent>(TEXT("SafeSpawnFacing")); Facing->SetupAttachment(Trigger);
}
void ACRCheckpoint::BeginPlay()
{ Super::BeginPlay(); Trigger->OnComponentBeginOverlap.AddDynamic(this, &ACRCheckpoint::Enter); }
bool ACRCheckpoint::SnapToSafeFloor()
{
#if WITH_EDITOR
    if (GetWorld() && !GetWorld()->IsGameWorld())
    {
        FVector P = GetActorLocation(); FHitResult Hit; FCollisionQueryParams Query(SCENE_QUERY_STAT(CRCheckpointEditorFloor), false, this);
        if (GetWorld()->LineTraceSingleByChannel(Hit, P, P - FVector(0,0,900), ECC_Visibility, Query) && !Hit.bStartPenetrating && Hit.ImpactNormal.Z > .65f
            && (CheckpointId != TEXT("CP02_RELAY_ACCESS") || (Hit.GetActor() && Hit.GetActor()->ActorHasTag(TEXT("CR_Ready_AccessRamp")))))
        {
            const FVector Safe = Hit.ImpactPoint + FVector(0,0,110);
            if (GetWorld()->OverlapBlockingTestByChannel(Safe, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeCapsule(42,96), Query)) return false;
            Modify(); SetActorLocation(Safe);
            UE_LOG(LogTemp, Display, TEXT("CR04_ANCHOR %s floor=%s position=%s"), *CheckpointId.ToString(), *GetNameSafe(Hit.GetActor()), *Safe.ToString()); return true;
        }
    }
#endif
    return false;
}
void ACRCheckpoint::EndPlay(const EEndPlayReason::Type Reason)
{ GetWorldTimerManager().ClearTimer(RetryTimer); Candidate.Reset(); Super::EndPlay(Reason); }
void ACRCheckpoint::Enter(UPrimitiveComponent*, AActor* Actor, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
    auto* Player = Cast<ACRCharacter>(Actor); if (!Player || !Player->IsPlayerControlled()) return;
    BeginCheckpointAttempt(*Player);
}
void ACRCheckpoint::BeginCheckpointAttempt(ACRCharacter& Player)
{
    Candidate = &Player; AttemptStarted = GetWorld()->GetTimeSeconds();
    GetWorldTimerManager().SetTimer(RetryTimer, this, &ACRCheckpoint::TryCheckpoint, .25f, true);
}
void ACRCheckpoint::TryCheckpoint()
{
    auto* G = GetWorld()->GetAuthGameMode<ACRGameMode>();
    if (!Candidate.IsValid() || !Trigger->IsOverlappingActor(Candidate.Get()) || !G)
    { GetWorldTimerManager().ClearTimer(RetryTimer); return; }
    if (G->RequestCheckpoint(*this, *Candidate.Get()) || G->HasPassedCheckpoint(CheckpointId))
    { GetWorldTimerManager().ClearTimer(RetryTimer); return; }
    if (GetWorld()->GetTimeSeconds() - AttemptStarted > 10)
    {
        GetWorldTimerManager().ClearTimer(RetryTimer);
        if (auto* PC = Cast<ACRPlayerController>(Candidate->GetController())) PC->ShowCheckpointFeedback(TEXT("CHECKPOINT UNAVAILABLE — leave and re-enter to retry."));
    }
}
bool ACRCheckpoint::ValidateSpawn(FString& Reason) const
{
    const int32 Zone = UCRChapterSaveGame::CheckpointZone(CheckpointId);
    ACRChapterStreamingController* Streaming = nullptr;
    for (TActorIterator<ACRChapterStreamingController> It(GetWorld()); It; ++It) { Streaming = *It; break; }
    if (!Streaming || !Streaming->IsZoneReady(Zone)) { Reason = TEXT("Target region is not ready"); return false; }
    FCollisionQueryParams Query(SCENE_QUERY_STAT(CRCheckpointFloor), false, this);
    if (const auto* PC = GetWorld()->GetFirstPlayerController()) if (const APawn* Pawn = PC->GetPawn()) Query.AddIgnoredActor(Pawn);
    const FVector P = GetActorLocation(); FHitResult Hit;
    if (!GetWorld()->LineTraceSingleByChannel(Hit, P, P - FVector(0,0,170), ECC_Visibility, Query)
        || !Hit.GetActor() || Hit.GetActor()->GetLevel() != Streaming->GetZoneLevel(Zone)->GetLoadedLevel()
        || !Hit.GetComponent() || !Hit.GetComponent()->IsPhysicsStateCreated() || Hit.ImpactNormal.Z < .65f
        || P.Z - Hit.ImpactPoint.Z < 96 || P.Z - Hit.ImpactPoint.Z > 150
        || GetWorld()->OverlapBlockingTestByChannel(P, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeCapsule(42,96), Query))
    { Reason = TEXT("Checkpoint floor or capsule clearance is invalid"); return false; }
    Reason.Reset(); return true;
}
