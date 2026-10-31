#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRWorkshopTrigger.generated.h"
class UBoxComponent;

UCLASS()
class CINDERRELAY_API ACRWorkshopTrigger : public AActor
{
	GENERATED_BODY()
public:
	ACRWorkshopTrigger();
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UBoxComponent> Volume;
private:
	UFUNCTION() void OnEntry(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);
};
