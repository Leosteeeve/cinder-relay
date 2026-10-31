#include "CRCharacter.h"
#include "CRHealthComponent.h"
#include "CRWeaponComponent.h"
#include "CRWeaponViewComponent.h"
#include "CRPlayerController.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"
#include "CRInteractable.h"
#include "TimerManager.h"
#include "Engine/World.h"
#include "Engine/LocalPlayer.h"

ACRCharacter::ACRCharacter()
{
	PrimaryActorTick.bCanEverTick = false;
	Health = CreateDefaultSubobject<UCRHealthComponent>(TEXT("Health"));
	Weapon = CreateDefaultSubobject<UCRWeaponComponent>(TEXT("Rook5"));
	WeaponView = CreateDefaultSubobject<UCRWeaponViewComponent>(TEXT("RookView"));
	GetCapsuleComponent()->InitCapsuleSize(42.f, 96.f);
	// Pawn defaults ignore Visibility; the combat body must receive enemy hitscan traces.
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
	bUseControllerRotationYaw = true;
	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
	Camera->SetupAttachment(GetCapsuleComponent());
	Camera->SetRelativeLocation(FVector(0.f, 0.f, 64.f));
	Camera->bUsePawnControlRotation = true;
	Camera->FieldOfView = 85.f;
	GetCharacterMovement()->GetNavAgentPropertiesRef().bCanCrouch = true;
	GetCharacterMovement()->SetCrouchedHalfHeight(60.f);
	GetCharacterMovement()->JumpZVelocity = 400.f;
	GetCharacterMovement()->AirControl = 0.2f;
	GetCharacterMovement()->MaxStepHeight = 35.f;
	GetCharacterMovement()->BrakingDecelerationWalking = 1600.f;
	GetCharacterMovement()->bOrientRotationToMovement = false;
}

void ACRCharacter::BeginPlay()
{
	Weapon->Data = RookData;
	Super::BeginPlay();
	Health->OnDeath.AddDynamic(this, &ACRCharacter::Died);
	GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
	GetCharacterMovement()->MaxWalkSpeedCrouched = CrouchSpeed;
	InstallInputContext();
	GetWorldTimerManager().SetTimer(PromptTimer, this, &ACRCharacter::UpdatePrompt, 0.1f, true);
}

void ACRCharacter::PawnClientRestart()
{
	Super::PawnClientRestart();
	InstallInputContext();
}

void ACRCharacter::InstallInputContext()
{
	if (const APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (ULocalPlayer* LP = PC->GetLocalPlayer())
		{
			if (auto* Input = LP->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(); Input && MappingContext)
			{
				InputSubsystem = Input;
				Input->AddMappingContext(MappingContext, 0);
				if (CombatMappingContext) Input->AddMappingContext(CombatMappingContext, 1);
			}
		}
	}
}

void ACRCharacter::EndPlay(const EEndPlayReason::Type Reason)
{
	GetWorldTimerManager().ClearTimer(PromptTimer);
	if (InputSubsystem.IsValid() && MappingContext) InputSubsystem->RemoveMappingContext(MappingContext);
	if (InputSubsystem.IsValid() && CombatMappingContext) InputSubsystem->RemoveMappingContext(CombatMappingContext);
	Super::EndPlay(Reason);
}

void ACRCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	auto* Input = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);
	if (FireAction) Input->BindAction(FireAction, ETriggerEvent::Started, this, &ACRCharacter::Fire);
	if (ReloadAction) Input->BindAction(ReloadAction, ETriggerEvent::Started, this, &ACRCharacter::Reload);
	if (AimAction)
	{
		Input->BindAction(AimAction, ETriggerEvent::Started, this, &ACRCharacter::AimStart);
		Input->BindAction(AimAction, ETriggerEvent::Completed, this, &ACRCharacter::AimStop);
		Input->BindAction(AimAction, ETriggerEvent::Canceled, this, &ACRCharacter::AimStop);
	}
	if (ForwardAction) Input->BindAction(ForwardAction, ETriggerEvent::Triggered, this, &ACRCharacter::MoveForward);
	if (BackAction) Input->BindAction(BackAction, ETriggerEvent::Triggered, this, &ACRCharacter::MoveBack);
	if (RightAction) Input->BindAction(RightAction, ETriggerEvent::Triggered, this, &ACRCharacter::MoveRight);
	if (LeftAction) Input->BindAction(LeftAction, ETriggerEvent::Triggered, this, &ACRCharacter::MoveLeft);
	if (YawAction) Input->BindAction(YawAction, ETriggerEvent::Triggered, this, &ACRCharacter::LookYaw);
	if (PitchAction) Input->BindAction(PitchAction, ETriggerEvent::Triggered, this, &ACRCharacter::LookPitch);
	if (InteractAction) Input->BindAction(InteractAction, ETriggerEvent::Started, this, &ACRCharacter::TryInteract);
	if (SprintAction)
	{
		Input->BindAction(SprintAction, ETriggerEvent::Started, this, &ACRCharacter::StartSprint);
		Input->BindAction(SprintAction, ETriggerEvent::Completed, this, &ACRCharacter::StopSprint);
		Input->BindAction(SprintAction, ETriggerEvent::Canceled, this, &ACRCharacter::StopSprint);
	}
	if (CrouchAction)
	{
		Input->BindAction(CrouchAction, ETriggerEvent::Started, this, &ACRCharacter::StartCrouch);
		Input->BindAction(CrouchAction, ETriggerEvent::Completed, this, &ACRCharacter::StopCrouch);
		Input->BindAction(CrouchAction, ETriggerEvent::Canceled, this, &ACRCharacter::StopCrouch);
	}
	if (JumpAction)
	{
		Input->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
		Input->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
		Input->BindAction(JumpAction, ETriggerEvent::Canceled, this, &ACharacter::StopJumping);
	}
}

