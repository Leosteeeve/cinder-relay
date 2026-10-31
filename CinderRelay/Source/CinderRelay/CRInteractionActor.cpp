#include "CRInteractionActor.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"

namespace
{
	ECRObjective RequiredObjective(ECRInteractionKind Kind)
	{
		switch (Kind)
		{
		case ECRInteractionKind::PowerModule: return ECRObjective::FindModule;
		case ECRInteractionKind::Relay: return ECRObjective::RestorePower;
		default: return ECRObjective::InvestigateSignal;
		}
	}
}

ACRInteractionActor::ACRInteractionActor()
{
	PrimaryActorTick.bCanEverTick = false;
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InteractionMesh"));
	SetRootComponent(Mesh);
	Mesh->SetCollisionProfileName(TEXT("BlockAll"));
}

bool ACRInteractionActor::CanInteract_Implementation(ACRCharacter* Player) const
{
	const auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>();
	return IsValid(Player) && !bUsed && Mode && Mode->GetObjective() == RequiredObjective(Kind) && Player->CanInteractWith(this);
}

void ACRInteractionActor::BeginPlay()
{
	Super::BeginPlay();
	const auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>();
	bUsed = Mode && Mode->GetObjective() > RequiredObjective(Kind);
	if (bUsed && Kind == ECRInteractionKind::PowerModule)
	{
		SetActorHiddenInGame(true);
		SetActorEnableCollision(false);
	}
	// Restore state silently: narrative/Blueprint completion events must never replay on streaming.
	if (bUsed) UE_LOG(LogTemp, Display, TEXT("CR_INTERACTION Reconciled kind=%d objective=%d"), int32(Kind), int32(Mode->GetObjective()));
}

FText ACRInteractionActor::GetInteractionPrompt_Implementation(ACRCharacter* Player) const
{
	if (bUsed) return FText::GetEmpty();
	if (!CanInteract_Implementation(Player))
		return Kind == ECRInteractionKind::Relay
			? NSLOCTEXT("Cinder", "NeedModule", "Relay Nine requires a functional power module.")
			: NSLOCTEXT("Cinder", "Inactive", "No active signal.");
	switch (Kind)
	{
	case ECRInteractionKind::PowerModule: return NSLOCTEXT("Cinder", "TakeModule", "[E] Take functional power module");
	case ECRInteractionKind::Relay: return NSLOCTEXT("Cinder", "Restore", "[E] Install module - restore Relay Nine");
	default: return NSLOCTEXT("Cinder", "Investigate", "[E] Investigate restored signal");
	}
}

void ACRInteractionActor::Interact_Implementation(ACRCharacter* Player)
{
	if (!CanInteract_Implementation(Player)) return;
	ACRGameMode* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>();
	// Set the local guard before publishing objective changes (re-entrancy safe).
	bUsed = true;
	if (!Mode->TryAdvance(RequiredObjective(Kind))) { bUsed = false; return; }
	if (Kind == ECRInteractionKind::PowerModule)
	{
		SetActorHiddenInGame(true);
		SetActorEnableCollision(false);
	}
	UE_LOG(LogTemp, Display, TEXT("CR_INTERACTION %s %d"), *GetName(), static_cast<int32>(Kind));
	OnInteractionCompleted();
}
