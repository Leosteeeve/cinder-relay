#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInteractable.h"
#include "CRInteractionActor.generated.h"

class UStaticMeshComponent;
UENUM(BlueprintType)
enum class ECRInteractionKind : uint8 { PowerModule, Relay, Signal };

UCLASS(Blueprintable)
class CINDERRELAY_API ACRInteractionActor : public AActor, public ICRInteractable
{
	GENERATED_BODY()
public:
	ACRInteractionActor();
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Mesh;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Interaction") ECRInteractionKind Kind = ECRInteractionKind::PowerModule;
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Interaction") bool bUsed = false;
	virtual bool CanInteract_Implementation(ACRCharacter* Player) const override;
	virtual FText GetInteractionPrompt_Implementation(ACRCharacter* Player) const override;
	virtual void Interact_Implementation(ACRCharacter* Player) override;
	UFUNCTION(BlueprintImplementableEvent, Category="Interaction") void OnInteractionCompleted();
};
