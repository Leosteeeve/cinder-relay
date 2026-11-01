#include "CRPlayerController.h"
#include "CRFieldPackModel.h"
#include "CRCharacter.h"
#include "CRHealthComponent.h"
#include "CRHUDWidget.h"
#include "CRAudioSettingsSubsystem.h"
#include "Engine/GameInstance.h"
bool ACRPlayerController::CanOpenFieldPack() const
{
    const auto* G=GetWorld()?GetWorld()->GetAuthGameMode<ACRGameMode>():nullptr;
    const auto* P=Cast<ACRCharacter>(GetPawn());
    return G&&P&&CRFieldPack::CanOpen(bStartupMenu,bPrototypePaused,bPrototypeDefeated,bPrototypeEnded,IsAssembling(),ActiveEnding.IsValid(),G->IsCheckpointReady(),!P->Health->IsDead())&&!P->Weapon->IsPresentationLocked();
}
void ACRPlayerController::ToggleFieldPack()
{
    if(bFieldPackOpen){bFieldPackOpen=false;if(HUD)HUD->SetFieldPack(false);ApplyPause(false);return;}
    if(!CanOpenFieldPack())return;
    bFieldPackOpen=true;ApplyPause(true);if(HUD){HUD->SetFieldPack(true);HUD->SetKeyboardFocus();}
}
void ACRPlayerController::CloseFieldPackForTravel()
{if(!bFieldPackOpen)return;bFieldPackOpen=false;if(HUD)HUD->SetFieldPack(false);}
void ACRPlayerController::RestorationChanged()
{
    const auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();if(!G)return;
    if(HUD&&((!bLastOptic&&G->HasSurveyOptic())||(!bLastUpgrade&&G->HasSurveyUpgrade())))
    {HUD->Notice(FText::FromString(G->HasSurveyUpgrade()?TEXT("SURVEY OPTIC INSTALLED"):TEXT("SURVEY OPTIC COLLECTED")));HUD->PlayInterfaceSound(G->HasSurveyUpgrade()?TEXT("Confirm"):TEXT("Collect"));}
    bLastOptic=G->HasSurveyOptic();bLastUpgrade=G->HasSurveyUpgrade();RefreshCombat();
}
void ACRPlayerController::FieldItemsChanged()
{if(HUD){HUD->Notice(FText::FromString(TEXT("AMMUNITION COLLECTED")));HUD->PlayInterfaceSound(TEXT("Collect"));if(bFieldPackOpen)HUD->RefreshFieldPack();}}
