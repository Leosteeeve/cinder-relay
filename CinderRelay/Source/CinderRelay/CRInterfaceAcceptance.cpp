#include "CRInterfaceAcceptance.h"
#if !UE_BUILD_SHIPPING
#include "CRAudioSettingsSubsystem.h"
#include "CRCharacter.h"
#include "CRChapterSaveSubsystem.h"
#include "CRChapterSaveGame.h"
#include "CRFieldPackModel.h"
#include "CRGameMode.h"
#include "CRHealthComponent.h"
#include "CRHUDWidget.h"
#include "CRPlayerController.h"
#include "CRWeaponComponent.h"
#include "AudioMixerBlueprintLibrary.h"
#include "Components/Button.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Engine/GameInstance.h"
#include "Engine/LocalPlayer.h"
#include "Engine/World.h"
#include "EnhancedInputSubsystems.h"
#include "Framework/Application/SlateApplication.h"
#include "HAL/FileManager.h"
#include "InputActionValue.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"

namespace
{
    // OpenLevel destroys the actor; this small test-only journal survives that handoff.
    struct FInterfaceRun
    {
        FString Mode, Suffix, Directory, Stage=TEXT("menu"), Events, Message;
        TArray<FString> Captures;
        double Started=0, StageStarted=0;
        bool Initialized=false, Travel=false;
    } Run;
    FString Quote(FString Text)
    {
        Text.ReplaceInline(TEXT("\\"),TEXT("\\\\")); Text.ReplaceInline(TEXT("\""),TEXT("\\\""));
        Text.ReplaceInline(TEXT("\r"),TEXT("\\r")); Text.ReplaceInline(TEXT("\n"),TEXT("\\n"));
        return TEXT("\"")+Text+TEXT("\"");
    }
    const FName InterfaceAudioGroups[]={TEXT("Master"),TEXT("SFX"),TEXT("Ambience"),TEXT("UI"),TEXT("Voice")};
    const float InterfaceAudioExpected[]={.65f,.85f,.50f,.65f,.85f};
    bool Visible(UCRHUDWidget* HUD,FName Name)
    {
        const UWidget* W=HUD?HUD->GetWidgetFromName(Name):nullptr;
        return W && W->GetVisibility()!=ESlateVisibility::Collapsed && W->GetVisibility()!=ESlateVisibility::Hidden;
    }
    FString Label(UCRHUDWidget* HUD,FName Name)
    {
        const UTextBlock* T=HUD?Cast<UTextBlock>(HUD->GetWidgetFromName(Name)):nullptr;
        return T?T->GetText().ToString():FString();
    }
}
#endif

ACRInterfaceAcceptance::ACRInterfaceAcceptance()
{
#if !UE_BUILD_SHIPPING
    PrimaryActorTick.bCanEverTick=true;
    PrimaryActorTick.bTickEvenWhenPaused=true;
#endif
}
void ACRInterfaceAcceptance::BeginPlay()
{
    Super::BeginPlay();
#if !UE_BUILD_SHIPPING
    FString Mode, Suffix, AudioSuffix;
    FParse::Value(FCommandLine::Get(),TEXT("CR055InterfaceCheck="),Mode);
    FParse::Value(FCommandLine::Get(),TEXT("CRCheckpointTest="),Suffix);
    FParse::Value(FCommandLine::Get(),TEXT("CR055AudioTest="),AudioSuffix);
    auto* Store=GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
    auto* Audio=GetGameInstance()->GetSubsystem<UCRAudioSettingsSubsystem>();
    const bool Guard=(Mode==TEXT("Write")||Mode==TEXT("Read")) && Suffix.StartsWith(TEXT("Phase055")) &&
        UCRAudioSettingsSubsystem::IsPreferenceSuffixValid(Suffix) && AudioSuffix==Suffix && Store && Audio &&
        Store->SlotName(0)==TEXT("CR04_TEST_")+Suffix+TEXT("_A") &&
        FPaths::GetCleanFilename(Audio->GetPreferencesPath())==TEXT("CR04_TEST_Audio_")+Suffix+TEXT(".ini");
    if(!Guard)
    {
        UE_LOG(LogTemp,Error,TEXT("CR055_INTERFACE REFUSED: exact isolated checkpoint/audio flags required"));
        bFinished=true; FPlatformMisc::RequestExitWithStatus(false,2); return;
    }
    if(!Run.Initialized)
    {
        Run.Initialized=true; Run.Mode=Mode; Run.Suffix=Suffix;
        Run.Directory=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Phase055")/Suffix/Mode);
        IFileManager::Get().MakeDirectory(*Run.Directory,true);
        Run.Started=Run.StageStarted=FPlatformTime::Seconds();
        Run.Events=TEXT("Evidence scope: automated Slate keyboard navigation; native gameplay fixtures; no human visual or auditory acceptance.\n");
    }
    else if(Run.Travel) { Run.Travel=false; Next(TEXT("ready")); }
#endif
}
void ACRInterfaceAcceptance::WeaponCue(FName Cue)
{
#if !UE_BUILD_SHIPPING
    if(Cue==TEXT("ReloadComplete")) ++ReloadCompletions;
#endif
}

