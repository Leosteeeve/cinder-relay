#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CREchoBridgeCatch.generated.h"

class UBoxComponent;
class UStaticMeshComponent;

/** Optional Chapter 02 bridge. A fresh visit starts closed. The parallel survey walk stays open. */
UCLASS()
class CINDERRELAY_API ACREchoBridgeCatch : public AActor
{
    GENERATED_BODY()
public:
    ACREchoBridgeCatch();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual float TakeDamage(float Damage, const FDamageEvent& Event, AController* InstigatorController, AActor* Causer) override;
    virtual void Tick(float DeltaSeconds) override;
    bool IsOpen() const { return Travel >= 1.f; }

    UPROPERTY(VisibleAnywhere, Category="Bridge") TObjectPtr<UStaticMeshComponent> Boom;
    UPROPERTY(VisibleAnywhere, Category="Bridge") TObjectPtr<UStaticMeshComponent> Witness;
    UPROPERTY(VisibleAnywhere, Category="Bridge") TObjectPtr<UBoxComponent> CatchTarget;
    UPROPERTY(VisibleAnywhere, Category="Bridge") TObjectPtr<UBoxComponent> ArmBarrier;
private:
    bool bReleased = false;
    float Travel = 0.f;
    void RestoreBridge();
    void ApplyPose();
};
