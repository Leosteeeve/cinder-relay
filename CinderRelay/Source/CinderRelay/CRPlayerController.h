#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "CRGameMode.h"
#include "CRPlayerController.generated.h"
class UCRHUDWidget;
class ACRCharacter;

UCLASS()
class CINDERRELAY_API ACRPlayerController : public APlayerController
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable) void TogglePrototypePause();
	UFUNCTION(BlueprintCallable) void ResumePrototype();
	UFUNCTION(BlueprintCallable) void RestartPrototype();
	UFUNCTION(BlueprintCallable) void ExitPrototype();
	UFUNCTION(BlueprintCallable) void RefreshHUD();
	void SetStreamingStatus(const FText& Text);
	void RetryStreaming();
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="UI") bool bPrototypePaused = false;
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="UI") bool bPrototypeEnded = false;
protected:
	virtual void BeginPlay() override;
	virtual void SetupInputComponent() override;
	virtual void OnPossess(APawn* InPawn) override;
private:
	void BindPawn();
	void ApplyPause(bool bPause);
	UFUNCTION() void ObjectiveChanged(ECRObjective Objective);
	UFUNCTION() void PromptChanged(FText Prompt);
	UPROPERTY(Transient) TObjectPtr<UCRHUDWidget> HUD;
	TWeakObjectPtr<ACRCharacter> ObservedPawn;
};
