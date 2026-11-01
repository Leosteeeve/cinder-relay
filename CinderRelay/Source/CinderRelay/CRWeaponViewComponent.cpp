#include "CRWeaponViewComponent.h"
#include "CRWeaponComponent.h"
#include "CRWeaponData.h"
#include "CRHealthComponent.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshSocket.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
UCRWeaponViewComponent::UCRWeaponViewComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    RookAppearance=TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Generated/Phase051/Meshes/SM_CR051_Rook5.SM_CR051_Rook5")));
    SurveyAppearance=TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("/Game/Generated/Phase051/Meshes/SM_CR051_SurveyOptic.SM_CR051_SurveyOptic")));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Mesh(TEXT("/Engine/BasicShapes/Cube.Cube")); Cube = Mesh.Object;
}
FTransform UCRWeaponViewComponent::SolveSightRoot(const FTransform& SightLocal,float EyeRelief)
{
    return SightLocal.Inverse()*FTransform(FVector(EyeRelief,0,0));
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
        P->SetMaterial(0,Accent?Weapon->Data->AccentMaterial:Weapon->Data->MetalMaterial); P->RegisterComponent(); FallbackParts.Add(P); return P;
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
    FallbackParts.Remove(Flash); FallbackParts.Remove(ImpactMarker);
    auto Imported=[this,Player](const TCHAR* Name)
    {
        auto* P=NewObject<UStaticMeshComponent>(Player,FName(Name)); Player->AddInstanceComponent(P);
        P->SetupAttachment(ViewRoot); P->SetCollisionEnabled(ECollisionEnabled::NoCollision); P->SetCastShadow(false);
        P->SetOnlyOwnerSee(true); P->SetCanEverAffectNavigation(false); P->RegisterComponent(); return P;
    };
    ImportedRook=Imported(TEXT("RookImported")); ImportedOptic=Imported(TEXT("SurveyOpticImported"));
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>()) G->OnRestorationChanged.AddDynamic(this,&UCRWeaponViewComponent::RefreshAppearance);
    AppearanceLoad=UAssetManager::GetStreamableManager().RequestAsyncLoad({RookAppearance.ToSoftObjectPath(),SurveyAppearance.ToSoftObjectPath()},FStreamableDelegate::CreateUObject(this,&UCRWeaponViewComponent::RefreshAppearance));
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
    P->Camera->SetFieldOfView(FMath::FInterpTo(P->Camera->FieldOfView,Aim?Weapon->GetAimFOV():BaseFOV,Delta,3.f/FMath::Max(.01f,D->AimSeconds)));
    Recoil=FMath::FInterpTo(Recoil,0,Delta,FMath::Max(1.f,D->RecoverySpeed));
    const bool Lower=Weapon->State==ECRWeaponState::Reloading || Weapon->bSprinting || Weapon->State==ECRWeaponState::Disabled;
    SmoothCover=FMath::FInterpTo(SmoothCover,CoverFraction,Delta,9);
    ReloadPose=FMath::FInterpTo(ReloadPose,Weapon->State==ECRWeaponState::Reloading?1.f:0.f,Delta,6);
    const float Speed=FMath::Clamp(P->GetVelocity().Size2D()/300.f,0.f,1.5f);
    GaitPhase+=Delta*(Speed>0.05f?Speed*8.f:1.5f);
    const float Bob=(Aim?0.f:.38f)*Speed;
    const auto* Chapter=GetWorld()->GetAuthGameMode<ACRGameMode>();
    const FTransform& SightRoot=Chapter && Chapter->HasSurveyUpgrade()?OpticAimRoot:IronAimRoot;
    FVector Target=Aim?(bSightAnchorsValid?SightRoot.GetLocation():D->AimLocation):(bSightAnchorsValid?ImportedHipLocation:D->HipLocation);
    Target.Z-=Lower?9.f:SmoothCover*14.f; Target.X-=Recoil;
    Target.Y+=FMath::Sin(GaitPhase)*Bob; Target.Z+=FMath::Cos(GaitPhase*2)*Bob*.65f;
    if(Aim && !bSightAnchorsValid && Chapter && Chapter->HasSurveyUpgrade()) Target.Z-=2.f; // Legacy rollback appearance only.
    ViewRoot->SetRelativeLocation(FMath::VInterpTo(ViewRoot->GetRelativeLocation(),Target,Delta,18));
    FRotator Pose(Aim && bSightAnchorsValid?0.f:Recoil,0,0);
    if(Aim && bSightAnchorsValid) Pose+=SightRoot.Rotator();
    Pose+=FRotator(-(Lower?25:SmoothCover*35),ReloadPose*12,ReloadPose*-28+(Lower?-10:0));
    ViewRoot->SetRelativeRotation(FMath::RInterpTo(ViewRoot->GetRelativeRotation(),Pose,Delta,18));
    // Native single-camera first-person depth scaling; no second scope render or renderer change.
    P->Camera->SetFirstPersonFieldOfView(P->Camera->FieldOfView);
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
    if(AppearanceLoad) { AppearanceLoad->CancelHandle(); AppearanceLoad.Reset(); }
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>()) G->OnRestorationChanged.RemoveDynamic(this,&UCRWeaponViewComponent::RefreshAppearance);
    if (GetWorld()) { GetWorld()->GetTimerManager().ClearTimer(FlashTimer); GetWorld()->GetTimerManager().ClearTimer(ImpactTimer); }
    if (Weapon.IsValid()) { Weapon->OnShot.RemoveDynamic(this,&UCRWeaponViewComponent::Shot); Weapon->OnCue.RemoveDynamic(this,&UCRWeaponViewComponent::Cue); }
    if (auto* Health=GetOwner()->FindComponentByClass<UCRHealthComponent>()) Health->OnHealthChanged.RemoveDynamic(this,&UCRWeaponViewComponent::Hurt);
    Super::EndPlay(Reason);
}
bool UCRWeaponViewComponent::CanUseAuthoredSights(const UStaticMesh* Rook,const UStaticMesh* Optic)
{
    return Rook && Optic && Rook->FindSocket(TEXT("SightAnchor_Iron")) && Optic->FindSocket(TEXT("SightAnchor_Optic"));
}
bool UCRWeaponViewComponent::HasImportedAppearance() const { return bSightAnchorsValid; }
void UCRWeaponViewComponent::RefreshAppearance()
{
    if(!ImportedRook || !ImportedOptic) return;
    ImportedRook->SetStaticMesh(RookAppearance.Get()); ImportedOptic->SetStaticMesh(SurveyAppearance.Get());
    bSightAnchorsValid=false;
    if(CanUseAuthoredSights(ImportedRook->GetStaticMesh(),ImportedOptic->GetStaticMesh()))
    {
        const auto* Iron=ImportedRook->GetStaticMesh()->FindSocket(TEXT("SightAnchor_Iron"));
        const auto* Optic=ImportedOptic->GetStaticMesh()->FindSocket(TEXT("SightAnchor_Optic"));
        if(Iron && Optic)
        {
            IronAimRoot=SolveSightRoot(FTransform(Iron->RelativeRotation,Iron->RelativeLocation),SightEyeRelief);
            OpticAimRoot=SolveSightRoot(FTransform(Optic->RelativeRotation,Optic->RelativeLocation),SightEyeRelief);
            bSightAnchorsValid=true;
        }
    }
    for(auto* Mesh:{ImportedRook.Get(),ImportedOptic.Get(),Flash.Get()})
        Mesh->SetFirstPersonPrimitiveType(bSightAnchorsValid?EFirstPersonPrimitiveType::FirstPerson:EFirstPersonPrimitiveType::None);
    if(auto* P=Cast<ACRCharacter>(GetOwner()))
    {
        P->Camera->SetEnableFirstPersonScale(bSightAnchorsValid);P->Camera->SetFirstPersonScale(.65f);
        P->Camera->SetEnableFirstPersonFieldOfView(bSightAnchorsValid);
    }
    if(Flash) Flash->SetRelativeLocation(bSightAnchorsValid?FVector(67,0,2.3):FVector(44,0,2));
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
    ImportedRook->SetVisibility(!bPresentationHidden && HasImportedAppearance());
    ImportedOptic->SetVisibility(!bPresentationHidden && HasImportedAppearance() && G && G->HasSurveyUpgrade());
    for(const auto& P:FallbackParts) P->SetVisibility(!bPresentationHidden && !HasImportedAppearance());
}
void UCRWeaponViewComponent::SetPresentationHidden(bool Hidden)
{ bPresentationHidden=Hidden; HideFlash(); HideImpact(); RefreshAppearance(); }
