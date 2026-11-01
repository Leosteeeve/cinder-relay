#include "CRWeaponViewComponent.h"
#include "Misc/AutomationTest.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshSocket.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRSightTransformTest, "CinderRelay.Presentation.SightAlignment", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FCRSightTransformTest::RunTest(const FString&)
{
    // Nonzero rotation exposes the fixed-translation shortcut and multiplication-order mistakes.
    for (const FTransform& Anchor : {FTransform(FRotator::ZeroRotator,FVector(-16,0,8.2)),
        FTransform(FRotator(3,8,-2),FVector(-13,1,11.6))})
    {
        const FTransform Root=UCRWeaponViewComponent::SolveSightRoot(Anchor,20.f);
        const FTransform InCamera=Anchor*Root;
        TestTrue(TEXT("Selected sight center is on the camera axis"),InCamera.GetLocation().Equals(FVector(20,0,0),.001));
        TestTrue(TEXT("Selected sight forward matches camera forward"),InCamera.GetRotation().GetForwardVector().Equals(FVector::ForwardVector,.001));
        const FVector Target=InCamera.TransformPosition(FVector(10000,0,0));
        TestTrue(TEXT("Distant static aim axis has no lateral error"),FMath::Abs(Target.Y)<.01 && FMath::Abs(Target.Z)<.01);
        // Camera-relative contract remains identical across standing/crouching and aspect/FOV changes.
        for (const FVector& Camera : {FVector(0,0,165),FVector(0,0,105)})
            TestTrue(TEXT("Crouch translates camera and sight together"),((Anchor*Root)*FTransform(Camera)).GetLocation().Equals(Camera+FVector(20,0,0),.001));
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRSightFallbackTest, "CinderRelay.Presentation.SightFallback", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FCRSightFallbackTest::RunTest(const FString&)
{
    UStaticMesh* Rook=NewObject<UStaticMesh>();
    UStaticMesh* Optic=NewObject<UStaticMesh>();
    TestFalse(TEXT("Missing pair uses primitive fallback"),UCRWeaponViewComponent::CanUseAuthoredSights(nullptr,nullptr));
    TestFalse(TEXT("Unanchored imports cannot replace the working fallback"),UCRWeaponViewComponent::CanUseAuthoredSights(Rook,Optic));
    auto* Iron=NewObject<UStaticMeshSocket>(Rook);Iron->SocketName=TEXT("SightAnchor_Iron");Rook->AddSocket(Iron);
    TestFalse(TEXT("Missing optic cannot expose a misaligned imported gun"),UCRWeaponViewComponent::CanUseAuthoredSights(Rook,nullptr));
    TestFalse(TEXT("Missing optic anchor retains fallback"),UCRWeaponViewComponent::CanUseAuthoredSights(Rook,Optic));
    auto* Survey=NewObject<UStaticMeshSocket>(Optic);Survey->SocketName=TEXT("SightAnchor_Optic");Optic->AddSocket(Survey);
    TestTrue(TEXT("Complete authored pair uses native aligned sights"),UCRWeaponViewComponent::CanUseAuthoredSights(Rook,Optic));
    TestFalse(TEXT("Missing gun still retains fallback with a valid optic"),UCRWeaponViewComponent::CanUseAuthoredSights(nullptr,Optic));
    Rook->RemoveSocket(Iron);
    TestFalse(TEXT("Missing iron anchor retains fallback"),UCRWeaponViewComponent::CanUseAuthoredSights(Rook,Optic));
    return true;
}
#endif
