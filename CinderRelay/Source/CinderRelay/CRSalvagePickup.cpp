#include "CRSalvagePickup.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "CRPlayerController.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
ACRSalvagePickup::ACRSalvagePickup()
{
    PrimaryActorTick.bCanEverTick=false;
    Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Salvage")); SetRootComponent(Mesh);
    Mesh->SetCollisionProfileName(TEXT("BlockAllDynamic")); Mesh->SetCanEverAffectNavigation(false);
}
void ACRSalvagePickup::BeginPlay()
{
    Super::BeginPlay();
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>()) G->OnRestorationChanged.AddDynamic(this,&ACRSalvagePickup::Reconcile);
    Reconcile();
}
void ACRSalvagePickup::Reconcile()
{
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>(); const bool Used=G && G->HasSurveyOptic();
    SetActorHiddenInGame(Used); SetActorEnableCollision(!Used);
}
bool ACRSalvagePickup::CanInteract_Implementation(ACRCharacter* P) const
{
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
    return G && !G->HasSurveyOptic() && !SourceId.IsNone() && P && P->CanInteractWith(this);
}
FText ACRSalvagePickup::GetInteractionPrompt_Implementation(ACRCharacter*) const
{ return NSLOCTEXT("Cinder","SurveyPickup","E  Recover Survey Optic  /  Optional restoration"); }
void ACRSalvagePickup::Interact_Implementation(ACRCharacter* P)
{
    if(!CanInteract_Implementation(P)) return;
    if(GetWorld()->GetAuthGameMode<ACRGameMode>()->TryCollectSurveyOptic(SourceId))
        if(auto* PC=Cast<ACRPlayerController>(P->GetController())) PC->ShowSubtitle(FText::FromString(TEXT("SURVEY OPTIC RECOVERED  /  Find the workshop calibration bench.")),5.f);
}
void ACRSalvagePickup::EndPlay(const EEndPlayReason::Type Reason)
{
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>()) G->OnRestorationChanged.RemoveDynamic(this,&ACRSalvagePickup::Reconcile);
    Super::EndPlay(Reason);
}
