#include "CRGameMode.h"
#include "CRChapterSaveGame.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRChapterMechanicsSaveTest,"CinderRelay.Chapter06.CheckpointDerivation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCRChapterMechanicsSaveTest::RunTest(const FString&)
{
    UWorld* World=UWorld::CreateWorld(EWorldType::Game,false); auto* G=World->SpawnActor<ACRGameMode>();
    TestTrue(TEXT("Historical map without stations is not locked"),G->IsModuleReleased() && G->IsAccessStopped());
    G->RegisterWorkshopDiagnostic(); G->RegisterAccessMachinery();
    TestFalse(TEXT("Placed diagnostic holds original module"),G->IsModuleReleased());
    G->TryAdvance(ECRObjective::ReachWorkshop);
    TestFalse(TEXT("Release cannot bypass route or verification"),G->TryDiagnosticStep(2));
    TestTrue(TEXT("Route accepted"),G->TryDiagnosticStep(0));
    TestFalse(TEXT("Duplicate route cannot advance"),G->TryDiagnosticStep(0));
    TestTrue(TEXT("Verify accepted"),G->TryDiagnosticStep(1));
    TestTrue(TEXT("Release accepted"),G->TryDiagnosticStep(2));
    TestTrue(TEXT("Module release uses chapter authority"),G->IsModuleReleased());
    auto* S=NewObject<UCRChapterSaveGame>(); S->CheckpointId=TEXT("CP01_WORKSHOP_ENTRY");S->TargetZone=1;S->CurrentObjective=ECRObjective::FindModule;S->Seal();
    TestTrue(TEXT("Existing CP01 schema1 restores"),G->RestoreSession(*S));
    TestFalse(TEXT("CP01 rollback replays transient diagnosis"),G->IsModuleReleased());
    S->CheckpointId=TEXT("CP02_RELAY_ACCESS");S->TargetZone=2;S->CurrentObjective=ECRObjective::RestorePower;S->Seal();
    TestTrue(TEXT("Existing CP02 schema1 restores"),G->RestoreSession(*S));
    TestTrue(TEXT("Carried module implies prior diagnostic complete"),G->IsModuleReleased());
    TestFalse(TEXT("Unfinished access safely replays"),G->IsAccessStopped());
    G->StopAccessMachinery();TestTrue(TEXT("Local stop latches"),G->IsAccessStopped());
    G->RestoreSession(*S);TestFalse(TEXT("CP02 rollback clears transient stop"),G->IsAccessStopped());
    S->CurrentObjective=ECRObjective::InvestigateSignal;S->Seal();
    TestTrue(TEXT("Old restored relay objective remains readable"),G->RestoreSession(*S));
    TestTrue(TEXT("Restored relay implies access complete"),G->IsAccessStopped());
    auto* Out=NewObject<UCRChapterSaveGame>();G->CaptureSession(*Out);
    TestTrue(TEXT("No new story IDs leaked into strict schema"),Out->ClaimedStoryBeatIds.IsEmpty());
    World->DestroyWorld(false);return true;
}
#endif
