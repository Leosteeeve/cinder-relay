#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInteractable.h"
#include "CRSalvagePickup.generated.h"
class UStaticMeshComponent;
UCLASS()
class CINDERRELAY_API ACRSalvagePickup : public AActor, public ICRInteractable
{
    GENERATED_BODY()
public:
    ACRSalvagePickup();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName SourceId;
    virtual bool CanInteract_Implementation(ACRCharacter* Player) const override;
    virtual FText GetInteractionPrompt_Implementation(ACRCharacter* Player) const override;
    virtual void Interact_Implementation(ACRCharacter* Player) override;
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    UFUNCTION() void Reconcile();
};
