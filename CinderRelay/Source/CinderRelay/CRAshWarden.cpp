#include "CRAshWarden.h"
#include "CRAshWardenController.h"
#include "CRHealthComponent.h"
#include "CRGameMode.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
ACRAshWarden::ACRAshWarden()
{
    PrimaryActorTick.bCanEverTick=false; AIControllerClass=ACRAshWardenController::StaticClass(); AutoPossessAI=EAutoPossessAI::PlacedInWorldOrSpawned;
    GetCapsuleComponent()->InitCapsuleSize(34,90); GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Ignore); GetCapsuleComponent()->SetCanEverAffectNavigation(false);
    GetCharacterMovement()->MaxWalkSpeed=200; GetCharacterMovement()->bOrientRotationToMovement=true; GetCharacterMovement()->RotationRate=FRotator(0,360,0); bUseControllerRotationYaw=false;
    BaseEyeHeight=64; Health=CreateDefaultSubobject<UCRHealthComponent>(TEXT("Health"));
    Silhouette=CreateDefaultSubobject<USceneComponent>(TEXT("Silhouette")); Silhouette->SetupAttachment(GetCapsuleComponent());
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    auto Part=[this](const TCHAR* Name,FVector Position,FVector Scale)
    {
        auto* M=CreateDefaultSubobject<UStaticMeshComponent>(Name); M->SetupAttachment(Silhouette); M->SetStaticMesh(Cube.Object); M->SetRelativeLocation(Position); M->SetRelativeScale3D(Scale/100);
        M->SetCollisionEnabled(ECollisionEnabled::QueryOnly); M->SetCollisionResponseToAllChannels(ECR_Ignore); M->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block); M->SetCanEverAffectNavigation(false); return M;
    };
    Body=Part(TEXT("ArmoredBody"),FVector(0,0,14),FVector(30,48,62));
    Head=Part(TEXT("Helmet"),FVector(0,0,63),FVector(34,34,34)); Head->SetStaticMesh(Sphere.Object); Head->ComponentTags.Add(TEXT("CR_Head"));
    Part(TEXT("LegL"),FVector(0,-13,-54),FVector(20,18,66)); Part(TEXT("LegR"),FVector(0,13,-54),FVector(20,18,66));
    Part(TEXT("ArmL"),FVector(9,-32,12),FVector(20,17,52)); Part(TEXT("ArmR"),FVector(9,32,12),FVector(20,17,52));
    Part(TEXT("ScoutCarbine"),FVector(36,12,30),FVector(54,8,9));
    Flash=Part(TEXT("ScoutFlash"),FVector(67,12,30),FVector(10,9,9)); Flash->SetCollisionEnabled(ECollisionEnabled::NoCollision); Flash->SetVisibility(false);
}
void ACRAshWarden::BeginPlay()
{
    Super::BeginPlay();
    if(const auto* GM=GetWorld()->GetAuthGameMode<ACRGameMode>(); GM && GM->IsEnemyDefeated(EnemyId))
    {
        UE_LOG(LogTemp,Display,TEXT("CR_ENEMY ReconciledDefeated id=%s"),*EnemyId.ToString());
        if(auto* AI=Cast<ACRAshWardenController>(GetController()))AI->Shutdown(); Destroy(); return;
    }
    Health->OnHealthChanged.AddDynamic(this,&ACRAshWarden::Damaged); Health->OnDeath.AddDynamic(this,&ACRAshWarden::Died);
    if(GetMesh()->GetSkeletalMeshAsset() && IdleAnimation)
    {
        TArray<USceneComponent*> Parts; Silhouette->GetChildrenComponents(true,Parts);
        for(auto* Part:Parts) if(Part!=Flash) Part->SetVisibility(false);
        GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision); GetMesh()->SetCanEverAffectNavigation(false);
        PlayPresentation(IdleAnimation,true);
    }
}
void ACRAshWarden::Damaged(float,float Damage)
{
    if(Damage<=0)return;
    HitReactionUntil=GetWorld()->GetTimeSeconds()+.3f;
    UGameplayStatics::PlaySoundAtLocation(this,HitSound,GetActorLocation(),.3f);
    if(GetMesh()->GetSkeletalMeshAsset()) { if(!Health->IsDead()) PlayPresentation(HitAnimation); }
    else { Silhouette->SetRelativeRotation(FRotator(-8,0,4)); GetWorldTimerManager().SetTimer(FlinchTimer,this,&ACRAshWarden::EndFlinch,.16f,false); }
}
void ACRAshWarden::EndFlinch() { if(!Health->IsDead())Silhouette->SetRelativeRotation(FRotator::ZeroRotator); }
void ACRAshWarden::Died()
{
    if(auto* GM=GetWorld()->GetAuthGameMode<ACRGameMode>())GM->RecordEnemyDefeated(EnemyId);
    if(auto* AI=Cast<ACRAshWardenController>(GetController()))AI->Shutdown();
    GetWorldTimerManager().ClearTimer(FlinchTimer); GetWorldTimerManager().ClearTimer(FlashTimer); EndFlash();
    GetCharacterMovement()->DisableMovement(); SetActorEnableCollision(false);
    if(GetMesh()->GetSkeletalMeshAsset()) PlayPresentation(DeathAnimation);
    else { Silhouette->SetRelativeLocation(FVector(0,0,-65)); Silhouette->SetRelativeRotation(FRotator(0,0,85)); }
    UGameplayStatics::PlaySoundAtLocation(this,DeathSound,GetActorLocation(),.35f);
    UE_LOG(LogTemp,Display,TEXT("CR_ENEMY Defeated id=%s"),*EnemyId.ToString());
}
void ACRAshWarden::PresentAttack() { if(GetWorld()->GetTimeSeconds()>=HitReactionUntil) PlayPresentation(AttackAnimation); Flash->SetVisibility(true); GetWorldTimerManager().SetTimer(FlashTimer,this,&ACRAshWarden::EndFlash,.08f,false); UGameplayStatics::PlaySoundAtLocation(this,ShotSound,GetActorLocation(),.2f); }
void ACRAshWarden::PlayPresentation(UAnimSequence* Animation,bool Loop)
{
    if(!Animation || !GetMesh()->GetSkeletalMeshAsset()) return;
    if(Loop && CurrentAnimation==Animation) return;
    GetMesh()->PlayAnimation(Animation,Loop); CurrentAnimation=Animation;
    PresentationUntil=Loop?0:GetWorld()->GetTimeSeconds()+Animation->GetPlayLength();
}
void ACRAshWarden::PresentAlert() { if(!Health->IsDead() && GetWorld()->GetTimeSeconds()>=HitReactionUntil) PlayPresentation(AlertAnimation); }
void ACRAshWarden::UpdatePresentation()
{
    // Reuse the existing bounded AI decision cadence; native skeletal evaluation interpolates poses.
    if(Health->IsDead() || GetWorld()->GetTimeSeconds()<PresentationUntil) return;
    PlayPresentation(GetVelocity().SizeSquared2D()>100?WalkAnimation:IdleAnimation,true);
}
void ACRAshWarden::EndFlash() { Flash->SetVisibility(false); }
void ACRAshWarden::EndPlay(const EEndPlayReason::Type Reason)
{
    if(auto* AI=Cast<ACRAshWardenController>(GetController()))AI->Shutdown();
    GetWorldTimerManager().ClearTimer(FlinchTimer); GetWorldTimerManager().ClearTimer(FlashTimer); Super::EndPlay(Reason);
}
