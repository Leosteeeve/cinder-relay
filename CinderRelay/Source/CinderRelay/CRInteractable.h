#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "CRInteractable.generated.h"

class ACRCharacter;

UINTERFACE(BlueprintType)
class CINDERRELAY_API UCRInteractable : public UInterface
{
	GENERATED_BODY()
};

class CINDERRELAY_API ICRInteractable
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Interaction")
	bool CanInteract(ACRCharacter* Player) const;
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Interaction")
	FText GetInteractionPrompt(ACRCharacter* Player) const;
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Interaction")
	void Interact(ACRCharacter* Player);
};
