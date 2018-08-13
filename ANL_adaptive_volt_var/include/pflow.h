/**
 * @file pflow.h
 * @brief Public header file for power flow application
 */

#ifndef PFLOW_H
#define PFLOW_H

#include <petsc.h>
#include "cJSON.h"

typedef struct _p_PFLOW *PFLOW;

PETSC_EXTERN PetscErrorCode PFLOWCreate(MPI_Comm,PFLOW*);
PETSC_EXTERN PetscErrorCode PFLOWDestroy(PFLOW*);
PETSC_EXTERN PetscErrorCode PFLOWReadMatPowerData(PFLOW,const char[]);
PETSC_EXTERN PetscErrorCode PFLOWSolve(PFLOW);
PETSC_EXTERN PetscErrorCode PFLOWPostSolve(PFLOW);

/* FUNCTIONS FOR PARSING DATA */
int PFLOWParserGetVal(cJSON *, const char *, double *, int);
double PFLOWParserGet(PFLOW,int,char *, const char *);
void PFLOWParserSet(PFLOW,int,char *, PetscScalar, const char *);


#endif


