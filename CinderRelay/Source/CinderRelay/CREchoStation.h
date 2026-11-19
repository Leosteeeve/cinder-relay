#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInteractable.h"
#include "CREchoStation.generated.h"
class UBoxComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

UCLASS()
class CINDERRELAY_API ACREchoStation : public AActor, public ICRInteractable
{
	GENERATED_BODY()
public:
	ACREchoStation();
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Echo", meta=(ClampMin="0",ClampMax="4")) int32 StationIndex = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Panel;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Rotor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UTextRenderComponent> Display;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UBoxComponent> TurnControl;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UBoxComponent> ConfirmControl;
	void OnConstruction(const FTransform& Transform) override;
	bool CanInteract_Implementation(ACRCharacter* Player) const override;
	FText GetInteractionPrompt_Implementation(ACRCharacter* Player) const override;
	void Interact_Implementation(ACRCharacter* Player) override;
protected:
	void BeginPlay() override;
	void EndPlay(const EEndPlayReason::Type Reason) override;
	void Tick(float DeltaSeconds) override;
private:
	UBoxComponent* AimedControl(ACRCharacter* Player) const;
	void Refresh();
	float TargetYaw = 0;
};
