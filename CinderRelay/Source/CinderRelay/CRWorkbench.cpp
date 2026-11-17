#include "CRWorkbench.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "CRHealthComponent.h"
#include "CRWeaponComponent.h"
#include "CRWeaponViewComponent.h"
#include "CRPlayerController.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "LevelSequence.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Sound/SoundBase.h"
#include "Kismet/GameplayStatics.h"
#include "TimerManager.h"
ACRWorkbench::ACRWorkbench()
{
    PrimaryActorTick.bCanEverTick=false;
    Surface=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CalibrationBench")); SetRootComponent(Surface);
    Surface->SetCollisionEnabled(ECollisionEnabled::NoCollision); Surface->SetCanEverAffectNavigation(false);
    // One native box ends at the real tabletop. The decorative rear rail must not seal empty air above it.
    InteractionBounds=CreateDefaultSubobject<UBoxComponent>(TEXT("BenchCollision")); InteractionBounds->SetupAttachment(Surface);
    InteractionBounds->SetBoxExtent(FVector(45,75,49)); InteractionBounds->SetRelativeLocation(FVector(0,0,49));
    InteractionBounds->SetCollisionProfileName(TEXT("BlockAllDynamic")); InteractionBounds->SetCanEverAffectNavigation(false);
    Hands=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("AssemblyHands")); Hands->SetupAttachment(Surface);
    Hands->SetCollisionEnabled(ECollisionEnabled::NoCollision); Hands->SetCanEverAffectNavigation(false);
    Hands->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("AssemblyCamera")); Camera->SetupAttachment(Surface);
    Camera->SetRelativeLocation(FVector(-62,0,166)); Camera->SetRelativeRotation(FRotator(-48,0,0)); Camera->FieldOfView=66;
    IronSequence = TSoftObjectPtr<ULevelSequence>(FSoftObjectPath(TEXT("/Game/Generated/Phase06/Sequences/LS_CR06_IronService.LS_CR06_IronService")));
}
void ACRWorkbench::BeginPlay()
{
    Super::BeginPlay(); Hands->SetVisibility(false);
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>(); if(G && G->HasSurveyUpgrade()) State=ECRAssemblyState::Completed;
    AssetLoad=UAssetManager::GetStreamableManager().RequestAsyncLoad({Sequence.ToSoftObjectPath(),AssemblyMesh.ToSoftObjectPath(),ActivationSound.ToSoftObjectPath(),IronSequence.ToSoftObjectPath()},FStreamableDelegate::CreateUObject(this,&ACRWorkbench::AssetsLoaded));
}
void ACRWorkbench::AssetsLoaded()
{
    bAssetsReady=Sequence.IsValid() && AssemblyMesh.IsValid() && Sequence->FindBindingsByTag(TEXT("CR03_Hands")).Num()==1 && AssemblyMesh->GetRefSkeleton().FindBoneIndex(TEXT("hand_R"))!=INDEX_NONE;
    if(bAssetsReady) Hands->SetSkeletalMeshAsset(AssemblyMesh.Get());
    UE_LOG(LogTemp,Display,TEXT("CR03_ASSEMBLY AssetsReady=%d level=%s"),bAssetsReady,*GetLevel()->GetOutermost()->GetName());
}
bool ACRWorkbench::CanInteract_Implementation(ACRCharacter* P) const
{
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
    return G && G->HasSurveyOptic() && !G->IsSurveyOpticActive() && CanStartService(P);
}

bool ACRWorkbench::CanStartService(ACRCharacter* P) const
{
    return bAssetsReady && (State == ECRAssemblyState::Idle || State == ECRAssemblyState::Completed) &&
        P && P->CanInteractWith(this) && P->Weapon->CanUse() && P->Weapon->State == ECRWeaponState::Ready &&
        P->GetCharacterMovement()->IsMovingOnGround();
}
FText ACRWorkbench::GetInteractionPrompt_Implementation(ACRCharacter*) const
{
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
    const TCHAR* T = !bAssetsReady ? TEXT("Workbench loading") : G && G->IsSurveyOpticActive()
        ? TEXT("SURVEY OPTIC FITTED  /  [1] Service and select iron sights") : G && G->HasSurveyOptic()
        ? TEXT("[E] Fit Survey Optic  /  [1] Service iron sights") : TEXT("[1] Service iron sights  /  Recover a Survey Optic for another build");
    return FText::FromString(T);
}
void ACRWorkbench::Interact_Implementation(ACRCharacter* P)
{
    if(!CanInteract_Implementation(P)) return;
    StartService(P, Sequence.Get(), false);
}

