#include "CRGameMode.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRRestorationSessionTest,"CinderRelay.Restoration.Session",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCRRestorationSessionTest::RunTest(const FString&)
{
    UWorld* World=UWorld::CreateWorld(EWorldType::Game,false);
    ACRGameMode* G=World->SpawnActor<ACRGameMode>();
    TestFalse(TEXT("Upgrade requires salvage"),G->TryApplySurveyUpgrade());
    TestFalse(TEXT("Anonymous source rejected"),G->TryCollectSurveyOptic(NAME_None));
    TestTrue(TEXT("Yard source collected"),G->TryCollectSurveyOptic(TEXT("CR03_YardCache")));
    TestFalse(TEXT("Workshop duplicate rejected"),G->TryCollectSurveyOptic(TEXT("CR03_WorkshopBackup")));
    TestEqual(TEXT("Optional salvage leaves objectives unchanged"),G->GetObjective(),ECRObjective::ReachWorkshop);
    TestTrue(TEXT("Upgrade commits once"),G->TryApplySurveyUpgrade());
    TestFalse(TEXT("Upgrade cannot duplicate"),G->TryApplySurveyUpgrade());
    TestTrue(TEXT("Story claimed"),G->ClaimStoryBeat(TEXT("CR03_Discovery")));
    TestFalse(TEXT("Story does not replay"),G->ClaimStoryBeat(TEXT("CR03_Discovery")));
    ACRGameMode* Fresh=World->SpawnActor<ACRGameMode>();
    TestFalse(TEXT("Fresh chapter resets salvage"),Fresh->HasSurveyOptic());
    TestFalse(TEXT("Fresh chapter resets upgrade"),Fresh->HasSurveyUpgrade());
    TestTrue(TEXT("Backup source independently usable"),Fresh->TryCollectSurveyOptic(TEXT("CR03_WorkshopBackup")));
    World->DestroyWorld(false); return true;
}
#endif
