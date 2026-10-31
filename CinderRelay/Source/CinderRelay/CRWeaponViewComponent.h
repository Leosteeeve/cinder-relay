#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CRWeaponViewComponent.generated.h"
class UCRWeaponComponent;
class USceneComponent;
class UStaticMeshComponent;
class UStaticMesh;
struct FStreamableHandle;
UCLASS(ClassGroup=(CinderRelay), meta=(BlueprintSpawnableComponent))
class CINDERRELAY_API UCRWeaponViewComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UCRWeaponViewComponent();
    UPROPERTY(EditDefaultsOnly, Category="Appearance") TSoftObjectPtr<UStaticMesh> RookAppearance;
    UPROPERTY(EditDefaultsOnly, Category="Appearance") TSoftObjectPtr<UStaticMesh> SurveyAppearance;
    void SetPresentationHidden(bool Hidden);
    bool HasImportedAppearance() const;
    virtual void TickComponent(float Delta, ELevelTick TickType, FActorComponentTickFunction* ThisTick) override;
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> FallbackParts;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> ImportedRook;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> ImportedOptic;
    TSharedPtr<FStreamableHandle> AppearanceLoad;
    bool bPresentationHidden=false;
    UFUNCTION() void RefreshAppearance();
    UPROPERTY() TObjectPtr<UStaticMesh> Cube;
    UPROPERTY() TObjectPtr<USceneComponent> ViewRoot;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Flash;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> ImpactMarker;
    TWeakObjectPtr<UCRWeaponComponent> Weapon;
    float Recoil = 0, BaseFOV = 85, CoverFraction = 0, CoverCountdown = 0;
    FTimerHandle FlashTimer, ImpactTimer;
    UFUNCTION() void Shot(FVector Impact, bool bHitTarget, bool bBlockingHit);
    UFUNCTION() void Cue(FName Name);
    UFUNCTION() void Hurt(float Health, float Damage);
    void HideFlash();
    void HideImpact();
};
