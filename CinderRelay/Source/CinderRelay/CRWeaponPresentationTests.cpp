#include "CRWeaponViewComponent.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRShotCueIdentityTest,"CinderRelay.Presentation.ShotCueIdentity",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCRShotCueIdentityTest::RunTest(const FString&)
{
    bool Spent=false;
    TestFalse(TEXT("An old montage cannot spend the next shot"),UCRWeaponViewComponent::ConsumeShotCue(12,11,Spent));
    TestFalse(TEXT("Stale event leaves the new shot available"),Spent);
    TestTrue(TEXT("Accepted shot emits once at its own marker"),UCRWeaponViewComponent::ConsumeShotCue(12,12,Spent));
    TestFalse(TEXT("Repeated marker cannot duplicate a case"),UCRWeaponViewComponent::ConsumeShotCue(12,12,Spent));
    Spent=false;
    TestFalse(TEXT("No montage cannot create a cosmetic shot"),UCRWeaponViewComponent::ConsumeShotCue(INDEX_NONE,INDEX_NONE,Spent));
    Spent=true;
    TestFalse(TEXT("Canceled or missing marker never changes authority"),UCRWeaponViewComponent::ConsumeShotCue(14,14,Spent));
    return true;
}
#endif
