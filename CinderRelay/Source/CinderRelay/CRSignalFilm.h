#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "CRSignalFilm.generated.h"

class UAudioComponent;
class UTextBlock;
class SWidget;

/** The opening and the inter-chapter recap. The caller owns travel and menu focus. */
UCLASS()
class CINDERRELAY_API UCRSignalFilm final : public UUserWidget
{
    GENERATED_BODY()

public:
    static UCRSignalFilm* Open(APlayerController* Owner, bool bRecap, FSimpleDelegate OnFinished);
    UFUNCTION() void FinishFilm();
    float GetPlaybackTime() const { return Playback; }
    float GetDuration() const;

protected:
    void NativeTick(const FGeometry& Geometry, float Delta) override;
    FReply NativeOnPreviewKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
    void NativeDestruct() override;

private:
    void BuildScreen();
    void EnterShot(int32 Shot);
    void StopCue();

    UPROPERTY(Transient) TObjectPtr<UTextBlock> Caption;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> ShotTitle;
    UPROPERTY(Transient) TObjectPtr<UAudioComponent> Sound;
    TWeakPtr<SWidget> Artwork;
    FSimpleDelegate WhenFinished;
    double StartedAt = 0;
    float Playback = 0;
    int32 ActiveShot = INDEX_NONE;
    bool bRecapVersion = false;
    bool bFinished = false;
};
