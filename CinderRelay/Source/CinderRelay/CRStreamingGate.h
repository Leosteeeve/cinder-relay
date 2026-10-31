#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRStreamingGate.generated.h"
class UBoxComponent;
class UStaticMeshComponent;
class ACRChapterStreamingController;

/** Persistent industrial shutter; overlap sensors only request the chapter's native sublevels. */
UCLASS()
class CINDERRELAY_API ACRStreamingGate : public AActor
{
    GENERATED_BODY()
public:
    ACRStreamingGate();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Door;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> Preload;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> Retention;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> Threshold;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Streaming", meta=(ClampMin="0", ClampMax="1")) int32 LeftZone = 0;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Streaming") bool bOpen = false;
    bool IsNear() const { return bNear; }
    bool IsInThreshold() const;
    void SetOpen(bool bValue);
    void SetChapterController(ACRChapterStreamingController* Value);
private:
    UFUNCTION() void BeginSensor(UPrimitiveComponent* Component, AActor* Other, UPrimitiveComponent* OtherComp, int32 Body, bool bSweep, const FHitResult& Hit);
    UFUNCTION() void EndSensor(UPrimitiveComponent* Component, AActor* Other, UPrimitiveComponent* OtherComp, int32 Body);
    TWeakObjectPtr<ACRChapterStreamingController> ChapterController;
    bool bNear = false;
};
