#include "CREchoStation.h"
#include "CREchoChapter.h"
#include "CRAudioSettingsSubsystem.h"
#include "CRCharacter.h"
#include "Camera/CameraComponent.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/World.h"

ACREchoStation::ACREchoStation()
{
	PrimaryActorTick.bCanEverTick=true;
	PrimaryActorTick.bStartWithTickEnabled=false;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
	Panel=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Panel"));
	Rotor=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Rotor"));
	for (UStaticMeshComponent* C : {Panel.Get(),Rotor.Get()})
	{
		C->SetupAttachment(RootComponent);
		C->SetCollisionProfileName(TEXT("NoCollision"));
		C->SetCanEverAffectNavigation(false);
	}
	Rotor->SetMobility(EComponentMobility::Movable);
	Rotor->SetRelativeLocation(FVector(0,195,40));
	TurnControl=CreateDefaultSubobject<UBoxComponent>(TEXT("TurnControl"));
	ConfirmControl=CreateDefaultSubobject<UBoxComponent>(TEXT("ConfirmControl"));
	for (UBoxComponent* C : {TurnControl.Get(),ConfirmControl.Get()})
	{
		C->SetupAttachment(RootComponent);
		C->SetCollisionProfileName(TEXT("NoCollision"));
		C->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
		C->SetCollisionResponseToAllChannels(ECR_Ignore);
		C->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
		C->SetGenerateOverlapEvents(false);
		C->SetCanEverAffectNavigation(false);
	}
	Display=CreateDefaultSubobject<UTextRenderComponent>(TEXT("Display"));
	Display->SetupAttachment(RootComponent);
	Display->SetRelativeLocation(FVector(26,0,62));
	Display->SetWorldSize(12.f);
	Display->SetHorizontalAlignment(EHTA_Center);
	Display->SetVerticalAlignment(EVRTA_TextCenter);
	Display->SetTextRenderColor(FColor(180,239,227));
}
void ACREchoStation::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	const bool Aerial = StationIndex==2;
	TurnControl->SetRelativeLocation(FVector(13,Aerial ? -43 : 0,0));
	TurnControl->SetBoxExtent(FVector(18,Aerial ? 40 : 52,71));
	ConfirmControl->SetRelativeLocation(FVector(13,47,0));
	ConfirmControl->SetBoxExtent(FVector(18,40,71));
	ConfirmControl->SetCollisionEnabled(Aerial ? ECollisionEnabled::QueryOnly : ECollisionEnabled::NoCollision);
	Rotor->SetVisibility(Aerial);
}
void ACREchoStation::BeginPlay()
{
	Super::BeginPlay();
	// Python authoring can change the instance index after native construction.
	// Apply the serialized station role again before exposing the interaction.
	const bool Aerial=StationIndex==2;
	TurnControl->SetRelativeLocation(FVector(13,Aerial ? -43 : 0,0));
	TurnControl->SetBoxExtent(FVector(18,Aerial ? 40 : 52,71));
	ConfirmControl->SetCollisionEnabled(Aerial ? ECollisionEnabled::QueryOnly : ECollisionEnabled::NoCollision);
	Rotor->SetVisibility(Aerial);
	if (auto* Chapter=GetWorld()->GetSubsystem<UCREchoChapter>()) Chapter->OnChanged.AddUObject(this,&ACREchoStation::Refresh);
	Refresh();
}
void ACREchoStation::EndPlay(const EEndPlayReason::Type Reason)
{
	if (auto* Chapter=GetWorld()->GetSubsystem<UCREchoChapter>()) Chapter->OnChanged.RemoveAll(this);
	Super::EndPlay(Reason);
}
void ACREchoStation::Refresh()
{
	const auto* C=GetWorld()->GetSubsystem<UCREchoChapter>();
	if (!C) return;
	const int32 Step=C->GetStep();
	FString Label;
	switch (StationIndex)
	{
		case 0: Label=Step>0 ? TEXT("LINE TAP / CARRIER LIVE") : TEXT("LINE TAP / OPEN CIRCUIT"); break;
		case 1: Label=Step>=2 ? TEXT("REFERENCE STRIP / 120 DEG") : TEXT("CHART ARCHIVE / REFERENCE STRIP"); break;
		case 2:
			Label=FString::Printf(TEXT("AERIAL / %03d DEG\n%s"),C->GetBearing(),
				Step>=3 ? TEXT("RETURN LOCKED") : TEXT("TEST                 TURN"));
			TargetYaw=C->GetBearing();
			if (!FMath::IsNearlyZero(FMath::FindDeltaAngleDegrees(Rotor->GetRelativeRotation().Yaw,TargetYaw),.1f))
				SetActorTickEnabled(true);
			break;
		case 3: Label=Step==4 ? TEXT("TRANSMISSION ACKNOWLEDGED") : TEXT("EAST TRANSMITTER"); break;
		case 4: Label=C->HasFieldLog() ? TEXT("OBSERVER LOG / FILED") : TEXT("OBSERVER'S FIELD LOG"); break;
	}
	Display->SetText(FText::FromString(Label));
}
void ACREchoStation::Tick(float Delta)
{
	Super::Tick(Delta);
	const float Next=FMath::FixedTurn(Rotor->GetRelativeRotation().Yaw,TargetYaw,150.f*Delta);
	Rotor->SetRelativeRotation(FRotator(0,Next,0));
	if (FMath::IsNearlyZero(FMath::FindDeltaAngleDegrees(Next,TargetYaw),.1f)) SetActorTickEnabled(false);
}
UBoxComponent* ACREchoStation::AimedControl(ACRCharacter* Player) const
{
	if (!Player || !Player->CanInteractWith(this)) return nullptr;
	const FVector Start=Player->Camera->GetComponentLocation();
	const FVector End=Start+Player->Camera->GetForwardVector()*Player->InteractionRange;
	FHitResult Hit;
	FCollisionQueryParams Query(SCENE_QUERY_STAT(EchoControl),false,Player);
	if (!GetWorld()->LineTraceSingleByChannel(Hit,Start,End,ECC_Visibility,Query)) return nullptr;
	if (Hit.GetComponent()==TurnControl) return TurnControl;
	return Hit.GetComponent()==ConfirmControl && StationIndex==2 ? ConfirmControl.Get() : nullptr;
}
bool ACREchoStation::CanInteract_Implementation(ACRCharacter* Player) const
{
	auto* C=GetWorld()->GetSubsystem<UCREchoChapter>();
	return C && C->CanOperate(StationIndex) && !IsActorTickEnabled() && AimedControl(Player);
}
FText ACREchoStation::GetInteractionPrompt_Implementation(ACRCharacter* Player) const
{
	const auto* C=GetWorld()->GetSubsystem<UCREchoChapter>();
	if (!C || !C->IsStarted()) return FText::GetEmpty();
	if (C->NeedsRetry()) return FText::FromString(TEXT("[E] Retry saving Echo checkpoint"));
	if (!C->CanOperate(StationIndex))
	{
		if (StationIndex==1 && C->GetStep()>=2) return FText::FromString(TEXT("Reference strip / return bearing 120 degrees."));
		if (StationIndex==4) return FText::FromString(TEXT("Observer log filed in the Field Pack."));
		return C->GetObjectiveText();
	}
	switch (StationIndex)
	{
		case 0: return FText::FromString(TEXT("[E] Close the line tap"));
		case 1: return FText::FromString(TEXT("[E] Read and keep the reference strip"));
		case 2:
			if (IsActorTickEnabled()) return FText::FromString(TEXT("Aerial turning..."));
			return FText::FromString(AimedControl(Player)==ConfirmControl ? TEXT("[E] Test return at the current bearing") : TEXT("[E] Turn aerial 60 degrees"));
		case 3: return FText::FromString(TEXT("[E] Transmit the matched carrier"));
		case 4: return FText::FromString(TEXT("[E] Read the observer's field log"));
		default: return FText::GetEmpty();
	}
}
void ACREchoStation::Interact_Implementation(ACRCharacter* Player)
{
	auto* C=GetWorld()->GetSubsystem<UCREchoChapter>();
	auto* Control=AimedControl(Player);
	if (!C || !Control || IsActorTickEnabled() || !C->CanOperate(StationIndex)) return;
	if (C->NeedsRetry()) { C->RetrySave(); return; }
	const bool Confirm=Control==ConfirmControl;
	const bool Wrong=StationIndex==2 && Confirm && C->GetBearing()!=120;
	C->Operate(StationIndex,Confirm);
	if (auto* Audio=UCRAudioSettingsSubsystem::Get(this))
	{
		FName Cue=TEXT("Confirm");
		if (Wrong) Cue=TEXT("UIError");
		else if (StationIndex==0) Cue=TEXT("BusEnergize");
		else if (StationIndex==1 || StationIndex==4) Cue=TEXT("Collect");
		else if (StationIndex==2 && !Confirm) Cue=TEXT("InterlockTravel");
		Audio->PlayEvent(Cue,this,GetActorLocation(),true);
	}
}
