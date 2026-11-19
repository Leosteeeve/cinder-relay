#include "CREchoBridgeCatch.h"
#include "CRAudioSettingsSubsystem.h"
#include "CREchoChapter.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/DamageEvents.h"
#include "Engine/World.h"

ACREchoBridgeCatch::ACREchoBridgeCatch()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.bStartWithTickEnabled = false;
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
    Boom = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Boom"));
    Boom->SetupAttachment(RootComponent);
    Boom->SetMobility(EComponentMobility::Movable);
    Boom->SetRelativeLocation(FVector(0,-160,143));
    Boom->SetCollisionProfileName(TEXT("NoCollision"));
    Witness = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Witness"));
    Witness->SetupAttachment(RootComponent);
    Witness->SetRelativeLocation(FVector(-39,0,154));
    Witness->SetMobility(EComponentMobility::Movable);
    Witness->SetCollisionProfileName(TEXT("NoCollision"));
    CatchTarget = CreateDefaultSubobject<UBoxComponent>(TEXT("CatchTarget"));
    CatchTarget->SetupAttachment(RootComponent);
    CatchTarget->SetRelativeLocation(Witness->GetRelativeLocation());
    CatchTarget->SetBoxExtent(FVector(12,33,32));
    CatchTarget->SetCollisionProfileName(TEXT("BlockAll"));
    CatchTarget->ComponentTags.Add(TEXT("CR_PointDamageReceiver"));
    ArmBarrier = CreateDefaultSubobject<UBoxComponent>(TEXT("ArmBarrier"));
    ArmBarrier->SetupAttachment(RootComponent);
    ArmBarrier->SetRelativeLocation(FVector(0,0,79));
    ArmBarrier->SetBoxExtent(FVector(12,160,78));
    ArmBarrier->SetCollisionProfileName(TEXT("BlockAll"));
}

void ACREchoBridgeCatch::BeginPlay()
{
    Super::BeginPlay();
    if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>())
    {
        Echo->OnChanged.AddUObject(this, &ACREchoBridgeCatch::RestoreBridge);
        RestoreBridge();
    }
}

void ACREchoBridgeCatch::EndPlay(const EEndPlayReason::Type Reason)
{
    if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>()) Echo->OnChanged.RemoveAll(this);
    Super::EndPlay(Reason);
}

void ACREchoBridgeCatch::RestoreBridge()
{
    const auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>();
    if (bReleased || !Echo || !Echo->IsBridgeReleased()) return;
    bReleased = true;
    Travel = 1.f;
    CatchTarget->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ApplyPose();
}

float ACREchoBridgeCatch::TakeDamage(float Damage, const FDamageEvent& Event, AController* InstigatorController, AActor* Causer)
{
    if (bReleased || Damage <= 0.f || !Event.IsOfType(FPointDamageEvent::ClassID)) return 0.f;
    const auto& PointHit = static_cast<const FPointDamageEvent&>(Event);
    if (PointHit.HitInfo.GetComponent() != CatchTarget) return 0.f;
    bReleased = true;
    if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>()) Echo->RecordBridgeRelease();
    CatchTarget->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    SetActorTickEnabled(true);
    if (auto* Audio = UCRAudioSettingsSubsystem::Get(this))
        Audio->PlayEvent(TEXT("InterlockTravel"), this, Witness->GetComponentLocation(), true);
    UE_LOG(LogTemp, Display, TEXT("CR02_BRIDGE_CATCH released"));
    return Damage;
}

void ACREchoBridgeCatch::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    Travel = FMath::Min(1.f, Travel + DeltaSeconds / .9f);
    ApplyPose();
}

void ACREchoBridgeCatch::ApplyPose()
{
    const float Rise = FMath::SmoothStep(0.f, 1.f, Travel);
    Boom->SetRelativeRotation(FRotator(0,0,-89.f*Rise));
    // The catch separates from the arm and drops onto the pier. It has no damage or physics authority.
    Witness->SetRelativeLocationAndRotation(FVector(-39,0,154-138*Rise), FRotator(64*Rise,0,25*Rise));
    if (IsOpen())
    {
        ArmBarrier->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        SetActorTickEnabled(false);
    }
}
