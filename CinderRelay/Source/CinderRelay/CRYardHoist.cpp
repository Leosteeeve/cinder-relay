#include "CRYardHoist.h"
#include "CRAudioSettingsSubsystem.h"
#include "CRCharacter.h"
#include "CRGameMode.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/World.h"
#include "Perception/AISense_Hearing.h"

namespace
{
	constexpr float LiftSeconds = 2.8f;
	constexpr float LiftHeight = 310.f;
	constexpr float RoofHeight = 415.f;
	constexpr float WinchHeight = 950.f;
	const FVector DownCenter(0, 0, 206);
}

ACRYardHoist::ACRYardHoist()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = false;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));

	WagonBody = CreateDefaultSubobject<UBoxComponent>(TEXT("WagonBody"));
	WagonBody->SetupAttachment(RootComponent);
	WagonBody->SetRelativeLocation(DownCenter);
	WagonBody->InitBoxExtent(FVector(504, 175, 206));
	WagonBody->SetCollisionProfileName(TEXT("BlockAllDynamic"));
	WagonBody->CanCharacterStepUpOn = ECB_No;
	WagonBody->SetGenerateOverlapEvents(false);
	// The bay straddles the north nav boundary. Scouts approach the pump on the yard side.
	WagonBody->SetCanEverAffectNavigation(false);
	Wagon = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Wagon"));
	Wagon->SetupAttachment(WagonBody);
	Wagon->SetRelativeLocation(-DownCenter);

	WestCable = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("WestCable"));
	EastCable = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("EastCable"));
	WestCable->SetupAttachment(RootComponent);
	EastCable->SetupAttachment(RootComponent);
	ConsoleFace = CreateDefaultSubobject<UBoxComponent>(TEXT("ConsoleFace"));
	ConsoleFace->SetupAttachment(RootComponent);
	ConsoleFace->SetRelativeLocation(FVector(-405, -1190, 134));
	ConsoleFace->InitBoxExtent(FVector(24, 54, 52));
	ConsoleFace->SetCollisionProfileName(TEXT("BlockAllDynamic"));
	ConsoleFace->SetGenerateOverlapEvents(false);
	ConsoleFace->SetCanEverAffectNavigation(false);
	Panel = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Panel"));
	Panel->SetupAttachment(ConsoleFace);
	Panel->SetRelativeRotation(FRotator(0, 180, 0));
	for (UStaticMeshComponent* Mesh : {Wagon.Get(), WestCable.Get(), EastCable.Get(), Panel.Get()})
	{
		Mesh->SetCollisionProfileName(TEXT("NoCollision"));
		Mesh->SetCanEverAffectNavigation(false);
	}
	Status = CreateDefaultSubobject<UTextRenderComponent>(TEXT("Status"));
	Status->SetupAttachment(ConsoleFace);
	Status->SetRelativeLocation(FVector(-31, 0, 77));
	Status->SetRelativeRotation(FRotator(0, 180, 0));
	Status->SetHorizontalAlignment(EHTA_Center);
	Status->SetVerticalAlignment(EVRTA_TextCenter);
	Status->SetWorldSize(14.f);
	Status->SetText(NSLOCTEXT("Cinder", "HoistStandby", "YARD HOIST\nBREAKER TRIPPED"));
	Status->SetTextRenderColor(FColor(255, 195, 85));
	SetTravel(0);
}

void ACRYardHoist::BeginPlay()
{
	Super::BeginPlay();
	auto* Game = GetWorld()->GetAuthGameMode<ACRGameMode>();
	if (!Game) return;
	Game->RegisterYardHoist();
	if (Game->IsYardHoistPowered())
	{
		TravelTime = LiftSeconds;
		SetTravel(1);
		ShowLocked();
	}
}

void ACRYardHoist::SetTravel(float Fraction)
{
	const float Height = LiftHeight * FMath::SmoothStep(0.f, 1.f, Fraction);
	WagonBody->SetRelativeLocation(DownCenter + FVector(0, 0, Height));
	const float Lower = RoofHeight + Height;
	for (UStaticMeshComponent* Cable : {WestCable.Get(), EastCable.Get()})
	{
		const float X = Cable == WestCable.Get() ? -310.f : 310.f;
		Cable->SetRelativeLocation(FVector(X, 0, (WinchHeight + Lower) * .5f));
		Cable->SetRelativeScale3D(FVector(.094f, .094f, (WinchHeight - Lower) / 100.f));
	}
}

bool ACRYardHoist::IsAtConsole(const ACRCharacter* Player) const
{
	return Player && FVector::DistSquared(Player->GetActorLocation(), ConsoleFace->GetComponentLocation()) <= FMath::Square(275.f);
}

bool ACRYardHoist::CanInteract_Implementation(ACRCharacter* Player) const
{
	const auto* Game = GetWorld()->GetAuthGameMode<ACRGameMode>();
	return Game && !Game->IsYardHoistPowered() && IsAtConsole(Player) && Player->CanInteractWith(this);
}

FText ACRYardHoist::GetInteractionPrompt_Implementation(ACRCharacter* Player) const
{
	if (TravelTime >= LiftSeconds) return NSLOCTEXT("Cinder", "HoistPassage", "Wagon secured. Cross underneath for the Signal Store.");
	if (IsActorTickEnabled()) return NSLOCTEXT("Cinder", "HoistLifting", "Hoist running. Wagon rising.");
	return IsAtConsole(Player) ? NSLOCTEXT("Cinder", "RepairHoist", "[E] Reset the hoist breaker and raise the wagon")
		: NSLOCTEXT("Cinder", "HoistRemote", "Wagon blocks the store cut. Hoist control is at the yellow booth.");
}

void ACRYardHoist::Interact_Implementation(ACRCharacter* Player)
{
	if (!CanInteract_Implementation(Player) || !GetWorld()->GetAuthGameMode<ACRGameMode>()->PowerYardHoist()) return;
	Status->SetText(NSLOCTEXT("Cinder", "HoistMoving", "POWER RESTORED\nWAGON RISING"));
	SetActorTickEnabled(true);
	// Perception receives the reachable pump position. The operator is the instigator,
	// so the existing Warden hearing/LOS rules can investigate without gaining sight.
	const FVector Pump = GetActorTransform().TransformPosition(FVector(0, -350, 48));
	UAISense_Hearing::ReportNoiseEvent(this, Pump, 1.f, Player, 2200.f, TEXT("YardHoist"));
	if (auto* Audio = UCRAudioSettingsSubsystem::Get(this))
		Audio->PlayEvent(TEXT("HoistLift"), this, Pump, true);
	UE_LOG(LogTemp, Display, TEXT("CR06_YARD PowerOn pump=%s"), *Pump.ToString());
}

void ACRYardHoist::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	TravelTime = FMath::Min(LiftSeconds, TravelTime + DeltaSeconds);
	SetTravel(TravelTime / LiftSeconds);
	if (TravelTime >= LiftSeconds)
	{
		ShowLocked();
		SetActorTickEnabled(false);
		UE_LOG(LogTemp, Display, TEXT("CR06_YARD WagonLocked clearance=%.0f"), LiftHeight);
	}
}

void ACRYardHoist::ShowLocked()
{
	Status->SetText(NSLOCTEXT("Cinder", "HoistClear", "LIFT LOCKED\nSTORE CUT OPEN"));
	Status->SetTextRenderColor(FColor(134, 240, 218));
}
