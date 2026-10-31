#include "CRChapterSaveGame.h"
#include "Misc/Crc.h"
#include "Serialization/MemoryWriter.h"

int32 UCRChapterSaveGame::CheckpointZone(FName Id)
{
    if (Id == TEXT("CP00_START_YARD")) return 0;
    if (Id == TEXT("CP01_WORKSHOP_ENTRY")) return 1;
    if (Id == TEXT("CP02_RELAY_ACCESS")) return 2;
    return INDEX_NONE;
}
bool UCRChapterSaveGame::ObjectiveAllowsCheckpoint(FName Id, ECRObjective Objective)
{
    const int32 Zone = CheckpointZone(Id), Value = static_cast<int32>(Objective);
    if (Value < 0 || Value >= static_cast<int32>(ECRObjective::Complete)) return false;
    return Zone == 0 ? Objective == ECRObjective::ReachWorkshop : Zone == 1 ? Value >= 1 : Zone == 2 && Value >= 2;
}
uint32 UCRChapterSaveGame::ComputeChecksum() const
{
    // Integrity of the small value payload; disk serialization remains native USaveGame.
    TArray<uint8> Bytes;
    FMemoryWriter Writer(Bytes);
    auto Number = [&Writer](auto Value) { Writer << Value; };
    auto Name = [&Writer](FName Value) { FString Text = Value.ToString().ToLower(); Writer << Text; };
    auto Names = [&Writer, &Name](TArray<FName> Values)
    {
        Values.Sort(FNameLexicalLess()); int32 Count = Values.Num(); Writer << Count;
        for (FName Value : Values) Name(Value);
    };
    Number(SchemaVersion); Name(ChapterId); Name(CheckpointId); Number(TargetZone); Number(SaveGeneration);
    Number(static_cast<uint8>(CurrentObjective)); Number(PlayerHealth); Number(MagazineAmmo); Number(ReserveAmmo);
    Names(DefeatedEnemyIds); Names(CollectedPickupIds); Number(SurveyOpticCollected); Name(SurveyOpticSourceId);
    Number(SurveyUpgradeApplied); Names(ClaimedStoryBeatIds);
    return FCrc::MemCrc32(Bytes.GetData(), Bytes.Num());
}
void UCRChapterSaveGame::Seal() { PayloadChecksum = ComputeChecksum(); }
bool UCRChapterSaveGame::Validate(FString& Reason) const
{
    auto Reject = [&Reason](const TCHAR* Text) { Reason = Text; return false; };
    if (SchemaVersion != 1) return Reject(TEXT("Unsupported checkpoint version"));
    if (ChapterId != TEXT("CH01_DeadStation")) return Reject(TEXT("Wrong chapter"));
    const int32 Zone = CheckpointZone(CheckpointId);
    if (Zone == INDEX_NONE || TargetZone != Zone) return Reject(TEXT("Invalid checkpoint or zone"));
    if (!ObjectiveAllowsCheckpoint(CheckpointId, CurrentObjective)) return Reject(TEXT("Checkpoint objective prerequisites are inconsistent"));
    if (SaveGeneration < 1 || SaveGeneration >= MAX_int64) return Reject(TEXT("Invalid checkpoint generation"));
    if (!FMath::IsFinite(PlayerHealth) || PlayerHealth <= 0 || PlayerHealth > 100 || MagazineAmmo < 0 || MagazineAmmo > 5 || ReserveAmmo < 0 || ReserveAmmo > 100)
        return Reject(TEXT("Invalid health or ammunition"));
    auto KnownUnique = [](const TArray<FName>& Values, const TArray<FName>& Known)
    {
        if (Values.Num() > Known.Num()) return false;
        TSet<FName> Seen;
        for (FName Value : Values) { if (!Known.Contains(Value) || Seen.Contains(Value)) return false; Seen.Add(Value); }
        return true;
    };
    if (!KnownUnique(DefeatedEnemyIds, {TEXT("CR02_Scout_1"), TEXT("CR02_Scout_2")})) return Reject(TEXT("Invalid enemy IDs"));
    if (!KnownUnique(CollectedPickupIds, {TEXT("CR02_YardAmmo")})) return Reject(TEXT("Invalid pickup IDs"));
    if (!KnownUnique(ClaimedStoryBeatIds, {TEXT("CR03_WorkshopDiscovery"), TEXT("CR03_AssemblyReflection"), TEXT("CR03_RelayEcho")})) return Reject(TEXT("Invalid story IDs"));
    if (SurveyUpgradeApplied && !SurveyOpticCollected) return Reject(TEXT("Upgrade without recovered component"));
    if (SurveyOpticCollected ? (SurveyOpticSourceId != TEXT("CR03_YardCache") && SurveyOpticSourceId != TEXT("CR03_WorkshopBackup")) : !SurveyOpticSourceId.IsNone())
        return Reject(TEXT("Invalid salvage source"));
    if (ClaimedStoryBeatIds.Contains(TEXT("CR03_WorkshopDiscovery")) && CurrentObjective < ECRObjective::FindModule) return Reject(TEXT("Premature Workshop story state"));
    if (ClaimedStoryBeatIds.Contains(TEXT("CR03_RelayEcho")) && CurrentObjective < ECRObjective::InvestigateSignal) return Reject(TEXT("Premature relay story state"));
    if (PayloadChecksum != ComputeChecksum()) return Reject(TEXT("Checkpoint integrity check failed"));
    Reason.Reset(); return true;
}
