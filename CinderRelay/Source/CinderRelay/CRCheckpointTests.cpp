#include "CRChapterSaveGame.h"
#include "CRChapterSaveSubsystem.h"
#include "CRGameMode.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/AutomationTest.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRCheckpointSchemaTest, "CinderRelay.Checkpoints.Schema", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FCRCheckpointSchemaTest::RunTest(const FString&)
{
    auto* S = NewObject<UCRChapterSaveGame>(); FString Reason;
    S->CheckpointId = TEXT("CP02_RELAY_ACCESS"); S->TargetZone = 2; S->CurrentObjective = ECRObjective::RestorePower;
    S->PlayerHealth = 60; S->MagazineAmmo = 3; S->ReserveAmmo = 33;
    S->DefeatedEnemyIds = {TEXT("CR02_Scout_1"), TEXT("CR02_Scout_2")}; S->CollectedPickupIds = {TEXT("CR02_YardAmmo")};
    S->SurveyOpticCollected = true; S->SurveyOpticSourceId = TEXT("CR03_WorkshopBackup"); S->SurveyUpgradeApplied = true;
    S->ClaimedStoryBeatIds = {TEXT("CR03_WorkshopDiscovery"), TEXT("CR03_AssemblyReflection")}; S->Seal();
    TestTrue(TEXT("Version1 valid snapshot"), S->Validate(Reason));
    TArray<uint8> Bytes; TestTrue(TEXT("Native serialization"), UGameplayStatics::SaveGameToMemory(S, Bytes));
    auto* Loaded = Cast<UCRChapterSaveGame>(UGameplayStatics::LoadGameFromMemory(Bytes));
    TestNotNull(TEXT("Native round-trip class"), Loaded); if (!Loaded) return false;
    TestTrue(TEXT("Native round-trip checksum and values"), Loaded->Validate(Reason));
    TestEqual(TEXT("Health round-trip"), Loaded->PlayerHealth, 60.f); TestEqual(TEXT("Ammo round-trip"), Loaded->ReserveAmmo, 33);
    auto Reject = [this, S, &Reason](const TCHAR* Label, TFunction<void(UCRChapterSaveGame&)> Mutate)
    { auto* Bad = DuplicateObject<UCRChapterSaveGame>(S, GetTransientPackage()); Mutate(*Bad); Bad->Seal(); TestFalse(Label, Bad->Validate(Reason)); };
    Reject(TEXT("Wrong chapter"), [](auto& V) { V.ChapterId = TEXT("CH02"); });
    Reject(TEXT("Future version"), [](auto& V) { V.SchemaVersion = 2; });
    Reject(TEXT("Unknown checkpoint"), [](auto& V) { V.CheckpointId = TEXT("unknown"); });
    Reject(TEXT("Mismatched zone"), [](auto& V) { V.TargetZone = 0; });
    Reject(TEXT("Dead health"), [](auto& V) { V.PlayerHealth = 0; });
    Reject(TEXT("Excess health"), [](auto& V) { V.PlayerHealth = 101; });
    Reject(TEXT("Nonfinite health"), [](auto& V) { V.PlayerHealth = std::numeric_limits<float>::infinity(); });
    Reject(TEXT("Negative magazine"), [](auto& V) { V.MagazineAmmo = -1; });
    Reject(TEXT("Excess magazine"), [](auto& V) { V.MagazineAmmo = 6; });
    Reject(TEXT("Invalid reserve"), [](auto& V) { V.ReserveAmmo = 101; });
    Reject(TEXT("Unknown enemy"), [](auto& V) { V.DefeatedEnemyIds = {TEXT("random")}; });
    Reject(TEXT("Duplicate pickup"), [](auto& V) { V.CollectedPickupIds.Add(TEXT("CR02_YardAmmo")); });
    Reject(TEXT("Upgrade without component"), [](auto& V) { V.SurveyOpticCollected = false; V.SurveyOpticSourceId = NAME_None; });
    Reject(TEXT("Premature relay objective"), [](auto& V) { V.CurrentObjective = ECRObjective::FindModule; });
    Loaded->ReserveAmmo++; TestFalse(TEXT("Corrupt payload rejected"), Loaded->Validate(Reason)); Loaded->ReserveAmmo--;
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false); auto* G = World->SpawnActor<ACRGameMode>();
    TestTrue(TEXT("Apply session snapshot"), G->RestoreSession(*Loaded)); TestTrue(TEXT("Apply same snapshot idempotently"), G->RestoreSession(*Loaded));
    TestTrue(TEXT("Defeated enemy restored"), G->IsEnemyDefeated(TEXT("CR02_Scout_2")));
    TestTrue(TEXT("Ammo pickup restored"), G->IsPickupCollected(TEXT("CR02_YardAmmo")));
    TestTrue(TEXT("Salvage and optic restored"), G->HasSurveyOptic() && G->HasSurveyUpgrade());
    TestFalse(TEXT("Story does not replay"), G->ClaimStoryBeat(TEXT("CR03_AssemblyReflection")));
    TestFalse(TEXT("Upgrade cannot duplicate"), G->TryApplySurveyUpgrade());
    TestFalse(TEXT("Alternative salvage cannot duplicate"), G->TryCollectSurveyOptic(TEXT("CR03_YardCache")));
    TestEqual(TEXT("Objective preserved"), G->GetObjective(), ECRObjective::RestorePower);
    World->DestroyWorld(false); return true;
}

