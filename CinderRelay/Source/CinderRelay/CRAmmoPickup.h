#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInteractable.h"
#include "CRAmmoPickup.generated.h"
class UStaticMeshComponent;
UCLASS()
class CINDERRELAY_API ACRAmmoPickup : public AActor,public ICRInteractable
{
    GENERATED_BODY()
public:
    ACRAmmoPickup();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName PickupId=TEXT("CR02_YardAmmo");
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="1",ClampMax="25")) int32 Amount=10;
    virtual bool CanInteract_Implementation(ACRCharacter* Player) const override;
    virtual FText GetInteractionPrompt_Implementation(ACRCharacter* Player) const override;
    virtual void Interact_Implementation(ACRCharacter* Player) override;
protected:
    virtual void BeginPlay() override;
private:
    bool bCollected=false;
};
