#include "CRWorkshopTrigger.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "Components/BoxComponent.h"
#include "Engine/World.h"

ACRWorkshopTrigger::ACRWorkshopTrigger()
{
	PrimaryActorTick.bCanEverTick = false;
	Volume = CreateDefaultSubobject<UBoxComponent>(TEXT("WorkshopEntry"));
	SetRootComponent(Volume);
	Volume->SetBoxExtent(FVector(150.f, 140.f, 150.f));
	Volume->SetCollisionProfileName(TEXT("Trigger"));
	Volume->SetCollisionResponseToAllChannels(ECR_Ignore);
	Volume->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
}

void ACRWorkshopTrigger::BeginPlay()
{
	Super::BeginPlay();
	// Editor MoveActorsToLevel uses native copy/paste; constructor-time serialized
	// delegate bindings are not a reliable runtime owner after migration/reload.
	UE_LOG(LogTemp, Display, TEXT("CR_ENTRY BeginPlay previous_binding=%d"), Volume->OnComponentBeginOverlap.IsBound());
	Volume->OnComponentBeginOverlap.AddUniqueDynamic(this, &ACRWorkshopTrigger::OnEntry);
	TArray<AActor*> Present;
	Volume->GetOverlappingActors(Present, ACRCharacter::StaticClass());
	if (!Present.IsEmpty()) if (auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>()) Mode->TryAdvance(ECRObjective::ReachWorkshop);
}

void ACRWorkshopTrigger::EndPlay(const EEndPlayReason::Type Reason)
{
	Volume->OnComponentBeginOverlap.RemoveDynamic(this, &ACRWorkshopTrigger::OnEntry);
	Super::EndPlay(Reason);
}

void ACRWorkshopTrigger::OnEntry(UPrimitiveComponent*, AActor* OtherActor, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
	if (!Cast<ACRCharacter>(OtherActor)) return;
	if (auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>()) Mode->TryAdvance(ECRObjective::ReachWorkshop);
}
