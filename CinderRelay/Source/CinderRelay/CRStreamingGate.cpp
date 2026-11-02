#include "CRStreamingGate.h"
#include "CRChapterStreamingController.h"
#include "CRChapterMechanics.h"
#include "CRCharacter.h"
#include "CRAudioSettingsSubsystem.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"

ACRStreamingGate::ACRStreamingGate()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.bStartWithTickEnabled = false;
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
    Door = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Shutter"));
    Door->SetupAttachment(RootComponent);
    Door->SetRelativeLocation(FVector(0, 0, 175));
    Door->SetRelativeScale3D(FVector(0.35, 3.6, 3.5));
    Door->SetMobility(EComponentMobility::Movable);
    Door->SetCollisionProfileName(TEXT("NoCollision"));
    SafetyBarrier = CreateDefaultSubobject<UBoxComponent>(TEXT("SafetyBarrier"));
    SafetyBarrier->SetupAttachment(RootComponent);
    SafetyBarrier->SetRelativeLocation(FVector(0,0,175));
    SafetyBarrier->SetBoxExtent(FVector(20,180,175));
    SafetyBarrier->SetCollisionProfileName(TEXT("BlockAll"));
    auto Control = [this](const TCHAR* Name, float X)
    {
        auto* C=CreateDefaultSubobject<UStaticMeshComponent>(Name);
        C->SetupAttachment(RootComponent); C->SetRelativeLocation(FVector(X,-230,135));
        C->SetRelativeScale3D(FVector(.16,.5,.65)); C->SetCollisionProfileName(TEXT("BlockAll"));
        return C;
    };
    ControlOutside=Control(TEXT("ControlOutside"),-45);
    ControlInside=Control(TEXT("ControlInside"),45);
    auto Sensor = [this](const TCHAR* Name, float HalfLength)
    {
        auto* Box = CreateDefaultSubobject<UBoxComponent>(Name);
        Box->SetupAttachment(RootComponent);
        Box->SetBoxExtent(FVector(HalfLength, 1450, 1100));
        Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        Box->SetCollisionResponseToAllChannels(ECR_Ignore);
        Box->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
        Box->SetGenerateOverlapEvents(true);
        Box->OnComponentBeginOverlap.AddDynamic(this, &ACRStreamingGate::BeginSensor);
        Box->OnComponentEndOverlap.AddDynamic(this, &ACRStreamingGate::EndSensor);
        return Box;
    };
    Preload = Sensor(TEXT("Preload800"), 800);
    Retention = Sensor(TEXT("Retention1000"), 1000);
    Threshold = Sensor(TEXT("Threshold180"), 180);
}

