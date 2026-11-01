#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/Button.h"
#include "CRHUDWidget.generated.h"
class UTextBlock; class USlider; struct FStreamableHandle; class UCRHUDWidget;
/** Context-bearing presentation button; never owns gameplay state. */
UCLASS()
class CINDERRELAY_API UCRInterfaceAction : public UButton
{
    GENERATED_BODY()
public: void Configure(UCRHUDWidget* Widget,int32 Id);
private:
    UFUNCTION() void Activated(); UFUNCTION() void Hovered();
    TWeakObjectPtr<UCRHUDWidget> Owner; int32 Action=0;
};
/** Existing event endpoint with a real Designer-authored UMG layout. */
UCLASS()
class CINDERRELAY_API UCRHUDWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    void SetObjective(const FText& Text); void SetPrompt(const FText& Text); void SetStreamingStatus(const FText& Text);
    void SetMenu(bool Visible,bool Ended,bool Defeated=false);
    void SetRecoveryMenu(bool Startup,bool Defeated,bool CanResume,bool CanContinue,const FString& Status);
    void SetCheckpointStatus(const FText& Text); void SetCombat(float Health,int32 Magazine,int32 Reserve,bool Reloading);
    void SetSightState(bool HideReticle,bool Installed);
    void ShotFeedback(bool Hit); void HitFeedback(bool Killed); void DamageFeedback();
    void SetSubtitle(const FText& Text); void SetAssembly(bool Active); void Notice(const FText& Text);
    bool HandleBack(); void HandleAction(int32 Action); void PlayInterfaceSound(FName Cue);
    void SetFieldPack(bool Open); void RefreshFieldPack();
    bool IsFieldPackVisible() const {return bPack;}
    UPROPERTY(EditDefaultsOnly,Category="Interface") TObjectPtr<UObject> BodyFont;
    UPROPERTY(EditDefaultsOnly,Category="Interface") TObjectPtr<UObject> TitleFont;
protected:
    virtual void NativeOnInitialized() override; virtual void NativeDestruct() override;
    virtual void NativeTick(const FGeometry& Geometry,float Delta) override;
    virtual FReply NativeOnKeyDown(const FGeometry& Geometry,const FKeyEvent& Event) override;
    virtual FReply NativeOnPreviewKeyDown(const FGeometry& Geometry,const FKeyEvent& Event) override;
private:
    UTextBlock* Text(FName Name) const; void Put(FName Name,const FText& Value); void Put(FName Name,const FString& Value);
    void SetObjectiveExpanded(bool Expanded);
    void Visibility(FName Name,bool Visible); void RefreshNavigation(); void MoveFocus(int32 Delta); void FocusIndex(int32 Index);
    void BeginModal(const FString& Title,const FString& Body,int32 Kind); void CloseModal();
    UCRInterfaceAction* AddAction(int32 Id,const FString& Label);
    void AddVolume(FName Group); void ChangeVolume(FName Group,float Value); void SaveVolumes(); void RefreshTitleArtwork();
    UFUNCTION() void ResumeClicked(); UFUNCTION() void RestartClicked(); UFUNCTION() void ExitClicked();
    UFUNCTION() void ContinueClicked(); UFUNCTION() void SettingsClicked(); UFUNCTION() void CreditsClicked();
    UFUNCTION() void PackCloseClicked();
    UFUNCTION() void MasterChanged(float V); UFUNCTION() void SFXChanged(float V); UFUNCTION() void AmbienceChanged(float V);
    UFUNCTION() void UIChanged(float V); UFUNCTION() void VoiceChanged(float V);
    UPROPERTY(Transient) TArray<TObjectPtr<UButton>> MenuNavigation;
    UPROPERTY(Transient) TMap<FName,TObjectPtr<USlider>> VolumeSliders;
    UPROPERTY(Transient) TMap<FName,TObjectPtr<UTextBlock>> VolumeLabels;
    TSharedPtr<FStreamableHandle> TitleLoad;
    TSharedPtr<FStreamableHandle> IconLoad;
    int32 Focused=0,ModalKind=0,PackCategory=0,PackSelection=0,VolumeFocus=0;
    bool bMenu=false,bStartup=false,bAssembly=false,bEnded=false,bDefeated=false,bPack=false,bKilled=false;
    bool bHadCombat=false,bWasReloading=false;
    float ShotPulse=0,HitPulse=0,HurtPulse=0,ObjectiveAge=0,NoticeAge=0;
    FText FullObjective;
};
