#include "../Source/CinderRelay/CRChapterMechanics.h"
#include <cstdio>
int main()
{
    int Failures = 0;
    auto Check = [&Failures](bool Pass, const char* Name) { if (!Pass) { ++Failures; std::printf("FAIL %s\n", Name); } };
    using namespace CRChapterMechanics;
    Check(!RetainNeighbor(false,true,false,0), "approach alone must not load neighbor");
    Check(RetainNeighbor(true,true,false,0), "accepted open request loads neighbor");
    Check(!RetainNeighbor(false,true,true,0), "standing at closed door alone must not request loading");
    Check(RetainNeighbor(false,false,true,.5f), "occupied open boundary retains both floors");
    Check(RetainNeighbor(false,false,false,.4f), "closing door retains geometry until sealed");
    Check(!RetainNeighbor(true,false,false,0), "abandoned closed request releases neighbor");
    Check(!CanPassDoor(true,false,1), "fully raised door cannot pass without native readiness");
    Check(!CanPassDoor(true,true,.5f), "partial motion cannot pass");
    Check(!CanPassDoor(false,true,1), "close request blocks passage");
    Check(CanPassDoor(true,true,1), "ready fully opened door passes");
    Check(!CanCloseDoor(true), "cannot close on player");
    Check(CanCloseDoor(false), "empty threshold can close");
    Check(DiagnosticStep(0,2)==0, "out of order release cannot award module access");
    Check(DiagnosticStep(0,0)==1, "route accepted");
    Check(DiagnosticStep(1,0)==1, "repeat cannot duplicate progress");
    Check(DiagnosticStep(1,2)==1, "wrong order preserves recoverable progress");
    Check(DiagnosticStep(1,1)==2 && DiagnosticStep(2,2)==3, "verify then release");
    Check(DiagnosticStep(3,2)==3, "finished activity is idempotent");
    Check(!HoldMachineOpen(0,true), "approaching a closed machine does not bypass its timed cycle");
    Check(HoldMachineOpen(1,true), "occupied open machinery remains safely open");
    Check(!HoldMachineOpen(1,false), "clear machinery may cycle");
    std::printf("CR06_MECHANICS failures=%d\n",Failures);
    return Failures ? 1 : 0;
}
