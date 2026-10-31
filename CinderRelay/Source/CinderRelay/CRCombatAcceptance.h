#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRCombatAcceptance.generated.h"
class ACRCharacter;
class ACRPlayerController;
class UCRHealthComponent;
UCLASS(NotBlueprintable,Transient)
class CINDERRELAY_API ACRCombatAcceptance : public AActor
{
    GENERATED_BODY()
public:
    ACRCombatAcceptance();
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float Delta) override;
private:
#if !UE_BUILD_SHIPPING
    TWeakObjectPtr<ACRCharacter> Player;
    TWeakObjectPtr<ACRPlayerController> PC;
    TWeakObjectPtr<AActor> Target, Wall;
    TWeakObjectPtr<UCRHealthComponent> TargetHealth;
    FString Stage=TEXT("startup"), Events;
    double Started=0, StageStarted=0;
    bool bFinished=false;
    int32 TestShots=0;
    void Next(const FString& Name);
    void Check(bool Condition,const TCHAR* Message);
    void Finish(bool Passed,const FString& Message);
    AActor* TestBlock(FVector Position,FVector Size,bool Damageable);
#endif
};
