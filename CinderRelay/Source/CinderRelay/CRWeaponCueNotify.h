#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "CRWeaponCueNotify.generated.h"
UCLASS()
class CINDERRELAY_API UCRWeaponCueNotify : public UAnimNotify
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category="Cosmetic") FName Cue=TEXT("EjectCase");
    virtual void Notify(USkeletalMeshComponent* Mesh,UAnimSequenceBase* Animation,const FAnimNotifyEventReference& EventReference) override;
    virtual FString GetNotifyName_Implementation() const override { return Cue.ToString(); }
};
