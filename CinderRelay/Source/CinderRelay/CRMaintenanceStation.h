#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInteractable.h"
#include "CRMaintenanceStation.generated.h"
class UStaticMeshComponent;
class UTextRenderComponent;

/** One chapter's physical diagnostic controls. No item authority or serialized IDs. */
UCLASS()
class CINDERRELAY_API ACRMaintenanceStation : public AActor, public ICRInteractable
{
    GENERATED_BODY()
public:
    ACRMaintenanceStation();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Panel;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UTextRenderComponent> Display;
    UPROPERTY(EditAnywhere, Category="Chapter", meta=(ClampMin="0",ClampMax="2")) int32 Step=0;
    virtual bool CanInteract_Implementation(ACRCharacter* Player) const override;
    virtual FText GetInteractionPrompt_Implementation(ACRCharacter* Player) const override;
    virtual void Interact_Implementation(ACRCharacter* Player) override;
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UFUNCTION() void Refresh();
};
