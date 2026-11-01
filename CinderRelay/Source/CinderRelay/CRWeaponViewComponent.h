#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CRWeaponViewComponent.generated.h"
class UCRWeaponComponent;
class USceneComponent;
class UStaticMeshComponent;
class UStaticMesh;
class USkeletalMesh;
class USkeletalMeshComponent;
class UAnimSequence;
class UAnimSequenceBase;
class UAnimMontage;
class USoundBase;
struct FStreamableHandle;
UCLASS(ClassGroup=(CinderRelay), meta=(BlueprintSpawnableComponent))
class CINDERRELAY_API UCRWeaponViewComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UCRWeaponViewComponent();
    UPROPERTY(EditDefaultsOnly, Category="Appearance") TSoftObjectPtr<UStaticMesh> RookAppearance;
    UPROPERTY(EditDefaultsOnly, Category="Appearance") TSoftObjectPtr<UStaticMesh> SurveyAppearance;
    UPROPERTY(EditDefaultsOnly, Category="Appearance|Sights", meta=(ClampMin="16",ClampMax="40")) float SightEyeRelief = 20.f;
    UPROPERTY(EditDefaultsOnly, Category="Appearance|Sights") FVector ImportedHipLocation = FVector(48,10,-10);
    /** Socket in mesh space -> camera-relative root, +X sight axis at the authored eye relief. */
    static FTransform SolveSightRoot(const FTransform& SightLocal, float EyeRelief);
    /** The appearance pair is atomic: incomplete imports use the original primitive view. */
    static bool CanUseAuthoredSights(const UStaticMesh* Rook, const UStaticMesh* Optic);
    void SetPresentationHidden(bool Hidden);
    bool HasImportedAppearance() const;
    bool HasAnimatedHands() const { return bHandlingReady; }
    /** Native async completion (including failure) releases input to the selected appearance. */
    bool IsPresentationResident() const { return bAppearanceSettled && bHandlingSettled; }
    void HandleAnimationCue(USkeletalMeshComponent* Mesh,UAnimSequenceBase* Animation,FName Cue,int32 MontageInstanceID);
    int32 GetAcceptedPresentationShots() const { return AcceptedPresentationShots; }
    int32 GetEjectedCases() const { return EjectedCases; }
    float GetHandlingActionPosition() const;
#if !UE_BUILD_SHIPPING
    void SuppressNextCaseForTest() { bSuppressNextCase=true; }
#endif
    /** An instance identity is consumed once. No animation cue can spend another shot. */
    static bool ConsumeShotCue(int32 Expected,int32 Received,bool& bSpent);
    UPROPERTY(EditDefaultsOnly, Category="Appearance|Animation") TSoftObjectPtr<USkeletalMesh> ArmsAppearance;
    /** Idle, Walk, Sprint, ADS, FireCycle, Reload, Dry, in that order. */
    UPROPERTY(EditDefaultsOnly, Category="Appearance|Animation") TArray<TSoftObjectPtr<UAnimSequence>> HandlingClips;
    virtual void TickComponent(float Delta, ELevelTick TickType, FActorComponentTickFunction* ThisTick) override;
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> Arms;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Feed;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> CycleHandle;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> CasePool;
    UPROPERTY() TArray<TObjectPtr<UAnimMontage>> ActionMontages;
    UPROPERTY() TObjectPtr<UAnimMontage> ActiveAction;
    UPROPERTY() TArray<TSoftObjectPtr<UStaticMesh>> HandlingProps;
    UPROPERTY() TArray<TSoftObjectPtr<USoundBase>> HandlingSounds;
    TSharedPtr<FStreamableHandle> HandlingLoad;
    struct FCaseMotion { FVector Origin=FVector::ZeroVector,Velocity=FVector::ZeroVector; FRotator Rotation=FRotator::ZeroRotator; float Age=2.f; };
    TArray<FCaseMotion> CaseMotions;
    bool bHandlingReady=false,bCaseSpent=true;
    bool bAppearanceSettled=false,bHandlingSettled=false;
#if !UE_BUILD_SHIPPING
    bool bSuppressNextCase=false;
#endif
    int32 ActiveShotInstance=INDEX_NONE,AcceptedPresentationShots=0,EjectedCases=0,NextCase=0;
    int32 ActiveActionInstance=INDEX_NONE;
    uint8 PlayedCueMask=0;
    void LoadHandling();
    void HandlingLoaded();
    void AttachAuthoredProp(UStaticMeshComponent* Prop,FName Bone);
    void PlayHandling(int32 Action);
    void CancelHandling(bool bClearCases);
    void TickCases(float Delta);
    UFUNCTION() void WeaponStateChanged();
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> FallbackParts;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> ImportedRook;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> ImportedOptic;
    TSharedPtr<FStreamableHandle> AppearanceLoad;
    bool bPresentationHidden=false;
    FTransform IronAimRoot=FTransform::Identity, OpticAimRoot=FTransform::Identity;
    bool bSightAnchorsValid=false;
    UFUNCTION() void RefreshAppearance();
    void AppearanceLoaded();
    UPROPERTY() TObjectPtr<UStaticMesh> Cube;
    UPROPERTY() TObjectPtr<USceneComponent> ViewRoot;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> Flash;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> ImpactMarker;
    TWeakObjectPtr<UCRWeaponComponent> Weapon;
    float Recoil = 0, BaseFOV = 85, CoverFraction = 0, CoverCountdown = 0;
    float GaitPhase=0, ReloadPose=0, SmoothCover=0;
    FTimerHandle FlashTimer, ImpactTimer;
    UFUNCTION() void Shot(FVector Impact, bool bHitTarget, bool bBlockingHit);
    UFUNCTION() void Cue(FName Name);
    UFUNCTION() void Hurt(float Health, float Damage);
    void HideFlash();
    void HideImpact();
};
