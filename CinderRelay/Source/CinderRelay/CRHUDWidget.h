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
	void SetMenu(bool bVisible, bool bEnded);
protected:
	virtual void NativeOnInitialized() override;
	virtual FReply NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& KeyEvent) override;
private:
	UFUNCTION() void ResumeClicked();
	UFUNCTION() void RestartClicked();
	UFUNCTION() void ExitClicked();
	UPROPERTY(Transient) TObjectPtr<UTextBlock> ObjectiveText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> PromptText;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> MenuTitle;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> MenuBody;
	UPROPERTY(Transient) TObjectPtr<UBorder> MenuBackdrop;
	UPROPERTY(Transient) TObjectPtr<UButton> ResumeButton;
};
