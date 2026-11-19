#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CRInterfaceLayout.generated.h"

class UWidgetTree;
class UWidget;

/** Shared visual construction only. Gameplay and modal authority remain in the existing HUD/controller. */
namespace CRInterfaceLayout
{
    CINDERRELAY_API bool Build(UWidgetTree* Tree, UObject* BodyFont, UObject* TitleFont, FName Panel = TEXT("HUDRoot"));
    void ApplyChapterLayout(UWidgetTree* Tree, UObject* BodyFont, UObject* TitleFont);
    UWidget* StationSection(UWidgetTree* Tree, UObject* Font, int32 TaskArea = INDEX_NONE, FName Name = NAME_None);
}

/** Editor bridge uses reflected properties, keeping UMGEditor out of the runtime module. */
UCLASS()
class CINDERRELAY_API UCRInterfaceLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Cinder Relay|Interface|Authoring")
    static bool BuildDesignerLayout(UObject* Blueprint, UObject* BodyFont, UObject* TitleFont, FName Panel);

    UFUNCTION(BlueprintCallable, Category="Cinder Relay|Interface|Authoring")
    static bool UpgradeDesignerArtworkAspect(UObject* Blueprint);

    UFUNCTION(BlueprintCallable, Category="Cinder Relay|Interface|Authoring")
    static bool ConfigureCompositeFont(UObject* Font, UObject* FontFace);

    UFUNCTION(BlueprintCallable, Category="Cinder Relay|Interface|Authoring")
    static TArray<FName> GetDesignerWidgetNames(UObject* Blueprint);
};
