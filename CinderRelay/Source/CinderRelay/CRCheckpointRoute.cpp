#include "CRCheckpointRoute.h"
#if !UE_BUILD_SHIPPING
#include "CRCharacter.h"
#include "CRCharacterMovementComponent.h"
#include "CRPlayerController.h"
#include "CRGameMode.h"
#include "CRChapterSaveGame.h"
#include "CRChapterSaveSubsystem.h"
#include "CRCheckpoint.h"
#include "CRChapterStreamingController.h"
#include "CRHealthComponent.h"
#include "CRWeaponComponent.h"
#include "CRWeaponViewComponent.h"
#include "CRAshWarden.h"
#include "CRAmmoPickup.h"
#include "CRSalvagePickup.h"
#include "CRWorkbench.h"
#include "CRInteractionActor.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"
#include "Engine/GameInstance.h"
#include "Engine/LocalPlayer.h"
#include "Engine/LevelStreaming.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMemory.h"
#include "HAL/IConsoleManager.h"
#include "RenderTimer.h"
#include "DynamicRHI.h"
#include "UnrealClient.h"
namespace { int32 Journey = 0; int32 RecoveryCycles = 0, LifeStep = 0; double RunStart = 0, MemoryAt = 0; FString Events, Frames, Memory; int64 PreservedGeneration = 0; }
namespace { bool bSlideCheck=false, bSlideVideo=false; int32 SlideMagazine=0,SlideTotalAmmo=0; double SlideBegin=0; }
namespace { bool bHandlingVideo = false, bHandlingVideoDone = false; int32 HandlingVideoShots = 0; }
#endif
ACRCheckpointRoute::ACRCheckpointRoute()
{
#if !UE_BUILD_SHIPPING
    PrimaryActorTick.bCanEverTick = true; PrimaryActorTick.bTickEvenWhenPaused = true;
#endif
}
void ACRCheckpointRoute::BeginPlay()
{
    Super::BeginPlay();
#if !UE_BUILD_SHIPPING
    FParse::Value(FCommandLine::Get(), TEXT("CRCheckpointRoute="), Route);
    bSlideEdges=FParse::Param(FCommandLine::Get(),TEXT("CRSlideEdges"));
    bSlideCheck=FParse::Param(FCommandLine::Get(),TEXT("CRSlideCheck"));
    bSlideVideo=FParse::Param(FCommandLine::Get(),TEXT("CR054Video"));
    bLifecycle = FParse::Param(FCommandLine::Get(), TEXT("CRCheckpointLifecycle"));
    bHandlingVideo = FParse::Param(FCommandLine::Get(), TEXT("CRHandlingVideo"));
    Started = StageStarted = FPlatformTime::Seconds();
    if (!RunStart) { RunStart = Started; Frames = TEXT("elapsed,stage,frame_ms,game_ms,render_ms,gpu_ms,x,y,z\n"); Memory = TEXT("elapsed,stage,working_set,private_commit\n"); }
    for (TActorIterator<ACRChapterStreamingController> It(GetWorld()); It; ++It) { Streaming = *It; break; }
    auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
    if (!Store || !Store->SlotName(0).StartsWith(TEXT("CR04_TEST_"))) { Finish(false, TEXT("Refusing acceptance on player save slots")); return; }
    if (!GetWorld()->GetAuthGameMode<ACRGameMode>()->IsStartupMenu())
    {
        Next(TEXT("startup"));
        if (Streaming.IsValid() && (Route == 2 || Route == 3) && Journey == 0)
        { Streaming->SetAcceptanceHold(Route == 2 ? 1 : 2, true); bHeld = true; }
    }
#endif
}
void ACRCheckpointRoute::Tick(float Delta)
{
    Super::Tick(Delta);
#if !UE_BUILD_SHIPPING
    if (bFinished) return;
    const double Now = FPlatformTime::Seconds(), Age = Now - StageStarted;
    if (Now - RunStart > 480 || Age > 75) { Finish(false, TEXT("Bounded checkpoint route timeout: ") + Stage); return; }
    PC = Cast<ACRPlayerController>(UGameplayStatics::GetPlayerController(this,0));
    if (Stage==TEXT("bench_controller_destroyed"))
    {
        Check(Player.IsValid()&&!Player->Weapon->IsPresentationLocked()&&!GetWorld()->GetAuthGameMode<ACRGameMode>()->HasSurveyUpgrade(),TEXT("Controller destruction aborts assembly without locking surviving player"));
        auto* RestoreStore=GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
        if(!bFinished && RestoreStore->PrepareContinue()) { bFinished=true; UGameplayStatics::OpenLevel(this,FName(*UGameplayStatics::GetCurrentLevelName(this,true))); } return;
    }
    if (!PC.IsValid()) return;
    auto* G = GetWorld()->GetAuthGameMode<ACRGameMode>(); auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
    if (Stage == TEXT("menu"))
    {
        // Capture-only handshake: no scene progression before the recorder owns
        // an observed foreground window. Normal acceptance/play never waits here.
        if(bSlideVideo && !IFileManager::Get().FileExists(*(FPaths::ProjectSavedDir()/TEXT("Phase054/Record.ready")))) return;
        if(bHandlingVideo && !IFileManager::Get().FileExists(*(FPaths::ProjectSavedDir()/TEXT("Phase053/Record.ready")))) return;
        if (Store->IsBusy()) return;
        Check(!PC->GetPawn(), TEXT("Cold launch menu holds player before selecting New Game or Continue"));
        if (Route == 1) { Check(!Store->HasCheckpoint(), TEXT("Dedicated route begins with missing slots")); Travel(false,0); }
        else { Check(Store->HasCheckpoint(), TEXT("Fresh process discovers a valid native disk checkpoint")); Travel(true,0); }
        return;
    }
    if (Stage == TEXT("startup"))
    {
        if (bHeld)
        {
            auto* L = Streaming->GetZoneLevel(Route == 2 ? 1 : 2);
            if (L && L->IsLevelLoaded() && L->IsLevelVisible())
            {
                Check(!UGameplayStatics::GetPlayerPawn(this,0), TEXT("Loaded and visible alone cannot release pawn while readiness is vetoed"));
                Streaming->SetAcceptanceHold(Route == 2 ? 1 : 2,false); bHeld = false;
            }
            return;
        }
        Player = Cast<ACRCharacter>(PC->GetPawn()); if (!Player.IsValid() || !G->IsCheckpointReady()) return;
        Check(!Player->IsSliding() && Streaming->IsZoneReady(G->GetStartingZone()) && Player->GetActorLocation().Z > -750, TEXT("Safe pawn released only into ready target checkpoint collision"));
        if (Route == 1) { Check(G->GetObjective()==ECRObjective::ReachWorkshop && Player->Weapon->Magazine==5, TEXT("New Game retains original starting state")); Next(TEXT("wait_cp00")); }
        else if (Route == 2 && Journey == 40)
        { Check(!G->HasSurveyOptic()&&!G->HasSurveyUpgrade()&&!PC->IsAssembling()&&Player->Weapon->CanUse(),TEXT("Restart during assembly and world EndPlay restore fresh playable state")); Travel(true,0); }
        else if (Route == 2) { Check(G->GetObjective()==ECRObjective::FindModule && G->DefeatedEnemies.Num()==2 && G->IsPickupCollected(TEXT("CR02_YardAmmo")), TEXT("CP01 restores objective, enemy deaths and consumed ammo")); Next(TEXT("restore_values")); }
        else if (Journey == 0 || Journey == 2 || Journey == 3)
        { Check(G->GetObjective()==ECRObjective::RestorePower && G->HasSurveyUpgrade(), TEXT("CP02 restores objective and completed Survey Optic")); Next(TEXT("restore_values")); }
        else if (Journey == 1)
        {
            Check(!G->HasSurveyOptic() && !G->HasSurveyUpgrade() && G->DefeatedEnemies.IsEmpty() && G->CollectedPickups.IsEmpty(), TEXT("Restart Chapter resets session state"));
            Check(Store->GetLatest() && Store->GetLatest()->SaveGeneration==PreservedGeneration, TEXT("Restart did not erase or overwrite stored checkpoint"));
            Walk({{-500,0}},TEXT("die"));
        }
        else if (Journey == 4) Walk({{-300,0}},TEXT("fight"));
        return;
    }
    if (!Player.IsValid() || !Streaming.IsValid()) { Finish(false,TEXT("Lost persistent player or streaming controller")); return; }
    Record(Delta);
    auto* W = Player->Weapon.Get();
    if (Player->Health->IsDead() && Stage != TEXT("die") && Stage!=TEXT("bench_dead")) { Finish(false,TEXT("Unexpected death in ")+Stage); return; }
    if (Stage == TEXT("walk"))
    {
        if (Waypoints.IsEmpty()) { Next(AfterWalk); return; }
        const FVector2D D = Waypoints[0] - FVector2D(Player->GetActorLocation().X,Player->GetActorLocation().Y);
        if (D.Size()<45) { Waypoints.RemoveAt(0); return; }
        PC->SetControlRotation(FRotator(0,FMath::RadiansToDegrees(FMath::Atan2(D.Y,D.X)),0)); Inject(Player->ForwardAction); Inject(Player->SprintAction); return;
    }
    if (Stage == TEXT("wait_cp00"))
    {
        if(!Store->IsBusy()&&Store->GetLatest()&&Store->GetLatest()->CheckpointId==TEXT("CP00_START_YARD"))
        { Check(Store->GetLatest()->SaveGeneration==1,TEXT("Fresh New Game confirms native CP00 write before entering combat")); if(bSlideCheck) Next(TEXT("slide_low_speed")); else Walk({{-300,0}},TEXT("fight")); }
    }
    else if(Stage==TEXT("slide_low_speed"))
    {
        if(Age<.15) Inject(Player->CrouchAction);
        else { Check(!Player->IsSliding(),TEXT("Slide rejects low speed and missing sprint")); Next(TEXT("slide_accelerate")); }
    }
    else if(Stage==TEXT("slide_accelerate"))
    {
        PC->SetControlRotation(FRotator::ZeroRotator); Inject(Player->ForwardAction); Inject(Player->SprintAction);
        if(Age>.4 && Player->GetVelocity().Size2D()>435 && Player->WeaponView->IsPresentationResident())
        { SlideMagazine=W->Magazine; SlideTotalAmmo=W->Magazine+W->Reserve;Inject(Player->CrouchAction); Next(TEXT("slide_active")); SlideBegin=Now; }
    }
    else if(Stage==TEXT("slide_active"))
    {
        Inject(Player->ForwardAction); Inject(Player->SprintAction);
        if(Age<.35) Inject(Player->CrouchAction);
        if(Age>.08 && Age<.3) { Check(Player->IsSliding() && Player->bIsCrouched,TEXT("Sprint Ctrl enters grounded crouched slide")); Check(Player->GetVelocity().Size2D()<=621,TEXT("Slide speed stays bounded")); }
        if(Age>.14 && Age<.25) Inject(Player->AimAction);
        if(Age>.27 && Age<.31) { Check(!W->bAiming,TEXT("ADS cannot activate during slide")); if(W->Magazine==SlideMagazine) Inject(Player->FireAction); }
        if(Age>.82)
        { Check(!Player->IsSliding()&&!Player->bIsCrouched,TEXT("Timed slide ends standing after Ctrl release")); Check(W->Magazine==SlideMagazine-1,TEXT("Slide hip fire spends exactly one round")); Inject(Player->CrouchAction);Next(TEXT("slide_cooldown")); }
    }
    else if(Stage==TEXT("slide_cooldown"))
    {
        Check(!Player->IsSliding(),TEXT("Cooldown prevents immediate retrigger"));
        if(Age>.15 && W->State==ECRWeaponState::Ready) { Inject(Player->ReloadAction); Next(TEXT("slide_reload")); }
    }
    else if(Stage==TEXT("slide_reload"))
    {
        if(Age>.1 && Age<.3) { Check(W->State==ECRWeaponState::Reloading,TEXT("Reload begins after slide with native weapon lock")); Inject(Player->SprintAction);Inject(Player->CrouchAction);Check(!Player->IsSliding(),TEXT("Reload cannot enter slide")); }
        if(Age>2.6) { Check(W->State==ECRWeaponState::Ready && W->Magazine==5 && W->Magazine+W->Reserve==SlideTotalAmmo-1,TEXT("Native reload transfers ammo once after slide")); Inject(Player->AimAction);Next(TEXT("slide_return")); }
    }
    else if(Stage==TEXT("slide_return"))
    {
        if(Age<.3) Inject(Player->AimAction);
        if(Age>.15) { Check(W->bAiming && !Player->IsSliding(),TEXT("ADS returns after movement and reload")); Walk({{-300,0}},TEXT("fight")); }
    }
    else if(Stage==TEXT("slide_edge_prepare"))
    {
        PC->SetControlRotation(FRotator::ZeroRotator);Inject(Player->ForwardAction);Inject(Player->SprintAction);
        if(Age>.35 && Player->GetVelocity().Size2D()>435)
        {
            SlideEdgeOrigin=Player->GetActorLocation();SlideTotalAmmo=W->Magazine+W->Reserve;
            if(SlideEdgeCase==3) { Inject(Player->JumpAction);Next(TEXT("slide_edge_air"));return; }
            if(SlideEdgeCase==1) SlideObstacle=SlideBlock(SlideEdgeOrigin+FVector(300,0,50),FVector(400,220,20));
            if(SlideEdgeCase==2) SlideObstacle=SlideBlock(SlideEdgeOrigin+FVector(175,0,0),FVector(20,220,250));
            Inject(Player->CrouchAction);Next(TEXT("slide_edge_active"));
        }
    }
    else if(Stage==TEXT("slide_edge_air"))
    {
        if(Age>.08 && Age<.2) Inject(Player->CrouchAction);
        if(Age>.2 && Age<.25) Check(Player->GetCharacterMovement()->IsFalling()&&!Player->IsSliding(),TEXT("Airborne Sprint Ctrl cannot enter slide"));
        if(Age>1.5 && Player->GetCharacterMovement()->IsMovingOnGround()) FinishSlideEdge();
    }
    else if(Stage==TEXT("slide_edge_active"))
    {
        Inject(Player->ForwardAction);
        if(Age<.15 || SlideEdgeCase==0) Inject(Player->CrouchAction);
        if(SlideEdgeCase==4 && Age>.12 && Age<.2) Inject(Player->ReloadAction);
        if(SlideEdgeCase==5 && Age>.12) { Check(Player->IsSliding(),TEXT("Pause fixture interrupts an active slide"));PC->TogglePrototypePause();Next(TEXT("slide_edge_pause"));return; }
        if(SlideEdgeCase==4)
        {
            if(Age>.22 && Age<.3) Check(!Player->IsSliding()&&W->State==ECRWeaponState::Reloading,TEXT("Valid reload cancels an active slide"));
            if(Age>2.8) { Check(W->State==ECRWeaponState::Ready&&W->Magazine+W->Reserve==SlideTotalAmmo,TEXT("Mid-slide reload conserves ammunition exactly once"));FinishSlideEdge(); }
        }
        else if(Age>.95)
        {
            Check(!Player->IsSliding(),TEXT("Bounded edge-case slide terminates"));
            if(SlideEdgeCase==0) Check(Player->bIsCrouched,TEXT("Holding Ctrl ends slide crouched without retrigger"));
            if(SlideEdgeCase==1) Check(Player->bIsCrouched,TEXT("Released Ctrl cannot expand capsule through a low ceiling"));
            if(SlideEdgeCase==2) Check(Player->GetActorLocation().X<SlideEdgeOrigin.X+135,TEXT("Native wall sweep shortens slide without penetration"));
            if(SlideObstacle.IsValid())SlideObstacle->Destroy();Next(TEXT("slide_edge_clear"));
        }
    }
    else if(Stage==TEXT("slide_edge_clear") && Age>.4)
    { Check(!Player->bIsCrouched,TEXT("Native stand resumes after Ctrl release and ceiling clearance"));FinishSlideEdge(); }
    else if(Stage==TEXT("slide_edge_pause") && Age>.4)
    { Check(GetWorld()->IsPaused()&&!Player->IsSliding(),TEXT("Pause clears slide and held actions safely"));PC->TogglePrototypePause();FinishSlideEdge(); }
    else if(Stage==TEXT("slide_workshop_review"))
    {
        PC->SetControlRotation(FRotator(-8,-65+float(Age)*16,0));
        if(Age>8) Finish(true,TEXT("Input-driven sprint slide fire reload combat and Workshop tour complete"));
    }
    else if (Stage == TEXT("fight"))
    {
        ACRAshWarden* Enemy = nullptr;
        for (TActorIterator<ACRAshWarden> It(GetWorld()); It; ++It) if (!It->Health->IsDead()) { Enemy=*It; break; }
        if (!Enemy)
        {
            Check(G->DefeatedEnemies.Num()==2,TEXT("Normal accepted shots defeated both original enemies"));
            if(bSlideEdges && SlideEdgeCase<6) { Walk({{-1250,0}},TEXT("slide_edge_prepare"));return; }
            if(Route==3&&Journey==4)Walk({{1000,0},{1850,0},{2800,-170}},TEXT("module"));else Walk({{1000,0},{1250,300}},TEXT("ammo")); return;
        }
        PC->SetControlRotation((Enemy->Head->GetComponentLocation()-Player->Camera->GetComponentLocation()).Rotation()); Inject(Player->AimAction);
        if (W->State==ECRWeaponState::Ready && Now-LastShot>1.05)
        { Inject(W->Magazine==0?Player->ReloadAction:Player->FireAction); LastShot=Now; }
    }
    else if (Stage == TEXT("ammo"))
    {
        if (G->IsPickupCollected(TEXT("CR02_YardAmmo"))) { Walk({{1500,0},{2050,0}},TEXT("wait_cp01")); return; }
        for (TActorIterator<ACRAmmoPickup> It(GetWorld()); It; ++It) { Interact(*It,It->GetActorLocation()); break; }
    }
    else if (Stage == TEXT("wait_cp01"))
    {
        if (!Store->IsBusy() && Store->GetLatest() && Store->GetLatest()->CheckpointId==TEXT("CP01_WORKSHOP_ENTRY"))
        { Check(Store->GetLatest()->MagazineAmmo==W->Magazine && Store->GetLatest()->PlayerHealth==Player->Health->Health,TEXT("CP01 native success captures actual stable health/ammo")); if(bSlideVideo) Next(TEXT("slide_workshop_review")); else Finish(true,TEXT("CP01 saved; exit process before next route")); }
    }
    else if (Stage == TEXT("restore_values"))
    {
        const auto* S = Store->GetLatest();
        Check(S && W->Magazine==S->MagazineAmmo && W->Reserve==S->ReserveAmmo && Player->Health->Health==S->PlayerHealth && W->State==ECRWeaponState::Ready,TEXT("Restored actual health and ammo match disk; weapon Ready without reload timer"));
        if (Route==2 && bHandlingVideo && !bHandlingVideoDone) { Next(TEXT("video_resident")); }
        else if (Route==2) Walk({{2800,-170}},TEXT("module"));
        else if (Journey==3 && ++RecoveryCycles<3) Travel(true,3);
        else if (Journey==2 || Journey==3) Walk({{5450,0},{6000,-320}},TEXT("relay"));
        else Walk({{3500,0},{2300,0}},TEXT("workshop_reconcile"));
    }
    else if(Stage==TEXT("video_resident") && Player->WeaponView->IsPresentationResident())
    { Inject(Player->ReloadAction);Next(TEXT("video_prepare")); }
    else if(Stage==TEXT("video_prepare") && Age>2.6 && W->State==ECRWeaponState::Ready)
    { Check(W->Magazine==5,TEXT("Recording begins with a completed native five-round reload"));Inject(Player->FireAction);HandlingVideoShots=1;Next(TEXT("video_cycle")); }
    else if(Stage==TEXT("video_cycle") && Age>1.05 && W->State==ECRWeaponState::Ready)
    {
        Check(W->Magazine==5-HandlingVideoShots,TEXT("Recorded input consumed exactly one accepted shot"));
        if(HandlingVideoShots<3) { Inject(Player->FireAction);++HandlingVideoShots;Next(TEXT("video_cycle")); }
        else { Inject(Player->ReloadAction);Next(TEXT("video_reload")); }
    }
    else if(Stage==TEXT("video_reload") && Age>2.6 && W->State==ECRWeaponState::Ready)
    { bHandlingVideoDone=true;Walk({{2800,-170}},TEXT("module")); }
    else if (Stage == TEXT("module"))
    {
        if (G->GetObjective()==ECRObjective::RestorePower)
        { if (Route==2) Walk({{2400,-170},{2130,-350}},TEXT("salvage")); else Walk({{3300,0},{4050,0},{5450,0},{6000,-320}},TEXT("relay")); return; }
        for (TActorIterator<ACRInteractionActor> It(GetWorld()); It; ++It) if (It->Kind==ECRInteractionKind::PowerModule) { Interact(*It,It->GetActorLocation()); break; }
    }
    else if (Stage==TEXT("salvage"))
    {
        if (G->HasSurveyOptic()) { Check(!G->TryCollectSurveyOptic(TEXT("CR03_YardCache")),TEXT("Alternative salvage cannot duplicate saved logical component")); Next(TEXT("bench_start")); return; }
        for (TActorIterator<ACRSalvagePickup> It(GetWorld()); It; ++It) if (It->SourceId==TEXT("CR03_WorkshopBackup")) { Interact(*It,It->Mesh->Bounds.Origin); break; }
    }
    else if (Stage.StartsWith(TEXT("bench_")))
    {
        if(Stage==TEXT("bench_dead") || Stage==TEXT("bench_destroyed"))
        {
            Check(!G->HasSurveyUpgrade()&&!PC->IsAssembling()&&!W->IsPresentationLocked()&&!PC->IsMoveInputIgnored()&&!PC->IsLookInputIgnored(),TEXT("Death or presentation actor EndPlay aborts without upgrade and releases ownership"));
            Travel(true,0);return;
        }
        ACRWorkbench* Bench=nullptr; for(TActorIterator<ACRWorkbench> It(GetWorld());It;++It){Bench=*It;break;}
        if (!Bench) { Finish(false,TEXT("Actual Workshop bench missing")); return; }
        if (Stage==TEXT("bench_start") || Stage==TEXT("bench_again"))
        {
            if (Bench->State==ECRAssemblyState::Playing) Next(bLifecycle&&LifeStep<5?TEXT("bench_fault"):Stage==TEXT("bench_start")?TEXT("bench_abort"):TEXT("bench_full"));
            else if(Bench->IsReady()) Interact(Bench,Bench->GetActorLocation()+FVector(0,0,96));
        }
        else if(Stage==TEXT("bench_fault") && Bench->GetPresentationSeconds()>1)
        {
            const int32 Fault=LifeStep++;
            UE_LOG(LogTemp,Display,TEXT("CR04_LIFECYCLE fault=%d"),Fault);
            if(Fault==0) { PC->SkipAssembly();Next(TEXT("bench_skipped")); }
            else if(Fault==1) { UGameplayStatics::ApplyDamage(Player.Get(),1000,nullptr,this,nullptr);Next(TEXT("bench_dead")); }
            else if(Fault==2) { Bench->Destroy();Next(TEXT("bench_destroyed")); }
            else if(Fault==3) Travel(false,40);
            else { PC->Destroy();Next(TEXT("bench_controller_destroyed")); }
        }
        else if(Stage==TEXT("bench_skipped") && Bench->State==ECRAssemblyState::Completed)
        { Check(G->HasSurveyUpgrade()&&W->GetAimFOV()==60&&W->CanUse()&&!PC->IsMoveInputIgnored()&&!PC->IsLookInputIgnored(),TEXT("Explicit Skip commits once and releases input"));Check(!G->TryApplySurveyUpgrade(),TEXT("Skip cannot duplicate upgrade"));Travel(true,0); }
        else if(Stage==TEXT("bench_abort") && Bench->GetPresentationSeconds()>1)
        {
            for(TActorIterator<ACRCheckpoint> It(GetWorld());It;++It) Check(!G->RequestCheckpoint(**It,*Player.Get()),TEXT("Checkpoint request rejected during actual assembly"));
            for(TActorIterator<ALevelSequenceActor> It(GetWorld());It;++It) if(It->GetSequencePlayer() && It->GetSequencePlayer()->IsPlaying()) { It->GetSequencePlayer()->Stop(); break; }
            Next(TEXT("bench_aborted"));
        }
        else if(Stage==TEXT("bench_aborted") && Bench->State==ECRAssemblyState::Idle)
        { Check(!G->HasSurveyUpgrade()&&!PC->IsAssembling()&&!PC->IsMoveInputIgnored()&&!PC->IsLookInputIgnored()&&W->CanUse(),TEXT("Actual Stop aborts without upgrade and restores controls")); Next(TEXT("bench_again")); }
        else if(Stage==TEXT("bench_full"))
        {
            if(PC->bPrototypePaused)
            { if(Now-PausedAt>1) { Check(FMath::Abs(Bench->GetPresentationSeconds()-PausedPosition)<.1,TEXT("Pause freezes actual assembly playback")); PC->ResumePrototype(); } return; }
            if(!bPauseChecked && Bench->GetPresentationSeconds()>6)
            { bPauseChecked=true; PausedPosition=Bench->GetPresentationSeconds(); PausedAt=Now; PC->TogglePrototypePause(); return; }
            if(Bench->State==ECRAssemblyState::Completed)
            { Check(G->HasSurveyUpgrade()&&W->GetAimFOV()==60&&!PC->IsAssembling()&&W->CanUse(),TEXT("Natural completion restores input and applied optic")); Inject(Player->FireAction); Next(TEXT("gun_cycle")); }
        }
    }
    else if(Stage==TEXT("gun_cycle") && Age>1 && W->State==ECRWeaponState::Ready) { Inject(Player->ReloadAction); Next(TEXT("gun_reload")); }
    else if(Stage==TEXT("gun_reload") && Age>1 && W->State==ECRWeaponState::Ready)
    { Check(W->Magazine==5&&Player->WeaponView->HasImportedAppearance(),TEXT("Existing imported upgraded weapon and reload still work")); Walk({{2400,-170},{3300,0},{4050,0}},TEXT("wait_cp02")); }
    else if(Stage==TEXT("wait_cp02"))
    {
        if(!Store->IsBusy()&&Store->GetLatest()&&Store->GetLatest()->CheckpointId==TEXT("CP02_RELAY_ACCESS"))
        { Check(Store->GetLatest()->SurveyUpgradeApplied,TEXT("CP02 confirms completed upgrade in native saved payload")); Finish(true,TEXT("CP02 saved; exit process before next route")); }
    }
    else if(Stage==TEXT("workshop_reconcile") && Streaming->IsZoneReady(1))
    {
        for(TActorIterator<ACRWorkbench> It(GetWorld());It;++It)Check(It->State==ECRAssemblyState::Completed,TEXT("Restored Workshop bench reconciles completed state"));
        for(TActorIterator<ACRSalvagePickup> It(GetWorld());It;++It)Check(It->IsHidden(),TEXT("Restored alternate salvage remains consumed"));
        Check(!G->ClaimStoryBeat(TEXT("CR03_AssemblyReflection"))&&!G->ClaimStoryBeat(TEXT("CR03_WorkshopDiscovery")),TEXT("Saved one-time story claims do not replay"));
        Walk({{1300,0},{-1100,0}},TEXT("yard_reconcile"));
    }
    else if(Stage==TEXT("yard_reconcile") && Streaming->IsZoneReady(0) && Streaming->IsZoneUnloaded(1) && Streaming->IsZoneUnloaded(2))
    {
        int32 Count=0;for(TActorIterator<ACRAshWarden> It(GetWorld());It;++It)++Count;
        Check(Count==0&&G->DefeatedEnemies.Num()==2,TEXT("Returning yard preserves saved enemy deaths across native unload/reload"));
        for(TActorIterator<ACRAmmoPickup> It(GetWorld());It;++It)Check(It->IsHidden(),TEXT("Saved ammo remains consumed in reloaded yard"));
        PreservedGeneration=Store->GetLatest()->SaveGeneration; Travel(false,1);
    }
    else if(Stage==TEXT("die") && Player->Health->IsDead())
    { Check(PC->bPrototypeDefeated&&W->State==ECRWeaponState::Disabled,TEXT("Actual enemy damage reaches death recovery menu")); Travel(true,3); }
    else if(Stage==TEXT("relay"))
    {
        if(G->GetObjective()==ECRObjective::InvestigateSignal) { Walk({{6500,-250},{6700,0}},TEXT("signal")); return; }
        for(TActorIterator<ACRInteractionActor> It(GetWorld());It;++It)if(It->Kind==ECRInteractionKind::Relay){Interact(*It,It->GetActorLocation());break;}
    }
    else if(Stage==TEXT("signal"))
    {
        if(G->GetObjective()==ECRObjective::Complete) { Next(TEXT("ending")); return; }
        for(TActorIterator<ACRInteractionActor> It(GetWorld());It;++It)if(It->Kind==ECRInteractionKind::Signal){Interact(*It,It->GetActorLocation());break;}
    }
    else if(Stage==TEXT("ending"))
    {
        if(!PC->bPrototypeEnded) return; // Real native ending playback, bounded by the route stage timeout.
        Check(PC->bPrototypeEnded,TEXT("Original MERIDIAN chapter ending still completes"));
        if(Journey==4) { Check(!G->HasSurveyOptic()&&!G->HasSurveyUpgrade(),TEXT("Optional workbench bypass reaches ending")); Finish(true,TEXT("Checkpoint recovery, backtracking, death retry, restart and optional ending passed")); }
        else Travel(false,4);
    }
#endif
}
#if !UE_BUILD_SHIPPING
AActor* ACRCheckpointRoute::SlideBlock(FVector Position,FVector Size)
{
    // Isolated Development fixture only; never saved to a map or a player save slot.
    FActorSpawnParameters Params;Params.ObjectFlags|=RF_Transient;
    auto* A=GetWorld()->SpawnActor<AActor>(Params);auto* C=NewObject<UStaticMeshComponent>(A);
    A->AddInstanceComponent(C);A->SetRootComponent(C);C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
    C->SetCollisionProfileName(TEXT("BlockAll"));C->SetCanEverAffectNavigation(false);C->RegisterComponent();A->SetActorLocation(Position);A->SetActorScale3D(Size/100.f);return A;
}
void ACRCheckpointRoute::FinishSlideEdge()
{
    if(SlideObstacle.IsValid())SlideObstacle->Destroy();SlideObstacle.Reset();++SlideEdgeCase;
    if(SlideEdgeCase<6) Walk({{-1250,0}},TEXT("slide_edge_prepare"));else Walk({{1000,0},{1250,300}},TEXT("ammo"));
}
void ACRCheckpointRoute::Next(const FString& Name) { if(bFinished)return;Stage=Name;StageStarted=FPlatformTime::Seconds();UE_LOG(LogTemp,Display,TEXT("CR04_ROUTE stage=%s route=%d journey=%d"),*Stage,Route,Journey); }
void ACRCheckpointRoute::Walk(TArray<FVector2D> Points,const FString& After) { Waypoints=MoveTemp(Points);AfterWalk=After;Next(TEXT("walk")); }
void ACRCheckpointRoute::Inject(const UInputAction* Action,float Value) { if(PC.IsValid()&&PC->GetLocalPlayer())if(auto* Input=PC->GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())Input->InjectInputForAction(Action,FInputActionValue(Value),{},{}); }
bool ACRCheckpointRoute::Interact(AActor* Actor,const FVector& Point)
{
    if(!Actor || !Player.IsValid())return false;PC->SetControlRotation((Point-Player->Camera->GetComponentLocation()).Rotation());
    if(FPlatformTime::Seconds()-StageStarted<.6 || !Player->CanInteractWith(Actor))return false;
    // Separate Started edges for E; repeat only when the previous input pulse has ended.
    if(FPlatformTime::Seconds()-LastShot<.4)return false;
    Inject(Player->InteractAction);LastShot=FPlatformTime::Seconds();return true;
}
void ACRCheckpointRoute::Check(bool Condition,const TCHAR* Message)
{ if(bFinished)return;if(!Condition){Finish(false,Message);return;}Events+=FString::Printf(TEXT("%.3f PASS %s\n"),FPlatformTime::Seconds()-RunStart,Message);UE_LOG(LogTemp,Display,TEXT("CR04_ROUTE PASS %s"),Message); }
void ACRCheckpointRoute::Travel(bool Continue,int32 NextJourney)
{ if(bFinished)return;bFinished=true;Journey=NextJourney;if(Continue)PC->ContinueCheckpoint();else PC->RestartPrototype(); }
void ACRCheckpointRoute::Record(float Delta)
{
    const double Time=FPlatformTime::Seconds()-RunStart;const FVector P=Player->GetActorLocation();
    Frames+=FString::Printf(TEXT("%.3f,%s,%.4f,%.4f,%.4f,%.4f,%.1f,%.1f,%.1f\n"),Time,*Stage,Delta*1000,FPlatformTime::ToMilliseconds(GGameThreadTime),FPlatformTime::ToMilliseconds(GRenderThreadTime),FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles()),P.X,P.Y,P.Z);
    if(Time-MemoryAt>1){MemoryAt=Time;auto M=FPlatformMemory::GetStats();Memory+=FString::Printf(TEXT("%.3f,%s,%llu,%llu\n"),Time,*Stage,M.UsedPhysical,M.UsedVirtual);}
}
void ACRCheckpointRoute::Finish(bool Success,const FString& Message)
{
    if(bFinished)return;bFinished=true;const FString Dir=FPaths::ProjectSavedDir()/TEXT("Phase04")/FString::FromInt(Route);IFileManager::Get().MakeDirectory(*Dir,true);
    const FString Receipt=FString::Printf(TEXT("{\"passed\":%s,\"route\":%d,\"journey\":%d,\"message\":\"%s\"}"),Success?TEXT("true"):TEXT("false"),Route,Journey,*Message);
    FFileHelper::SaveStringToFile(Receipt,*(Dir/TEXT("acceptance.json")));FFileHelper::SaveStringToFile(Events,*(Dir/TEXT("route.txt")));FFileHelper::SaveStringToFile(Frames,*(Dir/TEXT("frames.csv")));FFileHelper::SaveStringToFile(Memory,*(Dir/TEXT("memory.csv")));
    int32 ViewWidth=0,ViewHeight=0;if(PC.IsValid())PC->GetViewportSize(ViewWidth,ViewHeight);
    FString Settings=FString::Printf(TEXT("viewport=%dx%d\n"),ViewWidth,ViewHeight);for(const TCHAR* Name:{TEXT("r.ScreenPercentage"),TEXT("r.DynamicRes.OperationMode"),TEXT("r.VSync"),TEXT("t.MaxFPS"),TEXT("sg.ViewDistanceQuality"),TEXT("sg.AntiAliasingQuality"),TEXT("sg.ShadowQuality"),TEXT("sg.GlobalIlluminationQuality"),TEXT("sg.ReflectionQuality"),TEXT("sg.PostProcessQuality"),TEXT("sg.TextureQuality"),TEXT("sg.EffectsQuality"),TEXT("sg.FoliageQuality"),TEXT("sg.ShadingQuality")})if(auto* C=IConsoleManager::Get().FindConsoleVariable(Name))Settings+=FString::Printf(TEXT("%s=%s\n"),Name,*C->GetString());FFileHelper::SaveStringToFile(Settings,*(Dir/TEXT("settings.txt")));
    FScreenshotRequest::RequestScreenshot(Dir/TEXT("result.png"),true,false);
    UE_LOG(LogTemp,Display,TEXT("CR04_FINISH %s"),*Receipt);
    // Use the actual game's Exit Game path. The receipt reports acceptance independently of process exit.
    if(PC.IsValid()) PC->ExitPrototype(); else FPlatformMisc::RequestExitWithStatus(false,1);
}
#endif
