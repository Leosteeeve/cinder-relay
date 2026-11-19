#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInteractable.h"
#include "CRStreamingGate.generated.h"
class UBoxComponent;
class UStaticMeshComponent;
class ACRChapterStreamingController;

/** Persistent E-operated shutter; sensors retain native neighbors until the boundary seals. */
UCLASS()
class CINDERRELAY_API ACRStreamingGate : public AActor, public ICRInteractable
{
    GENERATED_BODY()
public:
    ACRStreamingGate();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Door;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UBoxComponent> SafetyBarrier;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> ControlOutside;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> ControlInside;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> Preload;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> Retention;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> Threshold;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Streaming", meta=(ClampMin="0", ClampMax="1")) int32 LeftZone = 0;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Streaming") bool bOpen = false;
    bool IsNear() const { return bNear; }
    bool WantsAdjacentZones() const;
    bool IsSealed() const { return Aperture <= 0 && !bOpen; }
    bool IsInThreshold() const;
    virtual bool CanInteract_Implementation(ACRCharacter* Player) const override;
    virtual FText GetInteractionPrompt_Implementation(ACRCharacter* Player) const override;
    virtual void Interact_Implementation(ACRCharacter* Player) override;
    void SetOpen(bool bValue);
    void SetChapterController(ACRChapterStreamingController* Value);
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
private:
    UFUNCTION() void BeginSensor(UPrimitiveComponent* Component, AActor* Other, UPrimitiveComponent* OtherComp, int32 Body, bool bSweep, const FHitResult& Hit);
    UFUNCTION() void EndSensor(UPrimitiveComponent* Component, AActor* Other, UPrimitiveComponent* OtherComp, int32 Body);
    TWeakObjectPtr<ACRChapterStreamingController> ChapterController;
    bool bNear = false;
    bool bRequested = false;
    bool bReady = false;
    float Aperture = 0;
    FVector ClosedLocation = FVector(0,0,175);
    FVector ClosedScale = FVector(1);
    void ApplyDoor();
};
