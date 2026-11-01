#include "CRWeaponCueNotify.h"
#include "CRWeaponViewComponent.h"
#include "Animation/ActiveMontageInstanceScope.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Actor.h"
void UCRWeaponCueNotify::Notify(USkeletalMeshComponent* Mesh,UAnimSequenceBase* Animation,const FAnimNotifyEventReference& EventReference)
{
    Super::Notify(Mesh,Animation,EventReference);
    const auto* Context=EventReference.GetContextData<UE::Anim::FAnimNotifyMontageInstanceContext>();
    if(!Context || !Mesh || !Mesh->GetOwner()) return;
    if(auto* View=Mesh->GetOwner()->FindComponentByClass<UCRWeaponViewComponent>())
        View->HandleAnimationCue(Mesh,Animation,Cue,Context->MontageInstanceID);
}
