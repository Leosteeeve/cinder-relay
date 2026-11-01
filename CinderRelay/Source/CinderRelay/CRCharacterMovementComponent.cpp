#include "CRCharacterMovementComponent.h"
#include "CRCharacter.h"
#include "CRHealthComponent.h"
#include "CRWeaponComponent.h"
#include "Engine/World.h"

bool UCRCharacterMovementComponent::TryStartSlide()
{
    auto* P=Cast<ACRCharacter>(CharacterOwner);
    if(!P || bSliding || !P->IsSprintHeld() || !IsMovingOnGround() || !CurrentFloor.IsWalkableFloor() ||
       !P->Health || P->Health->IsDead() || !P->Weapon || !P->Weapon->CanUse() ||
       P->Weapon->State==ECRWeaponState::Reloading || Velocity.Size2D()<SlideMinimumSpeed ||
       GetWorld()->GetTimeSeconds()<NextSlideTime) return false;
    SlideDirection=Velocity.GetSafeNormal2D();
    SlideStarted=GetWorld()->GetTimeSeconds(); bSliding=true;
    Velocity=SlideDirection*FMath::Min(Velocity.Size2D()+100.f,SlideMaximumSpeed);
    P->Weapon->SetAiming(false); P->Weapon->SetSprinting(false); P->Crouch();
    UE_LOG(LogTemp,Display,TEXT("CR_SLIDE Start time=%.3f speed=%.1f"),SlideStarted,Velocity.Size2D());
    return true;
}
void UCRCharacterMovementComponent::EndSlide(FName Reason)
{
    if(!bSliding) return;
    bSliding=false; NextSlideTime=GetWorld()->GetTimeSeconds()+SlideCooldown;
    UE_LOG(LogTemp,Display,TEXT("CR_SLIDE End reason=%s duration=%.3f speed=%.1f"),*Reason.ToString(),GetWorld()->GetTimeSeconds()-SlideStarted,Velocity.Size2D());
    if(auto* P=Cast<ACRCharacter>(CharacterOwner)) P->SlideEnded();
}
float UCRCharacterMovementComponent::DecayedSlideSpeed(float Speed,float Seconds,float FloorDirectionDot)
{
    // A floor normal opposing travel denotes uphill. Downhill still decelerates.
    const float Deceleration=FMath::Clamp(540.f-900.f*FloorDirectionDot,260.f,1000.f);
    return FMath::Max(0.f,Speed-Deceleration*FMath::Max(0.f,Seconds));
}
float UCRCharacterMovementComponent::GetMaxSpeed() const { return bSliding?SlideMaximumSpeed:Super::GetMaxSpeed(); }
void UCRCharacterMovementComponent::CalcVelocity(float DeltaTime,float Friction,bool bFluid,float BrakingDeceleration)
{
    if(!bSliding) { Super::CalcVelocity(DeltaTime,Friction,bFluid,BrakingDeceleration); return; }
    const float Speed=DecayedSlideSpeed(FMath::Min(Velocity.Size2D(),SlideMaximumSpeed),DeltaTime,
        FVector::DotProduct(SlideDirection,CurrentFloor.HitResult.ImpactNormal));
    Velocity=SlideDirection*Speed;
}
void UCRCharacterMovementComponent::UpdateCharacterStateBeforeMovement(float DeltaSeconds)
{
    if(bSliding)
    {
        const auto* P=Cast<ACRCharacter>(CharacterOwner);
        if(!P || !P->Weapon->CanUse() || P->Weapon->State==ECRWeaponState::Reloading || !IsMovingOnGround()) EndSlide(TEXT("InvalidState"));
        else if(GetWorld()->GetTimeSeconds()-SlideStarted>=SlideDuration) EndSlide(TEXT("Duration"));
        else bWantsToCrouch=true;
    }
    Super::UpdateCharacterStateBeforeMovement(DeltaSeconds);
}
void UCRCharacterMovementComponent::OnMovementUpdated(float DeltaSeconds,const FVector& OldLocation,const FVector& OldVelocity)
{
    Super::OnMovementUpdated(DeltaSeconds,OldLocation,OldVelocity);
    if(!bSliding) return;
    if(!IsMovingOnGround()) EndSlide(TEXT("Airborne"));
    else if(GetWorld()->GetTimeSeconds()-SlideStarted>.06 &&
        (Velocity.Size2D()<120.f || FVector::DotProduct(UpdatedComponent->GetComponentLocation()-OldLocation,SlideDirection)<40.f*DeltaSeconds))
        EndSlide(TEXT("Obstructed"));
}
