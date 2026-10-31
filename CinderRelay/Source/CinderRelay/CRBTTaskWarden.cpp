#include "CRBTTaskWarden.h"
#include "CRAshWardenController.h"
#include "BehaviorTree/BehaviorTreeComponent.h"
UCRBTTaskWarden::UCRBTTaskWarden() { NodeName=TEXT("Ash Warden: perceived state decision"); }
EBTNodeResult::Type UCRBTTaskWarden::ExecuteTask(UBehaviorTreeComponent& OwnerComp,uint8*)
{
    if(auto* AI=Cast<ACRAshWardenController>(OwnerComp.GetAIOwner())) { AI->Decide(); return EBTNodeResult::Succeeded; }
    return EBTNodeResult::Failed;
}
