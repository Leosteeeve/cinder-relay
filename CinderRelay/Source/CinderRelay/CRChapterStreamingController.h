#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRChapterStreamingController.generated.h"
class ULevelStreaming;
class ACRStreamingGate;

UENUM(BlueprintType)
enum class ECRZoneState : uint8 { Unloaded, Loading, LoadedOrShowing, Ready, Unloading, Failed };

/** Chapter-specific policy over three engine-owned ULevelStreamingDynamic objects. */
UCLASS()
class CINDERRELAY_API ACRChapterStreamingController : public AActor
{
    GENERATED_BODY()
public:
    ACRChapterStreamingController();
    UPROPERTY(EditAnywhere, Category="Streaming") TArray<TSoftObjectPtr<UWorld>> ZoneMaps;
    UPROPERTY(EditAnywhere, Category="Streaming", meta=(ClampMin="5")) float LoadTimeoutSeconds = 30;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Streaming") int32 CurrentZone = 0;
    UFUNCTION(BlueprintPure) bool IsZoneReady(int32 Zone) const;
    UFUNCTION(BlueprintCallable) void RetryFailedLoads();
    UFUNCTION() void Reconcile();
    bool IsZoneUnloaded(int32 Zone) const;
    ULevelStreaming* GetZoneLevel(int32 Zone) const;
    bool AreGatesClosedFor(int32 Zone) const;
#if !UE_BUILD_SHIPPING
    void SetAcceptanceHold(int32 Zone, bool bHold);
    void InjectAcceptanceFailure(int32 Zone);
#endif
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    struct FZone
    {
        TWeakObjectPtr<ULevelStreaming> Level;
        ECRZoneState State = ECRZoneState::Unloaded;
        bool bWanted = false;
        bool bFailed = false;
        uint32 Request = 0;
        double RequestedAt = 0;
        TWeakObjectPtr<AActor> FloorWitness;
    };
    FZone Zones[3];
    TArray<TWeakObjectPtr<ACRStreamingGate>> Gates;
    FTimerHandle Watchdog;
    bool bReconciling = false;
    bool bInitialized = false;
    bool bStopping = false;
    bool bPlayerReleased = false;
    bool bBootstrapConfigured = false;
    bool ValidatePrerequisites(int32 Zone);
    void SetState(int32 Zone, ECRZoneState State);
    void LogZone(int32 Zone, const TCHAR* Event) const;
#if !UE_BUILD_SHIPPING
    int32 AcceptanceHold = INDEX_NONE;
    double HoldExpires = 0;
#endif
};
