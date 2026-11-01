#pragma once
#include "CoreMinimal.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "CRCharacterMovementComponent.generated.h"

/** Single-player slide velocity policy. Native PhysWalking owns floors, steps and sweeps. */
UCLASS()
class CINDERRELAY_API UCRCharacterMovementComponent : public UCharacterMovementComponent
{
    GENERATED_BODY()
public:
    UPROPERTY(EditDefaultsOnly, Category="Slide", meta=(ClampMin="300")) float SlideMinimumSpeed=430.f;
    UPROPERTY(EditDefaultsOnly, Category="Slide", meta=(ClampMin="430",ClampMax="700")) float SlideMaximumSpeed=620.f;
    UPROPERTY(EditDefaultsOnly, Category="Slide", meta=(ClampMin="0.65",ClampMax="0.85")) float SlideDuration=.75f;
    UPROPERTY(EditDefaultsOnly, Category="Slide", meta=(ClampMin="0.5")) float SlideCooldown=1.f;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Slide") bool bSliding=false;
    bool TryStartSlide();
    void EndSlide(FName Reason);
    static float DecayedSlideSpeed(float Speed, float Seconds, float FloorDirectionDot);
    virtual float GetMaxSpeed() const override;
protected:
    virtual void CalcVelocity(float DeltaTime,float Friction,bool bFluid,float BrakingDeceleration) override;
    virtual void UpdateCharacterStateBeforeMovement(float DeltaSeconds) override;
    virtual void OnMovementUpdated(float DeltaSeconds,const FVector& OldLocation,const FVector& OldVelocity) override;
private:
    double SlideStarted=0, NextSlideTime=0;
    FVector SlideDirection=FVector::ForwardVector;
};
