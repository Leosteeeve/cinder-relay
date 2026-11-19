#include "CREchoChapter.h"
#include "CREchoStation.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "CRHealthComponent.h"
#include "CRPlayerController.h"
#include "CRWeaponComponent.h"
#include "Components/CapsuleComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Crc.h"
#include "TimerManager.h"
#include "UObject/StrongObjectPtr.h"
#if !UE_BUILD_SHIPPING
void StartEchoIntegrationCheck(UWorld& World,const FString& Route);
#endif

namespace
{
	const FName Anchors[] = {TEXT("ECHO_ARRIVAL"), TEXT("ECHO_LINE"), TEXT("ECHO_ARCHIVE"), TEXT("ECHO_AERIAL"), TEXT("ECHO_SENT")};
	const FVector Floors[] = {{-1250,0,0},{1400,250,0},{4960,-235,0},{7500,-150,420},{8160,260,420}};
	UCREchoStore* StoreFor(const UObject* Context)
	{
		const UWorld* World = Context ? Context->GetWorld() : nullptr;
		return World && World->GetGameInstance() ? World->GetGameInstance()->GetSubsystem<UCREchoStore>() : nullptr;
	}
	bool SafeTestSuffix(const FString& S)
	{
		if (S.IsEmpty() || S.Len() > 40) return false;
		for (TCHAR C : S) if (!FChar::IsAlnum(C) && C != TEXT('_')) return false;
		return true;
	}
}

uint32 UCREchoSave::Digest() const
{
	uint32 HealthBits;
	FMemory::Memcpy(&HealthBits,&Health,sizeof(Health));
	const FString Payload = FString::Printf(TEXT("%d|%s|%s|%lld|%d|%d|%d|%d|%d|%u|%d|%d"),
		Version,*Chapter.ToString(),*Checkpoint.ToString(),Generation,Step,Bearing,bLog,bBridge,bOptic,HealthBits,Mag,Reserve);
	return FCrc::StrCrc32(*Payload);
}
void UCREchoSave::Seal()
{
	check(FMath::IsWithinInclusive(Step,0,4));
	Checkpoint = Anchors[Step];
	Checksum = Digest();
}
bool UCREchoSave::Valid() const
{
	return Version == 1 && Chapter == TEXT("CH02_EchoCrossing") && FMath::IsWithinInclusive(Step,0,4)
		&& Checkpoint == Anchors[Step] && Generation > 0 && Generation < MAX_int64
		&& FMath::IsWithinInclusive(Bearing,0,300) && Bearing % 60 == 0
		&& (Step >= 2 || Bearing == 0) && (Step < 3 || Bearing == 120)
		&& FMath::IsFinite(Health) && Health > 0 && Health <= 100
		&& FMath::IsWithinInclusive(Mag,0,5) && FMath::IsWithinInclusive(Reserve,0,100) && Checksum == Digest();
}
FString UCREchoStore::Slot(int32 Index) const { return Prefix + (Index == 0 ? TEXT("_A") : TEXT("_B")); }
void UCREchoStore::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
#if !UE_BUILD_SHIPPING
	FString Suffix, Route;
	const bool HasTest = FParse::Value(FCommandLine::Get(),TEXT("CRCheckpointTest="),Suffix);
	const bool IsCheck = FParse::Value(FCommandLine::Get(),TEXT("CREchoCheck="),Route);
	if ((IsCheck || HasTest) && (!HasTest || !SafeTestSuffix(Suffix)))
	{
		bEnabled = false;
		UE_LOG(LogTemp,Error,TEXT("CR_ECHO_SAVE Invalid test namespace; persistence disabled"));
		return;
	}
	if (HasTest) Prefix = TEXT("CR04_TEST_") + Suffix + TEXT("_CH02_Echo");
