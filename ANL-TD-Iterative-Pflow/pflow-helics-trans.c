static char help[] = "User example calling DYN.\n\n";

#include <pflow.h>
#include <ValueFederate.h>
#include <unistd.h>

#define MAX_DFEDS 300 // Max. D federates allowed

typedef struct {
  helics_federate vfed;
  helics_publication pub[MAX_DFEDS];
  helics_subscription sub[MAX_DFEDS];
  helics_time_t      currenttime;
  PetscInt           nbdry;
  PetscInt           tbdry_bus[MAX_DFEDS];
  char               pub_topics[MAX_DFEDS][PETSC_MAX_PATH_LEN];
  char               sub_topics[MAX_DFEDS][PETSC_MAX_PATH_LEN];
  PetscInt           ndfeds;
  PetscInt           feeder_bdry_bus[MAX_DFEDS];
  PetscInt           feeder_bdry_to_tbdry_map[MAX_DFEDS];
} UserData;


PetscErrorCode ReadTransMetaData(char metadatafile[],UserData *user)
{
  FILE *fp;
  user->ndfeds = 0;
  char line[MAXLINE];
  PetscInt i,j;

  PetscFunctionBegin;
  fp = fopen(metadatafile,"r");

  fgets(line,MAXLINE,fp);
  sscanf(line,"%d,%d",&user->nbdry,&user->ndfeds); // Number of distribution federates
  if(user->ndfeds > MAX_DFEDS) {
    SETERRQ(PETSC_COMM_SELF,0,"Max. distribution feeders allowed = 300, Increase MAX_DFEDS value in source code");
  }
  for(i=0; i < user->nbdry;i++) {
    fgets(line,MAXLINE,fp);
    sscanf(line,"%d",&user->tbdry_bus[i]);
  }
  
  for(i=0; i < user->ndfeds;i++) {
    fgets(line,MAXLINE,fp);
    sscanf(line,"%d,%s",&user->feeder_bdry_bus[i],user->sub_topics[i]);
  }

  /* Set up feeder boundary to boundary bus map */
  for(i=0; i < user->ndfeds;i++) {
    for(j=0; j < user->nbdry; j++) {
      if(user->feeder_bdry_bus[i] == user->tbdry_bus[j]) {
	user->feeder_bdry_to_tbdry_map[i] = j;
	break;
      }
    }
  }
  fclose(fp);

  PetscFunctionReturn(0);
}
  
helics_status CreateTransmissionFederate(helics_federate *transfed)
{
  helics_federate_info_t fedinfo;
  helics_status   status;
  const char*    fedinitstring="--federates=1";
  helics_federate vfed;

  /* Create Federate Info object that describes the federate properties */
  fedinfo = helicsFederateInfoCreate();
  
  /* Set Federate name */
  status = helicsFederateInfoSetFederateName(fedinfo,"Transmission Federate");

  /* Set core type from string */
  status = helicsFederateInfoSetCoreTypeFromString(fedinfo,"zmq");

  /* Federate init string */
  status = helicsFederateInfoSetCoreInitString(fedinfo,fedinitstring);

  /* Set the message interval (timedelta) for federate. Note that
     HELICS minimum message time interval is 1 ns and by default
     it uses a time delta of 1 second. What is provided to the
     setTimedelta routine is a multiplier for the default timedelta.
  */
  /* Set one second message interval */
  status = helicsFederateInfoSetTimeDelta(fedinfo,1.0);

  status = helicsFederateInfoSetLoggingLevel(fedinfo,1);

  /* Create value federate */
  vfed = helicsCreateValueFederate(fedinfo);

  *transfed = vfed;

  return status;
}

