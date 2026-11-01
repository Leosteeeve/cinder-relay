#include "CRAudioSettingsSubsystem.h"
#include "Misc/AutomationTest.h"
#include "Misc/Paths.h"
#include "Misc/Guid.h"
#include "Misc/FileHelper.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRAudioPreferenceTest,"CinderRelay.Audio.Preferences",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCRAudioPreferenceTest::RunTest(const FString&)
{
    using Audio=UCRAudioSettingsSubsystem;
    TestEqual(TEXT("Negative volume clamps"),Audio::SanitizeVolume(-1,.8f),0.f);
    TestEqual(TEXT("Excess volume clamps"),Audio::SanitizeVolume(2,.8f),1.f);
    TestEqual(TEXT("NaN falls back"),Audio::SanitizeVolume(std::numeric_limits<float>::quiet_NaN(),.8f),.8f);
    TestEqual(TEXT("Infinity falls back"),Audio::SanitizeVolume(std::numeric_limits<float>::infinity(),.65f),.65f);
    TestTrue(TEXT("Safe test prefix"),Audio::IsPreferenceSuffixValid(TEXT("Phase055_Restart")));
    TestFalse(TEXT("Reject path traversal"),Audio::IsPreferenceSuffixValid(TEXT("../Player")));
    TestFalse(TEXT("Reject empty override"),Audio::IsPreferenceSuffixValid(TEXT("")));
    TestFalse(TEXT("Reject absolute path"),Audio::IsPreferenceSuffixValid(TEXT("C:\\Player")));
    const FString Filename=FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("Config/Phase055Tests"),TEXT("CR04_TEST_Audio_")+FGuid::NewGuid().ToString(EGuidFormats::Digits)+TEXT(".ini"));
    auto Values=Audio::DefaultVolumes();Values[TEXT("Master")]=.37f;Values[TEXT("SFX")]=.52f;Values[TEXT("Ambience")]=0.f;Values[TEXT("UI")]=.28f;
    TestTrue(TEXT("Independent native config write"),Audio::WritePreferences(Filename,Values));
    TMap<FName,float> Reloaded;
    TestTrue(TEXT("Fresh reader reloads independent preferences"),Audio::ReadPreferences(Filename,Reloaded));
    TestEqual(TEXT("Master persisted"),Reloaded.FindChecked(TEXT("Master")),.37f);
    TestEqual(TEXT("SFX persisted"),Reloaded.FindChecked(TEXT("SFX")),.52f);
    TestEqual(TEXT("Mute persists exactly"),Reloaded.FindChecked(TEXT("Ambience")),0.f);
    TestEqual(TEXT("UI persisted separately"),Reloaded.FindChecked(TEXT("UI")),.28f);
    TestEqual(TEXT("Weapon class preserved"),Reloaded.FindChecked(TEXT("Weapons")),1.f);
    const FString Malformed=Filename+TEXT(".malformed.ini");
    TestTrue(TEXT("Write bounded corrupt preference fixture"),FFileHelper::SaveStringToFile(TEXT("[CinderRelay.Audio]\nMaster=7\nSFX=-4\nAmbience=nan\n"),*Malformed));
    TestTrue(TEXT("Read malformed preferences"),Audio::ReadPreferences(Malformed,Reloaded));
    TestEqual(TEXT("Persisted excess clamps"),Reloaded.FindChecked(TEXT("Master")),1.f);
    TestEqual(TEXT("Persisted negative clamps"),Reloaded.FindChecked(TEXT("SFX")),0.f);
    TestTrue(TEXT("Persisted nonfinite cannot escape"),FMath::IsFinite(Reloaded.FindChecked(TEXT("Ambience"))));
    TestEqual(TEXT("Unspecified UI uses default"),Reloaded.FindChecked(TEXT("UI")),.8f);
    // Retain unique test-only artifacts for diagnosis; never delete player state.
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCRAudioSurfaceTest,"CinderRelay.Audio.SurfaceSelection",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCRAudioSurfaceTest::RunTest(const FString&)
{
    using Audio=UCRAudioSettingsSubsystem;
    TestEqual(TEXT("Authored metal physical material"),Audio::ChooseFootSurface(TEXT("PM_Metal"),TEXT("Floor"),0),FName(TEXT("FootMetal")));
    TestEqual(TEXT("Actual ramp overrides outdoor fallback"),Audio::ChooseFootSurface(NAME_None,TEXT("CR_Ramp"),0),FName(TEXT("FootConcrete")));
    TestEqual(TEXT("Actual gravel overrides interior fallback"),Audio::ChooseFootSurface(TEXT("PM_Gravel"),TEXT("Floor"),1),FName(TEXT("FootGravel")));
    TestEqual(TEXT("Workshop material"),Audio::ChooseFootSurface(NAME_None,TEXT("IndustrialFloor"),2),FName(TEXT("FootIndustrial")));
    TestEqual(TEXT("Default yard fallback"),Audio::ChooseFootSurface(NAME_None,NAME_None,0),FName(TEXT("FootGravel")));
    TestEqual(TEXT("Default workshop fallback"),Audio::ChooseFootSurface(NAME_None,NAME_None,1),FName(TEXT("FootIndustrial")));
    TestEqual(TEXT("Default bunker fallback"),Audio::ChooseFootSurface(NAME_None,NAME_None,2),FName(TEXT("FootConcrete")));
    return true;
}
#endif
