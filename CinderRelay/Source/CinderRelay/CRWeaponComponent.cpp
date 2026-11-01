#include "CRWeaponComponent.h"
#include "CRWeaponData.h"
#include "CRGameMode.h"
#include "CRCharacter.h"
#include "CRHealthComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Perception/AISense_Hearing.h"
#include "DrawDebugHelpers.h"
#include "TimerManager.h"
#include "Engine/World.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
UCRWeaponComponent::UCRWeaponComponent() { PrimaryComponentTick.bCanEverTick = false; }
void UCRWeaponComponent::BeginPlay()
{
    Super::BeginPlay();
    if (Data) { Magazine = FMath::Max(1,Data->MagazineCapacity); Reserve = FMath::Max(0,Data->InitialReserve); State = ECRWeaponState::Ready; }
    OnChanged.Broadcast();
}
void UCRWeaponComponent::EndPlay(const EEndPlayReason::Type Reason) { Disable(); Super::EndPlay(Reason); }
bool UCRWeaponComponent::CanUse() const
{
    const auto* Health = GetOwner()->FindComponentByClass<UCRHealthComponent>();
    return !bPresentationLocked && Data && State != ECRWeaponState::Disabled && GetWorld() && !GetWorld()->IsPaused() && (!Health || !Health->IsDead());
}
float UCRWeaponComponent::GetAimFOV() const
{
    const auto* G=GetWorld()?GetWorld()->GetAuthGameMode<ACRGameMode>():nullptr;
    return G && G->HasSurveyUpgrade()?60.f:Data?Data->AimFOV:65.f;
}
void UCRWeaponComponent::SetPresentationLocked(bool Locked)
{ bPresentationLocked=Locked; if(Locked) { bAiming=false; bSprinting=false; } OnChanged.Broadcast(); }
bool UCRWeaponComponent::RestoreCheckpointAmmo(int32 SavedMagazine, int32 SavedReserve)
{
    if (!Data || SavedMagazine < 0 || SavedMagazine > Data->MagazineCapacity || SavedReserve < 0 || SavedReserve > 100) return false;
    GetWorld()->GetTimerManager().ClearTimer(CycleTimer); GetWorld()->GetTimerManager().ClearTimer(ReloadTimer);
    Magazine = SavedMagazine; Reserve = SavedReserve; State = ECRWeaponState::Ready;
    NextShot = 0; LastDry = -1; bAiming = false; bSprinting = false; bPresentationLocked = false;
    OnChanged.Broadcast(); return true;
}
bool UCRWeaponComponent::TryFire()
{
    TRACE_CPUPROFILER_EVENT_SCOPE(CR_WeaponShot);
    auto* Player = Cast<ACRCharacter>(GetOwner());
    if (!CanUse() || !Player || bSprinting || State != ECRWeaponState::Ready || GetWorld()->GetTimeSeconds() < NextShot) return false;
    if (Magazine <= 0)
    {
        if (GetWorld()->GetTimeSeconds() - LastDry > .25) { LastDry = GetWorld()->GetTimeSeconds(); OnCue.Broadcast(TEXT("Dry")); }
        return false;
    }
    --Magazine; State = ECRWeaponState::Cycling;
    NextShot = GetWorld()->GetTimeSeconds() + FMath::Max(.1f,Data->ShotInterval);
    GetWorld()->GetTimerManager().SetTimer(CycleTimer,this,&UCRWeaponComponent::CompleteCycle,FMath::Max(.1f,Data->ShotInterval),false);
    const FVector Start = Player->Camera->GetComponentLocation(), Direction = Player->Camera->GetForwardVector();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CRWeaponShot), false, Player);
    FHitResult Hit; const FVector End = Start + Direction * Data->Range;
    const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params);
    // Camera chooses the reticle point; a separate short muzzle route guards adjacent cover.
    const FVector Muzzle = Start + Direction * 55 + Player->Camera->GetRightVector() * 12 - Player->Camera->GetUpVector()*10;
    FHitResult Cover;
    if (GetWorld()->LineTraceSingleByChannel(Cover, Start, Muzzle, ECC_Visibility, Params) ||
        GetWorld()->LineTraceSingleByChannel(Cover, Muzzle, bHit ? Hit.ImpactPoint : End, ECC_Visibility, Params)) Hit = Cover;
    bool bTarget = false;
    if (IsValid(Hit.GetActor()))
    {
        auto* Health = Hit.GetActor()->FindComponentByClass<UCRHealthComponent>();
        if (Health && !Health->IsDead())
        {
            const bool bHead = Hit.GetComponent() && Hit.GetComponent()->ComponentHasTag(TEXT("CR_Head"));
            const float Applied = UGameplayStatics::ApplyPointDamage(Hit.GetActor(), Data->BodyDamage * (bHead ? Data->HeadMultiplier : 1.f), Direction, Hit, Player->GetController(), Player, nullptr);
            bTarget = Applied > 0;
        }
    }
    const FVector Impact = Hit.bBlockingHit ? Hit.ImpactPoint : End;
    UAISense_Hearing::ReportNoiseEvent(this,Start,1.f,Player,2500,TEXT("RookShot"));
    UE_LOG(LogTemp,Display,TEXT("CR_SHOT ammo=%d reserve=%d target=%s hit=%d"),Magazine,Reserve,*GetNameSafe(Hit.GetActor()),bTarget);
    OnChanged.Broadcast(); OnShot.Broadcast(Impact,bTarget,Hit.bBlockingHit);
