#include "CREchoChapter.h"
#include "CREchoStation.h"
#include "CREchoBridgeCatch.h"
#include "CRCharacter.h"
#include "CRHealthComponent.h"
#include "CRGameMode.h"
#include "CRPlayerController.h"
#include "CRWeaponComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/GameInstance.h"
#include "Engine/LocalPlayer.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

ACREchoAcceptance::ACREchoAcceptance()
{
#if !UE_BUILD_SHIPPING
	PrimaryActorTick.bCanEverTick=true;
	PrimaryActorTick.bTickEvenWhenPaused=true;
#endif
}
#if !UE_BUILD_SHIPPING
void StartEchoIntegrationCheck(UWorld& World,const FString& Route)
{
	if (auto* Check=World.SpawnActor<ACREchoAcceptance>()) Check->Route=Route;
}
void ACREchoAcceptance::Next(const TCHAR* Event)
{
	StageTime=FPlatformTime::Seconds(); ++Stage;
	Events+=FString::Printf(TEXT("stage=%d %s\n"),Stage,Event);
	UE_LOG(LogTemp,Display,TEXT("CR_ECHO_CHECK stage=%d %s"),Stage,Event);
}
void ACREchoAcceptance::Finish(bool Pass,const TCHAR* Reason)
{
	bFinished=true;
	const FString Dir=FPaths::ProjectSavedDir()/TEXT("EchoCheck")/(Route==TEXT("Write")?TEXT("Write"):TEXT("Read"));
	IFileManager::Get().MakeDirectory(*Dir,true);
	const FString Receipt=FString::Printf(TEXT("{\"passed\":%s,\"stage\":%d,\"reason\":\"%s\"}"),Pass?TEXT("true"):TEXT("false"),Stage,Reason);
	FFileHelper::SaveStringToFile(Receipt,*(Dir/TEXT("acceptance.json")));
	FFileHelper::SaveStringToFile(Events,*(Dir/TEXT("route.txt")));
	UE_LOG(LogTemp,Display,TEXT("CR_ECHO_FINISH %s"),*Receipt);
	if (auto* PC=Cast<ACRPlayerController>(GetWorld()->GetFirstPlayerController())) PC->ExitPrototype();
	else FPlatformMisc::RequestExitWithStatus(false,Pass?0:1);
}
#endif
void ACREchoAcceptance::Tick(float Delta)
{
	Super::Tick(Delta);
#if !UE_BUILD_SHIPPING
	if (bFinished) return;
	const double Now=FPlatformTime::Seconds();
	if (Started==0) { Started=Now; StageTime=Now; }
	if (Route!=TEXT("Write") && Route!=TEXT("Read")) { Finish(false,TEXT("Unknown test route")); return; }
	if (Now-StageTime>100 || Now-Started>300) { Finish(false,TEXT("Timed out in current stage")); return; }
	UCREchoChapter* C=GetWorld()->GetSubsystem<UCREchoChapter>();
	UCREchoStore* Store=GetGameInstance()->GetSubsystem<UCREchoStore>();
	auto* PC=Cast<ACRPlayerController>(GetWorld()->GetFirstPlayerController());
	auto* P=PC?Cast<ACRCharacter>(PC->GetPawn()):nullptr;
	if (!Store->IsEnabled()) { Finish(false,TEXT("Dedicated test slot required")); return; }
	if (!P || !C->IsStarted() || !PC->GetLocalPlayer()) return;
	auto* Input=PC->GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>();
	if (!Input) return;
	auto Inject=[&](const UInputAction* Action){ Input->InjectInputForAction(Action,FInputActionValue(1.f),{},{}); };
	if (!Points.IsEmpty())
	{
		const FVector2D D=Points[0]-FVector2D(P->GetActorLocation());
		if (D.Size()<30) { Points.RemoveAt(0); return; }
		PC->SetControlRotation(FRotator(0,FMath::RadiansToDegrees(FMath::Atan2(D.Y,D.X)),0));
		Inject(P->ForwardAction); Inject(P->SprintAction); return;
	}
	auto Station=[&](int32 Index)->ACREchoStation*{
		for (TActorIterator<ACREchoStation> It(GetWorld());It;++It) if (It->StationIndex==Index) return *It;
		return nullptr;
	};
	auto Press=[&](int32 Index,bool Confirm=false){
		auto* S=Station(Index);
		if (!S) { Finish(false,TEXT("Missing authored station")); return; }
		const FVector Target=(Confirm ? S->ConfirmControl : S->TurnControl)->GetComponentLocation();
		PC->SetControlRotation((Target-P->Camera->GetComponentLocation()).Rotation());
		if (Now-LastPulse>.38 && !S->IsActorTickEnabled() && S->CanInteract_Implementation(P))
		{ LastPulse=Now; Inject(P->InteractAction); }
	};
	if (Stage==0)
	{
		const UCREchoSave* Saved=Store->GetLatest();
		if (Route==TEXT("Write"))
		{
			if (C->GetStep()!=0 || C->HasFieldLog() || C->IsBridgeReleased()) { Finish(false,TEXT("Fresh start was not clean")); return; }
			Points={{0,0},{800,0},{1400,250}};
			Next(TEXT("Fresh start; walking to line tap")); return;
		}
		if (!Saved || Saved->Step!=2 || !C->HasFieldLog() || !C->IsBridgeReleased() || C->GetStep()!=2 ||
			FVector::Dist2D(P->GetActorLocation(),FVector(4960,-235,0))>90 ||
			P->Weapon->Magazine!=Saved->Mag || P->Weapon->Reserve!=Saved->Reserve ||
			!FMath::IsNearlyEqual(P->Health->Health,Saved->Health) || Saved->bOptic!=GetWorld()->GetAuthGameMode<ACRGameMode>()->HasSurveyUpgrade())
		{ Finish(false,TEXT("Cross-process archive or equipment did not restore")); return; }
		Points={{5040,-80},{5520,0},{5890,0},{7180,0},{7350,0},{7500,-150}};
		Next(TEXT("Verified archive checkpoint, optional discoveries, health, ammo and optic; walking to aerial")); return;
	}
	if (Route==TEXT("Write"))
	{
		switch(Stage)
		{
		case 1:
			if (C->GetStep()!=1) { Press(0); return; }
			Points={{1550,0},{1610,-270}}; BeforeShot=P->Weapon->Magazine; Next(TEXT("Line tap powered; approaching optional bridge")); return;
		case 2:
		{
			TActorIterator<ACREchoBridgeCatch> Catch(GetWorld());
			if (!Catch) { Finish(false,TEXT("Missing optional bridge")); return; }
			if (Catch->IsOpen())
			{
				if (!C->IsBridgeReleased() || P->Weapon->Magazine!=BeforeShot-1) { Finish(false,TEXT("Bridge did not respond to a single accepted shot")); return; }
				Points={{1570,0},{1640,430},{2100,430},{3010,430},{3020,760}}; Next(TEXT("Verified optional bridge and one spent round; taking survey walkway")); return;
			}
			PC->SetControlRotation((Catch->CatchTarget->GetComponentLocation()-P->Camera->GetComponentLocation()).Rotation());
			if (!C->IsBridgeReleased() && Now-LastPulse>.6 && Now-StageTime>.7) { LastPulse=Now; Inject(P->FireAction); }
			return;
		}
		case 3:
			if (!C->HasFieldLog()) { Press(4); return; }
			Points={{3020,430},{4060,430},{4390,430},{4580,-235},{4960,-235}};
			Next(TEXT("Optional field log filed; crossing to chart house")); return;
		case 4:
			if (C->GetStep()!=2) { Press(1); return; }
			if (!Store->IsReady()) return;
			if (!Store->GetLatest() || Store->GetLatest()->Step!=2 || !Store->GetLatest()->bLog)
				{ Finish(false,TEXT("Archive was not persisted")); return; }
			Finish(true,TEXT("Reached archive on foot and verified native async checkpoint")); return;
		}
	}
	else
	{
		switch(Stage)
		{
		case 1:
			if (!C->GetRejectedBearings()) { Press(2,true); return; }
			if (C->GetStep()!=2 || C->GetBearing()!=0 || !C->GetNotice().ToString().Contains(TEXT("120")))
				{ Finish(false,TEXT("Incorrect return was not rejected with a readable clue")); return; }
			Next(TEXT("Wrong bearing rejected; operations displayed the chart clue")); return;
		case 2:
			if (C->GetBearing()!=120) { Press(2); return; }
			if (auto* S=Station(2); S && !S->IsActorTickEnabled() && FMath::Abs(FMath::FindDeltaAngleDegrees(S->Rotor->GetRelativeRotation().Yaw,120))<1)
				Next(TEXT("Two independent E turns physically moved aerial to 120 degrees"));
			return;
		case 3:
			if (C->GetStep()!=3) { Press(2,true); return; }
			Points={{7500,100},{7920,260},{8160,260}};
			Next(TEXT("Carrier locked; walking across upper deck to transmitter")); return;
		case 4:
			if (!C->IsComplete()) { Press(3); return; }
			if (!Store->IsReady()) return;
			if (!Store->GetLatest() || Store->GetLatest()->Step!=4) { Finish(false,TEXT("Transmission checkpoint failed")); return; }
			Finish(true,TEXT("Correct return transmitted and native final checkpoint completed")); return;
		}
	}
#endif
}
