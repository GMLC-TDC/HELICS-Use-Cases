static char help[] = "User example for pflow helics distribution federate.\n\n";

#include <petsc.h>
#include <ValueFederate.h>
#include <opendss.h>
#include <complex.h>

typedef struct {
  helics_federate vfed;
  helics_publication pub;
  helics_subscription sub;
  helics_time_t currenttime;
  char       pub_topic[PETSC_MAX_PATH_LEN];
} UserData;

helics_status CreateDistributionFederate(helics_federate *distfed,char* pub_topic)
{
  helics_federate_info_t fedinfo;
  helics_status   status;
  const char*    fedinitstring="--federates=1";
  helics_federate vfed;
  char            fedname[PETSC_MAX_PATH_LEN];
  PetscErrorCode ierr;
  
  /* Create Federate Info object that describes the federate properties */
  fedinfo = helicsFederateInfoCreate();

  ierr = PetscStrcpy(fedname,"Distribution Federate ");CHKERRQ(ierr);
  ierr = PetscStrcat(fedname,pub_topic);CHKERRQ(ierr);
  /* Set Federate name */
  status = helicsFederateInfoSetFederateName(fedinfo,fedname);

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

  *distfed = vfed;

  return status;
}

int main(int argc,char **argv)
{
  PetscErrorCode ierr;
  const char*    helicsversion;
  UserData       user;
  helics_status   status;
  PetscBool      flg;
  char           netfile[PETSC_MAX_PATH_LEN],dcommand[PETSC_MAX_PATH_LEN];
  char           sub_topic[PETSC_MAX_PATH_LEN];
  double complex *Stotal;
  PetscInt      iter=0;
  PetscScalar   Vm,Va;
  int           isupdated;
  PetscScalar   Pg,Qg;
  PetscBool     converged,pflow_conv=PETSC_FALSE;
  char          pubstr[PETSC_MAX_PATH_LEN],substr[PETSC_MAX_PATH_LEN];
  PetscInt      max_it=100;
  PetscInt      strlen;

  
  PetscInitialize(&argc,&argv,NULL,help);
  
  helicsversion = helicsGetVersion();

  printf("D FED: Helics version = %s\n",helicsversion);

  /* Get network data file from command line */
  ierr = PetscOptionsGetString(NULL,NULL,"-netfile",netfile,PETSC_MAX_PATH_LEN,&flg);CHKERRQ(ierr);

  ierr = PetscSNPrintf(dcommand,PETSC_MAX_PATH_LEN-1,"Redirect ");CHKERRQ(ierr);
  ierr = PetscStrcat(dcommand,netfile);CHKERRQ(ierr);

  /* Load the D file */
  ierr = OpenDSSRunCommand(dcommand);CHKERRQ(ierr);


  flg = PETSC_FALSE;
  /* Get the distribution topic for publication stream */
  ierr = PetscOptionsGetString(NULL,NULL,"-dtopic",user.pub_topic,PETSC_MAX_PATH_LEN,&flg);CHKERRQ(ierr);
  if(!flg) {
    SETERRQ(PETSC_COMM_SELF,0,"Need to specify the publication name, option -dtopic <topic_name>.\n This is same as the distribution feeder file name without the extension");
  }

    /* Create distribution federate */
  status = CreateDistributionFederate(&user.vfed,user.pub_topic);
  printf("Created D FEDERATE %s\n",user.pub_topic);

  /* Register the publication */
  user.pub = helicsFederateRegisterGlobalPublication(user.vfed,user.pub_topic,"string","");
  printf("D FEDERATE %s: Publication registered\n",user.pub_topic);

  /* Subscribe to transmission federate's publication */
  ierr = PetscStrcpy(sub_topic,"Trans/");
  ierr = PetscStrcat(sub_topic,user.pub_topic);
  user.sub = helicsFederateRegisterSubscription(user.vfed,sub_topic,"string","");
  printf("D FEDERATE %s: Subscription registered\n",user.pub_topic);

  status = helicsFederateEnterInitializationMode(user.vfed);
  printf("D FEDERATE %s: Entered initialization mode\n",user.pub_topic);

  status = helicsFederateEnterExecutionMode(user.vfed);
  printf("D FEDERATE %s: Entered execution mode\n",user.pub_topic);
  
  user.currenttime = 0.0;

  while(!pflow_conv && iter < max_it) {
    iter++;

    /*1. Get bus voltage from transmission */
    status = helicsFederateRequestTime(user.vfed,user.currenttime,&user.currenttime);
    
    isupdated = helicsSubscriptionIsUpdated(user.sub);
    if(isupdated) {
      status = helicsSubscriptionGetString(user.sub,substr,PETSC_MAX_PATH_LEN-1,&strlen);
      sscanf(substr,"%lf,%lf",&Vm,&Va);
      printf("D FEDERATE %s received Vm = %4.3f, Va = %4.3f from T FEDERATE\n",user.pub_topic,Vm,Va);
    }

        /* Set source bus voltage */
    ierr = OpenDSSVsourcesSetPU(Vm);CHKERRQ(ierr);
    ierr = OpenDSSVsourcesSetAngleDeg(Va);CHKERRQ(ierr);

    converged = PETSC_FALSE;

    PetscInt solve;
    /* 2. Solve power flow */
    printf("D FEDERATE %s running power flow\n",user.pub_topic);
    ierr = OpenDSSSolutionGetSolve(&solve);CHKERRQ(ierr);

    /* Send power injection to transmission */
    
       /* Get the net injection at the boundary bus */
    ierr = OpenDSSCircuitGetTotalPower(&Stotal);CHKERRQ(ierr);
    Pg = -creal(Stotal[0])/1000.0; /* Conversion to MW */
    Qg = -cimag(Stotal[0])/1000.0;

    ierr = PetscSNPrintf(pubstr,PETSC_MAX_PATH_LEN-1,"%18.16f,%18.16f",Pg,Qg);CHKERRQ(ierr);
    status = helicsPublicationPublishString(user.pub,pubstr);
    printf("D FEDERATE %s sent Pg = %4.3f, Qg = %4.3f from T FEDERATE\n",user.pub_topic,Pg,Qg);
    
    /*2. Publish Pg and Qg */
    status = helicsFederateRequestTime(user.vfed,user.currenttime,&user.currenttime);

    /*3. Receiving convergence status from transmission */
    status = helicsFederateRequestTime(user.vfed,user.currenttime,&user.currenttime);
    
    isupdated = helicsSubscriptionIsUpdated(user.sub);
    if(isupdated) {
      status = helicsSubscriptionGetString(user.sub,substr,PETSC_MAX_PATH_LEN-1,&strlen);
      sscanf(substr,"%d",(PetscBool*)&pflow_conv);
    }
  }
  
  status = helicsFederateEnterExecutionModeComplete(user.vfed);
  status = helicsFederateFinalize(user.vfed);

  PetscFinalize();
  return 0;
}
  
