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
	Volume->OnComponentBeginOverlap.AddDynamic(this, &ACRWorkshopTrigger::OnEntry);
}

void ACRWorkshopTrigger::OnEntry(UPrimitiveComponent*, AActor* OtherActor, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
	if (!Cast<ACRCharacter>(OtherActor)) return;
	if (auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>()) Mode->TryAdvance(ECRObjective::ReachWorkshop);
}
