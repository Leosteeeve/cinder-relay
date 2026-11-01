#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "CRCharacterMovementComponent.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRSlideDecayTest,"CinderRelay.Movement.SlideDecay",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCRSlideDecayTest::RunTest(const FString&)
{
    using M=UCRCharacterMovementComponent;
    const float Flat=M::DecayedSlideSpeed(600,.75f,0);
    TestTrue(TEXT("Useful bounded flat momentum"),Flat>150 && Flat<250);
    TestTrue(TEXT("Uphill loses speed faster"),M::DecayedSlideSpeed(600,.5f,-.35f)<M::DecayedSlideSpeed(600,.5f,0));
    TestTrue(TEXT("Downhill never accelerates"),M::DecayedSlideSpeed(600,.5f,.8f)<600);
    TestEqual(TEXT("No reverse slide at a long frame"),M::DecayedSlideSpeed(100,1,0),0.f);
    float Fine=600;for(int32 I=0;I<75;++I) Fine=M::DecayedSlideSpeed(Fine,.01f,0);
    TestTrue(TEXT("Fixed slope decay independent of frame subdivision"),FMath::IsNearlyEqual(Fine,Flat,.02f));
    return true;
}
#endif
