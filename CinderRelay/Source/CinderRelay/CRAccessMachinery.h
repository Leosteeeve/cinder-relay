#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInteractable.h"
#include "CRAccessMachinery.generated.h"
class UStaticMeshComponent;
class UBoxComponent;
class UTextRenderComponent;
/** Fictional maintenance shuttle. Safe timed crossing or a permanently available side walk. */
UCLASS()
class CINDERRELAY_API ACRAccessMachinery : public AActor, public ICRInteractable
{
    GENERATED_BODY()
public:
    ACRAccessMachinery();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Shuttle;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Control;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UBoxComponent> Barrier;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UTextRenderComponent> Status;
    virtual bool CanInteract_Implementation(ACRCharacter* Player) const override;
    virtual FText GetInteractionPrompt_Implementation(ACRCharacter* Player) const override;
    virtual void Interact_Implementation(ACRCharacter* Player) override;
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
private:
    float Aperture=0;
    bool bLastOpen=false;
};
