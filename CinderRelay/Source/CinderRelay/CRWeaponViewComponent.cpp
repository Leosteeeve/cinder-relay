#include "CRWeaponViewComponent.h"
#include "CRWeaponComponent.h"
#include "CRWeaponData.h"
#include "CRHealthComponent.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "CRAudioSettingsSubsystem.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "Sound/SoundBase.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
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
    ArmsAppearance=TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/Generated/Phase053/Gameplay/Animation/SK_CR053_FirstPersonArms.SK_CR053_FirstPersonArms")));
    for(const TCHAR* Name:{TEXT("Idle"),TEXT("Walk"),TEXT("Sprint"),TEXT("ADS"),TEXT("FireCycle"),TEXT("Reload"),TEXT("Dry")})
        HandlingClips.Add(TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(FString::Printf(TEXT("/Game/Generated/Phase053/Gameplay/Animation/AN_CR053_%s.AN_CR053_%s"),Name,Name))));
    for(const TCHAR* Name:{TEXT("Feed"),TEXT("CycleHandle"),TEXT("Case")})
        HandlingProps.Add(TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(FString::Printf(TEXT("/Game/Generated/Phase053/Gameplay/Meshes/SM_CR053_%s.SM_CR053_%s"),Name,Name))));
    for(const TCHAR* Name:{TEXT("Secure"),TEXT("Seat")})
        HandlingSounds.Add(TSoftObjectPtr<USoundBase>(FSoftObjectPath(FString::Printf(TEXT("/Game/Generated/Phase052/Audio/S_CR052_%s.S_CR052_%s"),Name,Name))));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Mesh(TEXT("/Engine/BasicShapes/Cube.Cube")); Cube = Mesh.Object;
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cone(TEXT("/Engine/BasicShapes/Cone.Cone")); FlashCone=Cone.Object;
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Glow(TEXT("/Game/Generated/Phase05/Materials/MI_CR05_Light.MI_CR05_Light")); FlashMaterial=Glow.Object;
}
FTransform UCRWeaponViewComponent::SolveSightRoot(const FTransform& SightLocal,float EyeRelief)
{
    return SightLocal.Inverse()*FTransform(FVector(EyeRelief,0,0));
}
void UCRWeaponViewComponent::BeginPlay()
{
    Super::BeginPlay(); auto* Player = Cast<ACRCharacter>(GetOwner());
    Weapon = GetOwner()->FindComponentByClass<UCRWeaponComponent>();
    if (!Player || !Weapon.IsValid() || !Weapon->Data) { bAppearanceSettled=bHandlingSettled=true;SetComponentTickEnabled(false); return; }
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
    Flash->SetStaticMesh(FlashCone); Flash->SetMaterial(0,FlashMaterial);
    Flash->SetRelativeRotation(FRotator(90,0,0)); Flash->SetRelativeScale3D(FVector(.04f,.04f,.12f));
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
    AppearanceLoad=UAssetManager::GetStreamableManager().RequestAsyncLoad({RookAppearance.ToSoftObjectPath(),SurveyAppearance.ToSoftObjectPath()},FStreamableDelegate::CreateUObject(this,&UCRWeaponViewComponent::AppearanceLoaded));
    if(!AppearanceLoad) AppearanceLoaded();
    Weapon->OnImpact.AddDynamic(this,&UCRWeaponViewComponent::ConfirmedImpact);
    Weapon->OnShot.AddDynamic(this,&UCRWeaponViewComponent::Shot); Weapon->OnCue.AddDynamic(this,&UCRWeaponViewComponent::Cue);
    Weapon->OnChanged.AddDynamic(this,&UCRWeaponViewComponent::WeaponStateChanged);
    LoadHandling();
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
    TickCases(Delta);
    const bool Lower=(!bHandlingReady && (Weapon->State==ECRWeaponState::Reloading || Weapon->bSprinting)) || Weapon->State==ECRWeaponState::Disabled;
    SmoothCover=FMath::FInterpTo(SmoothCover,CoverFraction,Delta,9);
    ReloadPose=FMath::FInterpTo(ReloadPose,!bHandlingReady && Weapon->State==ECRWeaponState::Reloading?1.f:0.f,Delta,6);
    const float Speed=FMath::Clamp(P->GetVelocity().Size2D()/300.f,0.f,1.5f);
    GaitPhase+=Delta*(Speed>0.05f?Speed*8.f:1.5f);
    const float Bob=(Aim || bHandlingReady?0.f:.38f)*Speed;
    const auto* Chapter=GetWorld()->GetAuthGameMode<ACRGameMode>();
    const FTransform& SightRoot=Chapter && Chapter->HasSurveyUpgrade()?OpticAimRoot:IronAimRoot;
    FVector Target=Aim?(bSightAnchorsValid?SightRoot.GetLocation():D->AimLocation):(bSightAnchorsValid?ImportedHipLocation:D->HipLocation);
    Target.Z-=Lower?9.f:SmoothCover*14.f; Target.X-=Recoil*(bHandlingReady?.55f:1.f);
    if(P->IsSliding()) { Target.Z-=3.5f; Target.X-=2.f; }
    Target.Y+=FMath::Sin(GaitPhase)*Bob; Target.Z+=FMath::Cos(GaitPhase*2)*Bob*.65f;
    if(Aim && !bSightAnchorsValid && Chapter && Chapter->HasSurveyUpgrade()) Target.Z-=2.f; // Legacy rollback appearance only.
    ViewRoot->SetRelativeLocation(FMath::VInterpTo(ViewRoot->GetRelativeLocation(),Target,Delta,18));
    FRotator Pose(Aim && bSightAnchorsValid?0.f:Recoil*(bHandlingReady?.35f:1.f),0,0);
    if(P->IsSliding()) Pose.Pitch-=4.f;
    if(Aim && bSightAnchorsValid) Pose+=SightRoot.Rotator();
    Pose+=FRotator(-(Lower?25:SmoothCover*35),ReloadPose*12,ReloadPose*-28+(Lower?-10:0));
    ViewRoot->SetRelativeRotation(FMath::RInterpTo(ViewRoot->GetRelativeRotation(),Pose,Delta,18));
    // Native single-camera first-person depth scaling; no second scope render or renderer change.
    P->Camera->SetFirstPersonFieldOfView(P->Camera->FieldOfView);
}
void UCRWeaponViewComponent::Shot(FVector Impact,bool Hit,bool BlockingHit)
{
    if (!Weapon.IsValid() || !Weapon->Data) return;
    PlayHandling(0);
    Recoil=FMath::Min(Weapon->Data->RecoilDegrees,2.f); Flash->SetVisibility(true);
    GetWorld()->GetTimerManager().SetTimer(FlashTimer,this,&UCRWeaponViewComponent::HideFlash,.055f,false);
    // Confirmed impact classification follows this accepted-shot event.
    if(auto* Audio=UCRAudioSettingsSubsystem::Get(this);Audio && Audio->IsReady())
        Audio->PlayEvent(TEXT("Shot"),this,GetOwner()->GetActorLocation(),false);
    else UGameplayStatics::PlaySound2D(this,Weapon->Data->ShotSound,.55f,1.f,0.f,nullptr,nullptr,false);

}
void UCRWeaponViewComponent::ConfirmedImpact(FVector Position,FVector Normal,ECRImpactKind Kind)
{
    if(!Weapon.IsValid() || !Weapon->Data || bPresentationHidden) return;
    const bool Enemy=Kind!=ECRImpactKind::Surface;
    ImpactMarker->SetWorldLocation(Position+Normal*1.5f); ImpactMarker->SetWorldRotation(Normal.Rotation());
    ImpactMarker->SetWorldScale3D(FVector(.008f,.045f,.018f)); ImpactMarker->SetVisibility(!Enemy);
    GetWorld()->GetTimerManager().SetTimer(ImpactTimer,this,&UCRWeaponViewComponent::HideImpact,.085f,false);
    if(auto* Audio=UCRAudioSettingsSubsystem::Get(this);Audio && Audio->IsReady())
        Audio->PlayEvent(Enemy?(Kind==ECRImpactKind::EnemyKill?TEXT("Kill"):TEXT("Hit")):TEXT("Impact"),this,Position,!Enemy);
    else if(Enemy) UGameplayStatics::PlaySound2D(this,Weapon->Data->HitSound,Kind==ECRImpactKind::EnemyKill?.4f:.26f,Kind==ECRImpactKind::EnemyKill?.8f:1.1f,0.f,nullptr,nullptr,false);
    else UGameplayStatics::PlaySoundAtLocation(this,Weapon->Data->ImpactSound,Position,.18f);
}
void UCRWeaponViewComponent::Cue(FName Name)
{
    if(Name==TEXT("Reload")) PlayHandling(1);
    else if(Name==TEXT("Dry")) PlayHandling(2);
    if(auto* Audio=UCRAudioSettingsSubsystem::Get(this);Audio && Audio->IsReady())
    {
        if(Name==TEXT("Reload") || Name==TEXT("Dry") || Name==TEXT("ReloadComplete"))
            Audio->PlayEvent(Name==TEXT("Reload")?FName(TEXT("ReloadStart")):Name,this,GetOwner()->GetActorLocation(),false);
    }
    else if(Weapon.IsValid() && Weapon->Data && (Name==TEXT("Reload") || Name==TEXT("Dry")))
        UGameplayStatics::PlaySound2D(this,Name==TEXT("Reload")?Weapon->Data->ReloadSound:Weapon->Data->DrySound,.35f,1.f,0.f,nullptr,nullptr,false);
}
void UCRWeaponViewComponent::Hurt(float,float Damage)
{
    if(Damage<=0 || !Weapon.IsValid() || !Weapon->Data) return;
    if(auto* Audio=UCRAudioSettingsSubsystem::Get(this);Audio && Audio->IsReady())
        Audio->PlayEvent(TEXT("Damage"),this,GetOwner()->GetActorLocation(),false);
    else UGameplayStatics::PlaySound2D(this,Weapon->Data->HurtSound,.4f,1.f,0.f,nullptr,nullptr,false);
}
void UCRWeaponViewComponent::HideFlash() { if (Flash) Flash->SetVisibility(false); }
void UCRWeaponViewComponent::HideImpact() { if (ImpactMarker) ImpactMarker->SetVisibility(false); }
void UCRWeaponViewComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    CancelHandling(true);
    if(HandlingLoad) { HandlingLoad->CancelHandle();HandlingLoad.Reset(); }
    if(AppearanceLoad) { AppearanceLoad->CancelHandle(); AppearanceLoad.Reset(); }
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>()) G->OnRestorationChanged.RemoveDynamic(this,&UCRWeaponViewComponent::RefreshAppearance);
    if (GetWorld()) { GetWorld()->GetTimerManager().ClearTimer(FlashTimer); GetWorld()->GetTimerManager().ClearTimer(ImpactTimer); }
    if (Weapon.IsValid()) { Weapon->OnImpact.RemoveDynamic(this,&UCRWeaponViewComponent::ConfirmedImpact); Weapon->OnShot.RemoveDynamic(this,&UCRWeaponViewComponent::Shot); Weapon->OnCue.RemoveDynamic(this,&UCRWeaponViewComponent::Cue); Weapon->OnChanged.RemoveDynamic(this,&UCRWeaponViewComponent::WeaponStateChanged); }
    if (auto* Health=GetOwner()->FindComponentByClass<UCRHealthComponent>()) Health->OnHealthChanged.RemoveDynamic(this,&UCRWeaponViewComponent::Hurt);
    Super::EndPlay(Reason);
}
bool UCRWeaponViewComponent::CanUseAuthoredSights(const UStaticMesh* Rook,const UStaticMesh* Optic)
{
    return Rook && Optic && Rook->FindSocket(TEXT("SightAnchor_Iron")) && Optic->FindSocket(TEXT("SightAnchor_Optic"));
}
bool UCRWeaponViewComponent::HasImportedAppearance() const { return bSightAnchorsValid; }
void UCRWeaponViewComponent::AppearanceLoaded()
{
    bAppearanceSettled=true;RefreshAppearance();
    if(bHandlingSettled) HandlingLoaded();
}
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
    const bool ShowHands=!bPresentationHidden && HasImportedAppearance() && bHandlingReady;
    if(Arms) Arms->SetVisibility(ShowHands);
    if(Feed) Feed->SetVisibility(ShowHands);
    if(CycleHandle) CycleHandle->SetVisibility(ShowHands);
    for(const auto& P:FallbackParts) P->SetVisibility(!bPresentationHidden && !HasImportedAppearance());
}
void UCRWeaponViewComponent::SetPresentationHidden(bool Hidden)
{ bPresentationHidden=Hidden; if(Hidden) CancelHandling(true); HideFlash(); HideImpact(); RefreshAppearance(); }
