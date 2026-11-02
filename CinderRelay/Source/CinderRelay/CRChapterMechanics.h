#pragma once

// Chapter-local, engine-independent transition rules shared by actors and bounded tests.
namespace CRChapterMechanics
{
    inline bool RetainNeighbor(bool Requested, bool Near, bool Occupied, float Aperture)
    { return (Requested && (Near || Occupied)) || Aperture > 0; }
    inline bool CanPassDoor(bool Requested, bool Ready, float Aperture)
    { return Requested && Ready && Aperture >= 1; }
    inline bool CanCloseDoor(bool Occupied) { return !Occupied; }
    inline int DiagnosticStep(int Current, int Selected)
    { return Current >= 0 && Current < 3 && Selected == Current ? Current + 1 : Current; }
    inline bool HoldMachineOpen(float Aperture, bool CapsuleInside) { return Aperture > .7f && CapsuleInside; }
}
