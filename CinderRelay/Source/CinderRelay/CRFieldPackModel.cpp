#include "CRFieldPackModel.h"
#include "CRCharacter.h"
#include "CRWeaponComponent.h"
FCRFieldPackSnapshot CRFieldPack::Read(const ACRGameMode& G,const ACRCharacter& P)
{
    FCRFieldPackSnapshot S;S.Objective=G.GetObjective();S.OpticCollected=G.HasSurveyOptic();S.OpticInstalled=G.HasSurveyUpgrade();S.AmmoCollected=G.IsPickupCollected(TEXT("CR02_YardAmmo"));
    if(P.Weapon){S.Magazine=P.Weapon->Magazine;S.Reserve=P.Weapon->Reserve;S.Reloading=P.Weapon->State==ECRWeaponState::Reloading;}return S;
}
TArray<FCRFieldPackItem> CRFieldPack::Items(const FCRFieldPackSnapshot& S,int32 Category)
{
    FCRFieldPackItem Rook{TEXT("Rook"),TEXT("ROOK-5"),S.Reloading?TEXT("RELOADING / PAUSED"):TEXT("EQUIPPED"),FString::Printf(TEXT("MAGAZINE  %02d / 05      RESERVE  %02d\n\nA manually cycled carbine.\nSurvey Optic: %s\n\nReload with R during gameplay."),S.Magazine,S.Reserve,S.OpticInstalled?TEXT("Installed"):TEXT("Not installed")),1};
    FCRFieldPackItem Optic{TEXT("Optic"),TEXT("Survey Optic"),S.OpticInstalled?TEXT("INSTALLED"):S.OpticCollected?TEXT("COLLECTED"):TEXT("NOT COLLECTED"),S.OpticInstalled?TEXT("Calibrated at the Workshop. Provides a closer sight picture on the ROOK-5."):S.OpticCollected?TEXT("Recovered optical equipment. Use the Workshop calibration bench to install it."):TEXT("Optional optical equipment. Recover it in the Rail Yard or at the Workshop."),S.OpticCollected?1:0};
    FCRFieldPackItem Ammo{TEXT("Ammo"),TEXT("Reserve ammunition"),S.Reserve>0?TEXT("AVAILABLE"):TEXT("EMPTY"),FString::Printf(TEXT("%d rounds in the magazine. %d rounds in reserve.\n\nRail Yard ammunition case: %s.\n\nLoaded and spare rounds for the ROOK-5."),S.Magazine,S.Reserve,S.AmmoCollected?TEXT("Collected"):TEXT("Not collected")),S.Reserve};
    bool Carried=S.Objective==ECRObjective::RestorePower,Installed=S.Objective>=ECRObjective::InvestigateSignal;
    FCRFieldPackItem Module{TEXT("PowerModule"),TEXT("Power Module"),Installed?TEXT("INSTALLED AT RELAY NINE"):Carried?TEXT("CARRIED"):TEXT("NOT FOUND"),Installed?TEXT("The recovered power module is installed at Relay Nine."):Carried?TEXT("A functional power module recovered from the Workshop. Bring it to Relay Nine to restore power.\n\nMission equipment cannot be dropped."):TEXT("Find a functional power module in the maintenance workshop."),Carried?1:0};
    switch(Category){case 0:return {Rook,Optic};case 1:return {Ammo};case 2:return {Optic};case 3:return {Module};default:return {};}
}
bool CRFieldPack::CanOpen(bool Startup,bool Paused,bool Defeated,bool Ended,bool Assembling,bool Ending,bool Ready,bool Alive)
{return !Startup&&!Paused&&!Defeated&&!Ended&&!Assembling&&!Ending&&Ready&&Alive;}
