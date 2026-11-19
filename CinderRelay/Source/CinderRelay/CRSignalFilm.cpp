#include "CRSignalFilm.h"
#include "Blueprint/WidgetTree.h"
#include "Brushes/SlateColorBrush.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/ScaleBox.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "MediaPlayer.h"
#include "MediaSoundComponent.h"
#include "MediaTexture.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Sound/SoundClass.h"
#include "Styling/CoreStyle.h"

UCRSignalFilm* UCRSignalFilm::Open(APlayerController* Owner, bool bRecap, FSimpleDelegate OnFinished)
{
    if (!IsValid(Owner) || !Owner->IsLocalController()) return nullptr;
    auto* Film = CreateWidget<UCRSignalFilm>(Owner, StaticClass());
    if (!Film) return nullptr;
    Film->bRecapVersion = bRecap;
    Film->WhenFinished = MoveTemp(OnFinished);
    Film->SetIsFocusable(true);

    Film->Player = NewObject<UMediaPlayer>(Film);
    Film->Player->SetDesiredPlayerName(TEXT("ElectraPlayer"));
    Film->Player->PlayOnOpen = false;
    Film->Player->OnMediaOpened.AddDynamic(Film, &UCRSignalFilm::MediaOpened);
    Film->Player->OnMediaOpenFailed.AddDynamic(Film, &UCRSignalFilm::MediaOpenFailed);
    Film->Player->OnEndReached.AddDynamic(Film, &UCRSignalFilm::MediaEnded);
    Film->Picture = NewObject<UMediaTexture>(Film);
    Film->Picture->NewStyleOutput = true;
    Film->Picture->AutoClear = true;
    Film->Picture->SetMediaPlayer(Film->Player);
    Film->Picture->UpdateResource();

    // This actor owns the synth for the lifetime of the local menu. The media
    // clock drives its sample queue while world time and pawn input are paused.
    Film->Sound = NewObject<UMediaSoundComponent>(Owner);
    Film->Sound->bIsUISound = true;
    Film->Sound->bAllowSpatialization = false;
    Film->Sound->SetAutoActivate(false);
    Film->Sound->SoundClass = Cast<USoundClass>(FSoftObjectPath(
        TEXT("/Game/Generated/Phase055/Audio/SC_CR055_SFX.SC_CR055_SFX")).ResolveObject());
    Film->Sound->SetMediaPlayer(Film->Player);
#if !UE_BUILD_SHIPPING
    FString CampaignCheck;
    if (FParse::Value(FCommandLine::Get(), TEXT("CRCampaignCheck="), CampaignCheck))
        Film->Sound->SetEnableEnvelopeFollowing(true);
#endif
    Film->Sound->RegisterComponentWithWorld(Owner->GetWorld());
    Film->Sound->SetComponentTickEnabled(false);
    Film->Sound->AddClockSink();
    Film->Sound->Start();
    Film->BuildScreen();
    Film->AddToViewport(1000);
    Film->SetUserFocus(Owner);
    Film->SetKeyboardFocus();

    const FString Name = bRecap ? TEXT("CR_Recap3D.mp4") : TEXT("CR_Opening3D.mp4");
    const FString File = FPaths::ConvertRelativePathToFull(FPaths::ProjectContentDir() / TEXT("Movies") / Name);
    if (!Film->Player->OpenFile(File)) Film->MediaOpenFailed(File);
    return Film;
}

void UCRSignalFilm::BuildScreen()
{
    auto* Root = WidgetTree->ConstructWidget<UCanvasPanel>();
    WidgetTree->RootWidget = Root;
    auto Fill = [Root](UWidget* W)
    {
        auto* CanvasSlot = Root->AddChildToCanvas(W);
        CanvasSlot->SetAnchors(FAnchors(0,0,1,1));
        CanvasSlot->SetOffsets(FMargin(0));
    };
    auto* Back = WidgetTree->ConstructWidget<UBorder>();
    Back->SetBrushColor(FLinearColor::Black);
    Fill(Back);
    auto* Fit = WidgetTree->ConstructWidget<UScaleBox>();
    Fit->SetStretch(EStretch::ScaleToFit);
    Fit->SetVisibility(ESlateVisibility::HitTestInvisible);
    Fill(Fit);
    SourceSize = WidgetTree->ConstructWidget<USizeBox>();
    SourceSize->SetWidthOverride(DisplaySize.X);
    SourceSize->SetHeightOverride(DisplaySize.Y);
    Fit->SetContent(SourceSize);
    auto* Image = WidgetTree->ConstructWidget<UImage>();
    Image->SetBrushResourceObject(Picture);
    SourceSize->SetContent(Image);

    FailureMessage = WidgetTree->ConstructWidget<UTextBlock>();
    FailureMessage->SetText(FText::FromString(TEXT("The film could not play. Select Skip to continue.")));
    FailureMessage->SetJustification(ETextJustify::Center);
    FailureMessage->SetVisibility(ESlateVisibility::Collapsed);
    auto* MessageSlot = Root->AddChildToCanvas(FailureMessage);
    MessageSlot->SetAnchors(FAnchors(.5f));
    MessageSlot->SetAlignment({.5f,.5f});
    MessageSlot->SetAutoSize(true);
    auto* Skip = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), TEXT("SkipFilm"));
    FButtonStyle Buttons;
    Buttons.SetNormal(FSlateColorBrush(FLinearColor(.014f,.022f,.024f,.86f)))
        .SetHovered(FSlateColorBrush(FLinearColor(.05f,.075f,.07f)))
        .SetPressed(FSlateColorBrush(FLinearColor(.09f,.07f,.04f)));
    Skip->SetStyle(Buttons);
    auto* Label = WidgetTree->ConstructWidget<UTextBlock>();
    Label->SetText(FText::FromString(TEXT("Skip   [Tab]")));
    Label->SetFont(FCoreStyle::GetDefaultFontStyle("Regular",18));
    Skip->SetContent(Label);
    Skip->OnClicked.AddDynamic(this,&UCRSignalFilm::FinishFilm);
    auto* SkipSlot = Root->AddChildToCanvas(Skip);
    SkipSlot->SetAnchors(FAnchors(1,0));
    SkipSlot->SetAlignment({1,0});
    SkipSlot->SetOffsets(FMargin(-28,20,150,43));
}

