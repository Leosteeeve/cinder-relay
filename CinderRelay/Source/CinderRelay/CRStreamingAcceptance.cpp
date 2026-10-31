#include "CRStreamingAcceptance.h"
#if !UE_BUILD_SHIPPING
#include "CRChapterStreamingController.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "CRInteractionActor.h"
#include "CRPlayerController.h"
#include "Camera/CameraComponent.h"
#include "Engine/LocalPlayer.h"
#include "Engine/LevelStreaming.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "EnhancedInputSubsystems.h"
#include "HAL/PlatformMemory.h"
#include "HAL/PlatformFileManager.h"
#include "HAL/IConsoleManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "RenderTimer.h"
#include "DynamicRHI.h"
#include "UnrealClient.h"
namespace { bool bVerifyRestart = false; }
#endif

ACRStreamingAcceptance::ACRStreamingAcceptance()
{
#if !UE_BUILD_SHIPPING
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.bTickEvenWhenPaused = true;
#endif
}
void ACRStreamingAcceptance::BeginPlay()
{
    Super::BeginPlay();
#if !UE_BUILD_SHIPPING
    Started = StageStarted = FPlatformTime::Seconds();
    Frames = TEXT("elapsed,stage,cycle,frame_ms,game_thread_ms,render_thread_ms,gpu_ms,x,y,z,A_loaded,A_visible,B_loaded,B_visible,C_loaded,C_visible\n");
    Memory = TEXT("elapsed,stage,cycle,working_set_bytes,private_commit_bytes,A_unloaded,B_unloaded,C_unloaded\n");
    if (FParse::Param(FCommandLine::Get(), TEXT("CRStreamExitCheck")))
    {
        Finish(true, TEXT("Exit-only lifecycle check; not gameplay acceptance"));
        return;
    }
    for (TActorIterator<ACRChapterStreamingController> It(GetWorld()); It; ++It) { Streaming = *It; break; }
    if (!Streaming.IsValid()) { Finish(false, TEXT("Persistent streaming controller missing")); return; }
    if (!bVerifyRestart) Streaming->SetAcceptanceHold(1, true);
    FString Settings;
    for (const TCHAR* Name : { TEXT("r.ScreenPercentage"), TEXT("r.DynamicRes.OperationMode"), TEXT("r.VSync"), TEXT("t.MaxFPS"), TEXT("sg.ViewDistanceQuality"), TEXT("sg.AntiAliasingQuality"), TEXT("sg.ShadowQuality"), TEXT("sg.GlobalIlluminationQuality"), TEXT("sg.ReflectionQuality"), TEXT("sg.PostProcessQuality"), TEXT("sg.TextureQuality"), TEXT("sg.EffectsQuality"), TEXT("sg.FoliageQuality"), TEXT("sg.ShadingQuality"), TEXT("r.AntiAliasingMethod"), TEXT("r.DynamicGlobalIlluminationMethod"), TEXT("r.ReflectionMethod"), TEXT("r.RayTracing"), TEXT("r.Lumen.HardwareRayTracing"), TEXT("r.Shadow.Virtual.Enable") })
        if (const auto* CVar = IConsoleManager::Get().FindConsoleVariable(Name)) Settings += FString::Printf(TEXT("%s=%s\n"), Name, *CVar->GetString());
    IFileManager::Get().MakeDirectory(*(FPaths::ProjectSavedDir() / TEXT("Phase01B")), true);
    FFileHelper::SaveStringToFile(Settings, *(FPaths::ProjectSavedDir() / TEXT("Phase01B/settings.txt")));
#endif
}
void ACRStreamingAcceptance::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
    if (bFinished) return;
    const double Now = FPlatformTime::Seconds(), Age = Now - StageStarted;
    if (Now - Started > 360 || Age > (Stage == TEXT("walk") ? 50 : 35)) { Finish(false, TEXT("Bounded timeout in ") + Stage); return; }
    auto* Mode = GetWorld()->GetAuthGameMode<ACRGameMode>();
    if (!Streaming.IsValid() || !Mode) { Finish(false, TEXT("Lost persistent authority")); return; }
    if (Stage == TEXT("startup"))
    {
        auto* Pawn = Cast<ACRCharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
        if (!Pawn) return;
        Player = Pawn; PC = Cast<ACRPlayerController>(Pawn->GetController());
        Check(Streaming->IsZoneReady(0) && Pawn->GetActorLocation().Z > 80, TEXT("Initial A floor ready before spawn"));
        if (bFinished) return;
        Check(Mode->GetObjective() == ECRObjective::ReachWorkshop, TEXT("Initial objective"));
        if (bVerifyRestart)
        {
            Check(!PC->bPrototypeEnded && !PC->bPrototypePaused && Streaming->CurrentZone == 0 && !Streaming->GetZoneLevel(1)->ShouldBeLoaded(), TEXT("Restart reset objective, UI and streaming"));
            if (!bFinished) Finish(true, TEXT("Restart verified after three backtracking cycles and ending"));
            return;
        }
        Advance(TEXT("warmup"));
    }
    if (!Player.IsValid() || !PC.IsValid() || UGameplayStatics::GetPlayerPawn(this, 0) != Player.Get()) { Finish(false, TEXT("Player identity changed during zone transition")); return; }
    if (Player->GetActorLocation().Z < -750) { Finish(false, TEXT("Player fell below floor")); return; }
    const FVector P = Player->GetActorLocation();
    auto* A = Streaming->GetZoneLevel(0); auto* B = Streaming->GetZoneLevel(1); auto* C = Streaming->GetZoneLevel(2);
    Frames += FString::Printf(TEXT("%.3f,%s,%d,%.4f,%.4f,%.4f,%.4f,%.1f,%.1f,%.1f,%d,%d,%d,%d,%d,%d\n"), Now-Started, *Stage, Cycle, double(DeltaSeconds*1000), FPlatformTime::ToMilliseconds(GGameThreadTime), FPlatformTime::ToMilliseconds(GRenderThreadTime), FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles()), P.X,P.Y,P.Z,A&&A->IsLevelLoaded(),A&&A->IsLevelVisible(),B&&B->IsLevelLoaded(),B&&B->IsLevelVisible(),C&&C->IsLevelLoaded(),C&&C->IsLevelVisible());
    if (Now - LastMemory >= 1)
    {
        LastMemory = Now; const auto Stats = FPlatformMemory::GetStats();
        Memory += FString::Printf(TEXT("%.3f,%s,%d,%llu,%llu,%d,%d,%d\n"), Now-Started, *Stage, Cycle, Stats.UsedPhysical, Stats.UsedVirtual, Streaming->IsZoneUnloaded(0), Streaming->IsZoneUnloaded(1), Streaming->IsZoneUnloaded(2));
    }
    if (Stage == TEXT("warmup"))
    {
        if (Age > 3) Walk({{1500,0}}, TEXT("held_gate"));
    }
    else if (Stage == TEXT("walk"))
    {
        FVector2D Delta = Route[0] - FVector2D(P.X,P.Y);
        if (Delta.Size() < 25)
        {
            Route.RemoveAt(0); Player->ClearHeldActions();
            if (Route.IsEmpty()) Advance(AfterWalk);
            return;
        }
        PC->SetControlRotation(FRotator(0, FMath::RadiansToDegrees(FMath::Atan2(Delta.Y,Delta.X)), 0));
        Inject(Player->ForwardAction); Inject(Player->SprintAction);
    }
    else if (Stage == TEXT("held_gate"))
    {
        PC->SetControlRotation(FRotator::ZeroRotator); Inject(Player->ForwardAction);
        if (Age > 1.0)
        {
            Check(B->IsLevelLoaded() && B->IsLevelVisible() && !Streaming->IsZoneReady(1) && Streaming->AreGatesClosedFor(1) && P.X < 1550, TEXT("Bounded readiness veto keeps gate collidable despite visible target"));
            Player->ClearHeldActions();
            Walk({{450,0}}, TEXT("reversed"));
        }
    }
    else if (Stage == TEXT("reversed"))
    {
        if (Age > 1)
        {
            Check(Streaming->IsZoneUnloaded(1) && Streaming->AreGatesClosedFor(1), TEXT("Reversal cancels demand; old target unloaded and shutter closed"));
            Streaming->SetAcceptanceHold(1, false);
            Streaming->InjectAcceptanceFailure(1);
            Walk({{1500,0}}, TEXT("failed_gate"));
        }
    }
    else if (Stage == TEXT("failed_gate"))
    {
        Check(Streaming->AreGatesClosedFor(1) && !Streaming->IsZoneReady(1), TEXT("Injected failure keeps boundary closed"));
        PC->RetryStreaming(); Advance(TEXT("retry"));
    }
    else if (Stage == TEXT("retry"))
    {
        if (Streaming->IsZoneReady(1)) { Check(true,TEXT("Retry recovered target")); Walk({{1850,0},{2500,0},{2800,-170}}, TEXT("module")); }
    }
    else if (Stage == TEXT("module"))
    {
        if (AimAndInteract(ECRInteractionKind::PowerModule)) Advance(TEXT("module_result"));
    }
    else if (Stage == TEXT("module_result"))
    {
        if (Age > .3)
        {
            Check(Mode->GetObjective() == ECRObjective::RestorePower, TEXT("Workshop entry and E module progress"));
            Walk({{3300,0},{3550,0},{5450,0},{6000,-320}}, TEXT("relay"));
        }
    }
    else if (Stage == TEXT("relay"))
    {
        if (AimAndInteract(ECRInteractionKind::Relay)) Advance(TEXT("relay_result"));
    }
    else if (Stage == TEXT("relay_result"))
    {
        if (Age > .3)
        {
            Check(Mode->GetObjective() == ECRObjective::InvestigateSignal && Streaming->IsZoneUnloaded(0) && Streaming->IsZoneUnloaded(1), TEXT("Relay powered, A and B truly unloaded"));
            Walk({{5800,0},{5450,0},{3500,0},{2800,-170}}, TEXT("return_module"));
        }
    }
    else if (Stage == TEXT("return_module"))
    {
        auto* Item = FindItem(ECRInteractionKind::PowerModule);
        Check(Item && Item->bUsed && Item->IsHidden() && !Item->GetActorEnableCollision(), TEXT("Reloaded module remains collected"));
        if (Item) Item->Interact_Implementation(Player.Get());
        Check(Mode->GetObjective() == ECRObjective::InvestigateSignal, TEXT("Repeated module and entry trigger do not progress"));
        Walk({{2400,0},{1300,0},{-1100,0}}, TEXT("yard_checkpoint"));
    }
    else if (Stage == TEXT("yard_checkpoint"))
    {
        if (Age > 3)
        {
            Check(Streaming->IsZoneUnloaded(1) && Streaming->IsZoneUnloaded(2), TEXT("Yard checkpoint B and C unloaded"));
            Walk({{1850,0},{3300,0},{3550,0},{5450,0},{6000,-320}}, TEXT("return_relay"));
        }
    }
    else if (Stage == TEXT("return_relay"))
    {
        auto* Item = FindItem(ECRInteractionKind::Relay);
        Check(Item && Item->bUsed, TEXT("Reloaded relay remains powered"));
        if (Item) Item->Interact_Implementation(Player.Get());
        Check(Mode->GetObjective() == ECRObjective::InvestigateSignal && Streaming->IsZoneUnloaded(0) && Streaming->IsZoneUnloaded(1), TEXT("Relay duplicate rejected, only C resident"));
        ++Cycle; Advance(TEXT("bunker_checkpoint"));
    }
    else if (Stage == TEXT("bunker_checkpoint"))
    {
        if (Age > 3)
        {
            Check(true, TEXT("Completed one C-B-A-B-C cycle"));
            if (Cycle < 3) Walk({{5800,0},{5450,0},{3500,0},{2800,-170}}, TEXT("return_module"));
            else Walk({{6500,-250},{6700,0}}, TEXT("signal"));
        }
    }
    else if (Stage == TEXT("signal"))
    {
        if (AimAndInteract(ECRInteractionKind::Signal)) Advance(TEXT("ending"));
    }
    else if (Stage == TEXT("ending") && Age > 3)
    {
        Check(Mode->GetObjective() == ECRObjective::Complete && PC->bPrototypeEnded && PC->bPrototypePaused, TEXT("Final signal ended chapter with paused HUD"));
        if (bFinished) return;
        FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir() / TEXT("Phase01B/ending.png"), true, false);
        Advance(TEXT("restart"));
    }
    else if (Stage == TEXT("restart") && Age > 2)
    {
        const FString Dir = FPaths::ProjectSavedDir() / TEXT("Phase01B");
        FFileHelper::SaveStringToFile(Frames, *(Dir / TEXT("frames.csv")));
        FFileHelper::SaveStringToFile(Memory, *(Dir / TEXT("memory.csv")));
        FFileHelper::SaveStringToFile(Events, *(Dir / TEXT("route.txt")));
        bVerifyRestart = true; bFinished = true; PC->RestartPrototype();
    }