int main(int argc,char **argv)
{
  PetscErrorCode ierr;
  UserData       user;
  PFLOW          pflow;
  const char*    helicsversion;
  helics_status   status;
  PetscBool      flg;
  char           netfile[PETSC_MAX_PATH_LEN]="datafiles/case_ACTIVSg200.m",metadatafile[PETSC_MAX_PATH_LEN]="metadatafile";
  PetscInt       i,strlen;
  
  PetscInitialize(&argc,&argv,"petscopt",help);
  
  helicsversion = helicsGetVersion();
  printf("T FEDERATE: Helics version = %s\n",helicsversion);

  /* Create PFLOW object */
  ierr = PFLOWCreate(PETSC_COMM_WORLD,&pflow);CHKERRQ(ierr);


  /* Read network data */
  ierr = PetscOptionsGetString(NULL,NULL,"-netfile",netfile,PETSC_MAX_PATH_LEN,&flg);CHKERRQ(ierr);
  ierr = PFLOWReadMatPowerData(pflow,netfile);

  /* Read Metadatafile describing connection between T & D */
  ierr = PetscOptionsGetString(NULL,NULL,"-metadatafile",metadatafile,PETSC_MAX_PATH_LEN,&flg);CHKERRQ(ierr);
  ierr = ReadTransMetaData(metadatafile,&user);

  /* Create transmission federate */
  status = CreateTransmissionFederate(&user.vfed);
  printf("Created T FEDERATE\n");

  for(i=0; i < user.ndfeds; i++) {
    ierr = PetscStrcpy(user.pub_topics[i],"Trans/");
    ierr = PetscStrcat(user.pub_topics[i],user.sub_topics[i]);
    /* Register the publication */
    user.pub[i] = helicsFederateRegisterGlobalPublication(user.vfed,user.pub_topics[i],"string","");
    printf("T FEDERATE: Publication registered for D federate %s\n",user.sub_topics[i]);

    /* Register the subscription */
    user.sub[i] = helicsFederateRegisterSubscription(user.vfed,user.sub_topics[i],"string","");
    printf("T FEDERATE: Subscription registered to D federate %s\n",user.sub_topics[i]);
  }

  status = helicsFederateEnterInitializationMode(user.vfed);
  printf("T FEDERATE entered initialization mode\n");


  status = helicsFederateEnterExecutionMode(user.vfed);
  printf("T FEDERATE entered execution mode\n");
  user.currenttime = 0.0;

  PetscInt      iter=0;
  PetscScalar   Vm[MAX_DFEDS],Va[MAX_DFEDS],Pd[MAX_DFEDS],Qd[MAX_DFEDS],Vmprv[MAX_DFEDS],Vaprv[MAX_DFEDS],Pdtemp,Qdtemp;
  PetscBool     found;
  int           isupdated;
  PetscBool     pflow_conv=PETSC_FALSE;
  PetscScalar   tol=1E-8,mis;
  char          pubstr[PETSC_MAX_PATH_LEN],substr[PETSC_MAX_PATH_LEN];
  PetscInt      max_it=100;

  /* Solve transmission power flow */
  printf("T FEDERATE running power flow\n");
  ierr = PFLOWSolve(pflow);CHKERRQ(ierr);

  while(!pflow_conv && iter < max_it) {
    iter++;
    
    /* 1. Semd boundary bus voltages to D federates */

       /* Get boundary bus voltages */
    for(i=0; i < user.nbdry; i++) {
      Pd[i] = Qd[i] = 0.0;
      ierr = PFLOWGetBusVoltage(pflow,user.tbdry_bus[i],&Vmprv[i],&Vaprv[i],&found);CHKERRQ(ierr);
    }

    for(i=0; i < user.ndfeds; i++) {
      ierr = PetscSNPrintf(pubstr,PETSC_MAX_PATH_LEN-1,"%18.16f,%18.16f",Vmprv[user.feeder_bdry_to_tbdry_map[i]],Vaprv[user.feeder_bdry_to_tbdry_map[i]]);CHKERRQ(ierr);
      status = helicsPublicationPublishString(user.pub[i],pubstr);
      printf("T FEDERATE sent Vm = %4.3f, Va = %4.3f to D FEDERATE on topic %s\n",Vmprv[user.feeder_bdry_to_tbdry_map[i]],Vaprv[user.feeder_bdry_to_tbdry_map[i]],user.pub_topics[i]);
    }

      /* Publish boundary bus voltage */
    status = helicsFederateRequestTime(user.vfed,user.currenttime,&user.currenttime);

    /* 2. Receive distribution power injection */
    status = helicsFederateRequestTime(user.vfed,user.currenttime,&user.currenttime);

    for(i=0; i < user.ndfeds; i++) {
      isupdated = helicsSubscriptionIsUpdated(user.sub[i]);
      if(isupdated) {
	status = helicsSubscriptionGetString(user.sub[i],substr,PETSC_MAX_PATH_LEN-1,&strlen);
	sscanf(substr,"%lf,%lf",&Pdtemp,&Qdtemp);
	printf("T FEDERATE received Pd = %4.3f, Qd = %4.3f from D FEDERATE %s\n",Pdtemp,Qdtemp,user.sub_topics[i]);
	Pd[user.feeder_bdry_to_tbdry_map[i]] += Pdtemp;
	Qd[user.feeder_bdry_to_tbdry_map[i]] += Qdtemp;
      }
    }

    for(i=0; i < user.nbdry; i++) {
      ierr = PFLOWSetLoadPower(pflow,user.tbdry_bus[i],Pd[i],Qd[i]);CHKERRQ(ierr);
    }

    /* 3. Solve Transmission power flow */
    printf("T FEDERATE running power flow\n");
    ierr = PFLOWSolve(pflow);CHKERRQ(ierr);

    for(i=0; i < user.nbdry; i++) {
      ierr = PFLOWGetBusVoltage(pflow,user.tbdry_bus[i],&Vm[i],&Va[i],&found);CHKERRQ(ierr);
    }

    /* 4. Compute voltage mismatch */
    mis = 0.0;
    for(i=0; i < user.nbdry; i++) {  
      mis += (Vm[i]-Vmprv[i])*(Vm[i]-Vmprv[i]) + ((Va[i]-Vaprv[i])*PETSC_PI/180.0)*((Va[i]-Vaprv[i])*PETSC_PI/180.0); /* Angle converted to radians */
    }
    
    if(PetscSqrtScalar(mis) < tol) {
      pflow_conv = PETSC_TRUE;
    }
    /* 5. Send convergence signal to D federates */
    for(i=0; i < user.ndfeds; i++) {
      ierr = PetscSNPrintf(pubstr,PETSC_MAX_PATH_LEN-1,"%d",(PetscInt)pflow_conv);CHKERRQ(ierr);
      status = helicsPublicationPublishString(user.pub[i],pubstr);
    }
       /* Publish convergence status */
    status = helicsFederateRequestTime(user.vfed,user.currenttime,&user.currenttime);

    printf("Iteration %d: mis = %g,converged = %d\n",iter,PetscSqrtScalar(mis),pflow_conv);
  }

  /* Destroy PFLOW object */
  ierr = PFLOWDestroy(&pflow);CHKERRQ(ierr);

  status = helicsFederateEnterExecutionModeComplete(user.vfed);  
  status = helicsFederateFinalize(user.vfed);


  PetscFinalize();
  return 0;
}
  
