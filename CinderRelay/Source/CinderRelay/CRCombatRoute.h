#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRCombatRoute.generated.h"
class ACRCharacter;
class ACRPlayerController;
class ACRChapterStreamingController;
class ACRAshWarden;
class ACRInteractionActor;
enum class ECRInteractionKind:uint8;
UCLASS(NotBlueprintable,Transient)
class CINDERRELAY_API ACRCombatRoute : public AActor
{
    GENERATED_BODY()
public:
    ACRCombatRoute();
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float Delta) override;
private:
#if !UE_BUILD_SHIPPING
    TWeakObjectPtr<ACRCharacter> Player;
    TWeakObjectPtr<ACRPlayerController> PC;
    TWeakObjectPtr<ACRChapterStreamingController> Streaming;
    TWeakObjectPtr<ACRAshWarden> Scout;
    TArray<FVector2D> Waypoints;
    FString Stage=TEXT("startup"),AfterWalk;
    double Started=0,StageStarted=0,LastShot=0,LastMemory=0;
    bool bFinished=false,bMoved=false,bReceivedDamage=false,bReloaded=false;
    float HiddenHealth=0;
    FVector ScoutStart;
    void Next(const FString& Name);
    void Walk(TArray<FVector2D> Points,const FString& NextStage);
    void Inject(const class UInputAction* Action,float Value=1);
    bool Interact(ACRInteractionActor* Item);
    ACRInteractionActor* FindItem(ECRInteractionKind Kind) const;
    TArray<ACRAshWarden*> Enemies() const;
    void Check(bool Condition,const TCHAR* Message);
    void Finish(bool Passed,const FString& Message);
    void Restart();
    void RecordFrame(float Delta);
#endif
};