#endif
}
#if !UE_BUILD_SHIPPING
void ACRStreamingAcceptance::Advance(const FString& Next)
{
    Stage = Next; StageStarted = FPlatformTime::Seconds();
    UE_LOG(LogTemp, Display, TEXT("CR_ACCEPT stage=%s cycle=%d"), *Stage, Cycle);
}
void ACRStreamingAcceptance::Walk(TArray<FVector2D> Points, const FString& Next)
{
    if (bFinished) return;
    Route = MoveTemp(Points); AfterWalk = Next; Advance(TEXT("walk"));
}
void ACRStreamingAcceptance::Inject(const UInputAction* Action, float Value)
{
    if (PC.IsValid() && PC->GetLocalPlayer())
        if (auto* Input = PC->GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
            Input->InjectInputForAction(Action, FInputActionValue(Value), {}, {});
}
ACRInteractionActor* ACRStreamingAcceptance::FindItem(ECRInteractionKind Kind) const
{
    for (TActorIterator<ACRInteractionActor> It(GetWorld()); It; ++It) if (It->Kind == Kind) return *It;
    return nullptr;
}
bool ACRStreamingAcceptance::AimAndInteract(ECRInteractionKind Kind)
{
    auto* Item = FindItem(Kind);
    if (!Item) return false;
    PC->SetControlRotation((Item->GetActorLocation() - Player->Camera->GetComponentLocation()).Rotation());
    if (FPlatformTime::Seconds() - StageStarted < .5) return false;
    Check(Player->CanInteractWith(Item) && Item->CanInteract_Implementation(Player.Get()), TEXT("Interaction is in range and line of sight"));
    if (bFinished) return false;
    Inject(Player->InteractAction); return true;
}
void ACRStreamingAcceptance::Check(bool bCondition, const TCHAR* Message)
{
    if (bFinished) return;
    if (!bCondition) { Finish(false, Message); return; }
    const FString Line = FString::Printf(TEXT("%.3f cycle=%d PASS %s\n"), FPlatformTime::Seconds()-Started, Cycle, Message);
    Events += Line; UE_LOG(LogTemp, Display, TEXT("CR_ACCEPT %s"), *Line);
}
void ACRStreamingAcceptance::Finish(bool bPassed, const FString& Message)
{
    if (bFinished) return;
    bFinished = true;
    const FString Dir = FPaths::ProjectSavedDir() / TEXT("Phase01B");
    IFileManager::Get().MakeDirectory(*Dir, true);
    if (!bVerifyRestart)
    {
        FFileHelper::SaveStringToFile(Frames, *(Dir / TEXT("frames.csv")));
        FFileHelper::SaveStringToFile(Memory, *(Dir / TEXT("memory.csv")));
        FFileHelper::SaveStringToFile(Events, *(Dir / TEXT("route.txt")));
    }
    const FString Receipt = FString::Printf(TEXT("{\"passed\":%s,\"restart_verified\":%s,\"message\":\"%s\",\"stage\":\"%s\",\"map\":\"%s\"}\n"), bPassed ? TEXT("true") : TEXT("false"), bVerifyRestart && bPassed ? TEXT("true") : TEXT("false"), *Message, *Stage, *GetWorld()->GetMapName());
    FFileHelper::SaveStringToFile(Receipt, *(Dir / TEXT("acceptance.json")));
    UE_LOG(LogTemp, Display, TEXT("CR_ACCEPT_FINISH %s"), *Receipt);
#if WITH_EDITOR
    // Let the Editor script end PIE before closing the editor/Slate world.
    if (GetWorld()->WorldType == EWorldType::PIE) return;
#endif
    FPlatformMisc::RequestExitWithStatus(false, bPassed ? 0 : 1);
}
#endif
