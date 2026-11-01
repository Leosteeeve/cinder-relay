#pragma once
#include "CoreMinimal.h"
#include "CRGameMode.h"
class ACRCharacter;
/** Value projection only. No item mutation, Actor ownership, saved identifiers or polling. */
struct FCRFieldPackItem
{
    FName Icon;
    FString Name,State,Description;
    int32 Quantity=0;
};
struct FCRFieldPackSnapshot
{
    ECRObjective Objective=ECRObjective::ReachWorkshop;
    int32 Magazine=0,Reserve=0;
    bool OpticCollected=false,OpticInstalled=false,AmmoCollected=false,Reloading=false;
};
namespace CRFieldPack
{
    FCRFieldPackSnapshot Read(const ACRGameMode& Mode,const ACRCharacter& Player);
    TArray<FCRFieldPackItem> Items(const FCRFieldPackSnapshot& Snapshot,int32 Category);
    bool CanOpen(bool Startup,bool Paused,bool Defeated,bool Ended,bool Assembling,bool Ending,bool Ready,bool Alive);
}
