#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "CRAshWarden.generated.h"
class UCRHealthComponent;
class UBehaviorTree;
class UStaticMeshComponent;
class USoundBase;
UCLASS()
class CINDERRELAY_API ACRAshWarden : public ACharacter
{
    GENERATED_BODY()
public:
    ACRAshWarden();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UCRHealthComponent> Health;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USceneComponent> Silhouette;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Body;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Head;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Encounter") FName EnemyId;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="AI") TObjectPtr<UBehaviorTree> Behavior;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="AI") float SightRadius=1500;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="AI") float MemorySeconds=5;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat") float ShotDamage=8;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat") float AttackInterval=1.8f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat") float AccuracyDegrees=2;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Combat") float AttackRange=1400;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Audio") TObjectPtr<USoundBase> ShotSound;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Audio") TObjectPtr<USoundBase> HitSound;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Audio") TObjectPtr<USoundBase> DeathSound;
    void PresentAttack();
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Flash;
    FTimerHandle FlinchTimer,FlashTimer;
    UFUNCTION() void Damaged(float Current,float Damage);
    UFUNCTION() void Died();
    void EndFlinch();
    void EndFlash();
};
