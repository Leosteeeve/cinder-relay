#include "CRAccessMachinery.h"
#include "CRGameMode.h"
#include "CRChapterMechanics.h"
#include "CRCharacter.h"
#include "CRPlayerController.h"
#include "CRAudioSettingsSubsystem.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Components/TextRenderComponent.h"
#include "Kismet/GameplayStatics.h"

ACRAccessMachinery::ACRAccessMachinery()
{
    PrimaryActorTick.bCanEverTick=true; PrimaryActorTick.TickInterval=.05f;
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
    Shuttle=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Shuttle")); Shuttle->SetupAttachment(RootComponent);
    Shuttle->SetRelativeLocation(FVector(0,0,150)); Shuttle->SetRelativeScale3D(FVector(.45,6,3));
    Shuttle->SetMobility(EComponentMobility::Movable); Shuttle->SetCollisionProfileName(TEXT("NoCollision"));
    Barrier=CreateDefaultSubobject<UBoxComponent>(TEXT("Barrier")); Barrier->SetupAttachment(RootComponent);
    Barrier->SetRelativeLocation(FVector(0,0,150)); Barrier->SetBoxExtent(FVector(30,300,150)); Barrier->SetCollisionProfileName(TEXT("BlockAll"));
    Control=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Control")); Control->SetupAttachment(RootComponent);
    Control->SetRelativeLocation(FVector(400,390,125)); Control->SetRelativeScale3D(FVector(.4,.5,.65)); Control->SetCollisionProfileName(TEXT("BlockAll"));
    Status=CreateDefaultSubobject<UTextRenderComponent>(TEXT("Status")); Status->SetupAttachment(RootComponent);
    Status->SetRelativeLocation(FVector(-40,0,355)); Status->SetRelativeRotation(FRotator(0,180,0)); Status->SetWorldSize(17); Status->SetHorizontalAlignment(EHTA_Center);
}
void ACRAccessMachinery::BeginPlay()
{
    Super::BeginPlay();
    Status->SetText(NSLOCTEXT("Cinder","MachineInitial","AMBER / WAIT\nSIDE SERVICE WALK ALWAYS OPEN"));
    Status->SetTextRenderColor(FColor(224,165,80));
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>()) G->RegisterAccessMachinery();
}
void ACRAccessMachinery::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if(GetWorld()->IsPaused()) return;
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>(); const APawn* Pawn=UGameplayStatics::GetPlayerPawn(this,0);
    const FVector P=Pawn?GetActorTransform().InverseTransformPosition(Pawn->GetActorLocation()):FVector(10000);
    const bool Stopped=G && G->IsAccessStopped();
    const bool Occupied=CRChapterMechanics::HoldMachineOpen(Aperture,FMath::Abs(P.X)<110 && FMath::Abs(P.Y)<365 && P.Z>-100 && P.Z<450);
    // Native blocking leaf never closes on the capsule. Side walkway remains available throughout.
    const bool Open=Stopped || Occupied || FMath::Fmod(GetWorld()->GetTimeSeconds(),5.f)<2.4f;
    Aperture=FMath::FInterpConstantTo(Aperture,Open?1.f:0.f,DeltaSeconds,2.f);
    Shuttle->SetRelativeLocation(FVector(0,0,150+330*Aperture));
    const bool Traversable=Aperture>=1 || Occupied;
    Barrier->SetCollisionEnabled(Traversable?ECollisionEnabled::NoCollision:ECollisionEnabled::QueryAndPhysics);
    if(Traversable!=bLastOpen || Stopped)
    {
        bLastOpen=Traversable;
        Status->SetText(FText::FromString(Stopped?TEXT("ACCESS MACHINERY STOPPED\nRELAY CONTROL AVAILABLE"):Traversable?TEXT("CYAN / CROSS\nSTOP CONTROL BEYOND SHUTTLE"):TEXT("AMBER / WAIT\nSIDE SERVICE WALK ALWAYS OPEN")));
        Status->SetTextRenderColor(Traversable?FColor(105,190,180):FColor(224,165,80));
        if(!Stopped && FMath::Abs(P.X)<1000) if(auto* Audio=UCRAudioSettingsSubsystem::Get(this)) Audio->PlayEvent(TEXT("FeedOut"),this,GetActorLocation(),true);
    }
    if(Stopped && Aperture>=1) SetActorTickEnabled(false);
}
bool ACRAccessMachinery::CanInteract_Implementation(ACRCharacter* Player) const
{
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
    return Player && G && !G->IsAccessStopped() && G->GetObjective()==ECRObjective::RestorePower && Player->CanInteractWith(this)
        && FVector::DistSquared(Player->GetActorLocation(),Control->GetComponentLocation())<FMath::Square(260.f);
}
FText ACRAccessMachinery::GetInteractionPrompt_Implementation(ACRCharacter* Player) const
{
    if(const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>(); G && G->IsAccessStopped())
        return NSLOCTEXT("Cinder","MachineLatched","Machinery stop latched. Relay access is clear.");
    return CanInteract_Implementation(Player)?NSLOCTEXT("Cinder","StopMachinery","[E] Latch machinery stop / clear relay access"):
        NSLOCTEXT("Cinder","CrossMachinery","Cross on cyan, or follow the side service walk. Stop control is beyond the shuttle.");
}
void ACRAccessMachinery::Interact_Implementation(ACRCharacter* Player)
{
    if(!CanInteract_Implementation(Player)) return;
    GetWorld()->GetAuthGameMode<ACRGameMode>()->StopAccessMachinery();
    if(auto* PC=Cast<ACRPlayerController>(Player->GetController())) PC->ShowSubtitle(NSLOCTEXT("Cinder","AccessLatched","MACHINERY STOP LATCHED / Return path clear. Install the module at Relay Nine."),5);
    if(auto* Audio=UCRAudioSettingsSubsystem::Get(this)) Audio->PlayEvent(TEXT("ReloadComplete"),this,Control->GetComponentLocation(),true);
}
