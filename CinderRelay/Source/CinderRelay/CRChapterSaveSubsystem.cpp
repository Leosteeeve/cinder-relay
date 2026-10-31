#include "CRChapterSaveSubsystem.h"
#include "CRChapterSaveGame.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
#include "HAL/FileManager.h"
#include "Misc/Paths.h"

void UCRChapterSaveSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
#if !UE_BUILD_SHIPPING
    FString Suffix;
    if (FParse::Value(FCommandLine::Get(), TEXT("CRCheckpointTest="), Suffix))
    {
        if (!SetTestPrefix(Suffix)) SetTestPrefix(TEXT("InvalidArgument")); // Never fall back to player slots for a malformed test flag.
    }
    else if (FParse::Param(FCommandLine::Get(), TEXT("CRRestorationCheck")) || FParse::Param(FCommandLine::Get(), TEXT("CRCombatCheck")) || FParse::Param(FCommandLine::Get(), TEXT("CRWeaponCheck")) || FParse::Param(FCommandLine::Get(), TEXT("CRStreamAcceptance"))) SetTestPrefix(TEXT("Legacy"));
#endif
    ScanSlots();
}
void UCRChapterSaveSubsystem::Deinitialize()
{
    bStopping = true; Queued = nullptr; TravelSnapshot = nullptr;
    OnWritten.Clear(); OnAvailabilityChanged.Clear(); Super::Deinitialize();
}
FString UCRChapterSaveSubsystem::SlotName(int32 Index) const { return SlotPrefix + (Index == 0 ? TEXT("_A") : TEXT("_B")); }
#if !UE_BUILD_SHIPPING
bool UCRChapterSaveSubsystem::SetTestPrefix(const FString& Suffix)
{
    if (IsBusy() || Suffix.IsEmpty() || Suffix.Len() > 40) return false;
    for (TCHAR C : Suffix) if (!FChar::IsAlnum(C) && C != TEXT('_')) return false;
    SlotPrefix = TEXT("CR04_TEST_") + Suffix; return true;
}
#endif
bool UCRChapterSaveSubsystem::ScanSlots()
{
    if (IsBusy() || bStopping) return false;
    bScanning = true; PendingReads = 2; ScanStarted = FPlatformTime::Seconds();
    Candidates.SetNum(2); Candidates[0] = nullptr; Candidates[1] = nullptr;
    Status = TEXT("Checking checkpoints..."); OnAvailabilityChanged.Broadcast();
    for (int32 I = 0; I < 2; ++I)
    {
        bSlotExists[I] = UGameplayStatics::DoesSaveGameExist(SlotName(I), 0);
        UGameplayStatics::AsyncLoadGameFromSlot(SlotName(I), 0, FAsyncLoadGameFromSlotDelegate::CreateUObject(this, &UCRChapterSaveSubsystem::SlotLoaded));
    }
    return true;
}
void UCRChapterSaveSubsystem::SlotLoaded(const FString& Slot, int32, USaveGame* Save)
{
    if (bStopping || !bScanning) return;
    const int32 Index = Slot == SlotName(0) ? 0 : Slot == SlotName(1) ? 1 : INDEX_NONE;
    if (Index == INDEX_NONE) return;
    auto* Candidate = Cast<UCRChapterSaveGame>(Save); FString Reason;
    if (Candidate && Candidate->Validate(Reason)) Candidates[Index] = Candidate;
    else if (bSlotExists[Index]) UE_LOG(LogTemp, Warning, TEXT("CR04_SAVE Rejected slot=%s reason=%s"), *Slot, Candidate ? *Reason : TEXT("Unreadable checkpoint file"));
    if (--PendingReads > 0) return;
    Latest = nullptr; LatestSlot = INDEX_NONE;
    for (int32 I = 0; I < 2; ++I) if (Candidates[I] && (!Latest || Candidates[I]->SaveGeneration > Latest->SaveGeneration)) { Latest = Candidates[I]; LatestSlot = I; }
    if (Candidates[0] && Candidates[1] && Candidates[0]->SaveGeneration == Candidates[1]->SaveGeneration && Candidates[0]->PayloadChecksum != Candidates[1]->PayloadChecksum)
    { Latest = nullptr; LatestSlot = INDEX_NONE; }
    const bool Invalid = (bSlotExists[0] && !Candidates[0]) || (bSlotExists[1] && !Candidates[1]);
    Status = Latest ? (Invalid ? TEXT("A checkpoint file is unavailable; another verified checkpoint can be continued.") : TEXT("Checkpoint available."))
        : (bSlotExists[0] || bSlotExists[1]) ? TEXT("Checkpoint unreadable or incompatible. Files retained. Start a new chapter or restore a backup.") : TEXT("No checkpoint yet. Start a new chapter.");
    LastScanMs = (FPlatformTime::Seconds() - ScanStarted) * 1000; bScanning = false;
    UE_LOG(LogTemp, Display, TEXT("CR04_SAVE ScanComplete valid=%d generation=%lld checkpoint=%s latency_ms=%.3f"), Latest != nullptr, Latest ? Latest->SaveGeneration : 0, Latest ? *Latest->CheckpointId.ToString() : TEXT("none"), LastScanMs);
    OnAvailabilityChanged.Broadcast();
}
uint64 UCRChapterSaveSubsystem::BeginRun() { Queued = nullptr; return ++RunEpoch; }
bool UCRChapterSaveSubsystem::RequestWrite(const UCRChapterSaveGame& Snapshot, uint64 Epoch)
{
    FString Reason;
    if (bStopping || bScanning || Epoch != RunEpoch || (Latest && Latest->SaveGeneration >= MAX_int64 - 1) || !Snapshot.Validate(Reason)) return false;
    auto* Copy = DuplicateObject<UCRChapterSaveGame>(&Snapshot, this);
    if (bWriting)
    {
        Queued = Copy; QueuedEpoch = Epoch;
        UE_LOG(LogTemp, Display, TEXT("CR04_SAVE Coalesced checkpoint=%s epoch=%llu"), *Copy->CheckpointId.ToString(), Epoch);
    }
    else StartWrite(Copy, Epoch);
    return true;
}
void UCRChapterSaveSubsystem::StartWrite(UCRChapterSaveGame* Snapshot, uint64 Epoch)
{
    if (!Snapshot || bStopping) return;
    Writing = Snapshot; WritingEpoch = Epoch; WritingIndex = LatestSlot == 0 ? 1 : 0;
    Writing->SaveGeneration = Latest ? Latest->SaveGeneration + 1 : 1; Writing->Seal();
    bWriting = true; WritingSlot = SlotName(WritingIndex); WriteStarted = FPlatformTime::Seconds();
#if !UE_BUILD_SHIPPING
    if (bFailNextWrite)
    {
        bFailNextWrite = false; WritingSlot = SlotPrefix + TEXT("_BlockedWrite");
        // A directory at the exact file path deterministically rejects native file creation.
        // Colons are not suitable: NTFS can interpret them as alternate data streams.
        IFileManager::Get().MakeDirectory(*(FPaths::ProjectSavedDir() / TEXT("SaveGames") / (WritingSlot + TEXT(".sav"))), true);
    }
#endif
    Status = TEXT("Saving checkpoint..."); OnAvailabilityChanged.Broadcast();
    UE_LOG(LogTemp, Display, TEXT("CR04_SAVE WriteRequested slot=%s generation=%lld checkpoint=%s epoch=%llu"), *WritingSlot, Writing->SaveGeneration, *Writing->CheckpointId.ToString(), Epoch);
    {
        TRACE_CPUPROFILER_EVENT_SCOPE(CR04_SerializeCheckpoint);
        UGameplayStatics::AsyncSaveGameToSlot(Writing, WritingSlot, 0, FAsyncSaveGameToSlotDelegate::CreateUObject(this, &UCRChapterSaveSubsystem::WriteFinished));
    }
    LastSerializeMs = (FPlatformTime::Seconds() - WriteStarted) * 1000;
    UE_LOG(LogTemp, Display, TEXT("CR04_SAVE SerializeDispatch ms=%.3f"), LastSerializeMs);
}
void UCRChapterSaveSubsystem::WriteFinished(const FString& Slot, int32, bool Success)
{
    if (bStopping || !bWriting || !Writing || Slot != WritingSlot) return;
#if !UE_BUILD_SHIPPING
    if (SlotPrefix.StartsWith(TEXT("CR04_TEST_")) && Slot == SlotPrefix + TEXT("_BlockedWrite"))
        IFileManager::Get().DeleteDirectory(*(FPaths::ProjectSavedDir() / TEXT("SaveGames") / (Slot + TEXT(".sav"))), false, false);
#endif
    LastCallbackMs = (FPlatformTime::Seconds() - WriteStarted) * 1000;
    if (Success) { Latest = Writing; LatestSlot = WritingIndex; bSlotExists[LatestSlot] = true; }
    Status = Success ? TEXT("CHECKPOINT SAVED") : TEXT("CHECKPOINT UNAVAILABLE. Previous checkpoint retained.");
    UE_LOG(LogTemp, Display, TEXT("CR04_SAVE WriteCompleted success=%d generation=%lld checkpoint=%s epoch=%llu latency_ms=%.3f"), Success, Writing->SaveGeneration, *Writing->CheckpointId.ToString(), WritingEpoch, LastCallbackMs);
    // Keep the writer occupied during callbacks; a callback can only queue another snapshot.
    OnWritten.Broadcast(Writing, Success, WritingEpoch);
    Writing = nullptr; bWriting = false;
    auto* Next = Queued.Get(); Queued = nullptr;
    if (Next && QueuedEpoch == RunEpoch) StartWrite(Next, QueuedEpoch);
    else OnAvailabilityChanged.Broadcast();
}
void UCRChapterSaveSubsystem::PrepareNewChapter() { Queued = nullptr; TravelSnapshot = nullptr; bHasTravelIntent = true; }
bool UCRChapterSaveSubsystem::PrepareContinue()
{
    FString Reason;
    if (IsBusy() || !Latest || !Latest->Validate(Reason)) return false;
    Queued = nullptr; TravelSnapshot = DuplicateObject<UCRChapterSaveGame>(Latest, this); bHasTravelIntent = true; return true;
}
bool UCRChapterSaveSubsystem::ConsumeTravelIntent(UCRChapterSaveGame*& Snapshot)
{
    Snapshot = nullptr;
    if (!bHasTravelIntent) return false;
    Snapshot = TravelSnapshot; TravelSnapshot = nullptr; bHasTravelIntent = false; return true;
}
