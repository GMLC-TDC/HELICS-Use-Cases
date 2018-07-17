static char help[] = "Broker for DYNHELICS\n";

#include <stdio.h>
#include <unistd.h>
#include <helics.h>
#include <petsc.h>

int main(int argc,char **argv)
{
  helics_broker broker;
  const char*   helicsversion;
  int            isconnected;
  char           initstring[PETSC_MAX_PATH_LEN];
  PetscInt       nfederates=0;
  PetscErrorCode ierr;

  PetscInitialize(&argc,&argv,"petscopt",help);

  helicsversion = helicsGetVersion();

  printf("BROKER: Helics version = %s\n",helicsversion);
  printf("%s",help);

  ierr = PetscOptionsGetInt(NULL,NULL,"-nfeds",&nfederates,NULL);CHKERRQ(ierr);
  if(!nfederates) {
    SETERRQ(PETSC_COMM_SELF,0,"Number of federates need to be given with option -nfeds");
  }
  ierr = PetscSNPrintf(initstring,PETSC_MAX_PATH_LEN-1,"%d",nfederates);
  ierr = PetscStrcat(initstring," --name=mainbroker");


  /* Create broker */
  broker = helicsCreateBroker("zmq","",initstring);

  isconnected = helicsBrokerIsConnected(broker);

  if(isconnected) {
    printf("BROKER: Created and connected\n");
  }

  while(helicsBrokerIsConnected(broker)) {
    usleep(1000); /* Sleep for 1 millisecond */
  }
  printf("BROKER: disconnected\n");
  helicsBrokerFree(broker);
  helicsCloseLibrary();

  printf("Helics library closed\n");
  PetscFinalize();
  return 0;
}

