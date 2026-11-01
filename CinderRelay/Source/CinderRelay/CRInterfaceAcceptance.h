#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRInterfaceAcceptance.generated.h"
class ACRCharacter;
class ACRPlayerController;
class UInputAction;
struct FKey;

/** Opt-in Development evidence route. Never runs against player saves/preferences. */
UCLASS(NotBlueprintable, Transient)
class CINDERRELAY_API ACRInterfaceAcceptance : public AActor
{
    GENERATED_BODY()
public:
    ACRInterfaceAcceptance();
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
private:
    UFUNCTION() void WeaponCue(FName Cue);
#if !UE_BUILD_SHIPPING
    TWeakObjectPtr<ACRCharacter> Player;
    TWeakObjectPtr<ACRPlayerController> PC;
    FString CapturePath, AfterCapture;
    bool bFinished=false, bHandedOff=false, bRecording=false, bPassed=false;
    int32 ReloadCompletions=0, BeforeMagazine=0, BeforeReserve=0;
    float OriginalHealth=100;
    FRotator OriginalRotation;
    FVector WalkStart=FVector::ZeroVector;
    void Next(const FString& Stage);
    bool Check(bool Condition, const FString& Message);
    void Key(const FKey& Key);
    void GameplayKey(const FKey& Key);
    void Inject(const UInputAction* Action);
    void Capture(const FString& Name, const FString& FollowingStage);
    void Finish(bool Passed, const FString& Message);
    void WriteReceipt();
#endif
};
