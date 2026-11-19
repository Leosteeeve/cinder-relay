#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "GameFramework/Actor.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Subsystems/WorldSubsystem.h"
#include "CREchoChapter.generated.h"

class ACRCharacter;

UCLASS()
class CINDERRELAY_API UCREchoSave : public USaveGame
{
	GENERATED_BODY()
public:
	UPROPERTY(SaveGame) int32 Version = 1;
	UPROPERTY(SaveGame) FName Chapter = TEXT("CH02_EchoCrossing");
	UPROPERTY(SaveGame) FName Checkpoint;
	UPROPERTY(SaveGame) int64 Generation = 0;
	UPROPERTY(SaveGame) int32 Step = 0;
	UPROPERTY(SaveGame) int32 Bearing = 0;
	UPROPERTY(SaveGame) bool bLog = false;
	UPROPERTY(SaveGame) bool bBridge = false;
	UPROPERTY(SaveGame) bool bOptic = false;
	UPROPERTY(SaveGame) float Health = 100;
	UPROPERTY(SaveGame) int32 Mag = 5;
	UPROPERTY(SaveGame) int32 Reserve = 25;
	UPROPERTY(SaveGame) uint32 Checksum = 0;
	void Seal();
	bool Valid() const;
private:
	uint32 Digest() const;
};

/** Spawned exclusively by the opt-in Development acceptance route. */
UCLASS(NotBlueprintable,Transient)
class ACREchoAcceptance : public AActor
{
	GENERATED_BODY()
public:
	ACREchoAcceptance();
	FString Route;
	void Tick(float Delta) override;
private:
#if !UE_BUILD_SHIPPING
	int32 Stage=0;
	double Started=0, LastPulse=-1, StageTime=0;
	int32 BeforeShot=0;
	bool bFinished=false;
	TArray<FVector2D> Points;
	FString Events;
	void Next(const TCHAR* Event);
	void Finish(bool Pass,const TCHAR* Reason);
#endif
};

DECLARE_MULTICAST_DELEGATE_TwoParams(FCREchoWritten, const UCREchoSave*, bool);

/** One ordered writer survives map travel. Slots never overlap with Chapter 01. */
UCLASS()
class CINDERRELAY_API UCREchoStore : public UGameInstanceSubsystem
{
	GENERATED_BODY()
public:
	void Initialize(FSubsystemCollectionBase& Collection) override;
	void Deinitialize() override;
	FSimpleMulticastDelegate OnAvailabilityChanged;
	FCREchoWritten OnWritten;
	bool IsReady() const { return bEnabled && PendingReads == 0 && !Writing && !Queued; }
	bool IsSaving() const { return Writing != nullptr || Queued != nullptr; }
	bool HasCheckpoint() const { return Latest != nullptr; }
	bool HasUnfinishedCheckpoint() const { return Latest && Latest->Step < 4; }
	bool IsEnabled() const { return bEnabled; }
	const UCREchoSave* GetLatest() const { return Latest; }
	bool Save(UCREchoSave* Snapshot);
private:
	FString Slot(int32 Index) const;
	void ReadFinished(const FString& SlotName, int32 User, USaveGame* Value);
	void Write(UCREchoSave* Value);
	void Written(const FString& SlotName, int32 User, bool Success);
	FString Prefix = TEXT("CinderRelay_CH02_Echo");
	int64 LastGeneration = 0;
	int32 PendingReads = 0, LatestIndex = INDEX_NONE, WritingIndex = INDEX_NONE;
	bool bEnabled = true;
	UPROPERTY(Transient) TArray<TObjectPtr<UCREchoSave>> Reads;
	UPROPERTY(Transient) TObjectPtr<UCREchoSave> Latest;
	UPROPERTY(Transient) TObjectPtr<UCREchoSave> Writing;
	UPROPERTY(Transient) TObjectPtr<UCREchoSave> Queued;
};

UCLASS()
class CINDERRELAY_API UCREchoChapter : public UWorldSubsystem
{
	GENERATED_BODY()
public:
	static bool IsEchoWorld(const UWorld* World);
	static bool HasCheckpoint(const UObject* Context);
	static bool HasUnfinishedCheckpoint(const UObject* Context);
	void OnWorldBeginPlay(UWorld& World) override;
	void Deinitialize() override;
	FSimpleMulticastDelegate OnChanged;
	int32 GetStep() const { return Step; }
	int32 GetBearing() const { return Bearing; }
	bool HasFieldLog() const { return bLog; }
	bool IsBridgeReleased() const { return bBridge; }
	bool IsComplete() const { return Step == 4; }
	bool IsReadyForTravel() const { return bStarted && !IsSaving(); }
	bool IsStarted() const { return bStarted; }
	bool IsSaving() const;
	bool NeedsRetry() const { return bSaveFailed; }
	int32 GetRejectedBearings() const { return Rejections; }
	FText GetObjectiveText() const;
	FText GetGuideText() const;
	FText GetNotice() const { return Notice; }
	bool CanOperate(int32 Index) const;
	void Operate(int32 Index, bool bConfirm);
	void RecordBridgeRelease();
	void RetrySave();
private:
	void TryStart();
	void SaveProgress();
	void SaveFinished(const UCREchoSave* Snapshot, bool bSuccess);
	bool PlaceAtCheckpoint(ACRCharacter& Player) const;
	bool bStarted = false, bPersistent = false, bContinue = false, bLog = false, bBridge = false, bSaveFailed = false;
	int32 Step = 0, Bearing = 0, Rejections = 0;
	FText Notice;
	FTimerHandle StartTimer;
};
