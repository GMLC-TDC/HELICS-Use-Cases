#ifndef OPENDSS_H
#define OPENDSS_H
#include <petsc.h>
#include <complex.h>
extern PetscErrorCode OpenDSSRunCommand(const char*);
extern PetscErrorCode OpenDSSVsourcesSetPU(PetscScalar);
extern PetscErrorCode OpenDSSVsourcesSetAngleDeg(PetscScalar);
extern PetscErrorCode OpenDSSSolutionGetSolve(PetscInt*);
extern PetscErrorCode OpenDSSCircuitGetTotalPower(double complex**);
#endif
