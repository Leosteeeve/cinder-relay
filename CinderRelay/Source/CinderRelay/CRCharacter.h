#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "CRCharacter.generated.h"

class UCameraComponent;
class UInputAction;
class UInputMappingContext;
class UEnhancedInputLocalPlayerSubsystem;
struct FInputActionValue;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FCRPromptChanged, FText, Prompt);

UCLASS()
class CINDERRELAY_API ACRCharacter : public ACharacter
{
	GENERATED_BODY()
public:
	ACRCharacter();
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera") TObjectPtr<UCameraComponent> Camera;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Movement", meta=(ClampMin="50", ClampMax="600")) float WalkSpeed = 300.f;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Movement", meta=(ClampMin="50", ClampMax="800")) float SprintSpeed = 500.f;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Movement", meta=(ClampMin="50", ClampMax="300")) float CrouchSpeed = 160.f;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Camera", meta=(ClampMin="0.01", ClampMax="3")) float MouseSensitivity = 0.12f;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Interaction", meta=(ClampMin="50", ClampMax="400")) float InteractionRange = 250.f;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputMappingContext> MappingContext;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> ForwardAction;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> BackAction;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> RightAction;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> LeftAction;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> YawAction;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> PitchAction;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> SprintAction;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> CrouchAction;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> JumpAction;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input") TObjectPtr<UInputAction> InteractAction;
	UPROPERTY(BlueprintAssignable) FCRPromptChanged OnPromptChanged;
	UFUNCTION(BlueprintPure) bool CanInteractWith(const AActor* Target) const;
	UFUNCTION(BlueprintPure) FText GetCurrentPrompt() const { return CurrentPrompt; }
	UFUNCTION(BlueprintCallable) void ClearHeldActions();
	UFUNCTION(BlueprintCallable) void TryInteract();
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void PawnClientRestart() override;
	virtual void OnStartCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;
	virtual void OnEndCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;
protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
	void InstallInputContext();
	TWeakObjectPtr<UEnhancedInputLocalPlayerSubsystem> InputSubsystem;
	AActor* TraceTarget() const;
	void UpdatePrompt();
	void MoveForward();
	void MoveBack();
	void MoveRight();
	void MoveLeft();
	void LookYaw(const FInputActionValue& Value);
	void LookPitch(const FInputActionValue& Value);
	void StartSprint();
	void StopSprint();
	void StartCrouch();
	void StopCrouch();
	FTimerHandle PromptTimer;
	FText CurrentPrompt;
};
