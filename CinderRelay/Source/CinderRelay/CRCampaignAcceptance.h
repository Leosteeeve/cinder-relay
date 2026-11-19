#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CRCampaignAcceptance.generated.h"

/** Opt-in packaged traversal of the campaign's film and map handoffs. */
UCLASS(Transient, NotBlueprintable)
class ACRCampaignAcceptance : public AActor
{
	GENERATED_BODY()
public:
	ACRCampaignAcceptance();
protected:
	void BeginPlay() override;
	void EndPlay(const EEndPlayReason::Type Reason) override;
	void Tick(float DeltaSeconds) override;
private:
#if !UE_BUILD_SHIPPING
	FString Mode, Directory;
	double LastFrame = -1;
	bool bRecording = false;
	void StopSound();
	void Finish(bool Pass, const FString& Reason);
#endif
};
