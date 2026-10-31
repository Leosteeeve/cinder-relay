#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInteractable.h"
#include "CRWorkbench.generated.h"
class UStaticMeshComponent;
class USkeletalMeshComponent;
class UCameraComponent;
class ULevelSequence;
class ALevelSequenceActor;
class USkeletalMesh;
class USoundBase;
class ACRPlayerController;
struct FStreamableHandle;
UENUM(BlueprintType) enum class ECRAssemblyState:uint8 { Idle, Preparing, Playing, Finalizing, Completed, Aborting };
/** One optional chapter presentation; native Sequencer completion owns the transaction. */
UCLASS()
class CINDERRELAY_API ACRWorkbench:public AActor,public ICRInteractable
{
    GENERATED_BODY()
public:
    ACRWorkbench();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Surface;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMeshComponent> Hands;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UCameraComponent> Camera;
    UPROPERTY(EditAnywhere, Category="Assembly") TSoftObjectPtr<ULevelSequence> Sequence;
    UPROPERTY(EditAnywhere, Category="Assembly") TSoftObjectPtr<USkeletalMesh> AssemblyMesh;
    UPROPERTY(EditAnywhere, Category="Assembly") TSoftObjectPtr<USoundBase> ActivationSound;
    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly) ECRAssemblyState State=ECRAssemblyState::Idle;
    virtual bool CanInteract_Implementation(ACRCharacter* Player) const override;
    virtual FText GetInteractionPrompt_Implementation(ACRCharacter* Player) const override;
    virtual void Interact_Implementation(ACRCharacter* Player) override;
    void Skip();
    void Abort();
    bool IsReady() const { return bAssetsReady; }
    float GetPresentationSeconds() const;
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    TWeakObjectPtr<ACRCharacter> Player;
    TWeakObjectPtr<ACRPlayerController> Controller;
    UPROPERTY(Transient) TObjectPtr<ALevelSequenceActor> SequenceActor;
    TSharedPtr<FStreamableHandle> AssetLoad;
    FTimerHandle CueTimer;
    uint8 PreviousMovementMode=0;
    bool bAssetsReady=false, bInputOwned=false, bActivationPlayed=false, bReflectionPlayed=false;
    void AssetsLoaded();
    void PresentationCues();
    void Restore(bool Successful);
    UFUNCTION() void Finished();
    UFUNCTION() void Stopped();
};