/** Real native async I/O, with test-only filenames; never touches the player slots. */
class FCRCheckpointDiskCommand : public IAutomationLatentCommand
{
public:
    explicit FCRCheckpointDiskCommand(FAutomationTestBase* InTest) : Test(InTest) {}
    virtual bool Update() override
    {
        if (!Store)
        {
            Store = NewObject<UCRChapterSaveSubsystem>(NewObject<UGameInstance>()); Store->AddToRoot();
            Store->SetTestPrefix(TEXT("Automation")); Store->BeginRun(); Started = FPlatformTime::Seconds();
            for (int I = 0; I < 2; ++I) UGameplayStatics::DeleteGameInSlot(Store->SlotName(I), 0);
            Store->OnWritten.AddLambda([this](const UCRChapterSaveGame*, bool Success, uint64) { if (Success) ++Successes; else ++Failures; });
            Store->ScanSlots(); return false;
        }
        if (FPlatformTime::Seconds() - Started > 20) { Test->AddError(TEXT("Native checkpoint I/O timed out")); return Finish(); }
        if (Store->IsBusy()) return false;
        auto* S = NewObject<UCRChapterSaveGame>(); S->Seal();
        switch (Step++)
        {
        case 0:
            Test->TestFalse(TEXT("Missing saves unavailable"), Store->HasCheckpoint());
            Test->TestTrue(TEXT("First async write accepted"), Store->RequestWrite(*S, Store->GetRunEpoch())); break;
        case 1:
            Test->TestTrue(TEXT("First native callback succeeds"), Successes == 1 && Store->GetLatest()->SaveGeneration == 1);
            Store->FailNextWriteForTest(); Store->RequestWrite(*S, Store->GetRunEpoch()); break;
        case 2:
            Test->TestTrue(TEXT("Failed async write never announces success or replaces valid save"), Failures == 1 && Successes == 1 && Store->GetLatest()->SaveGeneration == 1);
            Store->RequestWrite(*S, Store->GetRunEpoch()); break;
        case 3:
        {
            Test->TestTrue(TEXT("Alternating second generation"), Store->GetLatest()->SaveGeneration == 2);
            // Native SaveDataToSlot rejects an empty buffer; truncate only this dedicated test file.
            TArray<uint8> Empty; Test->TestTrue(TEXT("Corrupt only test newer slot"), FFileHelper::SaveArrayToFile(Empty, *(FPaths::ProjectSavedDir() / TEXT("SaveGames") / (Store->SlotName(1) + TEXT(".sav")))));
            Store->ScanSlots(); break;
        }
        case 4:
            Test->TestTrue(TEXT("Corrupt newer slot falls back to valid earlier generation"), Store->HasCheckpoint() && Store->GetLatest()->SaveGeneration == 1);
            S->SchemaVersion = 2; S->Seal(); UGameplayStatics::SaveGameToSlot(S, Store->SlotName(1), 0); Store->ScanSlots(); break;
        case 5:
            Test->TestTrue(TEXT("Future version does not hide earlier valid save"), Store->HasCheckpoint() && Store->GetLatest()->SaveGeneration == 1);
            Store->RequestWrite(*S, Store->GetRunEpoch()); S->MagazineAmmo = 4; S->Seal(); Store->RequestWrite(*S, Store->GetRunEpoch());
            S->MagazineAmmo = 2; S->Seal(); Store->RequestWrite(*S, Store->GetRunEpoch()); break;
        case 6:
            Test->TestTrue(TEXT("Coalescing retains latest immutable request"), Store->GetLatest()->SaveGeneration == 3 && Store->GetLatest()->MagazineAmmo == 2);
            Store->RequestWrite(*S, Store->GetRunEpoch()); S->MagazineAmmo = 1; S->Seal(); Store->RequestWrite(*S, Store->GetRunEpoch()); Store->BeginRun(); break;
        case 7:
            Test->TestTrue(TEXT("New run discards queued old-run snapshot"), Store->GetLatest()->SaveGeneration == 4 && Store->GetLatest()->MagazineAmmo == 5);
            return Finish();
        }
        return false;
    }
private:
    bool Finish()
    {
        Store->OnWritten.Clear(); for (int I = 0; I < 2; ++I) UGameplayStatics::DeleteGameInSlot(Store->SlotName(I), 0);
        Store->RemoveFromRoot(); Store = nullptr; return true;
    }
    FAutomationTestBase* Test; UCRChapterSaveSubsystem* Store = nullptr;
    double Started = 0; int32 Step = 0, Successes = 0, Failures = 0;
};
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRCheckpointDiskTest, "CinderRelay.Checkpoints.DiskFallback", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FCRCheckpointDiskTest::RunTest(const FString&) { ADD_LATENT_AUTOMATION_COMMAND(FCRCheckpointDiskCommand(this)); return true; }
#endif
