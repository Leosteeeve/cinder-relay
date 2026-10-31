#include "CRAmmoPickup.h"
#include "CRCharacter.h"
#include "CRWeaponComponent.h"
#include "CRGameMode.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
ACRAmmoPickup::ACRAmmoPickup() { PrimaryActorTick.bCanEverTick=false; Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AmmoCase")); SetRootComponent(Mesh); Mesh->SetCollisionProfileName(TEXT("BlockAll")); Mesh->SetCanEverAffectNavigation(false); }
void ACRAmmoPickup::BeginPlay()
{
    Super::BeginPlay(); if(const auto* GM=GetWorld()->GetAuthGameMode<ACRGameMode>())bCollected=GM->IsPickupCollected(PickupId);
    if(bCollected) { SetActorHiddenInGame(true); SetActorEnableCollision(false); }
}
bool ACRAmmoPickup::CanInteract_Implementation(ACRCharacter* P) const { return !bCollected&&IsValid(P)&&P->CanInteractWith(this)&&P->Weapon->CanUse()&&P->Weapon->Reserve<100; }
FText ACRAmmoPickup::GetInteractionPrompt_Implementation(ACRCharacter* P) const { return CanInteract_Implementation(P)?FText::FromString(FString::Printf(TEXT("E  Take ROOK-5 ammunition (+%d)"),Amount)):FText::GetEmpty(); }
void ACRAmmoPickup::Interact_Implementation(ACRCharacter* P)
{
    if(!CanInteract_Implementation(P)||P->Weapon->AddReserve(Amount)<=0)return;
    bCollected=true; if(auto* GM=GetWorld()->GetAuthGameMode<ACRGameMode>())GM->RecordPickupCollected(PickupId);
    SetActorHiddenInGame(true); SetActorEnableCollision(false); UE_LOG(LogTemp,Display,TEXT("CR_AMMO Collected id=%s"),*PickupId.ToString());
}