void ACRCharacter::MoveForward() { AddMovementInput(GetActorForwardVector(), 1.f); }
void ACRCharacter::MoveBack() { AddMovementInput(GetActorForwardVector(), -1.f); }
void ACRCharacter::MoveRight() { AddMovementInput(GetActorRightVector(), 1.f); }
void ACRCharacter::MoveLeft() { AddMovementInput(GetActorRightVector(), -1.f); }
void ACRCharacter::LookYaw(const FInputActionValue& Value) { AddControllerYawInput(Value.Get<float>() * MouseSensitivity); }
// Unreal MouseY is already positive when the mouse moves up; preserve that sign.
void ACRCharacter::LookPitch(const FInputActionValue& Value) { AddControllerPitchInput(Value.Get<float>() * MouseSensitivity); }
void ACRCharacter::StartSprint() { if (!Health->IsDead() && !Weapon->IsPresentationLocked()) { GetCharacterMovement()->MaxWalkSpeed = SprintSpeed; Weapon->SetSprinting(true); } }
void ACRCharacter::StopSprint() { GetCharacterMovement()->MaxWalkSpeed = WalkSpeed; Weapon->SetSprinting(false); }
void ACRCharacter::StartCrouch() { if(!Weapon->IsPresentationLocked()) Crouch(); }
void ACRCharacter::StopCrouch() { UnCrouch(); }
void ACRCharacter::ClearHeldActions() { StopSprint(); StopJumping(); UnCrouch(); AimStop(); }
void ACRCharacter::Fire() { Weapon->TryFire(); }
void ACRCharacter::Reload() { Weapon->TryReload(); }
void ACRCharacter::AimStart() { Weapon->SetAiming(true); }
void ACRCharacter::AimStop() { Weapon->SetAiming(false); }
void ACRCharacter::Died()
{
	Weapon->Disable(); ClearHeldActions(); GetCharacterMovement()->DisableMovement();
	if (auto* PC=Cast<ACRPlayerController>(Controller)) PC->PlayerDefeated();
}

void ACRCharacter::OnStartCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust)
{
	Super::OnStartCrouch(HalfHeightAdjust, ScaledHalfHeightAdjust);
	Camera->SetRelativeLocation(FVector(0.f, 0.f, 40.f));
}
void ACRCharacter::OnEndCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust)
{
	Super::OnEndCrouch(HalfHeightAdjust, ScaledHalfHeightAdjust);
	Camera->SetRelativeLocation(FVector(0.f, 0.f, 64.f));
}

AActor* ACRCharacter::TraceTarget() const
{
	if (!GetWorld() || !Controller || GetWorld()->IsPaused() || Health->IsDead() || Weapon->IsPresentationLocked()) return nullptr;
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(CRInteraction), false, this);
	const FVector Start = Camera->GetComponentLocation();
	GetWorld()->LineTraceSingleByChannel(Hit, Start, Start + Camera->GetForwardVector() * InteractionRange, ECC_Visibility, Params);
	AActor* Target = Hit.GetActor();
	return IsValid(Target) && Target->Implements<UCRInteractable>() ? Target : nullptr;
}

bool ACRCharacter::CanInteractWith(const AActor* Target) const { return Target && TraceTarget() == Target; }

void ACRCharacter::UpdatePrompt()
{
	AActor* Target = TraceTarget();
	const FText Next = Target ? ICRInteractable::Execute_GetInteractionPrompt(Target, this) : FText::GetEmpty();
	if (!CurrentPrompt.EqualTo(Next))
	{
		CurrentPrompt = Next;
		OnPromptChanged.Broadcast(CurrentPrompt);
	}
}

void ACRCharacter::TryInteract()
{
	if (AActor* Target = TraceTarget(); Target && ICRInteractable::Execute_CanInteract(Target, this))
	{
		ICRInteractable::Execute_Interact(Target, this);
		UpdatePrompt();
	}
}
