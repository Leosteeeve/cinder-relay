#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "CRGameMode.h"
#include "CRPlayerController.generated.h"
class UCRHUDWidget;
class ACRCharacter;
class ACRWorkbench;
class ACRZonePresentation;

UCLASS()
class CINDERRELAY_API ACRPlayerController : public APlayerController
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable) void TogglePrototypePause();
	UFUNCTION(BlueprintCallable) void ResumePrototype();
	UFUNCTION(BlueprintCallable) void RestartPrototype();
	UFUNCTION(BlueprintCallable) void ExitPrototype();
	UFUNCTION(BlueprintCallable) void ContinueCheckpoint();
	void ShowCheckpointFeedback(const FString& Text);
	UFUNCTION(BlueprintCallable) void RefreshHUD();
	void SetStreamingStatus(const FText& Text);
	void RetryStreaming();
	void PlayerDefeated();
	void ShowSubtitle(const FText& Text, float Seconds=5.f);
	void SetAssembly(ACRWorkbench* Workbench);
	bool IsAssembling() const { return ActiveWorkbench.IsValid(); }
	void SkipAssembly();
	void AbortAssembly();
	void FinishChapterPresentation();
	UFUNCTION() void RefreshCombat();
	UFUNCTION() void HealthChanged(float Health, float Damage);
	UFUNCTION() void ShotFeedback(FVector Impact, bool bHitTarget, bool bBlockingHit);
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="UI") bool bPrototypeDefeated = false;
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="UI") bool bPrototypePaused = false;
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="UI") bool bPrototypeEnded = false;
protected:
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	virtual void BeginPlay() override;
	virtual void SetupInputComponent() override;
	virtual void OnPossess(APawn* InPawn) override;
	virtual ASpectatorPawn* SpawnSpectatorPawn() override;
private:
	void BindPawn();
	void ApplyPause(bool bPause);
	void SaveAvailabilityChanged();
	void TravelToChapter();
	bool bStartupMenu = false, bPendingContinue = false, bOpeningShown=false;
	UFUNCTION() void ObjectiveChanged(ECRObjective Objective);
	UFUNCTION() void PromptChanged(FText Prompt);
	UPROPERTY(Transient) TObjectPtr<UCRHUDWidget> HUD;
	TWeakObjectPtr<ACRCharacter> ObservedPawn;
	TWeakObjectPtr<ACRWorkbench> ActiveWorkbench;
	TWeakObjectPtr<ACRZonePresentation> ActiveEnding;
	FTimerHandle SubtitleTimer;
	FTimerHandle CheckpointMessageTimer;
};
