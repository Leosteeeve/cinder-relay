#include "CRWeaponViewComponent.h"
#include "CRWeaponAnimInstance.h"
#include "CRWeaponComponent.h"
#include "CRCharacter.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "CRAudioSettingsSubsystem.h"

bool UCRWeaponViewComponent::ConsumeShotCue(int32 Expected,int32 Received,bool& Spent)
{
    if(Spent || Expected==INDEX_NONE || Expected!=Received) return false;
    Spent=true;return true;
}
void UCRWeaponViewComponent::LoadHandling()
{
    if(ArmsAppearance.IsNull() || HandlingClips.Num()!=7) { bHandlingSettled=true;return; }
    TArray<FSoftObjectPath> Paths={ArmsAppearance.ToSoftObjectPath()};
    for(const auto& Clip:HandlingClips) Paths.Add(Clip.ToSoftObjectPath());
    for(const auto& Prop:HandlingProps) Paths.Add(Prop.ToSoftObjectPath());
    for(const auto& Sound:HandlingSounds) Paths.Add(Sound.ToSoftObjectPath());
    HandlingLoad=UAssetManager::GetStreamableManager().RequestAsyncLoad(Paths,FStreamableDelegate::CreateUObject(this,&UCRWeaponViewComponent::HandlingLoaded));
    if(!HandlingLoad) bHandlingSettled=true;
}
void UCRWeaponViewComponent::AttachAuthoredProp(UStaticMeshComponent* Prop,FName Bone)
{
    if(!Prop || !Arms || !Arms->GetSkeletalMeshAsset()) return;
    const auto* Mesh=Arms->GetSkeletalMeshAsset();const int32 Index=Arms->GetBoneIndex(Bone);
    if(Index==INDEX_NONE) return;
    // Exported static vertices use the same armature space. Remove the actual
    // imported reference basis; never assume Blender/FBX bone axes are identity.
    FTransform Ref=Mesh->GetRefSkeleton().GetRefBonePose()[Index];
    for(int32 Parent=Mesh->GetRefSkeleton().GetParentIndex(Index);Parent!=INDEX_NONE;Parent=Mesh->GetRefSkeleton().GetParentIndex(Parent))
        Ref=Ref*Mesh->GetRefSkeleton().GetRefBonePose()[Parent];
    Prop->AttachToComponent(Arms,FAttachmentTransformRules::KeepRelativeTransform,Bone);
    Prop->SetRelativeTransform(Ref.Inverse());
}
void UCRWeaponViewComponent::HandlingLoaded()
{
    bHandlingSettled=true;
    if(!IsValid(GetOwner()) || !ViewRoot || !Weapon.IsValid() || bHandlingReady) return;
    // Either completion order is valid; missing base imports retain all legacy
    // recoil/reload behavior instead of hiding hands but disabling the fallback.
    if(!bAppearanceSettled || !HasImportedAppearance()) return;
    if(!ArmsAppearance.Get() || HandlingClips.Num()!=7 || HandlingProps.Num()!=3) return;
    for(const auto& Clip:HandlingClips) if(!Clip.Get() || Clip.Get()->GetSkeleton()!=ArmsAppearance.Get()->GetSkeleton()) return;
    for(const auto& Prop:HandlingProps) if(!Prop.Get()) return;
    for(FName Bone:{FName(TEXT("weapon")),FName(TEXT("feed")),FName(TEXT("cycle_handle")),FName(TEXT("wrist_R")),FName(TEXT("wrist_L"))})
        if(ArmsAppearance.Get()->GetRefSkeleton().FindBoneIndex(Bone)==INDEX_NONE) return;
    Arms=NewObject<USkeletalMeshComponent>(GetOwner(),TEXT("EliasFirstPersonArms"));GetOwner()->AddInstanceComponent(Arms);
    Arms->SetupAttachment(ViewRoot);Arms->SetSkeletalMeshAsset(ArmsAppearance.Get());
    Arms->SetCollisionEnabled(ECollisionEnabled::NoCollision);Arms->SetCanEverAffectNavigation(false);
    Arms->SetOnlyOwnerSee(true);Arms->SetCastShadow(false);Arms->SetFirstPersonPrimitiveType(EFirstPersonPrimitiveType::FirstPerson);
    Arms->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Arms->SetAnimInstanceClass(UCRWeaponAnimInstance::StaticClass());Arms->RegisterComponent();
    auto* Anim=Cast<UCRWeaponAnimInstance>(Arms->GetAnimInstance());
    if(!Anim) { Arms->DestroyComponent();Arms=nullptr;return; }
    Anim->Idle=HandlingClips[0].Get();Anim->Walk=HandlingClips[1].Get();Anim->Sprint=HandlingClips[2].Get();Anim->ADS=HandlingClips[3].Get();
    // Allocate three native montage wrappers once after async residency, not per shot.
    for(int32 Index=4;Index<7;++Index)
        ActionMontages.Add(UAnimMontage::CreateSlotAnimationAsDynamicMontage(HandlingClips[Index].Get(),TEXT("WeaponAction"),Index==4?.025f:.07f,.07f));
    auto Part=[this](const TCHAR* Name,UStaticMesh* Mesh)
    {
        auto* P=NewObject<UStaticMeshComponent>(GetOwner(),Name);GetOwner()->AddInstanceComponent(P);P->SetupAttachment(ViewRoot);
        P->SetStaticMesh(Mesh);P->SetCollisionEnabled(ECollisionEnabled::NoCollision);P->SetCanEverAffectNavigation(false);P->SetCastShadow(false);
        P->SetOnlyOwnerSee(true);P->SetFirstPersonPrimitiveType(EFirstPersonPrimitiveType::FirstPerson);P->RegisterComponent();return P;
    };
    Feed=Part(TEXT("RookFeedAnimated"),HandlingProps[0].Get());CycleHandle=Part(TEXT("RookCycleAnimated"),HandlingProps[1].Get());
    AttachAuthoredProp(ImportedRook,TEXT("weapon"));AttachAuthoredProp(ImportedOptic,TEXT("optic"));
    AttachAuthoredProp(Feed,TEXT("feed"));AttachAuthoredProp(CycleHandle,TEXT("cycle_handle"));
    Flash->AttachToComponent(ImportedRook,FAttachmentTransformRules::KeepRelativeTransform);
    for(int32 Index=0;Index<8;++Index)
    {
        auto* P=Part(*FString::Printf(TEXT("CosmeticCase%d"),Index),HandlingProps[2].Get());
        P->DetachFromComponent(FDetachmentTransformRules::KeepWorldTransform);P->SetFirstPersonPrimitiveType(EFirstPersonPrimitiveType::None);P->SetVisibility(false);
        CasePool.Add(P);CaseMotions.AddDefaulted();
    }
    bHandlingReady=true;RefreshAppearance();
    UE_LOG(LogTemp,Display,TEXT("CR_HANDLING Ready bones=%d clips=7 cases=8"),Arms->GetNumBones());
}
void UCRWeaponViewComponent::PlayHandling(int32 Action)
{
    if(!bHandlingReady || bPresentationHidden || !Arms || !ActionMontages.IsValidIndex(Action)) return;
    auto* Anim=Arms->GetAnimInstance();if(!Anim) return;
    bCaseSpent=true;ActiveShotInstance=INDEX_NONE;ActiveActionInstance=INDEX_NONE;PlayedCueMask=0;
    ActiveAction=ActionMontages[Action];
    if(Anim->Montage_Play(ActiveAction,1.f)<=0) {ActiveAction=nullptr;return;}
    if(const auto* Instance=Anim->GetActiveInstanceForMontage(ActiveAction))
    {
        ActiveActionInstance=Instance->GetInstanceID();
        if(Action==0) {ActiveShotInstance=ActiveActionInstance;bCaseSpent=false;++AcceptedPresentationShots;}
    }
}
void UCRWeaponViewComponent::HandleAnimationCue(USkeletalMeshComponent* Mesh,UAnimSequenceBase* Animation,FName Cue,int32 Instance)
{
    if(!bHandlingReady || Mesh!=Arms || bPresentationHidden || !Weapon.IsValid() || Weapon->IsPresentationLocked()) return;
    if(Instance!=ActiveActionInstance || Instance==INDEX_NONE) return;
    if(Animation==HandlingClips[5].Get() && Weapon->State==ECRWeaponState::Reloading)
    {
        const int32 Index=Cue==TEXT("FeedOut")?0:Cue==TEXT("FeedIn")?1:INDEX_NONE;
        if(Index!=INDEX_NONE && !(PlayedCueMask&(1<<Index)))
        {
            PlayedCueMask|=1<<Index;
            if(auto* Audio=UCRAudioSettingsSubsystem::Get(this);Audio && Audio->IsReady())
                Audio->PlayEvent(Index==0?TEXT("FeedOut"):TEXT("FeedIn"),this,GetOwner()->GetActorLocation(),false);
            else if(HandlingSounds.IsValidIndex(Index) && HandlingSounds[Index].Get())
                UGameplayStatics::PlaySound2D(this,HandlingSounds[Index].Get(),.24f,1.f,0.f,nullptr,nullptr,false);
        }
        return;
    }
    if(Cue!=TEXT("EjectCase") || Animation!=HandlingClips[4].Get() || Weapon->State!=ECRWeaponState::Cycling) return;
    if(!ConsumeShotCue(ActiveShotInstance,Instance,bCaseSpent) || CasePool.IsEmpty()) return;
#if !UE_BUILD_SHIPPING
    if(bSuppressNextCase) { bSuppressNextCase=false;return; }
#endif
    // Existing validated marker owns both cosmetic sounds; no gameplay reward.
    // Cycle and case share this authored timestamp rather than inventing a timer.
    if(auto* Audio=UCRAudioSettingsSubsystem::Get(this);Audio && Audio->IsReady())
    {
        Audio->PlayEvent(TEXT("Cycle"),this,GetOwner()->GetActorLocation(),false);
        Audio->PlayEvent(TEXT("Case"),this,GetOwner()->GetActorLocation(),false);
    }
    const int32 Index=NextCase++%CasePool.Num();auto& Motion=CaseMotions[Index];
    Motion.Age=0;Motion.Origin=ImportedRook->GetComponentTransform().TransformPosition(FVector(-8,4,4));
    Motion.Velocity=ImportedRook->GetComponentTransform().TransformVectorNoScale(FVector(-35,130,65));
    Motion.Rotation=ImportedRook->GetComponentRotation();CasePool[Index]->SetWorldLocation(Motion.Origin);CasePool[Index]->SetVisibility(true);++EjectedCases;
    UE_LOG(LogTemp,Verbose,TEXT("CR_HANDLING Case shot=%d montage=%d total=%d"),AcceptedPresentationShots,Instance,EjectedCases);
}
void UCRWeaponViewComponent::CancelHandling(bool ClearCases)
{
    bCaseSpent=true;ActiveShotInstance=INDEX_NONE;ActiveActionInstance=INDEX_NONE;PlayedCueMask=0;
    if(Arms && ActiveAction) if(auto* Anim=Arms->GetAnimInstance()) Anim->Montage_Stop(.08f,ActiveAction);
    ActiveAction=nullptr;
    if(ClearCases) for(int32 I=0;I<CasePool.Num();++I) {CasePool[I]->SetVisibility(false);CaseMotions[I].Age=2;}
}
float UCRWeaponViewComponent::GetHandlingActionPosition() const
{
    return Arms && Arms->GetAnimInstance() && ActiveAction?Arms->GetAnimInstance()->Montage_GetPosition(ActiveAction):0.f;
}
void UCRWeaponViewComponent::WeaponStateChanged()
{
    if(!Weapon.IsValid()) return;
    const bool Interrupted=Weapon->State==ECRWeaponState::Disabled || Weapon->IsPresentationLocked();
    if(Interrupted || Weapon->State==ECRWeaponState::Ready) CancelHandling(Interrupted);
}
void UCRWeaponViewComponent::TickCases(float Delta)
{
    for(int32 I=0;I<CasePool.Num();++I)
    {
        auto& M=CaseMotions[I];if(M.Age>=1.15f) continue;M.Age+=Delta;
        if(M.Age>=1.15f) {CasePool[I]->SetVisibility(false);continue;}
        // Bounded collisionless cosmetic trajectory; no physics, damage or pickup.
        CasePool[I]->SetWorldLocation(M.Origin+M.Velocity*M.Age+FVector(0,0,-280)*M.Age*M.Age);
        CasePool[I]->SetWorldRotation(M.Rotation+FRotator(240,430,180)*M.Age);
    }
}
