#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "CRWeaponData.generated.h"
class USoundBase;
class UMaterialInterface;
UCLASS(BlueprintType)
class CINDERRELAY_API UCRWeaponData : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Balance", meta=(ClampMin="1")) int32 MagazineCapacity = 5;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Balance", meta=(ClampMin="0")) int32 InitialReserve = 25;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Balance", meta=(ClampMin="0.1")) float ShotInterval = .9f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Balance", meta=(ClampMin="0.1")) float ReloadDuration = 2.4f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Balance", meta=(ClampMin="0")) float BodyDamage = 40;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Balance", meta=(ClampMin="1")) float HeadMultiplier = 1.75f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Balance", meta=(ClampMin="100")) float Range = 10000;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation") float AimFOV = 65;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation", meta=(ClampMin="0.01")) float AimSeconds = .18f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation") float RecoilDegrees = 2;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation") float RecoverySpeed = 12;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation") FVector HipLocation = FVector(28,18,-18);
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation") FVector AimLocation = FVector(28,0,-10);
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation") TObjectPtr<UMaterialInterface> MetalMaterial;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation") TObjectPtr<UMaterialInterface> AccentMaterial;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Audio") TObjectPtr<USoundBase> ShotSound;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Audio") TObjectPtr<USoundBase> ReloadSound;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Audio") TObjectPtr<USoundBase> DrySound;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Audio") TObjectPtr<USoundBase> HitSound;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Audio") TObjectPtr<USoundBase> ImpactSound;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Audio") TObjectPtr<USoundBase> HurtSound;
};
