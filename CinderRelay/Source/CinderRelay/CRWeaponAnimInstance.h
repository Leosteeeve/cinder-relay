#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "CRWeaponAnimInstance.generated.h"

/** A small native graph of engine sequence players, blends and one montage slot.
 * Animations are cosmetic. WeaponComponent remains the only combat authority. */
UCLASS(Transient, Blueprintable)
class CINDERRELAY_API UCRWeaponAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UPROPERTY(Transient, BlueprintReadOnly, Category="Presentation") TObjectPtr<UAnimSequence> Idle;
    UPROPERTY(Transient, BlueprintReadOnly, Category="Presentation") TObjectPtr<UAnimSequence> Walk;
    UPROPERTY(Transient, BlueprintReadOnly, Category="Presentation") TObjectPtr<UAnimSequence> Sprint;
    UPROPERTY(Transient, BlueprintReadOnly, Category="Presentation") TObjectPtr<UAnimSequence> ADS;
    UPROPERTY(Transient, BlueprintReadOnly, Category="Presentation") float WalkWeight=0;
    UPROPERTY(Transient, BlueprintReadOnly, Category="Presentation") float SprintWeight=0;
    UPROPERTY(Transient, BlueprintReadOnly, Category="Presentation") float AimWeight=0;
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;
protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* InProxy) override;
};
