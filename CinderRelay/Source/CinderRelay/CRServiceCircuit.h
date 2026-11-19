#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRServiceCircuit.generated.h"

class UBoxComponent;
class UPointLightComponent;
class UStaticMeshComponent;
enum class ECRObjective : uint8;

/** A maintenance-powered passage in one streamed level. All progress belongs to GameMode. */
UCLASS()
class CINDERRELAY_API ACRServiceCircuit : public AActor
{
    GENERATED_BODY()

public:
    ACRServiceCircuit();
    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditInstanceOnly, Category="Service") bool bRelayCircuit = false;
    UPROPERTY(EditInstanceOnly, Category="Service", meta=(ClampMin="1", ClampMax="3")) int32 RequiredStep = 1;
    UPROPERTY(VisibleAnywhere, Category="Service") TObjectPtr<UStaticMeshComponent> Housing;
    UPROPERTY(VisibleAnywhere, Category="Service") TObjectPtr<UStaticMeshComponent> UpperLeaf;
    UPROPERTY(VisibleAnywhere, Category="Service") TObjectPtr<UStaticMeshComponent> LowerLeaf;
    UPROPERTY(VisibleAnywhere, Category="Service") TObjectPtr<UBoxComponent> Passage;
    UPROPERTY(VisibleAnywhere, Category="Service") TObjectPtr<UPointLightComponent> Pilot;

private:
    UFUNCTION() void ProgressChanged();
    UFUNCTION() void ObjectiveChanged(ECRObjective Objective);
    bool HasPower() const;
    void ApplyPose(float Alpha);
    float Travel = 0.f;
    bool bPowered = false;
};
