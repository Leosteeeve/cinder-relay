#pragma once
#include "CoreMinimal.h"
#include "BehaviorTree/BTTaskNode.h"
#include "CRBTTaskWarden.generated.h"
UCLASS()
class CINDERRELAY_API UCRBTTaskWarden : public UBTTaskNode
{
    GENERATED_BODY()
public:
    UCRBTTaskWarden();
    virtual EBTNodeResult::Type ExecuteTask(UBehaviorTreeComponent& OwnerComp,uint8* NodeMemory) override;
};
