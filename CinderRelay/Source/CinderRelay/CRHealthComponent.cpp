#include "CRHealthComponent.h"
#include "GameFramework/Actor.h"
#include "Engine/World.h"
bool UCRHealthComponent::RestoreCheckpointHealth(float Value)
{
    if (!FMath::IsFinite(Value) || Value <= 0 || Value > MaxHealth) return false;
    Health = Value; LastDamageTime = -1000; OnHealthChanged.Broadcast(Health, 0); return true;
}
UCRHealthComponent::UCRHealthComponent() { PrimaryComponentTick.bCanEverTick = false; }
void UCRHealthComponent::BeginPlay()
{
    Super::BeginPlay(); Health = FMath::Max(1.f, MaxHealth);
    GetOwner()->OnTakeAnyDamage.AddUniqueDynamic(this, &UCRHealthComponent::ReceiveDamage);
}
void UCRHealthComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    GetOwner()->OnTakeAnyDamage.RemoveDynamic(this, &UCRHealthComponent::ReceiveDamage);
    Super::EndPlay(Reason);
}
void UCRHealthComponent::ReceiveDamage(AActor*, float Damage, const UDamageType*, AController*, AActor*)
{
    if (IsDead() || !FMath::IsFinite(Damage) || Damage <= 0) return;
    const float Applied = FMath::Min(Health, Damage); Health -= Applied;
    LastDamageTime = GetWorld()->GetTimeSeconds();
    UE_LOG(LogTemp, Display, TEXT("CR_DAMAGE actor=%s amount=%.1f health=%.1f"), *GetOwner()->GetName(), Applied, Health);
    OnHealthChanged.Broadcast(Health, Applied);
    if (IsDead()) OnDeath.Broadcast();
}
