#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "CRSignalFilm.generated.h"

class UMediaPlayer;
class UMediaSoundComponent;
class UMediaTexture;
class USizeBox;
class UTextBlock;

/** The opening and the inter-chapter recap. The caller owns travel and menu focus. */
UCLASS()
class CINDERRELAY_API UCRSignalFilm final : public UUserWidget
{
    GENERATED_BODY()

public:
    static UCRSignalFilm* Open(APlayerController* Owner, bool bRecap, FSimpleDelegate OnFinished);
    UFUNCTION() void FinishFilm();
    float GetPlaybackTime() const;
    float GetDuration() const;
    FIntPoint GetDecodedDimensions() const;
    bool HasDecodedMedia() const;
    bool HasPlaybackError() const { return bPlaybackFailed; }
#if !UE_BUILD_SHIPPING
    FSimpleMulticastDelegate OnNativeMediaEnd;
    float GetAudioEnvelope() const;
#endif

protected:
    void NativeTick(const FGeometry& Geometry, float Delta) override;
    FReply NativeOnPreviewKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
    void NativeDestruct() override;

private:
    void BuildScreen();
    UFUNCTION() void MediaOpened(FString Url);
    UFUNCTION() void MediaOpenFailed(FString Url);
    UFUNCTION() void MediaEnded();
    void CloseMedia();

    UPROPERTY(Transient) TObjectPtr<UMediaPlayer> Player;
    UPROPERTY(Transient) TObjectPtr<UMediaTexture> Picture;
    UPROPERTY(Transient) TObjectPtr<UMediaSoundComponent> Sound;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> FailureMessage;
    UPROPERTY(Transient) TObjectPtr<USizeBox> SourceSize;
    FSimpleDelegate WhenFinished;
    FIntPoint DisplaySize{1920,1080};
    bool bRecapVersion = false;
    bool bReachedEnd = false;
    bool bPlaybackFailed = false;
    bool bFinished = false;
};
