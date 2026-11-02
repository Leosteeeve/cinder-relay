#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CRInterfaceLayout.generated.h"

class UWidgetTree;

/** Shared visual construction only. Gameplay and modal authority remain in the existing HUD/controller. */
namespace CRInterfaceLayout
{
    CINDERRELAY_API bool Build(UWidgetTree* Tree, UObject* BodyFont, UObject* TitleFont, FName Panel = TEXT("HUDRoot"));
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
