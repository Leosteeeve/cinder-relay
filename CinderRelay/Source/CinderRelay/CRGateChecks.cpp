#include "CRCheckpointRoute.h"
#if !UE_BUILD_SHIPPING
#include "CRStreamingGate.h"
#include "CRChapterStreamingController.h"
#include "CRCharacter.h"
#include "CRPlayerController.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/LevelStreaming.h"
#include "EngineUtils.h"

// Opt-in fixture on fresh CR04_TEST_ slots. It never advances chapter authority directly.
void ACRCheckpointRoute::TickGateCheck()
{
    ACRStreamingGate* Gate=nullptr;
    for(TActorIterator<ACRStreamingGate> It(GetWorld());It;++It) if(It->LeftZone==0) { Gate=*It; break; }
    if(!Gate) { Finish(false,TEXT("Mechanical gate fixture missing AB")); return; }
    const double Now=FPlatformTime::Seconds(); const double Age=Now-GateCheckAt;
    auto* Level=Streaming->GetZoneLevel(1);
    auto Step=[this,Now](int32 Value) { GateCheckStep=Value;GateCheckAt=Now;UE_LOG(LogTemp,Display,TEXT("CR06_GATE_CHECK step=%d"),Value); };
    auto Press=[this,Gate]() { return Interact(Gate,Gate->ControlOutside->GetComponentLocation()); };
    auto Blocked=[Gate]() { return Gate->SafetyBarrier->GetCollisionEnabled()!=ECollisionEnabled::NoCollision; };
    auto Freeze=[this,Gate]() { GatePausedPose=Gate->Door->GetRelativeTransform();GatePausedWorldTime=GetWorld()->GetTimeSeconds(); };
    auto Frozen=[this,Gate]() { return Gate->Door->GetRelativeTransform().Equals(GatePausedPose,.001f) && FMath::IsNearlyEqual(GatePausedWorldTime,GetWorld()->GetTimeSeconds(),.001f); };
    switch(GateCheckStep)
    {
    case 0:
        if(Press())
        {
            Check(Streaming->IsZoneUnloaded(1) && Gate->IsSealed() && Blocked(),TEXT("Approach alone leaves native neighbor unloaded and boundary sealed"));
            if(bFinished)return;Streaming->SetAcceptanceHold(1,true);Step(1);
        } break;
    case 1:
        if(Age>.5 && Level && Level->IsLevelLoaded() && Level->IsLevelVisible())
        {
            Check(!Streaming->IsZoneReady(1) && Gate->IsSealed() && Blocked(),TEXT("Visible target cannot open real barrier while readiness veto is active"));
            if(!bFinished && Press()) Step(2);
        } break;
    case 2:
        if(Age>.45 && Streaming->IsZoneUnloaded(1))
        {
            Check(Gate->IsSealed() && Blocked(),TEXT("Cancel loading closes boundary before native neighbor is unloaded"));
            if(bFinished)return; Streaming->SetAcceptanceHold(1,false);Streaming->InjectAcceptanceFailure(1);
            if(Press()) Step(3);
        } break;
    case 3:
        if(Age>.4)
        {
            Check(!Streaming->IsZoneReady(1) && Gate->IsSealed() && Blocked(),TEXT("Injected load failure retains actual collidable boundary"));
            if(bFinished)return;PC->RetryStreaming();Step(4);
        } break;
    case 4:
        if(Streaming->IsZoneReady(1) && !Gate->IsSealed() && !Gate->bOpen)
        { Freeze();PC->TogglePrototypePause();Step(5); } break;
    case 5:
        if(Age>.4)
        {
            UE_LOG(LogTemp,Display,TEXT("CR06_GATE_PAUSE menu=%d paused=%d pose=%d world_delta=%.6f blocked=%d"),PC->bPrototypePaused,GetWorld()->IsPaused(),Gate->Door->GetRelativeTransform().Equals(GatePausedPose,.001f),GetWorld()->GetTimeSeconds()-GatePausedWorldTime,Blocked());
            Check(PC->bPrototypePaused && GetWorld()->IsPaused() && Frozen() && Blocked(),TEXT("Esc pause freezes real opening motion and keeps passage blocked"));
            PC->ResumePrototype();if(!bFinished)Step(6);
        } break;
    case 6:
        if(Gate->bOpen)
        {
            Check(Streaming->IsZoneReady(1) && !Blocked(),TEXT("Retry releases actual barrier only after native readiness and full opening"));
            if(!bFinished && Press())Step(7);
        } break;
    case 7:
        if(Age>.15 && !Gate->bOpen && !Gate->IsSealed())
        { Freeze();PC->ToggleFieldPack();Step(8); } break;
    case 8:
        if(Age>.4)
        {
            Check(PC->IsFieldPackOpen() && GetWorld()->IsPaused() && Frozen() && Blocked() && Level->IsLevelLoaded() && Level->IsLevelVisible(),TEXT("Field Pack freezes closing leaf while native geometry remains resident"));
            PC->ToggleFieldPack();if(!bFinished)Step(9);
        } break;
    case 9:
        Check(!PC->IsFieldPackOpen() && !GetWorld()->IsPaused() && !PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored() && !PC->bShowMouseCursor,TEXT("Closing Field Pack restores game input and cursor ownership"));
        Check(Level->IsLevelLoaded() && Level->IsLevelVisible(),TEXT("Unsealed closing boundary retains both native levels"));
        if(!bFinished && Press())Step(10);break;
    case 10:
        if(Gate->bOpen)
        {
            Check(!Blocked() && Streaming->IsZoneReady(1),TEXT("Reversing closing motion safely reopens resident boundary"));
            if(bFinished)return;Step(11);Walk({{1600,0}},TEXT("gate_occupied"));
        }break;
    case 11:
        if(Gate->IsInThreshold() && Press())Step(12);break;
    case 12:
        if(Age>.1)
        {
            Check(Gate->IsInThreshold() && Gate->bOpen && !Blocked() && Level->IsLevelVisible(),TEXT("Actual E close is rejected while player capsule occupies doorway"));
            if(bFinished)return;Step(13);Walk({{2050,0}},TEXT("wait_cp01"));
        }break;
    default:Finish(false,TEXT("Unexpected mechanical gate fixture state"));break;
    }
}
#endif