void ACRStreamingGate::BeginPlay()
{
    Super::BeginPlay(); ClosedLocation=Door->GetRelativeLocation(); ClosedScale=Door->GetRelativeScale3D();
    // Existing map overrides must not leave moving collision on the cosmetic leaf.
    Door->SetCollisionEnabled(ECollisionEnabled::NoCollision); Door->SetVisibility(true); ApplyDoor();
}
void ACRStreamingGate::SetChapterController(ACRChapterStreamingController* Value) { ChapterController = Value; }
bool ACRStreamingGate::IsInThreshold() const
{
    const APawn* Pawn = UGameplayStatics::GetPlayerPawn(this, 0);
    const FVector P=Pawn?GetActorTransform().InverseTransformPosition(Pawn->GetActorLocation()):FVector(10000);
    return Pawn && FMath::Abs(P.X)<230 && FMath::Abs(P.Y)<260 && P.Z>-120 && P.Z<450;
}
bool ACRStreamingGate::WantsAdjacentZones() const
{ return CRChapterMechanics::RetainNeighbor(bRequested,bNear,IsInThreshold(),Aperture); }
bool ACRStreamingGate::CanInteract_Implementation(ACRCharacter* Player) const
{ return Player && Player->CanInteractWith(this) && ChapterController.IsValid() && (!bRequested || CRChapterMechanics::CanCloseDoor(IsInThreshold())); }
FText ACRStreamingGate::GetInteractionPrompt_Implementation(ACRCharacter*) const
{
    if(bRequested && IsInThreshold()) return NSLOCTEXT("Cinder","GateClear","Move clear of the doorway to close");
    if(bRequested && !bReady) return NSLOCTEXT("Cinder","GateWait","Preparing access... [E] Cancel / F5 retry");
    return bRequested?NSLOCTEXT("Cinder","GateClose","[E] Close mechanical door"):NSLOCTEXT("Cinder","GateOpen","[E] Open mechanical door");
}
void ACRStreamingGate::Interact_Implementation(ACRCharacter* Player)
{
    if(!CanInteract_Implementation(Player)) return;
    bRequested=!bRequested; bNear=true;
    if(auto* Audio=UCRAudioSettingsSubsystem::Get(this)) Audio->PlayEvent(TEXT("FeedIn"),this,GetActorLocation()+FVector(0,0,130),true);
    UE_LOG(LogTemp,Display,TEXT("CR06_DOOR %s Request=%d"),*GetName(),bRequested);
    ChapterController->Reconcile(); SetActorTickEnabled(true);
}
void ACRStreamingGate::SetOpen(bool bValue)
{
    bReady=bValue; ApplyDoor();
    if((bRequested && bReady && Aperture<1) || ((!bRequested || !bReady) && Aperture>0)) SetActorTickEnabled(true);
}
void ACRStreamingGate::ApplyDoor()
{
    const bool Pass=CRChapterMechanics::CanPassDoor(bRequested,bReady,Aperture);
    SafetyBarrier->SetCollisionEnabled(Pass?ECollisionEnabled::NoCollision:ECollisionEnabled::QueryAndPhysics);
    // Roller sheet gathers into its header; isolation leaf retracts into a floor pocket.
    // Both are cosmetic: the fixed safety barrier remains the passage authority.
    if(LeftZone==0)
    {
        Door->SetRelativeLocation(ClosedLocation+FVector(0,0,175*Aperture));
        Door->SetRelativeScale3D(ClosedScale*FVector(1,1,FMath::Max(.015f,1-Aperture)));
    }
    else Door->SetRelativeLocation(ClosedLocation-FVector(0,0,360*Aperture));
    if(bOpen!=Pass)
    {
        bOpen=Pass;
        UE_LOG(LogTemp,Display,TEXT("CR_GATE %s %s t=%.3f"),LeftZone==0?TEXT("AB"):TEXT("BC"),bOpen?TEXT("Open"):TEXT("Closed"),GetWorld()->GetTimeSeconds());
    }
}
void ACRStreamingGate::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    // Pause may be requested after this frame's tick list was queued.
    if(GetWorld()->IsPaused()) return;
    const bool Target=bRequested && bReady;
    // Pause uses world delta. Never lower a leaf through the player capsule.
    if(!Target && IsInThreshold()) return;
    Aperture=FMath::FInterpConstantTo(Aperture,Target?1.f:0.f,DeltaSeconds,1.f/.85f);
    ApplyDoor();
    if(Aperture==(Target?1.f:0.f))
    {
        SetActorTickEnabled(false);
        if(auto* Audio=UCRAudioSettingsSubsystem::Get(this)) Audio->PlayEvent(TEXT("ReloadComplete"),this,GetActorLocation()+FVector(0,0,130),true);
        if(ChapterController.IsValid()) ChapterController->Reconcile();
    }
}
void ACRStreamingGate::BeginSensor(UPrimitiveComponent* Component, AActor* Other, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
    if (!Cast<ACRCharacter>(Other)) return;
    if (Component == Preload) bNear = true;
    if (ChapterController.IsValid()) ChapterController->Reconcile();
}
void ACRStreamingGate::EndSensor(UPrimitiveComponent* Component, AActor* Other, UPrimitiveComponent*, int32)
{
    if (!Cast<ACRCharacter>(Other)) return;
    if (Component == Retention) { bNear = false; bRequested = false; }
    if (ChapterController.IsValid()) ChapterController->Reconcile();
}
