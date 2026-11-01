#include "CRWeaponAnimInstance.h"
#include "CRWeaponComponent.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimNode_SequencePlayer.h"
#include "AnimNodes/AnimNode_TwoWayBlend.h"
#include "AnimNodes/AnimNode_Slot.h"
#include "GameFramework/Pawn.h"
#include "Components/SkeletalMeshComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace
{
struct FCRWeaponAnimProxy final : FAnimInstanceProxy
{
    FAnimNode_SequencePlayer_Standalone Idle,Walk,Sprint,ADS;
    FAnimNode_TwoWayBlend Move,Run,Aim;
    FAnimNode_Slot Action;
    int32 DebugUpdates=0;
    explicit FCRWeaponAnimProxy(UAnimInstance* Instance):FAnimInstanceProxy(Instance)
    {
        Move.A.SetLinkNode(&Idle);Move.B.SetLinkNode(&Walk);
        Run.A.SetLinkNode(&Move);Run.B.SetLinkNode(&Sprint);
        Aim.A.SetLinkNode(&Run);Aim.B.SetLinkNode(&ADS);
        Action.Source.SetLinkNode(&Aim);Action.SlotName=TEXT("WeaponAction");Action.bAlwaysUpdateSourcePose=true;
        for(auto* Player:{&Idle,&Walk,&Sprint,&ADS}) Player->SetLoopAnimation(true);
    }
    virtual FAnimNode_Base* GetCustomRootNode() override { return &Action; }
    virtual void PreUpdate(UAnimInstance* Instance,float Delta) override
    {
        FAnimInstanceProxy::PreUpdate(Instance,Delta);
        const auto* P=CastChecked<UCRWeaponAnimInstance>(Instance);
        // All UObject reads happen on the game thread, before parallel evaluation.
        Idle.SetSequence(P->Idle);Walk.SetSequence(P->Walk);Sprint.SetSequence(P->Sprint);ADS.SetSequence(P->ADS);
        Move.Alpha=P->WalkWeight;Run.Alpha=P->SprintWeight;Aim.Alpha=P->AimWeight;
        if(++DebugUpdates==120 && FParse::Param(FCommandLine::Get(),TEXT("CRHandlingDebug")))
            UE_LOG(LogTemp,Display,TEXT("CR_HANDLING_GRAPH idle=%s ads=%s time=%.3f weights=%.2f/%.2f/%.2f wrist=%s"),
                *GetNameSafe(P->Idle),*GetNameSafe(P->ADS),Idle.GetCurrentAssetTime(),Move.Alpha,Run.Alpha,Aim.Alpha,
                *Instance->GetOwningComponent()->GetBoneLocation(TEXT("wrist_R"),EBoneSpaces::ComponentSpace).ToString());
    }
};
}
FAnimInstanceProxy* UCRWeaponAnimInstance::CreateAnimInstanceProxy() { return new FCRWeaponAnimProxy(this); }
void UCRWeaponAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) { delete Proxy; }
void UCRWeaponAnimInstance::NativeUpdateAnimation(float Delta)
{
    Super::NativeUpdateAnimation(Delta);
    const APawn* Pawn=TryGetPawnOwner();const auto* Weapon=Pawn?Pawn->FindComponentByClass<UCRWeaponComponent>():nullptr;
    const float Speed=Pawn?Pawn->GetVelocity().Size2D():0;
    WalkWeight=FMath::FInterpTo(WalkWeight,FMath::Clamp(Speed/260.f,0.f,1.f),Delta,9.f);
    SprintWeight=FMath::FInterpTo(SprintWeight,Weapon&&Weapon->bSprinting?1.f:0.f,Delta,9.f);
    AimWeight=FMath::FInterpTo(AimWeight,Weapon&&Weapon->bAiming?1.f:0.f,Delta,16.f);
}
