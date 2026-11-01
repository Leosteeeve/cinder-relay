#include "CRAudioSettingsSubsystem.h"
#include "CRChapterStreamingController.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundClass.h"
#include "Sound/SoundMix.h"
#include "Sound/SoundAttenuation.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"

namespace
{
    const TCHAR* AudioRoot=TEXT("/Game/Generated/Phase055/Audio/");
    const TCHAR* ConfigSection=TEXT("CinderRelay.Audio");
    FSoftObjectPath AudioPath(const FString& Name) { return FSoftObjectPath(FString(AudioRoot)+Name+TEXT(".")+Name); }
}

UCRAudioSettingsSubsystem* UCRAudioSettingsSubsystem::Get(const UObject* Context)
{
    if(!Context) return nullptr;
    const UWorld* World=Context->GetWorld();
    return World && World->GetGameInstance()?World->GetGameInstance()->GetSubsystem<UCRAudioSettingsSubsystem>():nullptr;
}
TMap<FName,float> UCRAudioSettingsSubsystem::DefaultVolumes()
{
    return {{TEXT("Master"),.8f},{TEXT("SFX"),1.f},{TEXT("Weapons"),1.f},{TEXT("Foley"),1.f},
        {TEXT("Ambience"),.65f},{TEXT("UI"),.8f},{TEXT("Voice"),1.f},{TEXT("Music"),.7f}};
}
float UCRAudioSettingsSubsystem::SanitizeVolume(float Value,float DefaultValue)
{ return FMath::IsFinite(Value)?FMath::Clamp(Value,0.f,1.f):FMath::Clamp(DefaultValue,0.f,1.f); }
bool UCRAudioSettingsSubsystem::IsPreferenceSuffixValid(const FString& Suffix)
{
    if(Suffix.IsEmpty() || Suffix.Len()>40) return false;
    for(TCHAR Character:Suffix) if(!FChar::IsAlnum(Character) && Character!=TEXT('_')) return false;
    return true;
}
bool UCRAudioSettingsSubsystem::ReadPreferences(const FString& Filename,TMap<FName,float>& Values)
{
    Values=DefaultVolumes(); FConfigFile File;
    if(Filename.IsEmpty() || !FPaths::FileExists(Filename)) return false;
    File.Read(Filename);
    for(auto& Pair:Values) { float Value=Pair.Value; if(File.GetFloat(ConfigSection,*Pair.Key.ToString(),Value)) Pair.Value=SanitizeVolume(Value,Pair.Value); }
    return true;
}
bool UCRAudioSettingsSubsystem::WritePreferences(const FString& Filename,const TMap<FName,float>& Values)
{
    if(Filename.IsEmpty()) return false;
    IFileManager::Get().MakeDirectory(*FPaths::GetPath(Filename),true);
    FConfigFile File;
    for(const auto& Default:DefaultVolumes())
    {
        const float* Value=Values.Find(Default.Key);
        File.SetFloat(ConfigSection,*Default.Key.ToString(),SanitizeVolume(Value?*Value:Default.Value,Default.Value));
    }
    return File.Write(Filename,false);
}
void UCRAudioSettingsSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    PreferencesPath=FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("Config"),TEXT("CinderRelayAudio.ini"));
#if !UE_BUILD_SHIPPING
    FString Suffix;
    if(FParse::Value(FCommandLine::Get(),TEXT("CR055AudioTest="),Suffix))
    {
        // Invalid test input never falls back to a user's preference file.
        PreferencesPath=IsPreferenceSuffixValid(Suffix)?FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("Config"),TEXT("CR04_TEST_Audio_")+Suffix+TEXT(".ini")):FString();
    }