#endif
	PendingReads = 2;
	Reads.SetNum(2);
	for (int32 I=0; I<2; ++I)
		UGameplayStatics::AsyncLoadGameFromSlot(Slot(I),0,FAsyncLoadGameFromSlotDelegate::CreateUObject(this,&UCREchoStore::ReadFinished));
}
void UCREchoStore::ReadFinished(const FString& Name,int32,USaveGame* Value)
{
	if (!bEnabled || PendingReads <= 0) return;
	const int32 I = Name == Slot(0) ? 0 : Name == Slot(1) ? 1 : INDEX_NONE;
	if (I == INDEX_NONE) return;
	UCREchoSave* Candidate = Cast<UCREchoSave>(Value);
	if (Candidate && Candidate->Valid()) Reads[I] = Candidate;
	else if (Value) UE_LOG(LogTemp,Warning,TEXT("CR_ECHO_SAVE Rejected slot=%s"),*Name);
	if (--PendingReads != 0) return;
	for (int32 K=0; K<2; ++K)
		if (Reads[K] && (!Latest || Latest->Generation < Reads[K]->Generation)) { LatestIndex=K; Latest=Reads[K]; }
	LastGeneration=Latest ? Latest->Generation : 0;
	if (Reads[0] && Reads[1] && Reads[0]->Generation == Reads[1]->Generation && Reads[0]->Checksum != Reads[1]->Checksum)
	{
		Latest=nullptr; LatestIndex=INDEX_NONE;
		UE_LOG(LogTemp,Warning,TEXT("CR_ECHO_SAVE Conflicting generations retained"));
	}
	Reads.Reset();
	UE_LOG(LogTemp,Display,TEXT("CR_ECHO_SAVE Scan prefix=%s step=%d"),*Prefix,Latest ? Latest->Step : -1);
	OnAvailabilityChanged.Broadcast();
}
bool UCREchoStore::Save(UCREchoSave* Snapshot)
{
	if (!bEnabled || !Snapshot || PendingReads || LastGeneration >= MAX_int64-1) return false;
	Snapshot->Generation = LastGeneration+1;
	Snapshot->Seal();
	if (!Snapshot->Valid()) return false;
	if (Writing) Queued=Snapshot; else Write(Snapshot);
	return true;
}
void UCREchoStore::Write(UCREchoSave* Value)
{
	Writing = Value;
	WritingIndex = LatestIndex == 0 ? 1 : 0;
	Writing->Generation = LastGeneration+1;
	Writing->Seal();
	UGameplayStatics::AsyncSaveGameToSlot(Writing,Slot(WritingIndex),0,FAsyncSaveGameToSlotDelegate::CreateUObject(this,&UCREchoStore::Written));
}
void UCREchoStore::Written(const FString& Name,int32,bool Success)
{
	if (!bEnabled || !Writing || Name != Slot(WritingIndex)) return;
	// Keep the completed snapshot rooted during notification. A queued successor
	// starts first so listeners see the actual writer state even on the last callback.
	TStrongObjectPtr<UCREchoSave> Finished(Writing.Get());
	if (Success) { Latest=Writing; LatestIndex=WritingIndex; LastGeneration=Writing->Generation; }
	Writing=nullptr;
	if (UCREchoSave* Next=Queued.Get()) { Queued=nullptr; Write(Next); }
	UE_LOG(LogTemp,Display,TEXT("CR_ECHO_SAVE Written slot=%s step=%d generation=%lld success=%d"),
		*Name,Finished->Step,Finished->Generation,Success);
	OnWritten.Broadcast(Finished.Get(),Success);
	OnAvailabilityChanged.Broadcast();
}
void UCREchoStore::Deinitialize()
{
	bEnabled=false; Queued=nullptr; OnAvailabilityChanged.Clear(); OnWritten.Clear(); Super::Deinitialize();
}
bool UCREchoChapter::IsEchoWorld(const UWorld* World)
{
	return World && World->GetMapName().EndsWith(TEXT("L_CH02_EchoCrossing"));
}
bool UCREchoChapter::HasCheckpoint(const UObject* Context) { auto* S=StoreFor(Context); return S && S->HasCheckpoint(); }
bool UCREchoChapter::HasUnfinishedCheckpoint(const UObject* Context) { auto* S=StoreFor(Context); return S && S->HasUnfinishedCheckpoint(); }
bool UCREchoChapter::IsSaving() const { auto* S=StoreFor(this); return bPersistent && S && S->IsSaving(); }

