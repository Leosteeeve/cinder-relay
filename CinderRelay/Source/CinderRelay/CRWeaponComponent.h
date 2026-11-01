#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CRWeaponComponent.generated.h"
class UCRWeaponData;
UENUM(BlueprintType) enum class ECRWeaponState : uint8 { Ready, Cycling, Reloading, Disabled };
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FCRWeaponChanged);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FCRShotAccepted, FVector, Impact, bool, bHitTarget, bool, bBlockingHit);
UENUM(BlueprintType) enum class ECRImpactKind : uint8 { Surface, EnemyHit, EnemyKill };
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FCRImpactConfirmed,FVector,Position,FVector,Normal,ECRImpactKind,Kind);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FCRWeaponCue, FName, Cue);
UCLASS(ClassGroup=(CinderRelay), meta=(BlueprintSpawnableComponent))
class CINDERRELAY_API UCRWeaponComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UCRWeaponComponent();
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Weapon") TObjectPtr<UCRWeaponData> Data;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Weapon") ECRWeaponState State = ECRWeaponState::Disabled;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Weapon") int32 Magazine = 0;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Weapon") int32 Reserve = 0;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Weapon") bool bAiming = false;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Weapon") bool bSprinting = false;
    UPROPERTY(EditAnywhere, Category="Debug") bool bDebugTraces = false;
    UPROPERTY(BlueprintAssignable) FCRWeaponChanged OnChanged;
    UPROPERTY(BlueprintAssignable) FCRShotAccepted OnShot;
    UPROPERTY(BlueprintAssignable) FCRImpactConfirmed OnImpact;
    UPROPERTY(BlueprintAssignable) FCRWeaponCue OnCue;
    UFUNCTION(BlueprintCallable) bool TryFire();
    UFUNCTION(BlueprintCallable) bool TryReload();
    UFUNCTION(BlueprintCallable) void SetAiming(bool bAim);
    UFUNCTION(BlueprintCallable) void SetSprinting(bool bSprint);
    UFUNCTION(BlueprintCallable) void Disable();
    UFUNCTION(BlueprintCallable) int32 AddReserve(int32 Amount);
    UFUNCTION(BlueprintPure) bool CanUse() const;
    UFUNCTION(BlueprintPure) float GetAimFOV() const;
    bool IsPresentationLocked() const { return bPresentationLocked; }
    void SetPresentationLocked(bool Locked);
    bool RestoreCheckpointAmmo(int32 SavedMagazine, int32 SavedReserve);
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    bool bPresentationLocked=false;
    FTimerHandle CycleTimer, ReloadTimer;
    double NextShot = 0, LastDry = -1;
    void CompleteCycle();
    void CompleteReload();
};
