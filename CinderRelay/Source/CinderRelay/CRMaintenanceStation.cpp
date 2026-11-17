#include "CRMaintenanceStation.h"
#include "CRGameMode.h"
#include "CRCharacter.h"
#include "CRPlayerController.h"
#include "CRAudioSettingsSubsystem.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"

ACRMaintenanceStation::ACRMaintenanceStation()
{
    PrimaryActorTick.bCanEverTick=false;
    Panel=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Panel")); SetRootComponent(Panel);
    Panel->SetCollisionProfileName(TEXT("BlockAll"));
    Display=CreateDefaultSubobject<UTextRenderComponent>(TEXT("Display")); Display->SetupAttachment(Panel);
    Display->SetRelativeLocation(FVector(12,0,48)); Display->SetWorldSize(12); Display->SetHorizontalAlignment(EHTA_Center);
}
void ACRMaintenanceStation::BeginPlay()
{
    Super::BeginPlay();
    if (auto* G = GetWorld()->GetAuthGameMode<ACRGameMode>())
    {
        if (IsRelayService()) G->RegisterRelayService();
        else G->RegisterWorkshopDiagnostic();
        G->OnMaintenanceChanged.AddDynamic(this, &ACRMaintenanceStation::Refresh);
    }
    Refresh();
}
void ACRMaintenanceStation::EndPlay(const EEndPlayReason::Type Reason)
{
    if(auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>()) G->OnMaintenanceChanged.RemoveAll(this);
    Super::EndPlay(Reason);
}
void ACRMaintenanceStation::Refresh()
{
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
    const int32 Current = G ? (IsRelayService() ? G->GetRelayServiceStep() : G->GetDiagnosticStep()) : 0;
    const TCHAR* Labels[]={TEXT("01 / ROUTE\nBENCH SUPPLY"),TEXT("02 / VERIFY\nTEST LOAD"),TEXT("03 / RELEASE\nMODULE CRADLE")};
    const TCHAR* Label = IsRelayService() ? (Step == 0 ? TEXT("A / SERVICE BUS") : TEXT("B / INTERLOCK")) : Labels[FMath::Clamp(Step,0,2)];
    Display->SetText(FText::FromString(FString(Label)+(Current>Step?TEXT("\nCOMPLETE"):Current==Step?TEXT("\nREADY"):TEXT("\nAWAIT PREVIOUS STEP"))));
    Display->SetTextRenderColor(Current>Step?FColor(100,185,175):FColor(222,167,83));
}
bool ACRMaintenanceStation::CanInteract_Implementation(ACRCharacter* Player) const
{
    const auto* G = GetWorld()->GetAuthGameMode<ACRGameMode>();
    return G && Player && Player->CanInteractWith(this) && G->GetObjective() ==
        (IsRelayService() ? ECRObjective::RestorePower : ECRObjective::FindModule);
}
FText ACRMaintenanceStation::GetInteractionPrompt_Implementation(ACRCharacter*) const
{
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
    if (IsRelayService())
    {
        if (G && G->GetRelayServiceStep() > Step) return NSLOCTEXT("Cinder", "ServiceStepDone", "Auxiliary service step complete");
        if (!G || G->GetObjective() < ECRObjective::RestorePower) return NSLOCTEXT("Cinder", "ServiceModuleNeeded", "Bring the replacement module first");
        return Step == 0 ? NSLOCTEXT("Cinder", "PrimeService", "[E] Prime auxiliary service bus")
                         : NSLOCTEXT("Cinder", "ReleaseInterlock", "[E] Release machinery interlock");
    }
    if(G && G->GetDiagnosticStep()>Step) return NSLOCTEXT("Cinder","DiagnosticDone","Diagnostic step complete");
    const TCHAR* Prompts[]={TEXT("[E] Route bench supply / step 1"),TEXT("[E] Verify test load / step 2"),TEXT("[E] Release module cradle / step 3")};
    return FText::FromString(Prompts[FMath::Clamp(Step,0,2)]);
}
void ACRMaintenanceStation::Interact_Implementation(ACRCharacter* Player)
{
    if(!CanInteract_Implementation(Player)) return;
    auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
    if (IsRelayService())
    {
        if (G->GetRelayServiceStep() > Step) return;
        const bool Accepted = G->TryRelayServiceStep(Step);
        const TCHAR* Line = !Accepted ? TEXT("INTERLOCK HELD / Prime the service bus at A first.") : Step == 0
            ? TEXT("BUS ONLINE / Follow the blue-lit hall to B.") : TEXT("INTERLOCK OPEN / Follow the amber return walk. Latch the stop at the relay.");
        if (auto* PC = Cast<ACRPlayerController>(Player->GetController())) PC->ShowSubtitle(FText::FromString(Line), 5);
        if (auto* Audio = UCRAudioSettingsSubsystem::Get(this)) Audio->PlayEvent(Accepted ? TEXT("FeedIn") : TEXT("Dry"), this, GetActorLocation(), true);
        return;
    }
    if(G->GetDiagnosticStep()>Step) return;
    const bool Accepted=G->TryDiagnosticStep(Step);
    const TCHAR* Lines[]={TEXT("BENCH SUPPLY ROUTED / Follow 02 VERIFY in the load-test bay."),TEXT("TEST LOAD STABLE / Follow 03 RELEASE deeper in the hall."),TEXT("CRADLE RELEASED / Use the amber return walk to collect the module at the workshop bench.")};
    if(auto* PC=Cast<ACRPlayerController>(Player->GetController()))
        PC->ShowSubtitle(FText::FromString(Accepted?Lines[FMath::Clamp(Step,0,2)]:TEXT("CONTROL INTERLOCK / Follow the numbered labels. Previous completed steps are retained.")),5);
    if(auto* Audio=UCRAudioSettingsSubsystem::Get(this)) Audio->PlayEvent(Accepted?TEXT("FeedIn"):TEXT("Dry"),this,GetActorLocation(),true);
}
