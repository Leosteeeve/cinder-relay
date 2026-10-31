#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CRHealthComponent.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FCRHealthChanged, float, Health, float, Damage);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FCRDied);
UCLASS(ClassGroup=(CinderRelay), meta=(BlueprintSpawnableComponent))
class CINDERRELAY_API UCRHealthComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UCRHealthComponent();
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Health", meta=(ClampMin="1")) float MaxHealth = 100;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Health") float Health = 100;
    UPROPERTY(BlueprintAssignable) FCRHealthChanged OnHealthChanged;
    UPROPERTY(BlueprintAssignable) FCRDied OnDeath;
    UFUNCTION(BlueprintPure) bool IsDead() const { return Health <= 0; }
    bool RestoreCheckpointHealth(float Value);
    double GetLastDamageTime() const { return LastDamageTime; }
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    double LastDamageTime = -1000;
    UFUNCTION() void ReceiveDamage(AActor* Damaged, float Damage, const UDamageType* Type, AController* Instigator, AActor* Causer);
};
