#include "CRFieldPackModel.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRFieldPackProjection,"CinderRelay.Interface.FieldPackProjection",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCRFieldPackProjection::RunTest(const FString&)
{
    FCRFieldPackSnapshot S;S.Magazine=2;S.Reserve=17;
    TestEqual(TEXT("Weapon is existing equipment"),CRFieldPack::Items(S,0)[0].Quantity,1);
    TestEqual(TEXT("Supplies are actual reserve, not pickup total"),CRFieldPack::Items(S,1)[0].Quantity,17);
    TestEqual(TEXT("Uncollected optic"),CRFieldPack::Items(S,2)[0].State,FString(TEXT("NOT COLLECTED")));
    TestEqual(TEXT("Module not found"),CRFieldPack::Items(S,3)[0].Quantity,0);
    S.OpticCollected=true;TestEqual(TEXT("Carried optic"),CRFieldPack::Items(S,2)[0].State,FString(TEXT("COLLECTED")));
    S.OpticInstalled=true;TestEqual(TEXT("Installed optic"),CRFieldPack::Items(S,2)[0].State,FString(TEXT("INSTALLED")));
    S.Objective=ECRObjective::RestorePower;TestEqual(TEXT("Module carried"),CRFieldPack::Items(S,3)[0].State,FString(TEXT("CARRIED")));
    S.Objective=ECRObjective::InvestigateSignal;TestEqual(TEXT("Module installed"),CRFieldPack::Items(S,3)[0].State,FString(TEXT("INSTALLED AT RELAY NINE")));
    TestEqual(TEXT("Installed module no longer carried"),CRFieldPack::Items(S,3)[0].Quantity,0);
    S.AmmoCollected=true;S.Reserve=0;TestEqual(TEXT("Used ammo does not reappear"),CRFieldPack::Items(S,1)[0].Quantity,0);
    TestTrue(TEXT("Pickup history remains visible"),CRFieldPack::Items(S,1)[0].Description.Contains(TEXT("Collected")));
    TestTrue(TEXT("Invalid category is bounded"),CRFieldPack::Items(S,7).IsEmpty());return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRFieldPackAvailability,"CinderRelay.Interface.FieldPackAvailability",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCRFieldPackAvailability::RunTest(const FString&)
{
    TestTrue(TEXT("Ordinary combat allowed"),CRFieldPack::CanOpen(false,false,false,false,false,false,true,true));
    TestFalse(TEXT("Startup"),CRFieldPack::CanOpen(true,false,false,false,false,false,true,true));
    TestFalse(TEXT("Pause owner"),CRFieldPack::CanOpen(false,true,false,false,false,false,true,true));
    TestFalse(TEXT("Death"),CRFieldPack::CanOpen(false,false,true,false,false,false,true,false));
    TestFalse(TEXT("Assembly"),CRFieldPack::CanOpen(false,false,false,false,true,false,true,true));
    TestFalse(TEXT("Ending"),CRFieldPack::CanOpen(false,false,false,false,false,true,true,true));
    TestFalse(TEXT("Travel readiness"),CRFieldPack::CanOpen(false,false,false,false,false,false,false,true));return true;
}
#endif
