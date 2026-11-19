#include "CRServiceCircuit.h"
#include "CRGameMode.h"
#include "CRAudioSettingsSubsystem.h"
#include "Components/BoxComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"

ACRServiceCircuit::ACRServiceCircuit()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.bStartWithTickEnabled = false;
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));

    Housing = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Housing"));
    UpperLeaf = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("UpperLeaf"));
    LowerLeaf = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LowerLeaf"));
    for (UStaticMeshComponent* Mesh : {Housing.Get(), UpperLeaf.Get(), LowerLeaf.Get()})
    {
        Mesh->SetupAttachment(RootComponent);
        Mesh->SetCollisionProfileName(TEXT("NoCollision"));
        Mesh->SetCanEverAffectNavigation(false);
    }
    UpperLeaf->SetMobility(EComponentMobility::Movable);
    LowerLeaf->SetMobility(EComponentMobility::Movable);
    Passage = CreateDefaultSubobject<UBoxComponent>(TEXT("Passage"));
    Passage->SetupAttachment(RootComponent);
    Passage->SetRelativeLocation(FVector(0, 0, 130));
    Passage->SetBoxExtent(FVector(240, 11, 130));
    Passage->SetCollisionProfileName(TEXT("BlockAll"));
    Passage->SetCanEverAffectNavigation(false);

    Pilot = CreateDefaultSubobject<UPointLightComponent>(TEXT("Pilot"));
    Pilot->SetupAttachment(RootComponent);
    Pilot->SetRelativeLocation(FVector(0, 59, 252));
    Pilot->SetMobility(EComponentMobility::Movable);
    Pilot->SetCastShadows(false);
    Pilot->SetIntensityUnits(ELightUnits::Lumens);
    Pilot->SetIntensity(340.f);
    Pilot->SetAttenuationRadius(380.f);
    Pilot->SetLightColor(FLinearColor(1.f, .35f, .065f));
}

void ACRServiceCircuit::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    ApplyPose(0.f);
}

void ACRServiceCircuit::BeginPlay()
{
    Super::BeginPlay();
    if (ACRGameMode* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>())
    {
        Mode->OnMaintenanceChanged.AddDynamic(this, &ACRServiceCircuit::ProgressChanged);
        Mode->OnObjectiveChanged.AddDynamic(this, &ACRServiceCircuit::ObjectiveChanged);
    }
    bPowered = HasPower();
    Travel = bPowered ? 1.f : 0.f;
    ApplyPose(Travel);
}

void ACRServiceCircuit::EndPlay(const EEndPlayReason::Type Reason)
{
    if (ACRGameMode* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>())
    {
        Mode->OnMaintenanceChanged.RemoveAll(this);
        Mode->OnObjectiveChanged.RemoveAll(this);
    }
    Super::EndPlay(Reason);
}

bool ACRServiceCircuit::HasPower() const
{
    const ACRGameMode* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>();
    return Mode && (bRelayCircuit ? Mode->GetRelayServiceStep() : Mode->GetDiagnosticStep()) >= RequiredStep;
}

void ACRServiceCircuit::ObjectiveChanged(ECRObjective)
{
    ProgressChanged();
}

void ACRServiceCircuit::ProgressChanged()
{
    // Progress is monotonic within a world. Rollback loads a fresh instance and snaps in BeginPlay.
    if (bPowered || !HasPower()) return;
    bPowered = true;
    SetActorTickEnabled(true);
    if (UCRAudioSettingsSubsystem* Audio = UCRAudioSettingsSubsystem::Get(this))
        Audio->PlayEvent(bRelayCircuit ? TEXT("InterlockTravel") : TEXT("BusEnergize"), this,
            Pilot->GetComponentLocation(), true);
}

void ACRServiceCircuit::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    Travel = FMath::Min(1.f, Travel + DeltaSeconds / (bRelayCircuit ? 1.15f : .95f));
    ApplyPose(FMath::SmoothStep(0.f, 1.f, Travel));
    if (Travel >= 1.f) SetActorTickEnabled(false);
}

void ACRServiceCircuit::ApplyPose(float Alpha)
{
    constexpr float LeafHeight = 130.f;
    if (bRelayCircuit)
    {
        // Nested leaves rise on separate rails into the 390 cm high headstock.
        UpperLeaf->SetRelativeLocationAndRotation(FVector(0, -8, 260 + 120 * Alpha), FRotator::ZeroRotator);
        LowerLeaf->SetRelativeLocationAndRotation(FVector(0, 8, 130 + 245 * Alpha), FRotator::ZeroRotator);
    }
    else
    {
        // The two hinged leaves fold together below the fixed hinge. The bottom edge stays over its guides.
        const float Angle = 85.f * Alpha;
        const FRotator TopRotation(0, 0, Angle);
        const FVector TopHinge(0, 0, LeafHeight * 2);
        UpperLeaf->SetRelativeLocationAndRotation(TopHinge, TopRotation);
        LowerLeaf->SetRelativeLocationAndRotation(TopHinge + TopRotation.RotateVector(FVector(0, 0, -LeafHeight)),
            FRotator(0, 0, -Angle));
    }
    const bool bPassable = Alpha >= 1.f;
    const ECollisionEnabled::Type Collision = bPassable ? ECollisionEnabled::NoCollision : ECollisionEnabled::QueryAndPhysics;
    if (Passage->GetCollisionEnabled() != Collision) Passage->SetCollisionEnabled(Collision);
    Pilot->SetLightColor(FMath::Lerp(FLinearColor(1.f, .35f, .065f), FLinearColor(.17f, .82f, 1.f), Alpha));
}