#if !UE_BUILD_SHIPPING
void ACRInterfaceAcceptance::Next(const FString& Stage)
{
    Run.Stage=Stage; Run.StageStarted=FPlatformTime::Seconds();
    UE_LOG(LogTemp,Display,TEXT("CR055_INTERFACE stage=%s mode=%s"),*Stage,*Run.Mode);
}
bool ACRInterfaceAcceptance::Check(bool Condition,const FString& Message)
{
    if(bFinished) return false;
    Run.Events+=(Condition?TEXT("PASS "):TEXT("FAIL "))+Message+TEXT("\n");
    UE_LOG(LogTemp,Display,TEXT("CR055_INTERFACE %s %s"),Condition?TEXT("PASS"):TEXT("FAIL"),*Message);
    if(!Condition) Finish(false,Message);
    return Condition;
}
void ACRInterfaceAcceptance::Key(const FKey& InKey)
{
    if(!FSlateApplication::IsInitialized()) { Finish(false,TEXT("Slate unavailable")); return; }
    const FKeyEvent Event(InKey,FModifierKeysState(),uint32(0),false,0,0);
    FSlateApplication::Get().ProcessKeyDownEvent(Event);
    FSlateApplication::Get().ProcessKeyUpEvent(Event);
    Run.Events+=TEXT("SLATE_KEY ")+InKey.ToString()+TEXT("\n");
}
void ACRInterfaceAcceptance::GameplayKey(const FKey& InKey)
{
    if(!PC.IsValid()) return;
    PC->InputKey(FInputKeyEventArgs(nullptr,FInputDeviceId::CreateFromInternalId(0),InKey,IE_Pressed,FPlatformTime::Cycles64()));
    PC->InputKey(FInputKeyEventArgs(nullptr,FInputDeviceId::CreateFromInternalId(0),InKey,IE_Released,FPlatformTime::Cycles64()));
    Run.Events+=TEXT("PLAYER_INPUT_KEY ")+InKey.ToString()+TEXT("\n");
}
void ACRInterfaceAcceptance::Inject(const UInputAction* Action)
{
    if(Action && PC.IsValid() && PC->GetLocalPlayer())
        if(auto* Input=PC->GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
            Input->InjectInputForAction(Action,FInputActionValue(1.f),{},{});
}
void ACRInterfaceAcceptance::Capture(const FString& Name,const FString& FollowingStage)
{
    CapturePath=Run.Directory/(Name+TEXT(".png")); AfterCapture=FollowingStage;
    FScreenshotRequest::RequestScreenshot(CapturePath,true,false,false);
    Next(TEXT("capture"));
}
void ACRInterfaceAcceptance::Finish(bool Passed,const FString& Message)
{
    if(bFinished) return;
    bFinished=true; bPassed=Passed; Run.Message=Message;
    if(Player.IsValid()) Player->ClearHeldActions();
    if(bRecording)
    {
        UAudioMixerBlueprintLibrary::StopRecordingOutput(this,EAudioRecordingExportType::WavFile,TEXT("GameplayMix"),Run.Directory);
        bRecording=false;
    }
    Next(TEXT("finalize"));
}
void ACRInterfaceAcceptance::WriteReceipt()
{
    auto* Audio=GetGameInstance()->GetSubsystem<UCRAudioSettingsSubsystem>();
    const FString Wav=Run.Directory/TEXT("GameplayMix.wav");
    const bool HasAudio=IFileManager::Get().FileSize(*Wav)>44;
    if(!HasAudio) { bPassed=false; Run.Message+=TEXT("; native mixed WAV export missing"); }
    TArray<FString> Paths; for(const FString& P:Run.Captures) Paths.Add(Quote(P));
    const FString Receipt=FString::Printf(TEXT("{\"passed\":%s,\"mode\":%s,\"test_suffix\":%s,\"message\":%s,\"elapsed_seconds\":%.3f,\"captures\":[%s],\"audio_wav\":%s,\"audio_file_present\":%s,\"reload_completions\":%d,\"shot_audio_events\":%d,\"ui_audio_events\":%d,\"human_visual_acceptance\":false,\"human_auditory_acceptance\":false,\"scope\":\"Slate UI navigation and isolated native method/input fixtures; not full chapter traversal\"}\n"),
        bPassed?TEXT("true"):TEXT("false"),*Quote(Run.Mode),*Quote(Run.Suffix),*Quote(Run.Message),FPlatformTime::Seconds()-Run.Started,
        *FString::Join(Paths,TEXT(",")),*Quote(Wav),HasAudio?TEXT("true"):TEXT("false"),ReloadCompletions,
        Audio?Audio->GetEventCount(TEXT("Shot")):0,Audio?Audio->GetEventCount(TEXT("UIConfirm"))+Audio->GetEventCount(TEXT("UICancel"))+Audio->GetEventCount(TEXT("UISelect")):0);
    FFileHelper::SaveStringToFile(Receipt,*(Run.Directory/TEXT("acceptance.json")));
    FFileHelper::SaveStringToFile(Run.Events,*(Run.Directory/TEXT("checks.txt")));
    UE_LOG(LogTemp,Display,TEXT("CR055_INTERFACE_FINISH %s"),*Receipt);
    // Normal game exit exercises teardown/preferences; the runner reads the receipt for failure.
    if(PC.IsValid()) PC->ExitPrototype(); else FPlatformMisc::RequestExitWithStatus(false,bPassed?0:1);
}
#endif

void ACRInterfaceAcceptance::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
    if(bHandedOff) return;
    const double Age=FPlatformTime::Seconds()-Run.StageStarted;
    PC=Cast<ACRPlayerController>(UGameplayStatics::GetPlayerController(this,0));
    if(bFinished)
    {
        if(Run.Stage==TEXT("finalize") && Age>1 && (IFileManager::Get().FileSize(*(Run.Directory/TEXT("GameplayMix.wav")))>44 || Age>5))
        { Next(TEXT("exiting")); WriteReceipt(); }
        return;
    }
    if(FPlatformTime::Seconds()-Run.Started>85) { Finish(false,TEXT("Bounded interface route timeout at ")+Run.Stage); return; }
    if(!PC.IsValid() || !PC->GetInterface()) return;
    auto* HUD=PC->GetInterface(); auto* G=GetWorld()->GetAuthGameMode<ACRGameMode>();
    auto* Store=GetGameInstance()->GetSubsystem<UCRChapterSaveSubsystem>();
    auto* Audio=GetGameInstance()->GetSubsystem<UCRAudioSettingsSubsystem>();
    if(Run.Stage==TEXT("capture"))
    {
        if(Age>.5 && IFileManager::Get().FileSize(*CapturePath)>8) { Run.Captures.Add(CapturePath); Next(AfterCapture); }
        else if(Age>8) Finish(false,TEXT("Native ShowUI screenshot not produced: ")+CapturePath);
        return;
    }
    if(Run.Stage==TEXT("menu"))
    {
        if(Age<2 || Store->IsBusy() || !Audio->IsReady()) return;
        auto* Art=Cast<UImage>(HUD->GetWidgetFromName(TEXT("TitleBackground")));
        if(!Art || !Art->GetBrush().GetResourceObject()) return;
        if(!Check(G&&G->IsStartupMenu()&&!PC->GetPawn()&&PC->bPrototypePaused,TEXT("Cold title owns input before pawn spawn"))) return;
        if(!Check(Visible(HUD,TEXT("MenuBackdrop")),TEXT("Real main menu hierarchy visible"))) return;
        auto* Continue=Cast<UButton>(HUD->GetWidgetFromName(TEXT("Continue")));
        if(!Check(Continue&&Continue->GetIsEnabled()==Store->HasCheckpoint(),TEXT("Continue matches native disk checkpoint availability"))) return;
        if(!Check(Run.Mode==TEXT("Read")?Store->HasCheckpoint():!Store->HasCheckpoint(),TEXT("Write starts fresh; Read discovers previous native checkpoint"))) return;
        if(!Check(!PC->CanOpenFieldPack(),TEXT("Field Pack unavailable at startup"))) return;
        Capture(TEXT("01_MainMenu"),TEXT("open_settings")); return;
    }
    if(Run.Stage==TEXT("open_settings"))
    {
        HUD->SetKeyboardFocus();
        Key(EKeys::Down); if(Store->HasCheckpoint()) Key(EKeys::Down); Key(EKeys::Enter);
        Next(TEXT("settings")); return;
    }
    if(Run.Stage==TEXT("settings"))
    {
        if(Age<=.4) return;
        if(!Check(Visible(HUD,TEXT("ModalPanel"))&&Label(HUD,TEXT("ModalTitle"))==TEXT("SETTINGS"),TEXT("Slate keyboard opened Settings"))) return;
        if(Run.Mode==TEXT("Write"))
        {
            const auto Defaults=UCRAudioSettingsSubsystem::DefaultVolumes();
            for(int32 I=0;I<5;++I)
            {
                if(!Check(FMath::IsNearlyEqual(Audio->GetVolume(InterfaceAudioGroups[I]),Defaults.FindChecked(InterfaceAudioGroups[I]),.001f),TEXT("Fresh private preference default: ")+InterfaceAudioGroups[I].ToString())) return;
                for(int32 N=0;N<3;++N) Key(EKeys::Left);
                if(I<4) Key(EKeys::Down);
            }
        }
        for(int32 I=0;I<5;++I) if(!Check(FMath::IsNearlyEqual(Audio->GetVolume(InterfaceAudioGroups[I]),InterfaceAudioExpected[I],.001f),TEXT("UI or cross-process audio value: ")+InterfaceAudioGroups[I].ToString())) return;
        Capture(TEXT("02_Settings"),TEXT("settings_back")); return;
    }
    if(Run.Stage==TEXT("settings_back"))
    {
        Key(EKeys::Escape);
        if(!Check(!Visible(HUD,TEXT("ModalPanel")),TEXT("Slate Escape returns from Settings"))) return;
        TMap<FName,float> Saved; if(!Check(UCRAudioSettingsSubsystem::ReadPreferences(Audio->GetPreferencesPath(),Saved),TEXT("Independent audio config persisted"))) return;
        for(int32 I=0;I<5;++I) if(!Check(FMath::IsNearlyEqual(Saved.FindChecked(InterfaceAudioGroups[I]),InterfaceAudioExpected[I],.001f),TEXT("Persisted slider value: ")+InterfaceAudioGroups[I].ToString())) return;
        if(Run.Mode==TEXT("Write")) { Key(EKeys::Enter); Next(TEXT("confirm_new")); }
        else { Run.Travel=true; bHandedOff=true; Key(EKeys::Enter); }
        return;
    }
    if(Run.Stage==TEXT("confirm_new"))
    {
        if(Age<=.25) return;
        if(!Check(Label(HUD,TEXT("ModalTitle"))==TEXT("START NEW GAME?"),TEXT("New Game has explicit confirmation"))) return;
        Capture(TEXT("03_NewGameConfirmation"),TEXT("new_game")); return;
    }
    if(Run.Stage==TEXT("new_game"))
    {
        Key(EKeys::Up); Run.Travel=true; bHandedOff=true; Key(EKeys::Enter); return;
    }
    Player=Cast<ACRCharacter>(PC->GetPawn());
    if(Run.Stage==TEXT("ready"))
    {
        if(!Player.IsValid() || !G->IsCheckpointReady() || Store->IsBusy() || !Audio->IsReady() || Age<1) return;
        if(!Check(!PC->bPrototypePaused&&!PC->bShowMouseCursor&&Player->Weapon->CanUse(),TEXT("Travel releases ordinary gameplay input"))) return;
        if(!Check(Store->GetLatest()&&Store->GetLatest()->CheckpointId==TEXT("CP00_START_YARD"),TEXT("Native CP00 callback completed; schema/checkpoint implementation preserved"))) return;
        OriginalRotation=PC->GetControlRotation(); OriginalHealth=Player->Health->Health;
        Player->Weapon->OnCue.AddDynamic(this,&ACRInterfaceAcceptance::WeaponCue);
        UAudioMixerBlueprintLibrary::StartRecordingOutput(this,60); bRecording=true;
        FFileHelper::SaveStringToFile(TEXT("Native mixed output recording active; input route starts after this marker.\n"),*(Run.Directory/TEXT("Recording.ready")));
        Capture(TEXT("04_GameplayHUD"),TEXT("fire")); return;
    }
    if(!Player.IsValid()) { Finish(false,TEXT("Lost player after readiness")); return; }
    auto* Weapon=Player->Weapon.Get();
    if(Player->Health->IsDead()) { Finish(false,TEXT("Unexpected death during isolated interface route")); return; }
    if(Run.Stage==TEXT("fire"))
    {
        Run.Events+=TEXT("NATIVE_FIXTURE TryFire aimed upward; no fake hit/kill awards.\n");
        PC->SetControlRotation(FRotator(75,OriginalRotation.Yaw,0));
        if(!Check(Weapon->TryFire(),TEXT("Accepted native shot exercises gameplay/audio event routing"))) return;
        Next(TEXT("reload")); return;
    }
    if(Run.Stage==TEXT("reload") && Age>1.1)
    {
        PC->SetControlRotation(OriginalRotation);
        BeforeMagazine=Weapon->Magazine; BeforeReserve=Weapon->Reserve;
        if(!Check(Weapon->TryReload(),TEXT("Native partial reload starts"))) return;
        GameplayKey(EKeys::I); Next(TEXT("pack_reload")); return;
    }
    if(Run.Stage==TEXT("pack_reload") && Age>3)
    {
        if(!Check(PC->IsFieldPackOpen()&&PC->bPrototypePaused&&PC->bShowMouseCursor&&Visible(HUD,TEXT("PackPanel")),TEXT("I binding opens Field Pack and owns paused input"))) return;
        if(!Check(Weapon->State==ECRWeaponState::Reloading&&Weapon->Magazine==BeforeMagazine&&Weapon->Reserve==BeforeReserve&&ReloadCompletions==0,TEXT("Reload transfer remains frozen after more than its duration in the bag"))) return;
        const auto Items=CRFieldPack::Items(CRFieldPack::Read(*G,*Player),0);
        if(!Check(Label(HUD,TEXT("PackDetailBody"))==Items[0].Description,TEXT("Equipment detail reflects authoritative current ammunition"))) return;
        Capture(TEXT("05_FieldPackEquipment"),TEXT("pack_mission")); return;
    }
    if(Run.Stage==TEXT("pack_mission"))
    {
        Key(EKeys::Right); Key(EKeys::Right); Key(EKeys::Right);
        const auto Items=CRFieldPack::Items(CRFieldPack::Read(*G,*Player),3);
        if(!Check(Label(HUD,TEXT("PackDetailTitle"))==Items[0].Name&&Label(HUD,TEXT("PackDetailState")).Contains(Items[0].State),TEXT("Slate category switch displays actual mission-item state"))) return;
        Capture(TEXT("06_FieldPackMission"),TEXT("pack_close")); return;
    }
    if(Run.Stage==TEXT("pack_close")) { Key(EKeys::I); Next(TEXT("reload_resumed")); return; }
    if(Run.Stage==TEXT("reload_resumed") && Age>2.8)
    {
        if(!Check(!PC->IsFieldPackOpen()&&!PC->bPrototypePaused&&!PC->bShowMouseCursor,TEXT("I closes bag and restores input/cursor"))) return;
        if(!Check(Weapon->State==ECRWeaponState::Ready&&Weapon->Magazine==5&&Weapon->Magazine+Weapon->Reserve==BeforeMagazine+BeforeReserve&&ReloadCompletions==1,TEXT("Reload resumes and completes exactly once with conserved ammunition"))) return;
        Weapon->SetAiming(true); Next(TEXT("aim_pack")); return;
    }
    if(Run.Stage==TEXT("aim_pack") && Age>.3)
    {
        if(!Check(Weapon->bAiming,TEXT("Native aim state entered before inventory fixture"))) return;
        Run.Events+=TEXT("NATIVE_FIXTURE ToggleFieldPack during aim; normal ClearHeldActions owns cancellation.\n");
        PC->ToggleFieldPack();
        if(!Check(PC->IsFieldPackOpen()&&!Weapon->bAiming&&!Weapon->bSprinting&&!Player->IsSprintHeld(),TEXT("Bag clears aim/sprint held state"))) return;
        Key(EKeys::Escape); PC->SetControlRotation(OriginalRotation); WalkStart=Player->GetActorLocation(); Next(TEXT("walk")); return;
    }
    if(Run.Stage==TEXT("walk"))
    {
        Inject(Player->ForwardAction);
        if(Age>1) { if(!Check(FVector::Dist2D(WalkStart,Player->GetActorLocation())>100,TEXT("Enhanced Input walking moves through the real floor"))) return; Next(TEXT("sprint")); }
        return;
    }
    if(Run.Stage==TEXT("sprint"))
    {
        Inject(Player->ForwardAction); Inject(Player->SprintAction);
        if(Age>.6)
        {
            if(!Check(Player->IsSprintHeld()&&Player->GetVelocity().Size2D()>430,TEXT("Grounded sprint reaches authored slide threshold"))) return;
            Inject(Player->CrouchAction); Next(TEXT("slide"));
        }
        return;
    }
    if(Run.Stage==TEXT("slide") && Age>.05)
    {
        if(!Check(Player->IsSliding(),TEXT("Enhanced Input starts the native grounded slide"))) return;
        Run.Events+=TEXT("NATIVE_FIXTURE ToggleFieldPack during actual grounded slide.\n"); PC->ToggleFieldPack();
        if(!Check(PC->IsFieldPackOpen()&&!Player->IsSliding()&&!Player->IsSprintHeld()&&!Weapon->bAiming,TEXT("Bag cancels slide safely and clears held input"))) return;
        Key(EKeys::Escape); Next(TEXT("pause")); return;
    }
    if(Run.Stage==TEXT("pause") && Age>.3)
    {
        GameplayKey(EKeys::Escape); Next(TEXT("pause_capture")); return;
    }
    if(Run.Stage==TEXT("pause_capture") && Age>.3)
    {
        if(!Check(PC->bPrototypePaused&&!PC->IsFieldPackOpen()&&Visible(HUD,TEXT("MenuBackdrop")),TEXT("Esc still opens ordinary pause menu"))) return;
        if(!Check(!PC->CanOpenFieldPack(),TEXT("Ordinary pause retains its own input ownership"))) return;
        Capture(TEXT("07_Paused"),TEXT("low_health")); return;
    }
    if(Run.Stage==TEXT("low_health"))
    {
        Key(EKeys::Escape);
        Run.Events+=TEXT("ISOLATED_DAMAGE_FIXTURE Native ApplyDamage reduces current health to20 for HUD capture; restored immediately afterward. Not combat survival evidence.\n");
        OriginalHealth=Player->Health->Health;
        if(OriginalHealth>20) UGameplayStatics::ApplyDamage(Player.Get(),OriginalHealth-20,PC.Get(),this,nullptr);
        Next(TEXT("low_capture")); return;
    }
    if(Run.Stage==TEXT("low_capture") && Age>.5)
    {
        if(!Check(Label(HUD,TEXT("HealthState"))==TEXT("LOW HEALTH"),TEXT("Native damage event updates low-health HUD"))) return;
        Capture(TEXT("08_LowHealthHUD"),TEXT("restore")); return;
    }
    if(Run.Stage==TEXT("restore"))
    {
        if(!Check(Player->Health->RestoreCheckpointHealth(OriginalHealth),TEXT("Isolated low-health fixture restored through native health method"))) return;
        if(!Check(!CRFieldPack::CanOpen(false,false,false,false,true,false,true,true)&&!CRFieldPack::CanOpen(false,false,false,false,false,true,true,true),TEXT("Pure guard rejects workbench and ending; actual cinematic lifecycle remains separate route coverage"))) return;
        if(!Check(ReloadCompletions==1,TEXT("No delayed duplicate reload completion after inventory/pause"))) return;
        if(!Check(Audio->GetEventCount(TEXT("Shot"))==1&&Audio->GetEventCount(TEXT("ReloadComplete"))==1,TEXT("One accepted report and one reload-complete audio dispatch; counts do not establish listening quality"))) return;
        const int32 Steps=Audio->GetEventCount(TEXT("FootConcrete"))+Audio->GetEventCount(TEXT("FootMetal"))+Audio->GetEventCount(TEXT("FootGravel"))+Audio->GetEventCount(TEXT("FootIndustrial"));
        if(!Check(Steps>0,TEXT("Actual walking/sprint distance dispatched surface footsteps"))) return;
        if(!Check(Audio->GetEventCount(TEXT("SlideStart"))==1&&Audio->GetEventCount(TEXT("SlideEnd"))==1,TEXT("Actual slide has one start and one cancellation end audio dispatch"))) return;
        Next(TEXT("audio_tail")); return;
    }
    if(Run.Stage==TEXT("audio_tail") && Age>1)
        Finish(true,TEXT("Isolated UI input, real state projection, reload/pause/slide fixtures and cross-process preferences passed; review captures/WAV separately"));
#endif
}
