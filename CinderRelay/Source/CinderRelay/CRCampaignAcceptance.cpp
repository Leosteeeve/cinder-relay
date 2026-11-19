#include "CRCampaignAcceptance.h"
#if !UE_BUILD_SHIPPING
#include "CRChapterSaveSubsystem.h"
#include "CRCharacter.h"
#include "CREchoChapter.h"
#include "CRHealthComponent.h"
#include "CRHUDWidget.h"
#include "CRPlayerController.h"
#include "CRSignalFilm.h"
#include "CRWeaponComponent.h"
#include "AudioMixerBlueprintLibrary.h"
#include "Components/Button.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Framework/Application/SlateApplication.h"
#include "HAL/FileManager.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
namespace
{
	enum class ECampaignTest { Menu, Film, Arrival, Done };
	ECampaignTest Stage = ECampaignTest::Menu;
	double LastProgress = 0;
	int32 Frames = 0, ExpectedMag = -1, ExpectedReserve = -1;
	float ExpectedHealth = 0;
	bool ExpectedOptic = false;
	void Press(FKey Key)
	{
		const FKeyEvent Event(Key,FModifierKeysState(),0,false,0,0);
		FSlateApplication::Get().ProcessKeyDownEvent(Event);
		FSlateApplication::Get().ProcessKeyUpEvent(Event);
	}
}
#endif

ACRCampaignAcceptance::ACRCampaignAcceptance()
{
#if !UE_BUILD_SHIPPING
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bTickEvenWhenPaused = true;
#endif
}

void ACRCampaignAcceptance::BeginPlay()
{
	Super::BeginPlay();
#if !UE_BUILD_SHIPPING
	FString Suffix;
	FParse::Value(FCommandLine::Get(), TEXT("CRCampaignCheck="), Mode);
	FParse::Value(FCommandLine::Get(), TEXT("CRCheckpointTest="), Suffix);
	auto* Store = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
	Directory = FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Campaign")/Mode);
	if (!(Mode == TEXT("Opening") || Mode == TEXT("Handoff") || Mode == TEXT("Select") || Mode == TEXT("Resume")) ||
		Suffix.IsEmpty() || !Store || Store->SlotName(0) != TEXT("CR04_TEST_") + Suffix + TEXT("_A"))
		{ FPlatformMisc::RequestExitWithStatus(false,2); return; }
	IFileManager::Get().MakeDirectory(*(Directory/TEXT("frames")),true);
	LastProgress = FPlatformTime::Seconds();
#endif
}