void UCRSignalFilm::MediaOpened(FString Url)
{
    if (bFinished || bPlaybackFailed || !Player) return;
    Player->SetLooping(false);
    UE_LOG(LogTemp, Display, TEXT("CR_FILM Opened decoder=%s duration=%.3fs audio_tracks=%d file=%s"),
        *Player->GetPlayerName().ToString(), GetDuration(), Player->GetNumTracks(EMediaPlayerTrack::Audio), *Url);
    if (!Player->Play()) MediaOpenFailed(Url);
}

void UCRSignalFilm::MediaOpenFailed(FString Url)
{
    if (bFinished || bPlaybackFailed) return;
    bPlaybackFailed = true;
    UE_LOG(LogTemp, Error, TEXT("CR_FILM Movie playback failed: %s"), *Url);
    if (FailureMessage) FailureMessage->SetVisibility(ESlateVisibility::HitTestInvisible);
}

void UCRSignalFilm::MediaEnded()
{
    if (bFinished || bReachedEnd || bPlaybackFailed) return;
    bReachedEnd = true;
#if !UE_BUILD_SHIPPING
    OnNativeMediaEnd.Broadcast();
#endif
    UE_LOG(LogTemp, Display, TEXT("CR_FILM Native end reached"));
    // The media facade is dispatching events. Close it on the next Slate tick.
}

float UCRSignalFilm::GetPlaybackTime() const
{
    return Player ? FMath::Max(0.f, float(Player->GetDisplayTime().GetTotalSeconds())) : 0.f;
}

float UCRSignalFilm::GetDuration() const
{
    return Player ? FMath::Max(0.f, float(Player->GetDuration().GetTotalSeconds())) : 0.f;
}

FIntPoint UCRSignalFilm::GetDecodedDimensions() const
{
    return Picture ? FIntPoint(Picture->GetWidth(),Picture->GetHeight()) : FIntPoint::ZeroValue;
}

bool UCRSignalFilm::HasDecodedMedia() const
{
    const FIntPoint Size = GetDecodedDimensions();
    return Player && !bPlaybackFailed && Player->GetPlayerName() == TEXT("ElectraPlayer")
        && Size.X > 2 && Size.Y > 2 && Player->GetSelectedTrack(EMediaPlayerTrack::Audio) != INDEX_NONE
        && GetPlaybackTime() > 0.f;
}

#if !UE_BUILD_SHIPPING
float UCRSignalFilm::GetAudioEnvelope() const { return Sound ? Sound->GetEnvelopeValue() : 0.f; }
#endif

void UCRSignalFilm::NativeTick(const FGeometry& Geometry, float Delta)
{
    Super::NativeTick(Geometry, Delta);
    if (bReachedEnd)
    {
        FinishFilm();
        return;
    }
    const FIntPoint Dimensions = GetDecodedDimensions();
    if (SourceSize && Dimensions.X > 2 && Dimensions.Y > 2 && DisplaySize != Dimensions)
    {
        DisplaySize = Dimensions;
        SourceSize->SetWidthOverride(Dimensions.X);
        SourceSize->SetHeightOverride(Dimensions.Y);
    }
}

FReply UCRSignalFilm::NativeOnPreviewKeyDown(const FGeometry&, const FKeyEvent& Event)
{
    const FKey Key = Event.GetKey();
    if (!Event.IsRepeat() && (Key==EKeys::Tab || Key==EKeys::Enter || Key==EKeys::Escape)) FinishFilm();
    return FReply::Handled();
}

void UCRSignalFilm::CloseMedia()
{
    if (Sound)
    {
        Sound->RemoveClockSink();
        Sound->Stop();
        Sound->SetMediaPlayer(nullptr);
        Sound->DestroyComponent();
        Sound=nullptr;
    }
    if (Player)
    {
        Player->OnMediaOpened.RemoveAll(this);
        Player->OnMediaOpenFailed.RemoveAll(this);
        Player->OnEndReached.RemoveAll(this);
        if (Picture) Picture->SetMediaPlayer(nullptr);
        Player->Close();
        Player=nullptr;
    }
}

void UCRSignalFilm::FinishFilm()
{
    if (bFinished) return;
    bFinished=true;
    auto Callback=MoveTemp(WhenFinished);
    CloseMedia();
    RemoveFromParent();
    Callback.ExecuteIfBound();
}

void UCRSignalFilm::NativeDestruct()
{
    bFinished=true;
    WhenFinished.Unbind();
    CloseMedia();
    Super::NativeDestruct();
}