void UCREchoChapter::OnWorldBeginPlay(UWorld& World)
{
	Super::OnWorldBeginPlay(World);
	if (!IsEchoWorld(&World)) return;
	FString Mode = World.URL.GetOption(TEXT("EchoStart="),TEXT(""));
#if !UE_BUILD_SHIPPING
	FString Route;
	if (FParse::Value(FCommandLine::Get(),TEXT("CREchoCheck="),Route))
	{
		if (Route == TEXT("Write")) Mode=TEXT("New");
		if (Route == TEXT("Read")) Mode=TEXT("Continue");
	}
#endif
	bContinue = Mode.Equals(TEXT("Continue"),ESearchCase::IgnoreCase);
	bPersistent = World.WorldType == EWorldType::Game && (bContinue || Mode.Equals(TEXT("New"),ESearchCase::IgnoreCase));
	if (auto* Store=StoreFor(this)) Store->OnWritten.AddUObject(this,&UCREchoChapter::SaveFinished);
	World.GetTimerManager().SetTimer(StartTimer,this,&UCREchoChapter::TryStart,.04f,true,0.f);
#if !UE_BUILD_SHIPPING
	if (!Route.IsEmpty()) StartEchoIntegrationCheck(World,Route);
#endif
}
void UCREchoChapter::TryStart()
{
	UCREchoStore* Store=StoreFor(this);
	auto* PC=Cast<ACRPlayerController>(GetWorld()->GetFirstPlayerController());
	auto* Player=PC ? Cast<ACRCharacter>(PC->GetPawn()) : nullptr;
	if (!Player || !Player->HasActorBegunPlay() || !Player->Weapon->Data || !Store) return;
	if (bPersistent && Store->IsEnabled() && !Store->IsReady()) return;
	GetWorld()->GetTimerManager().ClearTimer(StartTimer);
	if (bPersistent && (!Store->IsEnabled() || (bContinue && !Store->HasCheckpoint())))
	{
		Notice=FText::FromString(TEXT("No verified Echo checkpoint. Restart Echo Crossing from the pause menu."));
		OnChanged.Broadcast(); return;
	}
	bool Optic = false;
	auto* Game=GetWorld()->GetAuthGameMode<ACRGameMode>();
	if (bContinue && bPersistent)
	{
		const UCREchoSave* Saved = Store->GetLatest();
		Step=Saved->Step; Bearing=Saved->Bearing; bLog=Saved->bLog; bBridge=Saved->bBridge; Optic=Saved->bOptic;
		if (!PlaceAtCheckpoint(*Player) || !Player->Weapon->RestoreCheckpointAmmo(Saved->Mag,Saved->Reserve)
			|| !Player->Health->RestoreCheckpointHealth(Saved->Health))
		{
			Notice=FText::FromString(TEXT("Unable to restore the Echo checkpoint safely. Restart from the pause menu."));
			OnChanged.Broadcast(); return;
		}
		UE_LOG(LogTemp,Display,TEXT("CR_ECHO Restore anchor=%s step=%d bearing=%d fieldlog=%d bridge=%d"),
			*Saved->Checkpoint.ToString(),Step,Bearing,bLog,bBridge);
	}
	else if (bPersistent)
	{
		if (!PlaceAtCheckpoint(*Player))
		{
			Notice=FText::FromString(TEXT("The arrival floor is unavailable. Restart Echo Crossing from the pause menu."));
			OnChanged.Broadcast(); return;
		}
		const FURL& URL=GetWorld()->URL;
		Optic=FCString::Atoi(URL.GetOption(TEXT("EchoOptic="),TEXT("0"))) == 1;
		const int32 Mag=FCString::Atoi(URL.GetOption(TEXT("EchoMag="),TEXT("5")));
		const int32 Reserve=FCString::Atoi(URL.GetOption(TEXT("EchoReserve="),TEXT("25")));
		const float Health=FCString::Atof(URL.GetOption(TEXT("EchoHealth="),TEXT("100")));
		Player->Weapon->RestoreCheckpointAmmo(FMath::Clamp(Mag,0,5),FMath::Clamp(Reserve,0,100));
		Player->Health->RestoreCheckpointHealth(FMath::IsFinite(Health) ? FMath::Clamp(Health,1.f,100.f) : 100.f);
	}
	if (Optic && Game) { Game->TryCollectSurveyOptic(TEXT("CR03_YardCache")); Game->TryApplySurveyUpgrade(); }
	bStarted=true;
	if (bPersistent && !bContinue) SaveProgress();
	OnChanged.Broadcast();
	UE_LOG(LogTemp,Display,TEXT("CR_ECHO Ready step=%d optic=%d hp=%.2f mag=%d reserve=%d persistent=%d"),
		Step,Optic,Player->Health->Health,Player->Weapon->Magazine,Player->Weapon->Reserve,bPersistent);
}
bool UCREchoChapter::PlaceAtCheckpoint(ACRCharacter& Player) const
{
	const FVector Floor=Floors[Step];
	FCollisionQueryParams Query(SCENE_QUERY_STAT(EchoCheckpoint),false,&Player);
	FHitResult Hit;
	if (!GetWorld()->LineTraceSingleByChannel(Hit,Floor+FVector(0,0,130),Floor-FVector(0,0,70),ECC_Visibility,Query)
		|| Hit.ImpactNormal.Z < .7 || FMath::Abs(Hit.ImpactPoint.Z-Floor.Z)>35) return false;
	const UCapsuleComponent* Capsule=Player.GetCapsuleComponent();
	const FVector Stand=Hit.ImpactPoint+FVector(0,0,Capsule->GetScaledCapsuleHalfHeight()+4);
	if (GetWorld()->OverlapBlockingTestByChannel(Stand,FQuat::Identity,ECC_Pawn,Capsule->GetCollisionShape(),Query)) return false;
	return Player.TeleportTo(Stand,FRotator::ZeroRotator);
}
void UCREchoChapter::SaveProgress()
{
	if (!bPersistent || !bStarted) return;
	auto* Player=Cast<ACRCharacter>(UGameplayStatics::GetPlayerPawn(this,0));
	auto* Game=GetWorld()->GetAuthGameMode<ACRGameMode>();
	auto* Store=StoreFor(this);
	if (!Player || !Game || !Store) return;
	auto* Snapshot=NewObject<UCREchoSave>(Store);
	Snapshot->Step=Step; Snapshot->Bearing=Bearing; Snapshot->bLog=bLog; Snapshot->bBridge=bBridge;
	Snapshot->bOptic=Game->HasSurveyUpgrade(); Snapshot->Health=Player->Health->Health;
	Snapshot->Mag=Player->Weapon->Magazine; Snapshot->Reserve=Player->Weapon->Reserve;
	bSaveFailed=!Store->Save(Snapshot);
}
void UCREchoChapter::SaveFinished(const UCREchoSave* S,bool Success)
{
	if (!bStarted || !bPersistent || S->Step!=Step || S->Bearing!=Bearing || S->bLog!=bLog || S->bBridge!=bBridge) return;
	bSaveFailed=!Success;
	if (auto* PC=Cast<ACRPlayerController>(GetWorld()->GetFirstPlayerController()))
		PC->ShowCheckpointFeedback(Success ? TEXT("ECHO CHECKPOINT SAVED") : TEXT("ECHO SAVE FAILED / Use the station to retry."));
	OnChanged.Broadcast();
}
void UCREchoChapter::RetrySave() { if (bSaveFailed) { SaveProgress(); OnChanged.Broadcast(); } }
void UCREchoChapter::RecordBridgeRelease()
{
	if (!bStarted || bBridge) return;
	bBridge=true; SaveProgress(); OnChanged.Broadcast();
}
void UCREchoChapter::Deinitialize()
{
	if (GetWorld()) GetWorld()->GetTimerManager().ClearTimer(StartTimer);
	if (auto* Store=StoreFor(this)) Store->OnWritten.RemoveAll(this);
	OnChanged.Clear(); Super::Deinitialize();
}

