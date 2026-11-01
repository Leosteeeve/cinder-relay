#include "CRZonePresentation.h"
#include "CRCharacter.h"
#include "CRPlayerController.h"
#include "CRWeaponComponent.h"
#include "CRHealthComponent.h"
#include "Components/PointLightComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "LevelSequence.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "TimerManager.h"
ACRZonePresentation::ACRZonePresentation()
{
    PrimaryActorTick.bCanEverTick=false;
    StatusLight=CreateDefaultSubobject<UPointLightComponent>(TEXT("StatusLight")); SetRootComponent(StatusLight);
    StatusLight->SetMobility(EComponentMobility::Movable); StatusLight->SetIntensityUnits(ELightUnits::Lumens);
    StatusLight->SetIntensity(0); StatusLight->SetLightColor(FLinearColor(.15f,.65f,.7f));
    StatusLight->SetAttenuationRadius(700); StatusLight->SetCastShadows(false);
}
void ACRZonePresentation::BeginPlay()
{
    Super::BeginPlay();
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>()) G->OnObjectiveChanged.AddDynamic(this,&ACRZonePresentation::ObjectiveChanged);
    AssetLoad=UAssetManager::GetStreamableManager().RequestAsyncLoad({PowerSequence.ToSoftObjectPath(),EndingSequence.ToSoftObjectPath()},FStreamableDelegate::CreateUObject(this,&ACRZonePresentation::AssetsReady));
}
void ACRZonePresentation::AssetsReady()
{
    // Restore the steady appearance without replaying a saved narrative event.
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>(); G && G->GetObjective()>=ECRObjective::InvestigateSignal) StatusLight->SetIntensity(500);
    UE_LOG(LogTemp,Display,TEXT("CR05_PRESENTATION AssetsReady power=%d ending=%d"),PowerSequence.IsValid(),EndingSequence.IsValid());
}
bool ACRZonePresentation::Play(ULevelSequence* Sequence)
{
    Cleanup();
    if(!Sequence || Sequence->FindBindingsByTag(TEXT("CR05_Presentation")).Num()!=1) return false;
    FActorSpawnParameters Params; Params.OverrideLevel=GetLevel(); PlaybackActor=GetWorld()->SpawnActor<ALevelSequenceActor>(Params);
    if(!PlaybackActor) return false;
    PlaybackActor->SetSequence(Sequence); auto* Playback=PlaybackActor->GetSequencePlayer();
    if(!Playback) { Cleanup(); return false; }
    PlaybackActor->SetBindingByTag(TEXT("CR05_Presentation"),{this});
    Playback->OnFinished.AddDynamic(this,&ACRZonePresentation::Finished); Playback->OnStop.AddDynamic(this,&ACRZonePresentation::Stopped);
    Playback->Play(); UE_LOG(LogTemp,Display,TEXT("CR05_PRESENTATION Play sequence=%s duration=%.3f"),*Sequence->GetName(),Playback->GetDuration().AsSeconds()); return true;
}
void ACRZonePresentation::ObjectiveChanged(ECRObjective Objective)
{
    if(Objective==ECRObjective::InvestigateSignal && !bEnding && !Play(PowerSequence.Get())) StatusLight->SetIntensity(500);
}
bool ACRZonePresentation::BeginEnding(ACRPlayerController* PC)
{
    if(bEnding || !PC || !EndingSequence.IsValid()) return false;
    auto* P=Cast<ACRCharacter>(PC->GetPawn()); if(!P || P->Health->IsDead()) return false;
    if(!Play(EndingSequence.Get())) return false;
    bEnding=true; Controller=PC; Player=P; bOwnsInput=true;
    P->ClearHeldActions(); P->GetCharacterMovement()->StopMovementImmediately(); P->Weapon->SetPresentationLocked(true);
    PC->SetIgnoreMoveInput(true); PC->FlushPressedKeys();
    PC->ShowSubtitle(FText::FromString(TEXT("RELAY NINE / LOCAL POWER STABLE\n[The returned signal breaks into an irregular carrier tone.]  Tab Skip")),8.f);
    return true;
}
void ACRZonePresentation::Finished()
{
    if(bFinalizing) return; bFinalizing=true;
    const uint32 Generation=PlaybackGeneration;
    GetWorldTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Generation]()
    {
        if(Generation!=PlaybackGeneration || !bFinalizing) return;
        const bool End=bEnding; auto PC=Controller; Cleanup(); StatusLight->SetIntensity(500);
        UE_LOG(LogTemp,Display,TEXT("CR05_PRESENTATION Finished ending=%d"),End);
        if(End && PC.IsValid() && !PC->bPrototypeDefeated) PC->FinishChapterPresentation();
    }));
}
void ACRZonePresentation::Stopped()
{
    // Native OnStop precedes OnFinished at the natural end. Never destroy MovieScene reentrantly.
    const uint32 Generation=PlaybackGeneration;
    GetWorldTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Generation]() { if(Generation==PlaybackGeneration && !bFinalizing && PlaybackActor) Finished(); }));
}
void ACRZonePresentation::SkipEnding() { if(bEnding && !GetWorld()->IsPaused()) Finished(); }
void ACRZonePresentation::Cleanup()
{
    ++PlaybackGeneration;
    if(IsValid(PlaybackActor))
    {
        if(auto* P=PlaybackActor->GetSequencePlayer()) { P->OnFinished.RemoveAll(this); P->OnStop.RemoveAll(this); P->Stop(); }
        PlaybackActor->Destroy();
    }
    PlaybackActor=nullptr;
    if(bOwnsInput)
    {
        if(Player.IsValid()) { Player->Weapon->SetPresentationLocked(false); Player->ClearHeldActions(); }
        if(Controller.IsValid()) { Controller->SetIgnoreMoveInput(false); Controller->FlushPressedKeys(); }
    }
    bOwnsInput=false; bEnding=false; bFinalizing=false; Player.Reset(); Controller.Reset();
}
void ACRZonePresentation::AbortPresentation() { Cleanup(); }
void ACRZonePresentation::EndPlay(const EEndPlayReason::Type Reason)
{
    const bool End=bEnding; auto PC=Controller; Cleanup();
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>()) G->OnObjectiveChanged.RemoveAll(this);
    if(AssetLoad) { AssetLoad->CancelHandle(); AssetLoad.Reset(); }
    if(End && Reason==EEndPlayReason::RemovedFromWorld && PC.IsValid() && !PC->bPrototypeDefeated) PC->FinishChapterPresentation();
    Super::EndPlay(Reason);
}
