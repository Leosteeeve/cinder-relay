#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "CRChapterSaveSubsystem.generated.h"
class UCRChapterSaveGame;
class USaveGame;

DECLARE_MULTICAST_DELEGATE(FCRSaveAvailabilityChanged);
DECLARE_MULTICAST_DELEGATE_ThreeParams(FCRCheckpointWritten, const UCRChapterSaveGame*, bool, uint64);

/** One Chapter01 writer, two native slots, one coalesced immutable pending snapshot. */
UCLASS()
class CINDERRELAY_API UCRChapterSaveSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    bool ScanSlots();
    bool RequestWrite(const UCRChapterSaveGame& Snapshot, uint64 Epoch);
    uint64 BeginRun();
    uint64 GetRunEpoch() const { return RunEpoch; }
    bool IsBusy() const { return bScanning || bWriting; }
    bool IsWriting() const { return bWriting; }
    bool HasCheckpoint() const { return Latest != nullptr; }
    bool AreSlotsMissing() const { return !bScanning && !bSlotExists[0] && !bSlotExists[1]; }
    const UCRChapterSaveGame* GetLatest() const { return Latest; }
    const FString& GetStatus() const { return Status; }
    FString SlotName(int32 Index) const;
    void PrepareNewChapter();
    bool PrepareContinue();
    bool ConsumeTravelIntent(UCRChapterSaveGame*& Snapshot);
    FCRSaveAvailabilityChanged OnAvailabilityChanged;
    FCRCheckpointWritten OnWritten;
    double LastSerializeMs = 0, LastCallbackMs = 0, LastScanMs = 0;
#if !UE_BUILD_SHIPPING
    bool SetTestPrefix(const FString& Suffix);
    void FailNextWriteForTest() { if (SlotPrefix.StartsWith(TEXT("CR04_TEST_"))) bFailNextWrite = true; }
#endif
private:
    void SlotLoaded(const FString& Slot, int32 User, USaveGame* Save);
    void StartWrite(UCRChapterSaveGame* Snapshot, uint64 Epoch);
    void WriteFinished(const FString& Slot, int32 User, bool Success);
    UPROPERTY(Transient) TObjectPtr<UCRChapterSaveGame> Latest;
    UPROPERTY(Transient) TArray<TObjectPtr<UCRChapterSaveGame>> Candidates;
    UPROPERTY(Transient) TObjectPtr<UCRChapterSaveGame> Writing;
    UPROPERTY(Transient) TObjectPtr<UCRChapterSaveGame> Queued;
    UPROPERTY(Transient) TObjectPtr<UCRChapterSaveGame> TravelSnapshot;
    FString SlotPrefix = TEXT("CinderRelay_CH01"), Status = TEXT("Checking checkpoints..."), WritingSlot;
    bool bSlotExists[2] = {false, false};
    bool bScanning = false, bWriting = false, bStopping = false, bHasTravelIntent = false;
    int32 PendingReads = 0, LatestSlot = INDEX_NONE, WritingIndex = INDEX_NONE;
    uint64 RunEpoch = 0, WritingEpoch = 0, QueuedEpoch = 0;
    double ScanStarted = 0, WriteStarted = 0;
#if !UE_BUILD_SHIPPING
    bool bFailNextWrite = false;
#endif
};
