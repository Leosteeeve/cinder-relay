#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "CRAudioSettingsSubsystem.generated.h"

class USoundBase;
class USoundClass;
class USoundMix;
class USoundAttenuation;
class ACRChapterStreamingController;
struct FStreamableHandle;

/** Audio presentation/preferences only. Never stores chapter state or loads in a shot callback. */
UCLASS()
class CINDERRELAY_API UCRAudioSettingsSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    static UCRAudioSettingsSubsystem* Get(const UObject* WorldContext);
    float GetVolume(FName Category) const;
    void SetVolume(FName Category, float Volume);
    void SavePreferences();
    void ApplyMix(UWorld* World);
    void PlayUI(FName Event);
    void PlayEvent(FName Event, const UObject* WorldContext, FVector Location, bool Spatial);
    bool IsReady() const { return bReady; }
    USoundBase* GetResidentSound(FName Event) const;
    int32 GetEnvironmentZone(FVector FallbackLocation) const;
    static float SanitizeVolume(float Value, float DefaultValue);
    static bool IsPreferenceSuffixValid(const FString& Suffix);
    static FName ChooseFootSurface(FName PhysicalMaterial, FName ComponentName, int32 Zone);
    // Narrow, independent configuration helpers also allow tests to use fresh private paths.
    static bool ReadPreferences(const FString& Filename, TMap<FName, float>& Values);
    static bool WritePreferences(const FString& Filename, const TMap<FName, float>& Values);
    static TMap<FName, float> DefaultVolumes();
    const FString& GetPreferencesPath() const { return PreferencesPath; }
#if !UE_BUILD_SHIPPING
    int32 GetEventCount(FName Event) const { const int32* Count=EventCounts.Find(Event); return Count?*Count:0; }
#endif
private:
    void AssetsReady();
    FName ResolveVariant(FName Event, FVector Position);
    TSharedPtr<FStreamableHandle> AssetLoad;
    TArray<FName> SoundNames;
    TMap<FName, float> Volumes;
    TMap<FName, int32> Variants;
    FString PreferencesPath;
    TWeakObjectPtr<UWorld> AudioWorld;
    TWeakObjectPtr<ACRChapterStreamingController> Streaming;
    bool bReady=false;
    double LastUISelect=-1;
    UPROPERTY(Transient) TMap<FName, TObjectPtr<USoundBase>> Sounds;
    UPROPERTY(Transient) TMap<FName, TObjectPtr<USoundClass>> Classes;
    UPROPERTY(Transient) TObjectPtr<USoundMix> Mix;
    UPROPERTY(Transient) TObjectPtr<USoundAttenuation> SpatialAttenuation;
#if !UE_BUILD_SHIPPING
    TMap<FName, int32> EventCounts;
#endif
};
