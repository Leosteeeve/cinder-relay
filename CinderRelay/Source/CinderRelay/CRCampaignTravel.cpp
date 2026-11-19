#include "CRPlayerController.h"
#include "CRCharacter.h"
#include "CREchoChapter.h"
#include "CRHUDWidget.h"
#include "CRHealthComponent.h"
#include "CRSignalFilm.h"
#include "CRWeaponComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

void ACRPlayerController::PresentFilm(bool bRecap, FSimpleDelegate After)
{
	if (CampaignFilm || bTravelling) return;
	auto Finished = FSimpleDelegate::CreateWeakLambda(this, [this, After]()
	{
		CampaignFilm = nullptr;
		if (bPrototypePaused && HUD) ApplyPause(true);
		After.ExecuteIfBound();
	});
	CampaignFilm = UCRSignalFilm::Open(this, bRecap, Finished);
	if (!CampaignFilm) Finished.ExecuteIfBound();
}

void ACRPlayerController::PlayCampaignFilm(bool bRecap)
{
	PresentFilm(bRecap, FSimpleDelegate());
}

void ACRPlayerController::EnterEchoCrossing(bool bContinue)
{
	if (bTravelling || CampaignFilm) return;
	const auto* Store = GetGameInstance()->GetSubsystem<UCREchoStore>();
	if (!Store || !Store->IsReady() || (bContinue && !Store->HasUnfinishedCheckpoint())) return;
	if (bContinue) TravelToEcho(true);
	else PresentFilm(true, FSimpleDelegate::CreateUObject(this, &ACRPlayerController::TravelToEcho, false));
}

void ACRPlayerController::TravelToEcho(bool bContinue)
{
	if (bTravelling) return;
	if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>(); Echo && Echo->IsSaving()) return;
	FString Options = bContinue ? TEXT("EchoStart=Continue") : TEXT("EchoStart=New");
	if (!bContinue && bPrototypeEnded && !UCREchoChapter::IsEchoWorld(GetWorld()))
	{
		const auto* Chapter = GetWorld()->GetAuthGameMode<ACRGameMode>();
		const auto* Technician = Cast<ACRCharacter>(GetPawn());
		if (Chapter && Technician && Technician->Health && Technician->Weapon)
			Options += FString::Printf(TEXT("?EchoOptic=%d?EchoMag=%d?EchoReserve=%d?EchoHealth=%.2f"),
				Chapter->HasSurveyUpgrade(), Technician->Weapon->Magazine, Technician->Weapon->Reserve, Technician->Health->Health);
	}
	bTravelling = true;
	CloseFieldPackForTravel();
	ApplyPause(false);
	UE_LOG(LogTemp, Display, TEXT("CR_CAMPAIGN Travel EchoCrossing %s"), *Options);
	UGameplayStatics::OpenLevel(this, TEXT("/Game/Generated/Chapter02/Maps/L_CH02_EchoCrossing"), true, Options);
}

void ACRPlayerController::ReturnToTitle()
{
	if (bTravelling || CampaignFilm) return;
	if (auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>(); Echo && Echo->IsSaving()) return;
	bTravelling = true;
	CloseFieldPackForTravel();
	ApplyPause(false);
	UGameplayStatics::OpenLevel(this, TEXT("/Game/Generated/Phase01B/Maps/L_CH01_Persistent"));
}

void ACRPlayerController::EchoUpdated()
{
	auto* Echo = GetWorld()->GetSubsystem<UCREchoChapter>();
	if (!Echo || !HUD) return;
	if (bEchoInputHeld && Echo->IsStarted())
	{
		bEchoInputHeld=false;
		SetIgnoreMoveInput(false);
		SetIgnoreLookInput(false);
		if (auto* Technician = Cast<ACRCharacter>(GetPawn())) Technician->Weapon->SetPresentationLocked(false);
	}
	const FText Notice = Echo->GetNotice();
	if (!Notice.IsEmpty() && !LastEchoNotice.EqualTo(Notice)) ShowSubtitle(Notice, 5.f);
	LastEchoNotice = Notice;
	if (Echo->IsComplete() && !Echo->IsSaving() && !Echo->NeedsRetry() && !bPrototypeEnded) FinishChapterPresentation();
	else RefreshHUD();
}