FText UCREchoChapter::GetObjectiveText() const
{
	static const TCHAR* Lines[]={
		TEXT("Sample the west line tap.\nFollow the cable to the intake."),
		TEXT("Find the reference strip.\nCross the river to the chart house."),
		TEXT("Tune the aerial.\nClimb the ramp, then match the strip and test the return."),
		TEXT("Transmit the carrier.\nUse the east transmitter on the upper deck."),
		TEXT("Transmission acknowledged.\nThe second pulse crossed the water.")};
	return FText::FromString(Lines[Step]);
}
FText UCREchoChapter::GetGuideText() const
{
	static const TCHAR* Guides[]={
		TEXT("The line tap stands on the west bank before the bridge. Use E at its cabinet."),
		TEXT("Take the north walkway or release the south boom. The inspection platform holds an optional observer log. The chart house is across the river."),
		TEXT("The reference strip reads 120 degrees. On the aerial deck, use E on TURN to advance by 60 degrees. Aim at TEST RETURN and use E to check the setting."),
		TEXT("The aerial is locked at 120 degrees. Walk east along the deck to the separate transmitter and send the return."),
		TEXT("The matched pulse crossed the river and a second pulse came back.")};
	return FText::FromString(Guides[Step]);
}
bool UCREchoChapter::CanOperate(int32 Index) const
{
	return bStarted && ((Index == 4 && !bLog) || (Step < 4 && Index == Step) || bSaveFailed);
}
void UCREchoChapter::Operate(int32 Index,bool bConfirm)
{
	if (!CanOperate(Index)) return;
	if (bSaveFailed && !(Index == 4 && !bLog) && !(Step < 4 && Index == Step)) { RetrySave(); return; }
	bool Accepted = true;
	if (Index == 4)
	{
		bLog=true;
		Notice=FText::FromString(TEXT("Observer log recovered: the first pulse dies at the river. Record the second return. Filed in the Field Pack."));
	}
	else if (Index == 2 && !bConfirm)
	{
		Bearing=(Bearing+60)%360;
		Notice=FText::FromString(FString::Printf(TEXT("Aerial turning to %03d degrees."),Bearing));
	}
	else if (Index == 2 && Bearing != 120)
	{
		++Rejections; Accepted=false;
		Notice=FText::FromString(TEXT("Local echo only. The chart-house strip marks 120 degrees. Turn the aerial, then test again."));
	}
	else
	{
		++Step;
		static const TCHAR* Results[]={TEXT("Carrier reaches the far bank. Find its reference in the chart house."),
			TEXT("Reference strip recovered: RETURN BEARING 120 degrees. The aerial deck is uphill."),
			TEXT("Matched return from across the river. Aerial locked. The transmitter is ready."),
			TEXT("A second pulse returns across the water. Transmission acknowledged.")};
		Notice=FText::FromString(Results[Step-1]);
	}
	if (Accepted) SaveProgress();
	UE_LOG(LogTemp,Display,TEXT("CR_ECHO Operate station=%d confirm=%d step=%d bearing=%03d accepted=%d log=%d"),Index,bConfirm,Step,Bearing,Accepted,bLog);
	OnChanged.Broadcast();
}
