#include "CRWeaponViewComponent.h"
#include "CRWeaponComponent.h"
#include "CRWeaponData.h"
#include "CRHealthComponent.h"
#include "CRCharacter.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
UCRWeaponViewComponent::UCRWeaponViewComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Mesh(TEXT("/Engine/BasicShapes/Cube.Cube")); Cube = Mesh.Object;
}
void UCRWeaponViewComponent::BeginPlay()
{
    Super::BeginPlay(); auto* Player = Cast<ACRCharacter>(GetOwner());
    Weapon = GetOwner()->FindComponentByClass<UCRWeaponComponent>();
    if (!Player || !Weapon.IsValid() || !Weapon->Data) { SetComponentTickEnabled(false); return; }
    BaseFOV = Player->Camera->FieldOfView;
    ViewRoot = NewObject<USceneComponent>(Player,TEXT("RookViewRoot")); Player->AddInstanceComponent(ViewRoot);
    ViewRoot->SetupAttachment(Player->Camera); ViewRoot->RegisterComponent(); ViewRoot->SetRelativeLocation(Weapon->Data->HipLocation);
    auto Part = [this,Player](const TCHAR* Name,FVector Position,FVector Scale,bool Accent)
    {
        auto* P = NewObject<UStaticMeshComponent>(Player,FName(Name)); Player->AddInstanceComponent(P);
        P->SetupAttachment(ViewRoot); P->SetStaticMesh(Cube); P->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        P->SetCastShadow(false); P->SetCanEverAffectNavigation(false); P->SetOnlyOwnerSee(true);
        P->SetRelativeLocation(Position); P->SetRelativeScale3D(Scale/100.f);
        P->SetMaterial(0,Accent?Weapon->Data->AccentMaterial:Weapon->Data->MetalMaterial); P->RegisterComponent(); return P;
    };
    // Intentional abstract greybox: these pieces are silhouettes, not mechanical assembly instructions.
    Part(TEXT("RookBody"),FVector(0,0,0),FVector(30,6,10),false);
    Part(TEXT("RookShroud"),FVector(28,0,2),FVector(28,4,4),false);
    Part(TEXT("RookGrip"),FVector(-8,0,-8),FVector(8,5,10),true);
    Part(TEXT("RookStock"),FVector(-22,0,-2),FVector(18,5,8),true);
    Part(TEXT("RookFeed"),FVector(6,0,-8),FVector(7,5,10),true);
    Part(TEXT("RookSightLeft"),FVector(-4,-2.5,9),FVector(3,1,4),true);
    Part(TEXT("RookSightRight"),FVector(-4,2.5,9),FVector(3,1,4),true);
    Part(TEXT("RookSightFront"),FVector(34,0,10),FVector(1.5,1,2),true);
    Flash=Part(TEXT("RookFlash"),FVector(44,0,2),FVector(10,5,5),true); Flash->SetVisibility(false);
    ImpactMarker=Part(TEXT("RookImpact"),FVector::ZeroVector,FVector(3,3,3),true);
    ImpactMarker->DetachFromComponent(FDetachmentTransformRules::KeepWorldTransform); ImpactMarker->SetVisibility(false);
    Weapon->OnShot.AddDynamic(this,&UCRWeaponViewComponent::Shot); Weapon->OnCue.AddDynamic(this,&UCRWeaponViewComponent::Cue);
    if (auto* Health=Player->FindComponentByClass<UCRHealthComponent>()) Health->OnHealthChanged.AddDynamic(this,&UCRWeaponViewComponent::Hurt);
}
void UCRWeaponViewComponent::TickComponent(float Delta,ELevelTick TickType,FActorComponentTickFunction* ThisTick)
{
    TRACE_CPUPROFILER_EVENT_SCOPE(CR_WeaponPresentation);
    Super::TickComponent(Delta,TickType,ThisTick);
    auto* P=Cast<ACRCharacter>(GetOwner()); if (!P || !Weapon.IsValid() || !Weapon->Data || !ViewRoot) return;
    const auto* D=Weapon->Data.Get();
    CoverCountdown-=Delta;
    if (CoverCountdown<=0)
    {
        CoverCountdown=.1f; FHitResult Hit; FCollisionQueryParams Params(SCENE_QUERY_STAT(CRViewCover),false,P);
        CoverFraction=GetWorld()->LineTraceSingleByChannel(Hit,P->Camera->GetComponentLocation(),P->Camera->GetComponentLocation()+P->Camera->GetForwardVector()*95,ECC_Visibility,Params)?1.f:0.f;
    }
    const bool Aim=Weapon->bAiming && Weapon->CanUse();
    P->Camera->SetFieldOfView(FMath::FInterpTo(P->Camera->FieldOfView,Aim?D->AimFOV:BaseFOV,Delta,3.f/FMath::Max(.01f,D->AimSeconds)));
    Recoil=FMath::FInterpTo(Recoil,0,Delta,FMath::Max(1.f,D->RecoverySpeed));
    const bool Lower=Weapon->State==ECRWeaponState::Reloading || Weapon->bSprinting || Weapon->State==ECRWeaponState::Disabled;
    FVector Target=Aim?D->AimLocation:D->HipLocation; Target.Z-=Lower?9.f:CoverFraction*14.f; Target.X-=Recoil;
    ViewRoot->SetRelativeLocation(FMath::VInterpTo(ViewRoot->GetRelativeLocation(),Target,Delta,18));
    ViewRoot->SetRelativeRotation(FMath::RInterpTo(ViewRoot->GetRelativeRotation(),FRotator(Recoil-(Lower?25:CoverFraction*35),0,Lower?-10:0),Delta,18));
}
void UCRWeaponViewComponent::Shot(FVector Impact,bool Hit,bool BlockingHit)
{
    if (!Weapon.IsValid() || !Weapon->Data) return;
    Recoil=Weapon->Data->RecoilDegrees; Flash->SetVisibility(true);
    GetWorld()->GetTimerManager().SetTimer(FlashTimer,this,&UCRWeaponViewComponent::HideFlash,.055f,false);
    ImpactMarker->SetWorldLocation(Impact); ImpactMarker->SetVisibility(BlockingHit);
    if(BlockingHit) GetWorld()->GetTimerManager().SetTimer(ImpactTimer,this,&UCRWeaponViewComponent::HideImpact,.18f,false);
    UGameplayStatics::PlaySound2D(this,Weapon->Data->ShotSound,.45f);
    if(BlockingHit) UGameplayStatics::PlaySound2D(this,Hit?Weapon->Data->HitSound:Weapon->Data->ImpactSound,.3f);
}
void UCRWeaponViewComponent::Cue(FName Name)
{
    if (Weapon.IsValid() && Weapon->Data) UGameplayStatics::PlaySound2D(this,Name==TEXT("Reload")?Weapon->Data->ReloadSound:Weapon->Data->DrySound,.35f);
}
void UCRWeaponViewComponent::Hurt(float,float Damage)
{
    if (Damage>0 && Weapon.IsValid() && Weapon->Data) UGameplayStatics::PlaySound2D(this,Weapon->Data->HurtSound,.4f);
}
void UCRWeaponViewComponent::HideFlash() { if (Flash) Flash->SetVisibility(false); }
void UCRWeaponViewComponent::HideImpact() { if (ImpactMarker) ImpactMarker->SetVisibility(false); }
void UCRWeaponViewComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    if (GetWorld()) { GetWorld()->GetTimerManager().ClearTimer(FlashTimer); GetWorld()->GetTimerManager().ClearTimer(ImpactTimer); }
    if (Weapon.IsValid()) { Weapon->OnShot.RemoveDynamic(this,&UCRWeaponViewComponent::Shot); Weapon->OnCue.RemoveDynamic(this,&UCRWeaponViewComponent::Cue); }
    if (auto* Health=GetOwner()->FindComponentByClass<UCRHealthComponent>()) Health->OnHealthChanged.RemoveDynamic(this,&UCRWeaponViewComponent::Hurt);
    Super::EndPlay(Reason);
}