void ACRWorkbench::ServiceIronSights(ACRCharacter* P)
{
    if (CanStartService(P) && IronSequence.IsValid()) StartService(P, IronSequence.Get(), true);
}

void ACRWorkbench::StartService(ACRCharacter* P, ULevelSequence* Selected, bool Iron)
{
    auto* PC=Cast<ACRPlayerController>(P->GetController()); if(!PC || PC->IsAssembling()) return;
    State=ECRAssemblyState::Preparing; Player=P; Controller=PC; bIronService=Iron;
    FActorSpawnParameters Spawn; Spawn.OverrideLevel=GetLevel();
    SequenceActor=GetWorld()->SpawnActor<ALevelSequenceActor>(Spawn);
    if(!SequenceActor) { Abort(); return; }
    // Installed 5.8.4 headers declare InitializePlayerWithSequence, but its DLL exports no implementation.
    // SetSequence is exported and initializes the native player against this actor's owning level.
    SequenceActor->SetSequence(Selected);
    auto* Playback=SequenceActor->GetSequencePlayer();
    if(!Playback) { Abort(); return; }
    SequenceActor->SetBindingByTag(TEXT("CR03_Hands"),{this});
    Playback->OnFinished.AddDynamic(this,&ACRWorkbench::Finished); Playback->OnStop.AddDynamic(this,&ACRWorkbench::Stopped);
    P->ClearHeldActions(); PC->FlushPressedKeys(); PreviousMovementMode=P->GetCharacterMovement()->MovementMode;
    P->GetCharacterMovement()->StopMovementImmediately(); P->GetCharacterMovement()->DisableMovement();
    P->Weapon->SetPresentationLocked(true); P->WeaponView->SetPresentationHidden(true);
    PC->SetIgnoreMoveInput(true); PC->SetIgnoreLookInput(true); bInputOwned=true; PC->SetAssembly(this);
    Hands->SetVisibility(true); PC->SetViewTargetWithBlend(this,.8f,VTBlend_Cubic);
    State=ECRAssemblyState::Playing; bReflectionPlayed=false; bActivationPlayed=false;
    PC->ShowSubtitle(FText::GetEmpty(),.1f);
    Playback->Play(); GetWorldTimerManager().SetTimer(CueTimer,this,&ACRWorkbench::PresentationCues,.05f,true);
    UE_LOG(LogTemp,Display,TEXT("CR03_ASSEMBLY Playing duration=%.3f"),Playback->GetDuration().AsSeconds());
}
float ACRWorkbench::GetPresentationSeconds() const
{ return SequenceActor && SequenceActor->GetSequencePlayer()?SequenceActor->GetSequencePlayer()->GetCurrentTime().AsSeconds():0.f; }
void ACRWorkbench::PresentationCues()
{
    if(State!=ECRAssemblyState::Playing) return;
    if(!Player.IsValid() || Player->Health->IsDead() || !Controller.IsValid() || !IsValid(SequenceActor) || !SequenceActor->GetSequencePlayer()) { Abort(); return; }
    if(!SequenceActor->GetSequencePlayer()->IsPlaying() && !SequenceActor->GetSequencePlayer()->IsPaused()) { Stopped(); return; }
    if (bIronService) return;
    const float Seconds=GetPresentationSeconds();
    if(Seconds>=4 && !bReflectionPlayed)
    {
        bReflectionPlayed=true;
        if(GetWorld()->GetAuthGameMode<ACRGameMode>()->ClaimStoryBeat(TEXT("CR03_AssemblyReflection")))
            Controller->ShowSubtitle(FText::FromString(TEXT("ELIAS: Funny. Machines remember what people forget.")),5.f);
    }
    if(Seconds>=15 && !bActivationPlayed)
    {
        bActivationPlayed=true; UGameplayStatics::PlaySoundAtLocation(this,ActivationSound.Get(),GetActorLocation(),.5f);
        Controller->ShowSubtitle(FText::FromString(TEXT("SURVEY OPTIC  /  CALIBRATION VERIFIED")),3.f);
    }
}
void ACRWorkbench::Finished()
{
    if(State!=ECRAssemblyState::Playing || !Player.IsValid() || Player->Health->IsDead()) { Abort(); return; }
    State=ECRAssemblyState::Finalizing;
    // Leave MovieScene's callback stack before stopping/destroying its player. This is lifecycle
    // deferral, not a timed completion test: only OnFinished or explicit Skip can enter Finalizing.
    GetWorldTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]()
    {
        if(State!=ECRAssemblyState::Finalizing) return;
        if(!Player.IsValid() || Player->Health->IsDead()) { Abort(); return; }
        auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
        bool Applied = bIronService;
        if (G && bIronService) G->SelectSurveyOptic(false);
        if (G && !bIronService) Applied = G->TryApplySurveyUpgrade() || G->SelectSurveyOptic(true);
        Restore(Applied); State=G && G->HasSurveyUpgrade()?ECRAssemblyState::Completed:ECRAssemblyState::Idle;
        UE_LOG(LogTemp,Display,TEXT("CR03_ASSEMBLY Finalized applied=%d"),Applied);
    }));
}
void ACRWorkbench::Skip() { if(State==ECRAssemblyState::Playing && !GetWorld()->IsPaused()) { UE_LOG(LogTemp,Display,TEXT("CR03_ASSEMBLY Skip")); Finished(); } }
void ACRWorkbench::Stopped()
{
    // UE5.8 FinishPlaybackInternal calls StopInternal (OnStop) BEFORE broadcasting OnFinished.
    GetWorldTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]()
    { if(State==ECRAssemblyState::Playing) Abort(); }));
}
void ACRWorkbench::Abort()
{
    if(State==ECRAssemblyState::Idle || State==ECRAssemblyState::Completed || State==ECRAssemblyState::Aborting) return;
    State=ECRAssemblyState::Aborting; Restore(false);
    const auto* G = GetWorld()->GetAuthGameMode<ACRGameMode>();
    State = G && G->HasSurveyUpgrade() ? ECRAssemblyState::Completed : ECRAssemblyState::Idle;
    UE_LOG(LogTemp,Warning,TEXT("CR03_ASSEMBLY Aborted without upgrade"));
}
void ACRWorkbench::Restore(bool Successful)
{
    GetWorldTimerManager().ClearTimer(CueTimer);
    if(IsValid(SequenceActor))
    {
        if(auto* Playback=SequenceActor->GetSequencePlayer()) { Playback->OnFinished.RemoveAll(this); Playback->OnStop.RemoveAll(this); Playback->Stop(); }
        SequenceActor->Destroy(); SequenceActor=nullptr;
    }
    SequenceActor=nullptr;
    Hands->SetVisibility(false);
    if(Player.IsValid())
    {
        Player->Weapon->SetPresentationLocked(false); Player->WeaponView->SetPresentationHidden(false); Player->ClearHeldActions();
        if(bInputOwned && !Player->Health->IsDead()) Player->GetCharacterMovement()->SetMovementMode(static_cast<EMovementMode>(PreviousMovementMode));
    }
    if(Controller.IsValid())
    {
        if(Player.IsValid()) Controller->SetViewTargetWithBlend(Player.Get(),Successful?.65f:0.f,VTBlend_Cubic);
        if(bInputOwned) { Controller->SetIgnoreMoveInput(false); Controller->SetIgnoreLookInput(false); }
        Controller->FlushPressedKeys(); Controller->SetAssembly(nullptr);
        const TCHAR* Result = !Successful ? TEXT("Workbench service interrupted. Your build is unchanged.") : bIronService
            ? TEXT("IRON SIGHTS READY / RMB to aim. Return to the bench to fit the Survey Optic.")
            : TEXT("SURVEY OPTIC FITTED / RMB to use the tighter sight picture.");
        Controller->ShowSubtitle(FText::FromString(Result),4.f);
    }
    bInputOwned=false; bIronService=false; Player.Reset(); Controller.Reset();
}
void ACRWorkbench::EndPlay(const EEndPlayReason::Type Reason)
{ Abort(); if(AssetLoad) { AssetLoad->CancelHandle(); AssetLoad.Reset(); } Super::EndPlay(Reason); }
