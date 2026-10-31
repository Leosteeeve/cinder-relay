#include "CRChapterStreamingController.h"
#include "CRStreamingGate.h"
#include "CRGameMode.h"
#include "CRPlayerController.h"
#include "CRInteractionActor.h"
#include "Components/PrimitiveComponent.h"
#include "Engine/Level.h"
#include "Engine/LevelStreaming.h"
#include "Engine/LevelStreamingDynamic.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "ProfilingDebugging/MiscTrace.h"
#include "TimerManager.h"

ACRChapterStreamingController::ACRChapterStreamingController()
{
    PrimaryActorTick.bCanEverTick = false;
    for (const TCHAR* Name : {TEXT("RailYard"), TEXT("Workshop"), TEXT("RelayBunker")})
    {
        const FString Path = FString::Printf(TEXT("/Game/Generated/Phase01B/Maps/L_CH01_%s.L_CH01_%s"), Name, Name);
        ZoneMaps.Add(TSoftObjectPtr<UWorld>(FSoftObjectPath(Path)));
    }
}
void ACRChapterStreamingController::BeginPlay()
{
    Super::BeginPlay();
    for (TActorIterator<ACRStreamingGate> It(GetWorld()); It; ++It)
    {
        Gates.Add(*It); It->SetChapterController(this); It->SetOpen(false);
    }
    for (int32 I = 0; I < 3; ++I)
    {
        if (ZoneMaps.IsValidIndex(I)) Zones[I].Level = UGameplayStatics::GetStreamingLevel(this, FName(*ZoneMaps[I].ToSoftObjectPath().GetLongPackageName()));
        if (auto* Level = Zones[I].Level.Get())
        {
            Level->bShouldBlockOnLoad = false; Level->bShouldBlockOnUnload = false;
            Level->OnLevelLoaded.AddDynamic(this, &ACRChapterStreamingController::Reconcile);
            Level->OnLevelShown.AddDynamic(this, &ACRChapterStreamingController::Reconcile);
            Level->OnLevelHidden.AddDynamic(this, &ACRChapterStreamingController::Reconcile);
            Level->OnLevelUnloaded.AddDynamic(this, &ACRChapterStreamingController::Reconcile);
            if (!Level->IsA<ULevelStreamingDynamic>()) Zones[I].bFailed = true;
        }
        else Zones[I].bFailed = true;
    }
    bInitialized = true;
    GetWorldTimerManager().SetTimer(Watchdog, this, &ACRChapterStreamingController::Reconcile, 0.25f, true);
    Reconcile();
}
void ACRChapterStreamingController::EndPlay(const EEndPlayReason::Type Reason)
{
    bStopping = true;
    GetWorldTimerManager().ClearTimer(Watchdog);
    for (FZone& Zone : Zones) if (auto* L = Zone.Level.Get())
    {
        L->OnLevelLoaded.RemoveDynamic(this, &ACRChapterStreamingController::Reconcile);
        L->OnLevelShown.RemoveDynamic(this, &ACRChapterStreamingController::Reconcile);
        L->OnLevelHidden.RemoveDynamic(this, &ACRChapterStreamingController::Reconcile);
        L->OnLevelUnloaded.RemoveDynamic(this, &ACRChapterStreamingController::Reconcile);
    }
    Super::EndPlay(Reason);
}
bool ACRChapterStreamingController::IsZoneReady(int32 I) const
{
    const auto* L = GetZoneLevel(I);
    return I >= 0 && I < 3 && Zones[I].State == ECRZoneState::Ready && !Zones[I].bFailed && L && L->IsLevelLoaded() && L->IsLevelVisible();
}
ULevelStreaming* ACRChapterStreamingController::GetZoneLevel(int32 I) const { return I >= 0 && I < 3 ? Zones[I].Level.Get() : nullptr; }
bool ACRChapterStreamingController::IsZoneUnloaded(int32 I) const
{
    const auto* L = GetZoneLevel(I);
    return L && !L->IsLevelLoaded() && !L->IsLevelVisible() && !L->ShouldBeLoaded() && L->GetLevelStreamingState() == ELevelStreamingState::Unloaded;
}
bool ACRChapterStreamingController::AreGatesClosedFor(int32 I) const
{
    for (const auto& Gate : Gates) if (Gate.IsValid() && (Gate->LeftZone == I || Gate->LeftZone + 1 == I) && Gate->bOpen) return false;
    return Gates.Num() == 2;
}
void ACRChapterStreamingController::LogZone(int32 I, const TCHAR* Event) const
{
    const auto* L = Zones[I].Level.Get();
    UE_LOG(LogTemp, Display, TEXT("CR_STREAM %c %s t=%.3f request=%u state=%d loaded=%d visible=%d wanted=%d player=%c witness_valid=%d"),
        TCHAR('A' + I), Event, GetWorld()->GetTimeSeconds(), Zones[I].Request, int32(Zones[I].State), L && L->IsLevelLoaded(), L && L->IsLevelVisible(), Zones[I].bWanted, TCHAR('A' + CurrentZone), Zones[I].FloorWitness.IsValid());
    TRACE_BOOKMARK(TEXT("CR_STREAM %c %s request=%u"), TCHAR('A' + I), Event, Zones[I].Request);
}
void ACRChapterStreamingController::SetState(int32 I, ECRZoneState State)
{
    if (Zones[I].State == State) return;
    Zones[I].State = State;
    static const TCHAR* Names[] = {TEXT("Unloaded"), TEXT("Loading"), TEXT("LoadedOrShowing"), TEXT("Ready"), TEXT("Unloading"), TEXT("Failed")};
    LogZone(I, Names[int32(State)]);
}
bool ACRChapterStreamingController::ValidatePrerequisites(int32 I)
{
    ULevelStreaming* Streaming = GetZoneLevel(I);
    ULevel* Level = Streaming ? Streaming->GetLoadedLevel() : nullptr;
    if (!Level || !Streaming->IsLevelVisible()) return false;
    static const FVector FloorPoints[] = {FVector(-1450,0,0), FVector(2600,0,0), FVector(5900,0,-600)};
    FHitResult Hit;
    const FVector P = FloorPoints[I];
    if (!GetWorld()->LineTraceSingleByChannel(Hit, P + FVector(0,0,70), P - FVector(0,0,120), ECC_Visibility)) return false;
    if (!Hit.GetActor() || Hit.GetActor()->GetLevel() != Level || !Hit.GetComponent() || !Hit.GetComponent()->IsRegistered() || !Hit.GetComponent()->IsPhysicsStateCreated()) return false;
    bool bModule = false, bRelay = false, bSignal = false, bEntry = false, bRamp = false;
    for (AActor* Actor : Level->Actors)
    {
        if (!IsValid(Actor) || !Actor->HasActorBegunPlay()) continue;
        bEntry |= Actor->ActorHasTag(TEXT("CR_Ready_WorkshopEntry"));
        bRamp |= Actor->ActorHasTag(TEXT("CR_Ready_AccessRamp"));
        if (auto* Item = Cast<ACRInteractionActor>(Actor))
        {
            bModule |= Item->Kind == ECRInteractionKind::PowerModule;
            bRelay |= Item->Kind == ECRInteractionKind::Relay;
            bSignal |= Item->Kind == ECRInteractionKind::Signal;
        }
    }
    if ((I == 1 && (!bModule || !bEntry)) || (I == 2 && (!bRelay || !bSignal || !bRamp))) return false;
    Zones[I].FloorWitness = Hit.GetActor(); // Weak evidence only, never retains a streamed actor.
    return true;
}
void ACRChapterStreamingController::Reconcile()
{
    if (!bInitialized || bStopping || bReconciling) return;
    TGuardValue<bool> Guard(bReconciling, true);
    const double Now = GetWorld()->GetTimeSeconds();
    if (const APawn* Pawn = UGameplayStatics::GetPlayerPawn(this, 0))
    {
        const float X = Pawn->GetActorLocation().X;
        if (CurrentZone == 0 && X > 1760) CurrentZone = 1;
        if (CurrentZone == 1 && X < 1440) CurrentZone = 0;
        if (CurrentZone == 1 && X > 3760) CurrentZone = 2;
        if (CurrentZone == 2 && X < 3440) CurrentZone = 1;
    }
    bool Wanted[3] = {false, false, false}; Wanted[CurrentZone] = true;
    for (const auto& Gate : Gates) if (Gate.IsValid() && (Gate->IsNear() || Gate->IsInThreshold()) && Gate->LeftZone >= 0 && Gate->LeftZone < 2)
        Wanted[Gate->LeftZone] = Wanted[Gate->LeftZone + 1] = true;
    // Close the opaque boundary BEFORE removing old geometry. Latest demand wins over stale events.
    for (const auto& Gate : Gates) if (Gate.IsValid() && Gate->LeftZone >= 0 && Gate->LeftZone < 2)
        if (!Wanted[Gate->LeftZone] || !Wanted[Gate->LeftZone + 1]) Gate->SetOpen(false);
    for (int32 I = 0; I < 3; ++I)
    {
        FZone& Z = Zones[I]; auto* L = Z.Level.Get();
        if (Z.bWanted != Wanted[I])
        {
            Z.bWanted = Wanted[I]; ++Z.Request; Z.RequestedAt = Now;
            LogZone(I, Z.bWanted ? TEXT("LoadRequested") : TEXT("UnloadRequested"));
        }
        if (!L) { Z.bFailed = true; SetState(I, ECRZoneState::Failed); continue; }
        if (L->GetLevelStreamingState() == ELevelStreamingState::FailedToLoad) Z.bFailed = true;
        if (Z.bWanted && Z.State != ECRZoneState::Ready && Now - Z.RequestedAt > LoadTimeoutSeconds) Z.bFailed = true;
        // These engine-owned desired flags coalesce reversals. No duplicate latent actions exist.
        L->SetShouldBeVisible(Z.bWanted);
        L->SetShouldBeLoaded(Z.bWanted);
        if (Z.bFailed) { SetState(I, ECRZoneState::Failed); continue; }
        if (!Z.bWanted)
        {
            SetState(I, IsZoneUnloaded(I) ? ECRZoneState::Unloaded : ECRZoneState::Unloading);
            continue;
        }
        bool bHeld = false;
#if !UE_BUILD_SHIPPING
        bHeld = AcceptanceHold == I && Now < HoldExpires;
        if (AcceptanceHold == I && Now >= HoldExpires) AcceptanceHold = INDEX_NONE;
#endif
        if (!L->IsLevelLoaded()) SetState(I, ECRZoneState::Loading);
        else if (!L->IsLevelVisible() || bHeld) SetState(I, ECRZoneState::LoadedOrShowing);
        else if (Z.State == ECRZoneState::Ready || ValidatePrerequisites(I)) SetState(I, ECRZoneState::Ready);
        else SetState(I, ECRZoneState::LoadedOrShowing);
    }
    for (const auto& Gate : Gates) if (Gate.IsValid() && Gate->LeftZone >= 0 && Gate->LeftZone < 2)
        Gate->SetOpen(Wanted[Gate->LeftZone] && Wanted[Gate->LeftZone + 1] && IsZoneReady(Gate->LeftZone) && IsZoneReady(Gate->LeftZone + 1));
    if (!bPlayerReleased && IsZoneReady(0))
    {
        bPlayerReleased = true;
        if (auto* GM = GetWorld()->GetAuthGameMode<ACRGameMode>()) GM->ReleaseStartingPlayer();
    }
    bool bWaiting = false, bFailed = false;
    for (int32 I = 0; I < 3; ++I) { bWaiting |= Wanted[I] && !IsZoneReady(I); bFailed |= Wanted[I] && Zones[I].bFailed; }
    if (auto* PC = Cast<ACRPlayerController>(UGameplayStatics::GetPlayerController(this, 0)))
        PC->SetStreamingStatus(bFailed ? NSLOCTEXT("Cinder", "StreamRetry", "Access unavailable. Press R to retry.") : bWaiting ? NSLOCTEXT("Cinder", "StreamWait", "Preparing access...") : FText::GetEmpty());
}
void ACRChapterStreamingController::RetryFailedLoads()
{
    for (int32 I = 0; I < 3; ++I) if (Zones[I].bFailed)
    {
        auto* L = GetZoneLevel(I);
        if (!L || !L->IsA<ULevelStreamingDynamic>()) { LogZone(I, TEXT("RetryMissingRegistration")); continue; }
        if (L->GetLevelStreamingState() == ELevelStreamingState::FailedToLoad && !L->GetLoadedLevel())
        {
            // UE 5.8.4 SetWorldAsset resets FailedToLoad on asset change. Preserve the same engine object.
            const TSoftObjectPtr<UWorld> Asset = L->GetWorldAsset();
            L->SetWorldAsset(TSoftObjectPtr<UWorld>()); L->SetWorldAsset(Asset);
        }
        Zones[I].bFailed = false; Zones[I].RequestedAt = GetWorld()->GetTimeSeconds(); ++Zones[I].Request;
        LogZone(I, TEXT("Retry"));
    }
    Reconcile();
}
#if !UE_BUILD_SHIPPING
void ACRChapterStreamingController::SetAcceptanceHold(int32 I, bool bHold)
{
    AcceptanceHold = bHold ? I : INDEX_NONE;
    HoldExpires = GetWorld()->GetTimeSeconds() + 20; // Bounded test veto; production never sets it.
    Reconcile();
}
void ACRChapterStreamingController::InjectAcceptanceFailure(int32 I)
{
    if (I >= 0 && I < 3) { Zones[I].bFailed = true; LogZone(I, TEXT("InjectedFailure")); Reconcile(); }
}
#endif
