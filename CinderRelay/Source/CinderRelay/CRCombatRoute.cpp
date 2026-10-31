#include "CRCombatRoute.h"
#if !UE_BUILD_SHIPPING
#include "CRCharacter.h"
#include "CRPlayerController.h"
#include "CRHealthComponent.h"
#include "CRWeaponComponent.h"
#include "CRGameMode.h"
#include "CRAshWarden.h"
#include "CRAshWardenController.h"
#include "CRChapterStreamingController.h"
#include "CRInteractionActor.h"
#include "CRAmmoPickup.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMemory.h"
#include "HAL/IConsoleManager.h"
#include "RenderTimer.h"
#include "DynamicRHI.h"
#include "UnrealClient.h"
#include "CRWorkbench.h"
#include "CRSalvagePickup.h"
#include "CRWeaponViewComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "LevelSequenceActor.h"
#include "LevelSequencePlayer.h"
namespace { int32 CombatScenario=0; FString Events,Frames,Memory; double RunStarted=0; }
#endif
ACRCombatRoute::ACRCombatRoute()
{
#if !UE_BUILD_SHIPPING
    PrimaryActorTick.bCanEverTick=true; PrimaryActorTick.bTickEvenWhenPaused=true;
#endif
}
void ACRCombatRoute::BeginPlay()
{
    Super::BeginPlay();
#if !UE_BUILD_SHIPPING
    Started=StageStarted=FPlatformTime::Seconds();
    bRestoration=FParse::Param(FCommandLine::Get(),TEXT("CRRestorationCheck"));
    if(!RunStarted) { RunStarted=Started; if(bRestoration) FParse::Value(FCommandLine::Get(),TEXT("CRRestorationStart="),CombatScenario); Frames=TEXT("elapsed,stage,scenario,frame_ms,game_thread_ms,render_thread_ms,gpu_ms,health,ammo,enemies,x,y,z\n"); Memory=TEXT("elapsed,stage,working_set_bytes,private_commit_bytes\n"); }
    for(TActorIterator<ACRChapterStreamingController> It(GetWorld());It;++It){Streaming=*It;break;}
    IFileManager::Get().MakeDirectory(*(FPaths::ProjectSavedDir()/TEXT("Phase02")),true);
    if(bRestoration) IFileManager::Get().MakeDirectory(*(FPaths::ProjectSavedDir()/TEXT("Phase03")),true);
#endif
}
void ACRCombatRoute::Tick(float Delta)
{
    Super::Tick(Delta);
#if !UE_BUILD_SHIPPING
    if(bFinished)return;
    const double Now=FPlatformTime::Seconds(),Age=Now-StageStarted;
    if(Now-RunStarted>(bRestoration?600:360) || Age>65) { Finish(false,TEXT("Bounded combat route timeout: ")+Stage); return; }
    if(Stage==TEXT("startup"))
    {
        Player=Cast<ACRCharacter>(UGameplayStatics::GetPlayerPawn(this,0)); if(!Player.IsValid())return;
        PC=Cast<ACRPlayerController>(Player->GetController());
        const auto List=Enemies(); if(List.Num()!=2)return;
        for(auto* E:List) { auto* AI=Cast<ACRAshWardenController>(E->GetController()); if(!AI||!AI->bNavigationReady)return; }
        Check(Streaming.IsValid()&&Streaming->IsZoneReady(0),TEXT("Safe streamed initial floor and native navigation ready"));
        Check(Player->Health->Health==100&&Player->Weapon->Magazine==5&&Player->Weapon->Reserve==25,TEXT("Initial health and ROOK-5 ammo"));
        Check(GetWorld()->GetAuthGameMode<ACRGameMode>()->DefeatedEnemies.IsEmpty(),TEXT("Restart starts with empty defeated-enemy record")); if(bFinished)return;
        Scout=List[0]; ScoutStart=Scout->GetActorLocation();
        if(bRestoration) Check(!GetWorld()->GetAuthGameMode<ACRGameMode>()->HasSurveyOptic()&&!GetWorld()->GetAuthGameMode<ACRGameMode>()->HasSurveyUpgrade(),TEXT("Restart clears salvage and applied upgrade"));
        if(CombatScenario==(bRestoration?4:2)) { Finish(true,TEXT("Combat, restoration, skip, cancel, streaming and optional ending route passed")); return; }
        if(CombatScenario==0)
        {
            auto* AI=Cast<ACRAshWardenController>(Scout->GetController()); Check(AI->InjectNavigationFailure()>0,TEXT("Native unreachable navigation request fails without endless retry"));
            auto* Path=UNavigationSystemV1::FindPathToLocationSynchronously(this,Scout->GetActorLocation(),FVector(-900,-1150,90),Scout.Get());
            Check(Path&&Path->IsValid()&&!Path->IsPartial()&&Path->PathPoints.Num()>2,TEXT("Native yard path routes around train cover"));
            if(bRestoration) Walk({{-1280,-290}},TEXT("03_yard"));else Walk({{-700,-350}},TEXT("receive"));
        }
        else Walk({{-300,0}},TEXT("fight"));
        return;
    }
    if(!Player.IsValid()||!PC.IsValid()||!Streaming.IsValid()||UGameplayStatics::GetPlayerPawn(this,0)!=Player.Get()) { Finish(false,TEXT("Lost player or persistent streaming authority")); return; }
    RecordFrame(Delta);
    if(Scout.IsValid()&&FVector::Dist2D(ScoutStart,Scout->GetActorLocation())>75)bMoved=true;
    if(Player->Health->Health<100)bReceivedDamage=true;
    if(Player->Health->IsDead()&&Stage!=TEXT("death")&&Stage!=TEXT("restart_death")) { Finish(false,TEXT("Unexpected defeat in ")+Stage); return; }
    if(Player->GetActorLocation().Z<-750){Finish(false,TEXT("Fell below streamed floor"));return;}
    auto* W=Player->Weapon.Get(); auto* GM=GetWorld()->GetAuthGameMode<ACRGameMode>();
    if(bRestoration && RestorationStage(Age))return;
    if(Stage==TEXT("walk"))
    {
        if(Waypoints.IsEmpty()) { Next(AfterWalk);return; }
        const FVector2D Here(Player->GetActorLocation().X,Player->GetActorLocation().Y),Diff=Waypoints[0]-Here;
        if(Diff.Size()<55) { Waypoints.RemoveAt(0);return; }
        PC->SetControlRotation(FRotator(0,FMath::RadiansToDegrees(FMath::Atan2(Diff.Y,Diff.X)),0));
        Inject(Player->ForwardAction); Inject(Player->SprintAction);return;
    }
    if(Stage==TEXT("receive"))
    {
        auto* AI=Scout.IsValid()?Cast<ACRAshWardenController>(Scout->GetController()):nullptr;
        if(bReceivedDamage) { Check(AI&&AI->bSight,TEXT("Native perception acquired visible player; enemy inflicted real damage")); Walk({{-1500,-350},{-1500,-1150},{-900,-1150}},TEXT("hidden")); }
    }
    else if(Stage==TEXT("hidden"))
    {
        if(Age<.4)HiddenHealth=Player->Health->Health;
        if(Age>6)
        {
            bool Hidden=true; for(auto* E:Enemies())if(auto* AI=Cast<ACRAshWardenController>(E->GetController())) Hidden&=!AI->HasAttackLine()&&!AI->bSight;
            Check(Hidden&&Player->Health->Health==HiddenHealth,TEXT("Real train geometry blocks sight and enemy damage"));
            auto* AI=Scout.IsValid()?Cast<ACRAshWardenController>(Scout->GetController()):nullptr;
            Check(AI&&AI->State!=ECRWardenState::Combat&&AI->State!=ECRWardenState::Investigate,TEXT("Lost-target memory expires; no omniscient pursuit"));
            Check(bMoved,TEXT("Enemy moved using native navigation after failed request"));
            Walk({{-1500,-1150},{-1500,-350},{-500,0}},TEXT("death"));
        }
    }
    else if(Stage==TEXT("death"))
    {
        if(Player->Health->IsDead()) { Check(PC->bPrototypeDefeated&&W->State==ECRWeaponState::Disabled,TEXT("Real enemy fire causes defeat menu and disables weapon")); FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Phase02/defeat.png"),true,false);Next(TEXT("restart_death")); }
    }
    else if(Stage==TEXT("restart_death")&&Age>1) { CombatScenario=1; Restart(); }
    else if(Stage==TEXT("fight"))
    {
        TArray<ACRAshWarden*> Alive; for(auto* E:Enemies())if(!E->Health->IsDead())Alive.Add(E);
        if(Alive.IsEmpty())
        {
            Check(GM->DefeatedEnemies.Num()==2&&bReceivedDamage,TEXT("Two scouts defeated by accepted player shots; player also received damage"));
            Check(bReloaded,TEXT("Reload used during actual encounter"));
            FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Phase02/combat-after.png"),true,false);
            Walk({{1000,0},{1250,300}},TEXT("ammo")); return;
        }
        auto* Enemy=Alive[0]; PC->SetControlRotation((Enemy->Head->GetComponentLocation()-Player->Camera->GetComponentLocation()).Rotation()); Inject(Player->AimAction);
        if(Age>1 && !bReceivedDamage)return;
        if(Age>1 && Now-LastShot>1.05 && W->State==ECRWeaponState::Ready)
        {
            if(!bReloaded&&GM->DefeatedEnemies.Num()==1&&W->Magazine<5) { Inject(Player->ReloadAction);bReloaded=true;LastShot=Now; }
            else if(W->Magazine==0) { Inject(Player->ReloadAction);LastShot=Now; }
            else { Inject(Player->FireAction);LastShot=Now; if(GM->DefeatedEnemies.IsEmpty()) FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Phase02/combat.png"),true,false); }
        }
    }
    else if(Stage==TEXT("ammo"))
    {
        ACRAmmoPickup* Pickup=nullptr; for(TActorIterator<ACRAmmoPickup> It(GetWorld());It;++It){Pickup=*It;break;}
        Check(Pickup!=nullptr,TEXT("Limited ammo pickup exists in streamed yard"));if(bFinished)return;
        PC->SetControlRotation((Pickup->GetActorLocation()-Player->Camera->GetComponentLocation()).Rotation());
        if(Age>.5) { if(!GM->IsPickupCollected(Pickup->PickupId))Inject(Player->InteractAction);else if(bRestoration&&CombatScenario!=3) Walk({{1500,0},{1850,0},{2130,-350}},TEXT("03_bench_empty"));else Walk({{1500,0},{1850,0},{2800,-170}},TEXT("module")); }
    }
    else if(Stage==TEXT("module"))
    {
        if(Interact(FindItem(ECRInteractionKind::PowerModule)))Next(TEXT("module_result"));
    }
    else if(Stage==TEXT("module_result")&&Age>.3)
    {
        Check(GM->GetObjective()==ECRObjective::RestorePower,TEXT("Existing module objective progresses after combat")); Walk({{3300,0},{3550,0},{5450,0},{6000,-320}},TEXT("relay"));
    }
    else if(Stage==TEXT("relay"))
    {
        if(Interact(FindItem(ECRInteractionKind::Relay)))Next(TEXT("relay_result"));
    }
    else if(Stage==TEXT("relay_result")&&Age>1)
    {
        Check(GM->GetObjective()==ECRObjective::InvestigateSignal&&Streaming->IsZoneUnloaded(0),TEXT("Relay restored, Rail Yard genuinely unloaded"));
        Walk({{5800,0},{5450,0},{3500,0},{2800,-170},{2400,0},{1300,0},{-1100,0}},TEXT("revisit"));
    }
    else if(Stage==TEXT("revisit")&&Age>2)
    {
        Check(Enemies().IsEmpty()&&GM->DefeatedEnemies.Num()==2,TEXT("Defeated scouts do not revive after zone reload"));
        Check(GM->GetObjective()==ECRObjective::InvestigateSignal&&Streaming->IsZoneUnloaded(1)&&Streaming->IsZoneUnloaded(2),TEXT("Backtracking preserves chapter state and unloads B/C"));
        for(TActorIterator<ACRAmmoPickup> It(GetWorld());It;++It)Check(It->IsHidden()&&!It->GetActorEnableCollision(),TEXT("Ammo pickup remains consumed after reload"));
        Walk({{1850,0},{2800,-170}},TEXT("module_revisit"));
    }
    else if(Stage==TEXT("module_revisit")&&Age>.5)
    {
        if(bRestoration && CombatScenario==1)
        {
            Check(GM->HasSurveyUpgrade()&&W->GetAimFOV()==60,TEXT("Upgrade survives actual Workshop unload and return"));
            for(TActorIterator<ACRWorkbench> It(GetWorld());It;++It)Check(It->State==ECRAssemblyState::Completed,TEXT("Reloaded workbench reconciles completion without replay"));
            for(TActorIterator<ACRSalvagePickup> It(GetWorld());It;++It)Check(It->IsHidden()&&!It->GetActorEnableCollision(),TEXT("Reloaded salvage remains consumed"));
        }
        const auto* Item=FindItem(ECRInteractionKind::PowerModule); Check(Item&&Item->bUsed&&Item->IsHidden(),TEXT("Original power-module reconciliation preserved"));
        Walk({{3300,0},{3550,0},{5450,0},{6500,-250},{6700,0}},TEXT("signal"));
    }
    else if(Stage==TEXT("signal")) { if(Interact(FindItem(ECRInteractionKind::Signal)))Next(TEXT("ending")); }
    else if(Stage==TEXT("ending")&&Age>1)
    {
        if(bRestoration&&CombatScenario==3)Check(!GM->HasSurveyOptic()&&!GM->HasSurveyUpgrade(),TEXT("Chapter ending reached without salvage or optional workbench"));
        Check(GM->GetObjective()==ECRObjective::Complete&&PC->bPrototypeEnded,TEXT("Original final signal and ending still work"));
        FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Phase02/ending.png"),true,false); Next(TEXT("final_restart"));
    }
    else if(Stage==TEXT("final_restart")&&Age>1) { CombatScenario=bRestoration&&CombatScenario==3?4:2; Restart(); }
#endif
}
#if !UE_BUILD_SHIPPING
bool ACRCombatRoute::RestorationStage(double Age)
{
    if(!Stage.StartsWith(TEXT("03_"))) return false;
    auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>(); auto* W=Player->Weapon.Get();
    ACRWorkbench* Bench=nullptr; for(TActorIterator<ACRWorkbench> It(GetWorld());It;++It){Bench=*It;break;}
    auto AimAt=[this](AActor* A,FVector Point){PC->SetControlRotation((Point-Player->Camera->GetComponentLocation()).Rotation());};
    if(Stage==TEXT("03_yard") || Stage==TEXT("03_collect"))
    {
        const bool Yard=Stage==TEXT("03_yard"); ACRSalvagePickup* Item=nullptr;
        for(TActorIterator<ACRSalvagePickup> It(GetWorld());It;++It)if(It->SourceId==(Yard?TEXT("CR03_YardCache"):TEXT("CR03_WorkshopBackup"))){Item=*It;break;}
        if(!Item)return true;
        AimAt(Item,Item->Mesh->Bounds.Origin);
        if(G->HasSurveyOptic())
        {
            Check(Item->IsHidden()&&!Item->GetActorEnableCollision(),TEXT("Collected salvage hides and disables its collision"));
            Check(!G->TryCollectSurveyOptic(TEXT("OtherSource")),TEXT("Second logical component cannot duplicate rewards"));
            if(Yard) { Check(G->DefeatedEnemies.IsEmpty(),TEXT("Yard salvage reached without defeating enemies"));Walk({{-700,-350}},TEXT("receive")); }
            else Next(TEXT("03_start"));
        }
        else if(Age>.7)
        {
            if(!Player->CanInteractWith(Item))
            {
                FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(CR03SalvageDiagnosis),false,Player.Get());
                const FVector Eye=Player->Camera->GetComponentLocation(),End=Eye+Player->Camera->GetForwardVector()*Player->InteractionRange;
                GetWorld()->LineTraceSingleByChannel(Hit,Eye,End,ECC_Visibility,Params);
                UE_LOG(LogTemp,Warning,TEXT("CR03_TRACE eye=%s end=%s target=%s target_center=%s hit=%s component=%s distance=%.2f"),*Eye.ToString(),*End.ToString(),*Item->GetName(),*Item->Mesh->Bounds.Origin.ToString(),*GetNameSafe(Hit.GetActor()),*GetNameSafe(Hit.GetComponent()),Hit.Distance);
                FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Phase03/trace-failure.png"),true,false);
            }
            Check(Player->CanInteractWith(Item)&&Item->CanInteract_Implementation(Player.Get()),TEXT("Salvage has a valid short-range camera trace"));if(!bFinished)Inject(Player->InteractAction);
        }
        return true;
    }
    if(!Bench) { Finish(false,TEXT("Workshop presentation actor missing"));return true; }
    if(Stage==TEXT("03_bench_empty"))
    {
        AimAt(Bench,Bench->GetActorLocation()+FVector(0,0,96));
        if(Age>.7 && Bench->IsReady())
        {
            Check(!G->HasSurveyOptic()&&!Bench->CanInteract_Implementation(Player.Get()),TEXT("Workbench rejects missing component"));
            Check(W->GetAimFOV()==65,TEXT("Unmodified ROOK-5 preserves base ADS")); Next(TEXT("03_collect"));
        }
    }
    else if(Stage==TEXT("03_start") || Stage==TEXT("03_start_again"))
    {
        const bool Again=Stage==TEXT("03_start_again");
        AimAt(Bench,Bench->GetActorLocation()+FVector(0,0,96));
        if(Bench->State==ECRAssemblyState::Playing)
        {
            Check(Bench->Hands->GetNumBones()>=39&&Bench->Hands->GetBoneIndex(TEXT("hand_R"))!=INDEX_NONE&&Bench->Hands->GetBoneIndex(TEXT("optic"))!=INDEX_NONE,TEXT("Imported rig has the authored hands, fingers and prop hierarchy"));
            Check(PC->IsAssembling()&&W->IsPresentationLocked()&&!W->CanUse()&&PC->IsMoveInputIgnored()&&PC->IsLookInputIgnored(),TEXT("Assembly owns input and blocks fire/reload"));
            Check(!Bench->CanInteract_Implementation(Player.Get()),TEXT("Duplicate workbench interaction rejected"));
            AssemblyAmmo=W->Magazine;AssemblyReserve=W->Reserve;AssemblyHealth=Player->Health->Health;
            Next(Again?TEXT("03_full"):CombatScenario==2?TEXT("03_skip"):TEXT("03_abort"));
        }
        else if(Age>.7)
        {
            Check(Bench->CanInteract_Implementation(Player.Get()),TEXT("Owned component starts actual trace-based bench interaction"));
            if(!bFinished)Inject(Player->InteractAction);
        }
    }
    else if(Stage==TEXT("03_abort") && Age>2)
    {
        bool Stopped=false;
        for(TActorIterator<ALevelSequenceActor> It(GetWorld());It;++It) if(It->GetLevel()==Bench->GetLevel() && It->GetSequencePlayer() && It->GetSequencePlayer()->IsPlaying())
        { It->GetSequencePlayer()->Stop();Stopped=true;break; }
        Check(Stopped,TEXT("Injected a genuine native sequence stop before completion"));Next(TEXT("03_abort_verify"));
    }
    else if(Stage==TEXT("03_abort_verify") && Bench->State==ECRAssemblyState::Idle)
    {
        Check(!G->HasSurveyUpgrade()&&!PC->IsAssembling()&&!W->IsPresentationLocked()&&!PC->IsMoveInputIgnored()&&!PC->IsLookInputIgnored()&&Player->GetCharacterMovement()->IsMovingOnGround(),TEXT("Cancellation grants no upgrade and restores all controls"));
        Check(W->Magazine==AssemblyAmmo&&W->Reserve==AssemblyReserve&&Player->Health->Health==AssemblyHealth,TEXT("Cancellation preserves ammunition and health"));
        Next(TEXT("03_start_again"));
    }
    else if(Stage==TEXT("03_skip") && Age>2)
    {
        PC->SkipAssembly();Next(TEXT("03_skip_verify"));
    }
    else if(Stage==TEXT("03_skip_verify") && Bench->State==ECRAssemblyState::Completed)
    {
        Check(G->HasSurveyUpgrade()&&Bench->State==ECRAssemblyState::Completed&&!PC->IsAssembling()&&W->CanUse(),TEXT("Skip finalizes upgrade once and restores gameplay"));
        Check(!G->TryApplySurveyUpgrade(),TEXT("Skipped upgrade cannot commit twice"));Next(TEXT("03_skip_restart"));
    }
    else if(Stage==TEXT("03_skip_restart") && Age>1) { CombatScenario=3;Restart(); }
    else if(Stage==TEXT("03_full"))
    {
        const float Position=Bench->GetPresentationSeconds();
        if(PC->bPrototypePaused)
        {
            if(FPlatformTime::Seconds()-PauseStarted>1.5)
            {
                Check(FMath::Abs(Position-PausePosition)<.1f,TEXT("Pause freezes actual Sequencer time"));PC->ResumePrototype();
            }
            return true;
        }
        if(Position>8 && !bAssemblyPaused)
        { bAssemblyPaused=true;PausePosition=Position;PauseStarted=FPlatformTime::Seconds();PC->TogglePrototypePause();return true; }
        const float CaptureTimes[]={3.f,7.f,13.f,18.f};
        if(AssemblyCapture<4 && Position>=CaptureTimes[AssemblyCapture])
        {
            FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/FString::Printf(TEXT("Phase03/assembly-%02d.png"),AssemblyCapture),true,false);
            if(AssemblyCapture==0)FirstHand=Bench->Hands->GetBoneLocation(TEXT("hand_R"));
            if(AssemblyCapture==1)Check(FVector::Dist(FirstHand,Bench->Hands->GetBoneLocation(TEXT("hand_R")))>10,TEXT("Imported hand bone moves under actual Sequencer playback"));
            ++AssemblyCapture;
        }
        if(Bench->State==ECRAssemblyState::Completed)
        {
            Check(AssemblyCapture==4&&G->HasSurveyUpgrade()&&!PC->IsAssembling()&&!PC->IsMoveInputIgnored()&&!PC->IsLookInputIgnored()&&W->CanUse(),TEXT("Natural 22-second sequence completes and releases gameplay"));
            Check(W->Magazine==AssemblyAmmo&&W->Reserve==AssemblyReserve&&Player->Health->Health==AssemblyHealth,TEXT("Full presentation preserves ammunition and health"));
            Check(Player->WeaponView->HasImportedAppearance(),TEXT("Imported ROOK-5 appearance loaded; cube fallback not active"));Next(TEXT("03_ads"));
        }
    }
    else if(Stage==TEXT("03_ads"))
    {
        Inject(Player->AimAction);
        if(Age>1)
        {
            Check(W->GetAimFOV()==60&&FMath::Abs(Player->Camera->FieldOfView-60)<.2f,TEXT("Applied optic changes actual ADS camera to 60 degrees"));
            FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Phase03/upgraded-ads.png"),true,false);
            Inject(Player->FireAction);Next(TEXT("03_fire"));
        }
    }
    else if(Stage==TEXT("03_fire") && Age>1 && W->State==ECRWeaponState::Ready)
    {
        // Screenshot capture can stall between input injection and the accepted shot.
        // Observe the native cycle state; wall time since injection is not weapon readiness.
        Check(W->Magazine==AssemblyAmmo-1,TEXT("Upgraded weapon still fires and consumes one round"));Inject(Player->ReloadAction);Next(TEXT("03_reload"));
    }
    else if(Stage==TEXT("03_reload") && Age>3)
    {
        Check(W->State==ECRWeaponState::Ready&&W->Magazine==5,TEXT("Upgraded weapon completes original reload"));Walk({{2400,-170},{2800,-170}},TEXT("module"));
    }
    return true;
}
TArray<ACRAshWarden*> ACRCombatRoute::Enemies() const { TArray<ACRAshWarden*> List;for(TActorIterator<ACRAshWarden> It(GetWorld());It;++It)List.Add(*It);List.Sort([](const ACRAshWarden& A,const ACRAshWarden& B){return A.EnemyId.LexicalLess(B.EnemyId);});return List; }
void ACRCombatRoute::Next(const FString& Name){if(bFinished)return;Stage=Name;StageStarted=FPlatformTime::Seconds();UE_LOG(LogTemp,Display,TEXT("CR02_ROUTE stage=%s scenario=%d"),*Stage,CombatScenario);}
void ACRCombatRoute::Walk(TArray<FVector2D> Points,const FString& NextStage){Waypoints=MoveTemp(Points);AfterWalk=NextStage;Next(TEXT("walk"));}
void ACRCombatRoute::Inject(const UInputAction* Action,float Value){if(PC.IsValid()&&PC->GetLocalPlayer())if(auto* Input=PC->GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())Input->InjectInputForAction(Action,FInputActionValue(Value),{},{});}
ACRInteractionActor* ACRCombatRoute::FindItem(ECRInteractionKind Kind) const {for(TActorIterator<ACRInteractionActor> It(GetWorld());It;++It)if(It->Kind==Kind)return *It;return nullptr;}
bool ACRCombatRoute::Interact(ACRInteractionActor* Item)
{
    if(!Item)return false; PC->SetControlRotation((Item->GetActorLocation()-Player->Camera->GetComponentLocation()).Rotation());
    if(FPlatformTime::Seconds()-StageStarted<.6)return false;
    Check(Player->CanInteractWith(Item)&&Item->CanInteract_Implementation(Player.Get()),TEXT("Original interaction valid through camera trace"));if(bFinished)return false;Inject(Player->InteractAction);return true;
}
void ACRCombatRoute::Check(bool Condition,const TCHAR* Message){if(bFinished)return;if(!Condition){Finish(false,Message);return;}Events+=FString::Printf(TEXT("%.3f PASS %s\n"),FPlatformTime::Seconds()-RunStarted,Message);UE_LOG(LogTemp,Display,TEXT("CR02_ROUTE PASS %s"),Message);}
void ACRCombatRoute::Restart(){if(bFinished)return;bFinished=true;PC->RestartPrototype();}
void ACRCombatRoute::RecordFrame(float Delta)
{
    const double Time=FPlatformTime::Seconds()-RunStarted;const FVector P=Player->GetActorLocation();
    Frames+=FString::Printf(TEXT("%.3f,%s,%d,%.4f,%.4f,%.4f,%.4f,%.1f,%d,%d,%.1f,%.1f,%.1f\n"),Time,*Stage,CombatScenario,Delta*1000.,FPlatformTime::ToMilliseconds(GGameThreadTime),FPlatformTime::ToMilliseconds(GRenderThreadTime),FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles()),Player->Health->Health,Player->Weapon->Magazine,Enemies().Num(),P.X,P.Y,P.Z);
    if(Time-LastMemory>1){LastMemory=Time;const auto Stats=FPlatformMemory::GetStats();Memory+=FString::Printf(TEXT("%.3f,%s,%llu,%llu\n"),Time,*Stage,Stats.UsedPhysical,Stats.UsedVirtual);}
}
void ACRCombatRoute::Finish(bool Passed,const FString& Message)
{
    if(bFinished)return;bFinished=true;const FString Dir=FPaths::ProjectSavedDir()/(bRestoration?TEXT("Phase03"):TEXT("Phase02"));
    const FString Receipt=FString::Printf(TEXT("{\"passed\":%s,\"mode\":\"combat\",\"scenario\":%d,\"message\":\"%s\"}"),Passed?TEXT("true"):TEXT("false"),CombatScenario,*Message);
    FFileHelper::SaveStringToFile(Receipt,*(Dir/TEXT("acceptance.json")));FFileHelper::SaveStringToFile(Events,*(Dir/TEXT("route.txt")));FFileHelper::SaveStringToFile(Frames,*(Dir/TEXT("frames.csv")));FFileHelper::SaveStringToFile(Memory,*(Dir/TEXT("memory.csv")));
    FString Settings;for(const TCHAR* Name:{TEXT("r.ScreenPercentage"),TEXT("r.DynamicRes.OperationMode"),TEXT("r.VSync"),TEXT("t.MaxFPS"),TEXT("sg.ViewDistanceQuality"),TEXT("sg.AntiAliasingQuality"),TEXT("sg.ShadowQuality"),TEXT("sg.GlobalIlluminationQuality"),TEXT("sg.ReflectionQuality"),TEXT("sg.PostProcessQuality"),TEXT("sg.TextureQuality"),TEXT("sg.EffectsQuality"),TEXT("sg.FoliageQuality"),TEXT("sg.ShadingQuality"),TEXT("r.AntiAliasingMethod"),TEXT("r.RayTracing"),TEXT("r.Lumen.HardwareRayTracing")})if(const auto* C=IConsoleManager::Get().FindConsoleVariable(Name))Settings+=FString::Printf(TEXT("%s=%s\n"),Name,*C->GetString());FFileHelper::SaveStringToFile(Settings,*(Dir/TEXT("settings.txt")));
    UE_LOG(LogTemp,Display,TEXT("CR02_FINISH %s"),*Receipt);
#if WITH_EDITOR
    if(GetWorld()->WorldType==EWorldType::PIE)return;
#endif
    FPlatformMisc::RequestExitWithStatus(false,Passed?0:1);
}
#endif
