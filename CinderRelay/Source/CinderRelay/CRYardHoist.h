#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInteractable.h"
#include "CRYardHoist.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

/** The yard transfer wagon lifts once and remains locked overhead until a new run. */
UCLASS()
class CINDERRELAY_API ACRYardHoist : public AActor, public ICRInteractable
{
	GENERATED_BODY()
public:
	ACRYardHoist();
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UBoxComponent> WagonBody;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Wagon;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> WestCable;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> EastCable;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UBoxComponent> ConsoleFace;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Panel;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UTextRenderComponent> Status;
	virtual bool CanInteract_Implementation(ACRCharacter* Player) const override;
	virtual FText GetInteractionPrompt_Implementation(ACRCharacter* Player) const override;
	virtual void Interact_Implementation(ACRCharacter* Player) override;
protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
private:
	void SetTravel(float Fraction);
	void ShowLocked();
	bool IsAtConsole(const ACRCharacter* Player) const;
	float TravelTime = 0.f;
};
