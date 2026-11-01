#include "CRCombatAcceptance.h"
#if !UE_BUILD_SHIPPING
#include "CRCharacter.h"
#include "CRPlayerController.h"
#include "CRWeaponComponent.h"
#include "CRWeaponData.h"
#include "CRWeaponViewComponent.h"
#include "CRHealthComponent.h"
#include "CRGameMode.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
namespace { bool VerifyWeaponRestart=false; }
#endif
ACRCombatAcceptance::ACRCombatAcceptance()
{
#if !UE_BUILD_SHIPPING
    PrimaryActorTick.bCanEverTick=true; PrimaryActorTick.bTickEvenWhenPaused=true;
#endif
}
void ACRCombatAcceptance::BeginPlay()
{
    Super::BeginPlay();
#if !UE_BUILD_SHIPPING
    Started=StageStarted=FPlatformTime::Seconds();
#endif
}
void ACRCombatAcceptance::Tick(float Delta)
{
    Super::Tick(Delta);
#if !UE_BUILD_SHIPPING
    if (bFinished) return;
    const double Age=FPlatformTime::Seconds()-StageStarted;
    if (FPlatformTime::Seconds()-Started>75) { Finish(false,TEXT("Weapon check timeout: ")+Stage); return; }
    if(Stage==TEXT("startup"))
    {
        Player=Cast<ACRCharacter>(UGameplayStatics::GetPlayerPawn(this,0)); if(!Player.IsValid()) return;
        PC=Cast<ACRPlayerController>(Player->GetController());
        if(!Player->WeaponView->HasAnimatedHands()) return;
        Check(Player->Weapon->Data && Player->Weapon->Magazine==5 && Player->Weapon->Reserve==25 && Player->Health->Health==100,TEXT("Initial ROOK-5 data/ammo/health")); if(bFinished)return;
        if(VerifyWeaponRestart) { Check(!PC->bPrototypeDefeated && GetWorld()->GetAuthGameMode<ACRGameMode>()->GetObjective()==ECRObjective::ReachWorkshop,TEXT("Restart resets defeat/ammo/objective")); if(!bFinished)Finish(true,TEXT("Weapon state, damage, cover, pause/death/restart checks passed")); return; }
        PC->SetControlRotation(FRotator::ZeroRotator);
        Target=TestBlock(Player->Camera->GetComponentLocation()+FVector(180,0,0),FVector(25,70,70),true);
        TargetHealth=Target->FindComponentByClass<UCRHealthComponent>(); Next(TEXT("first")); return;
    }
    if(!Player.IsValid()||!PC.IsValid()) { Finish(false,TEXT("Lost player")); return; }
    auto* W=Player->Weapon.Get();
    if(Stage==TEXT("first") && Age>.2)
    {
        Check(W->TryFire(),TEXT("One accepted shot")); Check(W->Magazine==4 && TargetHealth->Health==60,TEXT("One ammo and one body damage event"));
        for(int I=0;I<8;++I) Check(!W->TryFire(),TEXT("Spam rejected by cycling/cooldown"));
        Check(W->Magazine==4 && TargetHealth->Health==60,TEXT("No duplicate damage/ammo consumption")); Next(TEXT("miss"));
    }
    else if(Stage==TEXT("miss") && Age>.2)
    {
        PC->SetControlRotation(FRotator(70,0,0)); Next(TEXT("miss_fire"));
    }
    else if(Stage==TEXT("miss_fire")&&Age>1)
    {
        Check(Player->WeaponView->GetEjectedCases()==1,TEXT("Accepted shot has exactly one native notify case; rejected spam has none"));
        Check(W->TryFire()&&W->Magazine==3&&TargetHealth->Health==60,TEXT("Miss consumes ammunition"));
        Wall=TestBlock(Player->Camera->GetComponentLocation()+FVector(90,0,0),FVector(20,150,150),false); PC->SetControlRotation(FRotator::ZeroRotator); Next(TEXT("cover"));
    }
    else if(Stage==TEXT("cover")&&Age>1)
    {
        Check(Player->WeaponView->GetEjectedCases()==2,TEXT("Second montage instance emits its own case exactly once"));
        Check(W->TryFire()&&W->Magazine==2&&TargetHealth->Health==60,TEXT("Real solid cover blocks damage"));
        Wall->Destroy(); Target->Destroy(); Next(TEXT("partial_reload"));
    }
    else if(Stage==TEXT("partial_reload")&&Age>1)
    {
        Check(Player->WeaponView->GetEjectedCases()==3,TEXT("Cover shot still has one cosmetic case"));
        Check(W->TryReload()&&!W->TryFire()&&!W->TryReload(),TEXT("Partial reload rejects fire and duplicate reload"));
        W->SetSprinting(true); Check(W->State==ECRWeaponState::Reloading&&!W->bAiming,TEXT("Sprint leaves reload valid, disables ADS"));
        PausedActionPosition=Player->WeaponView->GetHandlingActionPosition();PC->TogglePrototypePause(); Next(TEXT("paused"));
    }
    else if(Stage==TEXT("paused")&&Age>.6)
    {
        Check(W->Magazine==2&&W->Reserve==25&&W->State==ECRWeaponState::Reloading,TEXT("Pause freezes reload transfer"));
        Check(FMath::Abs(Player->WeaponView->GetHandlingActionPosition()-PausedActionPosition)<.01f,TEXT("Pause freezes the native handling montage"));
        PC->TogglePrototypePause(); Next(TEXT("reload_finish"));
    }
    else if(Stage==TEXT("reload_finish")&&Age>2.6)
    {
        Check(W->Magazine==5&&W->Reserve==22&&W->State==ECRWeaponState::Ready&&!W->TryReload(),TEXT("Partial reload conserves total, full-mag reload rejected"));
        Check(Player->WeaponView->GetEjectedCases()==3,TEXT("Reload and idle do not eject spent cases"));
        W->SetAiming(true); Next(TEXT("ads"));
    }
    else if(Stage==TEXT("ads")&&Age>.5)
    {
        Check(FMath::Abs(Player->Camera->FieldOfView-65)<1,TEXT("ADS reaches configured FOV")); W->SetAiming(false); PC->SetControlRotation(FRotator(70,0,0)); Next(TEXT("empty_mag"));
    }
    else if(Stage==TEXT("empty_mag")&&Age>1)
    {
        Check(W->TryFire(),TEXT("Accepted paced shot")); ++TestShots;
        if(TestShots<5) Next(TEXT("empty_mag")); else Next(TEXT("empty_reload"));
    }
    else if(Stage==TEXT("empty_reload")&&Age>1)
    {
        Check(Player->WeaponView->GetEjectedCases()==8,TEXT("Five paced shots add five cases, not one per animation tick"));
        Check(W->Magazine==0&&!W->TryFire()&&W->Magazine==0,TEXT("Empty fire never produces negative ammo"));
        Check(FMath::Abs(Player->Camera->FieldOfView-85)<1,TEXT("ADS reverses to original FOV"));
        Check(W->TryReload(),TEXT("Empty-mag reload accepted")); Next(TEXT("reserve_case"));
    }
    else if(Stage==TEXT("reserve_case")&&Age>2.6)
    {
        Check(W->Magazine==5&&W->Reserve==17,TEXT("Empty reload transfers exactly five"));
        Check(Player->WeaponView->GetEjectedCases()==8,TEXT("Dry fire and empty reload produce no spent case"));
        // Explicit isolated edge-case fixture, not the integrated gameplay route.
        Player->WeaponView->SuppressNextCaseForTest();
        W->Reserve=0; Check(W->TryFire(),TEXT("Zero reserve does not discard a chambered shot")); Next(TEXT("zero_reload"));
    }
    else if(Stage==TEXT("zero_reload")&&Age>1)
    {
        Check(W->State==ECRWeaponState::Ready&&Player->WeaponView->GetAcceptedPresentationShots()==9&&Player->WeaponView->GetEjectedCases()==8,TEXT("Deliberately missing cosmetic case cannot block Ready or duplicate ammunition"));
        Check(!W->TryReload()&&W->Magazine==4&&W->Reserve==0,TEXT("Zero-reserve reload rejected"));
        Check(W->AddReserve(2)==2&&W->TryReload(),TEXT("Limited reserve pickup allows reload"));
        UGameplayStatics::ApplyDamage(Player.Get(),100,PC.Get(),this,nullptr); Next(TEXT("dead"));
    }
    else if(Stage==TEXT("dead")&&Age>.5)
    {
        Check(Player->Health->IsDead()&&PC->bPrototypeDefeated&&W->State==ECRWeaponState::Disabled&&W->Magazine==4&&W->Reserve==2,TEXT("Death cancels reload without transfer and presents restart"));
        UGameplayStatics::ApplyDamage(Player.Get(),40,PC.Get(),this,nullptr); Check(Player->Health->Health==0&&!W->TryFire(),TEXT("Dead player cannot fire or take more damage"));
        if(bFinished)return; VerifyWeaponRestart=true; bFinished=true; PC->RestartPrototype();
    }
#endif
}
#if !UE_BUILD_SHIPPING
AActor* ACRCombatAcceptance::TestBlock(FVector Position,FVector Size,bool Damageable)
{
    auto* A=GetWorld()->SpawnActor<AActor>();
    auto* Mesh=NewObject<UStaticMeshComponent>(A); A->AddInstanceComponent(Mesh); A->SetRootComponent(Mesh);
    Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube"))); Mesh->SetCollisionProfileName(TEXT("BlockAll")); Mesh->SetCanEverAffectNavigation(false); Mesh->RegisterComponent(); A->SetActorLocation(Position); A->SetActorScale3D(Size/100);
    if(Damageable) { auto* H=NewObject<UCRHealthComponent>(A); A->AddInstanceComponent(H); H->RegisterComponent(); }
    return A;
}
void ACRCombatAcceptance::Next(const FString& Name) { if(bFinished)return; Stage=Name; StageStarted=FPlatformTime::Seconds(); UE_LOG(LogTemp,Display,TEXT("CR02_CHECK stage=%s"),*Stage); }
void ACRCombatAcceptance::Check(bool Condition,const TCHAR* Message)
{
    if(bFinished)return;
    if(!Condition) { Finish(false,Message); return; }
    Events+=FString::Printf(TEXT("PASS %s\n"),Message); UE_LOG(LogTemp,Display,TEXT("CR02_CHECK PASS %s"),Message);
}
void ACRCombatAcceptance::Finish(bool Passed,const FString& Message)
{
    if(bFinished)return; bFinished=true;
    const FString Dir=FPaths::ProjectSavedDir()/TEXT("Phase02"); IFileManager::Get().MakeDirectory(*Dir,true);
    const FString Receipt=FString::Printf(TEXT("{\"passed\":%s,\"mode\":\"weapon\",\"message\":\"%s\"}"),Passed?TEXT("true"):TEXT("false"),*Message);
    FFileHelper::SaveStringToFile(Receipt,*(Dir/TEXT("acceptance.json"))); FFileHelper::SaveStringToFile(Events,*(Dir/TEXT("checks.txt")));
    UE_LOG(LogTemp,Display,TEXT("CR02_FINISH %s"),*Receipt);
#if WITH_EDITOR
    if(GetWorld()->WorldType==EWorldType::PIE)return;
#endif
    FPlatformMisc::RequestExitWithStatus(false,Passed?0:1);
}
#endif
