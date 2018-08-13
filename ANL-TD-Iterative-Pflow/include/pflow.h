#ifndef PFLOW_H
#define PFLOW_H

#include <petsc.h>

#define epsilon 1E-8 /**< epsilon value for finite differences */
#define MAXLINE 1000 /**< Max. number of characters in a line */
#define ISOLATED_BUS 4 /**< Isolated bus */
#define REF_BUS 3 /**< Reference bus (swing bus) */
#define PV_BUS 2 /**< PV (voltage-controlled) bus */
#define PQ_BUS 1 /**< PQ bus */
#define NGEN_AT_BUS_MAX 15 /**< Maximum number of generators allowed at a bus */
#define NLOAD_AT_BUS_MAX 10 /**< Maximum number of loads allowed at a bus */
#define NPHASE 1 /**< Per-phase analysis */

typedef void* PFLOW;

extern PetscErrorCode PFLOWCreate(MPI_Comm,PFLOW*);
extern PetscErrorCode PFLOWDestroy(PFLOW*);
extern PetscErrorCode PFLOWReadMatPowerData(PFLOW,const char[]);
extern PetscErrorCode PFLOWSolve(PFLOW);
extern PetscErrorCode PFLOWGetBusVoltage(PFLOW,PetscInt,PetscScalar*,PetscScalar*,PetscBool*);
extern PetscErrorCode PFLOWSetLoadPower(PFLOW,PetscInt,PetscScalar,PetscScalar);

#endif


