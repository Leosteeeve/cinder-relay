#include "CRStreamingGate.h"
#include "CRChapterStreamingController.h"
#include "CRCharacter.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"

ACRStreamingGate::ACRStreamingGate()
{
    PrimaryActorTick.bCanEverTick = false;
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
    Door = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Shutter"));
    Door->SetupAttachment(RootComponent);
    Door->SetRelativeLocation(FVector(0, 0, 175));
    Door->SetRelativeScale3D(FVector(0.35, 3.6, 3.5));
    Door->SetCollisionProfileName(TEXT("BlockAll"));
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

void ACRStreamingGate::SetChapterController(ACRChapterStreamingController* Value) { ChapterController = Value; }
bool ACRStreamingGate::IsInThreshold() const
{
    const APawn* Pawn = UGameplayStatics::GetPlayerPawn(this, 0);
    return Pawn && FMath::Abs(Pawn->GetActorLocation().X - GetActorLocation().X) < 230;
}
void ACRStreamingGate::SetOpen(bool bValue)
{
    if (bOpen == bValue) return;
    bOpen = bValue;
    Door->SetCollisionEnabled(bOpen ? ECollisionEnabled::NoCollision : ECollisionEnabled::QueryAndPhysics);
    Door->SetVisibility(!bOpen);
    UE_LOG(LogTemp, Display, TEXT("CR_GATE %s %s t=%.3f"), LeftZone == 0 ? TEXT("AB") : TEXT("BC"), bOpen ? TEXT("Open") : TEXT("Closed"), GetWorld()->GetTimeSeconds());
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
    if (Component == Retention) bNear = false;
    if (ChapterController.IsValid()) ChapterController->Reconcile();
}
