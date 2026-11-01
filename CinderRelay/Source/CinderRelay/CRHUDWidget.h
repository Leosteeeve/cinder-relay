#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "CRHUDWidget.generated.h"
class UTextBlock;
class UBorder;
class UButton;

/** Small native UMG widget tree; no polling bindings or custom Slate framework. */
UCLASS()
class CINDERRELAY_API UCRHUDWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	void SetObjective(const FText& Text);
	void SetPrompt(const FText& Text);
	void SetStreamingStatus(const FText& Text);
	void SetMenu(bool bVisible, bool bEnded, bool bDefeated=false);
	void SetRecoveryMenu(bool Startup, bool Defeated, bool CanResume, bool CanContinue, const FString& Status);
	void SetCheckpointStatus(const FText& Text);
	void SetCombat(float Health, int32 Magazine, int32 Reserve, bool Reloading);
	void ShotFeedback(bool Hit);
	void HitFeedback(bool Killed);
	void DamageFeedback();
	void SetSubtitle(const FText& Text);
	void SetAssembly(bool Active);
protected:
	virtual void NativeOnInitialized() override;
	virtual void NativeTick(const FGeometry& Geometry, float Delta) override;
	virtual FReply NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& KeyEvent) override;
private:
	UPROPERTY(Transient) TObjectPtr<UTextBlock> SubtitleText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> ControlsText;
	UFUNCTION() void ResumeClicked();
	UFUNCTION() void RestartClicked();
	UFUNCTION() void ExitClicked();
	UFUNCTION() void ContinueClicked();
	UPROPERTY(Transient) TObjectPtr<UButton> ContinueButton;
	UPROPERTY(Transient) TObjectPtr<UButton> RestartButton;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> SaveStatusText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> CheckpointText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> ObjectiveText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> PromptText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> StreamingText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> CombatText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> ReticleText;
	UPROPERTY(Transient) TObjectPtr<UBorder> DamageBorder;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> HitText;
	bool bKillFeedback=false;
	float ShotPulse=0, HitPulse=0, HurtPulse=0;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> MenuTitle;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> MenuBody;
	UPROPERTY(Transient) TObjectPtr<UBorder> MenuBackdrop;
	UPROPERTY(Transient) TObjectPtr<UButton> ResumeButton;
};
