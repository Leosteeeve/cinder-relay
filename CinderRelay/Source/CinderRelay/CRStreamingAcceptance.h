#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRStreamingAcceptance.generated.h"
class ACRCharacter;
class ACRPlayerController;
class ACRChapterStreamingController;
class ACRInteractionActor;
enum class ECRInteractionKind : uint8;

/** Opt-in Development acceptance route, never placed in a map or spawned in Shipping. */
UCLASS(NotBlueprintable, Transient)
class CINDERRELAY_API ACRStreamingAcceptance : public AActor
{
    GENERATED_BODY()
public:
    ACRStreamingAcceptance();
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
private:
#if !UE_BUILD_SHIPPING
    void Advance(const FString& Next);
    void Walk(TArray<FVector2D> Points, const FString& Next);
    void Inject(const class UInputAction* Action, float Value = 1);
    void Check(bool bCondition, const TCHAR* Message);
    void Finish(bool bPassed, const FString& Message);
    ACRInteractionActor* FindItem(ECRInteractionKind Kind) const;
    bool AimAndInteract(ECRInteractionKind Kind);
    TWeakObjectPtr<ACRCharacter> Player;
    TWeakObjectPtr<ACRPlayerController> PC;
    TWeakObjectPtr<ACRChapterStreamingController> Streaming;
    TArray<FVector2D> Route;
    FString Stage = TEXT("startup"), AfterWalk, Events, Frames, Memory;
    double Started = 0, StageStarted = 0, LastMemory = 0;
    bool bFinished = false;
    int32 Cycle = 0;
#endif
};