void ACRCampaignAcceptance::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
	if (Stage == ECampaignTest::Done) return;
	const double Now = FPlatformTime::Seconds();
	if (Now - LastProgress > 180) { Finish(false,TEXT("Campaign handoff timed out")); return; }
	auto* PC = Cast<ACRPlayerController>(GetWorld()->GetFirstPlayerController());
	if (!PC || !PC->GetInterface()) return;
	auto* HUD = PC->GetInterface();
	if (Stage == ECampaignTest::Menu)
	{
		auto* Store = GetGameInstance()->GetSubsystem<UCREchoStore>();
		if (!Store || !Store->IsReady() || !PC->bPrototypePaused) return;
		HUD->SetKeyboardFocus();
		if (Mode == TEXT("Resume"))
		{
			auto* Continue = Cast<UButton>(HUD->GetWidgetFromName(TEXT("Continue")));
			auto* First = GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
			if (!First || First->IsBusy()) return;
			if (!Store->HasUnfinishedCheckpoint() || !Continue || !Continue->GetIsEnabled())
				{ Finish(false,TEXT("Title cannot resume existing crossing checkpoint")); return; }
			Continue->OnClicked.Broadcast();
			if (First->HasCheckpoint()) Press(EKeys::Enter);
			if (PC->GetCampaignFilm()) { Finish(false,TEXT("Resume unexpectedly replayed film")); return; }
			UE_LOG(LogTemp,Display,TEXT("CR_CAMPAIGN_CHECK Title continued Echo checkpoint without replaying film"));
			Stage=ECampaignTest::Done;
			return; // The cross-process Echo fixture takes over in the destination world.
		}
		if (Mode == TEXT("Handoff") && !PC->bPrototypeEnded) return;
		auto* Start = Cast<UButton>(HUD->GetWidgetFromName(Mode == TEXT("Opening") ? TEXT("Restart") : TEXT("Chapters")));
		if (!Start || !Start->IsVisible() || !Start->GetIsEnabled()) return;
		if (Mode == TEXT("Handoff"))
		{
			const auto* Player = Cast<ACRCharacter>(PC->GetPawn());
			if (!Player) { Finish(false,TEXT("No ending pawn")); return; }
			ExpectedMag = Player->Weapon->Magazine;
			ExpectedReserve = Player->Weapon->Reserve;
			ExpectedHealth = Player->Health->Health;
			ExpectedOptic = GetWorld()->GetAuthGameMode<ACRGameMode>()->HasSurveyUpgrade();
		}
		Start->OnClicked.Broadcast();
		if (Mode == TEXT("Opening")) Press(EKeys::Up);
		Press(EKeys::Enter);
		if (!PC->GetCampaignFilm()) { Finish(false,TEXT("Selected menu action did not start the film")); return; }
		UAudioMixerBlueprintLibrary::StartRecordingOutput(this,38);
		bRecording = true;
		Stage = ECampaignTest::Film;
		LastProgress = Now;
	}
	if (Stage == ECampaignTest::Film)
	{
		auto* Film = PC->GetCampaignFilm();
		if (!Film) { StopSound(); Stage = ECampaignTest::Arrival; LastProgress = Now; return; }
		const double T = Film->GetPlaybackTime();
		const bool Record = FParse::Param(FCommandLine::Get(),TEXT("CRFilmCapture"));
		if ((Frames == 0 || T - LastFrame >= (Record ? .064 : 3.0)) && !FScreenshotRequest::IsScreenshotRequested())
		{
			LastFrame = T;
			FScreenshotRequest::RequestScreenshot(Directory/FString::Printf(TEXT("frames/%07d.png"),FMath::RoundToInt(T*1000)),true,false,false);
			++Frames;
		}
		if (Mode == TEXT("Select") && T > 3 && Frames >= 2)
		{
			const bool BeforeEnding = T < Film->GetDuration() * .5;
			StopSound(); Stage = ECampaignTest::Arrival; LastProgress = Now; Press(EKeys::Tab);
			if (!BeforeEnding || PC->GetCampaignFilm()) Finish(false,TEXT("Tab did not skip the recap during its first half"));
			else UE_LOG(LogTemp,Display,TEXT("CR_CAMPAIGN_CHECK Recap skipped by Tab at %.2fs"),T);
			return;
		}
		return;
	}
	if (Stage == ECampaignTest::Arrival)
	{
		const auto* Player = Cast<ACRCharacter>(PC->GetPawn());
		if (!Player || PC->GetCampaignFilm() || PC->bPrototypePaused) return;
		if (Mode == TEXT("Opening"))
		{
			if (UCREchoChapter::IsEchoWorld(GetWorld()) || !GetWorld()->GetAuthGameMode<ACRGameMode>()->IsCheckpointReady()) return;
		}
		else
		{
			const auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>();
			if (!UCREchoChapter::IsEchoWorld(GetWorld()) || !Echo || !Echo->IsStarted()) return;
			if (Echo->GetStep() != 0 || (Mode == TEXT("Handoff") && (ExpectedMag != Player->Weapon->Magazine ||
				ExpectedReserve != Player->Weapon->Reserve || !FMath::IsNearlyEqual(ExpectedHealth,Player->Health->Health,.1f) ||
				ExpectedOptic != GetWorld()->GetAuthGameMode<ACRGameMode>()->HasSurveyUpgrade())))
				{ Finish(false,TEXT("Cross-chapter arrival state differs")); return; }
		}
		Finish(Frames >= 2, Mode + TEXT(" film and playable destination verified"));
	}
#endif
}

void ACRCampaignAcceptance::EndPlay(const EEndPlayReason::Type Reason)
{
#if !UE_BUILD_SHIPPING
	if (bRecording)
	{
		StopSound();
		if (Stage == ECampaignTest::Film) Stage = ECampaignTest::Arrival;
	}
#endif
	Super::EndPlay(Reason);
}

#if !UE_BUILD_SHIPPING
void ACRCampaignAcceptance::StopSound()
{
	if (bRecording) UAudioMixerBlueprintLibrary::StopRecordingOutput(this,EAudioRecordingExportType::WavFile,TEXT("Soundtrack"),Directory);
	bRecording = false;
}
void ACRCampaignAcceptance::Finish(bool Pass, const FString& Reason)
{
	StopSound();
	Stage = ECampaignTest::Done;
	UE_LOG(LogTemp,Display,TEXT("CR_CAMPAIGN_CHECK pass=%d frames=%d %s"),Pass,Frames,*Reason);
	FFileHelper::SaveStringToFile(FString::Printf(TEXT("pass=%d\nframes=%d\n%s"),Pass,Frames,*Reason),*(Directory/TEXT("result.txt")));
	FPlatformMisc::RequestExitWithStatus(false,Pass ? 0 : 2);
}
#endif