#if !UE_BUILD_SHIPPING
    if (bDebugTraces) DrawDebugLine(GetWorld(),Start,Impact,bTarget?FColor::Red:FColor::Cyan,false,1.f,0,1.f);
#endif
    return true;
}
void UCRWeaponComponent::CompleteCycle() { if (State == ECRWeaponState::Cycling) { State = ECRWeaponState::Ready; OnChanged.Broadcast(); } }
bool UCRWeaponComponent::TryReload()
{
    if (!CanUse() || State != ECRWeaponState::Ready || Magazine >= Data->MagazineCapacity || Reserve <= 0) return false;
    State = ECRWeaponState::Reloading; bAiming = false;
    GetWorld()->GetTimerManager().SetTimer(ReloadTimer,this,&UCRWeaponComponent::CompleteReload,FMath::Max(.1f,Data->ReloadDuration),false);
    OnChanged.Broadcast(); OnCue.Broadcast(TEXT("Reload")); return true;
}
void UCRWeaponComponent::CompleteReload()
{
    if (State != ECRWeaponState::Reloading || !Data) return;
    const int32 Transfer = FMath::Min(FMath::Max(0,Data->MagazineCapacity-Magazine),Reserve);
    Magazine += Transfer; Reserve -= Transfer; State = ECRWeaponState::Ready;
    OnChanged.Broadcast(); UE_LOG(LogTemp,Display,TEXT("CR_RELOAD ammo=%d reserve=%d"),Magazine,Reserve);
}
void UCRWeaponComponent::SetAiming(bool bAim) { bAiming = bAim && CanUse() && !bSprinting && State != ECRWeaponState::Reloading; OnChanged.Broadcast(); }
void UCRWeaponComponent::SetSprinting(bool bSprint) { bSprinting = bSprint; if (bSprint) bAiming = false; OnChanged.Broadcast(); }
void UCRWeaponComponent::Disable()
{
    if (GetWorld()) { GetWorld()->GetTimerManager().ClearTimer(CycleTimer); GetWorld()->GetTimerManager().ClearTimer(ReloadTimer); }
    State = ECRWeaponState::Disabled; bAiming = false; bSprinting = false; OnChanged.Broadcast();
}
int32 UCRWeaponComponent::AddReserve(int32 Amount)
{
    if (!CanUse() || Amount <= 0) return 0;
    const int32 Added = FMath::Min(Amount,FMath::Max(0,100-Reserve)); Reserve += Added; OnChanged.Broadcast(); return Added;
}