#endif
    ReadPreferences(PreferencesPath,Volumes);
    for(const TCHAR* Name:{TEXT("Cycle"),TEXT("Case"),TEXT("Dry"),TEXT("ReloadStart"),TEXT("FeedOut"),TEXT("FeedIn"),TEXT("ReloadComplete"),
        TEXT("UISelect"),TEXT("UIConfirm"),TEXT("UICancel"),TEXT("UIError"),TEXT("Collect"),TEXT("Confirm"),TEXT("Hit"),TEXT("Kill"),TEXT("Impact"),TEXT("Damage"),
        TEXT("SlideStart"),TEXT("SlideLoop"),TEXT("SlideEnd")}) SoundNames.Add(Name);
    for(const TCHAR* Family:{TEXT("RookOutdoor"),TEXT("RookWorkshop"),TEXT("RookBunker"),TEXT("FootConcrete"),TEXT("FootMetal"),TEXT("FootGravel"),TEXT("FootIndustrial")})
        for(int32 I=1;I<=3;++I) SoundNames.Add(FName(*FString::Printf(TEXT("%s%d"),Family,I)));
    TArray<FSoftObjectPath> Paths;
    for(FName Name:SoundNames) Paths.Add(AudioPath(TEXT("S_CR055_")+Name.ToString()));
    for(const auto& Pair:Volumes) Paths.Add(AudioPath(TEXT("SC_CR055_")+Pair.Key.ToString()));
    Paths.Add(AudioPath(TEXT("SMX_CR055_Settings"))); Paths.Add(AudioPath(TEXT("ATT_CR055_Spatial")));
    AssetLoad=UAssetManager::GetStreamableManager().RequestAsyncLoad(Paths,FStreamableDelegate::CreateUObject(this,&UCRAudioSettingsSubsystem::AssetsReady));
}
void UCRAudioSettingsSubsystem::AssetsReady()
{
    bReady=true;
    for(FName Name:SoundNames)
    {
        auto* Sound=Cast<USoundBase>(AudioPath(TEXT("S_CR055_")+Name.ToString()).ResolveObject());
        Sounds.Add(Name,Sound); bReady&=Sound!=nullptr;
    }
    for(const auto& Pair:Volumes)
    {
        auto* Class=Cast<USoundClass>(AudioPath(TEXT("SC_CR055_")+Pair.Key.ToString()).ResolveObject());
        Classes.Add(Pair.Key,Class); bReady&=Class!=nullptr;
    }
    Mix=Cast<USoundMix>(AudioPath(TEXT("SMX_CR055_Settings")).ResolveObject());
    SpatialAttenuation=Cast<USoundAttenuation>(AudioPath(TEXT("ATT_CR055_Spatial")).ResolveObject());
    bReady&=Mix!=nullptr && SpatialAttenuation!=nullptr;
    UE_LOG(LogTemp,Display,TEXT("CR055_AUDIO Ready=%d critical_sounds=%d"),bReady,SoundNames.Num());
    if(AudioWorld.IsValid()) ApplyMix(AudioWorld.Get());
}
float UCRAudioSettingsSubsystem::GetVolume(FName Category) const
{ const float* Value=Volumes.Find(Category);return Value?*Value:1.f; }
void UCRAudioSettingsSubsystem::SetVolume(FName Category,float Volume)
{
    float* Existing=Volumes.Find(Category); if(!Existing) return;
    *Existing=SanitizeVolume(Volume,DefaultVolumes().FindChecked(Category));
    if(bReady && AudioWorld.IsValid()) UGameplayStatics::SetSoundMixClassOverride(AudioWorld.Get(),Mix,Classes.FindChecked(Category),*Existing,1.f,.08f,true);
}
void UCRAudioSettingsSubsystem::SavePreferences()
{
    const bool Saved=!PreferencesPath.IsEmpty() && WritePreferences(PreferencesPath,Volumes);
    UE_LOG(LogTemp,Display,TEXT("CR055_AUDIO PreferencesSaved=%d"),Saved);
}
void UCRAudioSettingsSubsystem::ApplyMix(UWorld* World)
{
    if(!World) return;
    if(AudioWorld.Get()!=World || !Streaming.IsValid())
    {
        AudioWorld=World; Streaming.Reset();
        for(TActorIterator<ACRChapterStreamingController> It(World);It;++It) {Streaming=*It;break;}
    }
    if(!bReady) return;
    UGameplayStatics::SetBaseSoundMix(World,Mix);
    for(const auto& Pair:Volumes) UGameplayStatics::SetSoundMixClassOverride(World,Mix,Classes.FindChecked(Pair.Key),Pair.Value,1.f,.08f,true);
}
int32 UCRAudioSettingsSubsystem::GetEnvironmentZone(FVector Position) const
{
    // Existing persistent streaming policy is authoritative; coordinate fallback
    // only covers isolated fixtures/rollback maps lacking that actor.
    return Streaming.IsValid()?FMath::Clamp(Streaming->CurrentZone,0,2):Position.X<1600?0:Position.X<4800?1:2;
}
FName UCRAudioSettingsSubsystem::ChooseFootSurface(FName PhysicalMaterial,FName ComponentName,int32 Zone)
{
    const FString Surface=(PhysicalMaterial.ToString()+TEXT(" ")+ComponentName.ToString()).ToLower();
    if(Surface.Contains(TEXT("metal")) || Surface.Contains(TEXT("grate")) || Surface.Contains(TEXT("rail"))) return TEXT("FootMetal");
    if(Surface.Contains(TEXT("gravel")) || Surface.Contains(TEXT("yardground"))) return TEXT("FootGravel");
    if(Surface.Contains(TEXT("concrete")) || Surface.Contains(TEXT("ramp"))) return TEXT("FootConcrete");
    if(Surface.Contains(TEXT("industrial")) || Surface.Contains(TEXT("workshopfloor"))) return TEXT("FootIndustrial");
    return Zone==0?FName(TEXT("FootGravel")):Zone==1?FName(TEXT("FootIndustrial")):FName(TEXT("FootConcrete"));
}
FName UCRAudioSettingsSubsystem::ResolveVariant(FName Event,FVector Position)
{
    if(Event==TEXT("Shot")) Event=GetEnvironmentZone(Position)==0?TEXT("RookOutdoor"):GetEnvironmentZone(Position)==1?TEXT("RookWorkshop"):TEXT("RookBunker");
    const FString Family=Event.ToString();
    if(Family.StartsWith(TEXT("Rook")) || Family.StartsWith(TEXT("Foot")))
    {
        int32& Index=Variants.FindOrAdd(Event); Index=Index%3+1;
        return FName(*(Family+FString::FromInt(Index)));
    }
    return Event;
}
USoundBase* UCRAudioSettingsSubsystem::GetResidentSound(FName Event) const
{ const auto* Sound=Sounds.Find(Event);return bReady && Sound?Sound->Get():nullptr; }
void UCRAudioSettingsSubsystem::PlayUI(FName Event)
{
    TRACE_CPUPROFILER_EVENT_SCOPE(CR055_UIAudio);
    if(!AudioWorld.IsValid() || !bReady) return;
    if(Event==TEXT("UISelect")) {const double Now=FPlatformTime::Seconds();if(Now-LastUISelect<.055)return;LastUISelect=Now;}
    if(USoundBase* Sound=GetResidentSound(Event))
    {
        UGameplayStatics::PlaySound2D(AudioWorld.Get(),Sound,1.f,1.f,0.f,nullptr,nullptr,true);
#if !UE_BUILD_SHIPPING
        ++EventCounts.FindOrAdd(Event);
#endif
    }
}
void UCRAudioSettingsSubsystem::PlayEvent(FName Event,const UObject* Context,FVector Location,bool Spatial)
{
    TRACE_CPUPROFILER_EVENT_SCOPE(CR055_GameAudio);
    if(!bReady || !Context || !Context->GetWorld() || Context->GetWorld()->IsPaused()) return;
    if(USoundBase* Sound=GetResidentSound(ResolveVariant(Event,Location)))
    {
        if(Spatial) UGameplayStatics::PlaySoundAtLocation(Context,Sound,Location,1.f,1.f,0.f,SpatialAttenuation);
        else UGameplayStatics::PlaySound2D(Context,Sound,1.f,1.f,0.f,nullptr,nullptr,false);
#if !UE_BUILD_SHIPPING
        ++EventCounts.FindOrAdd(Event);
#endif
    }
}
void UCRAudioSettingsSubsystem::Deinitialize()
{
    bReady=false;
    if(AssetLoad) {AssetLoad->CancelHandle();AssetLoad.Reset();}
    Sounds.Reset();Classes.Reset();Mix=nullptr;SpatialAttenuation=nullptr;Streaming.Reset();AudioWorld.Reset();
    Super::Deinitialize();
}
