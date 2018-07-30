static char help[] = "This code implements the distribution federate of the T-D power flow use-case. A global convergence for the federation is implemented in this use-case. The The distribution federate obtains the upstream distribution substation voltage from transmission federate, solves power flow, and sends the updated injection into transmission. This code does not use HELICS iterative API\n\n";

#include <petsc.h>
#include <ValueFederate.h>
#include <opendss.h>
#include <complex.h>

typedef struct {
  helics_federate vfed;
  helics_publication pub;
  helics_subscription sub;
  helics_time_t currenttime;
  helics_iteration_status currenttimeiter;
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

  status = helicsFederateInfoSetMaxIterations(fedinfo,100);
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
  PetscScalar   Pg,Qg,Pgprv,Qgprv;
  PetscInt      pflowT_conv=0,pflowD_conv=0,global_conv=0;
  char          pubstr[PETSC_MAX_PATH_LEN],substr[PETSC_MAX_PATH_LEN];
  PetscInt      strlen;
  PetscReal     tol=1E-6,mis;

  
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

  user.currenttime = 0.0;
  user.currenttimeiter = iterating;

  PetscInt solve;
  /* Solve power flow */
  //  printf("D FEDERATE %s running power flow\n",user.pub_topic);
  ierr = OpenDSSSolutionGetSolve(&solve);CHKERRQ(ierr);

  /* Send power injection to transmission */
  /* Get the net injection at the boundary bus */
  ierr = OpenDSSCircuitGetTotalPower(&Stotal);CHKERRQ(ierr);
  Pgprv = -creal(Stotal[0])/1000.0; /* Conversion to MW */
  Qgprv = -cimag(Stotal[0])/1000.0;

  ierr = PetscSNPrintf(pubstr,PETSC_MAX_PATH_LEN-1,"%18.16f,%18.16f,%d",Pgprv,Qgprv,pflowD_conv);CHKERRQ(ierr);
  status = helicsPublicationPublishString(user.pub,pubstr);
  //  printf("D FEDERATE %s sent Pg = %4.3f, Qg = %4.3f, conv = %d from T FEDERATE\n",user.pub_topic,Pgprv,Qgprv,pflowD_conv);

  status = helicsFederateEnterExecutionMode(user.vfed);
  printf("D FEDERATE %s: Entered execution mode\n",user.pub_topic);
    
  while(user.currenttimeiter == iterating) {
    iter++;

    status = helicsSubscriptionGetString(user.sub,substr,PETSC_MAX_PATH_LEN-1,&strlen);
    sscanf(substr,"%lf,%lf,%d",&Vm,&Va,&pflowT_conv);
    //    printf("D FEDERATE %s received Vm = %4.3f, Va = %4.3f, conv = %d from T FEDERATE\n",user.pub_topic,Vm,Va,pflowT_conv);

    global_conv = pflowT_conv & pflowD_conv;

    if(global_conv) {
      helicsFederateRequestTimeIterative(user.vfed,user.currenttime,no_iteration,&user.currenttime,&user.currenttimeiter);
    } else {
      /* Set source bus voltage */
      ierr = OpenDSSVsourcesSetPU(Vm);CHKERRQ(ierr);
      ierr = OpenDSSVsourcesSetAngleDeg(Va);CHKERRQ(ierr);

      /* 2. Solve power flow */
      //      printf("D FEDERATE %s running power flow\n",user.pub_topic);
      ierr = OpenDSSSolutionGetSolve(&solve);CHKERRQ(ierr);

      /* Send power injection to transmission */    
      /* Get the net injection at the boundary bus */
      ierr = OpenDSSCircuitGetTotalPower(&Stotal);CHKERRQ(ierr);
      Pg = -creal(Stotal[0])/1000.0; /* Conversion to MW */
      Qg = -cimag(Stotal[0])/1000.0;

      mis = PetscSqrtScalar((Pg-Pgprv)/100*(Pg-Pgprv)/100 + (Qg-Qgprv)/100*(Qg-Qgprv)/100); /* Divide by 100 for conversion to pu */
      if(mis < tol) {
	pflowD_conv = 1;
      } else {
	pflowD_conv = 0;
	Pgprv = Pg;
	Qgprv = Qg;
      }
      ierr = PetscSNPrintf(pubstr,PETSC_MAX_PATH_LEN-1,"%18.16f,%18.16f,%d",Pg,Qg,pflowD_conv);CHKERRQ(ierr);
      status = helicsPublicationPublishString(user.pub,pubstr);
      //      printf("D FEDERATE %s sent Pg = %4.3f, Qg = %4.3f, conv = %d to T FEDERATE\n",user.pub_topic,Pg,Qg,pflowD_conv);
    
      fflush(NULL);

      /*3. Publish Pg, Qg, and convergence status to transmission */
      status = helicsFederateRequestTimeIterative(user.vfed,user.currenttime,force_iteration,&user.currenttime,&user.currenttimeiter);

      printf("Iteration %d: D Federate %s mis = %g,converged = %d\n",iter,user.pub_topic,mis,pflowD_conv);

    }
    
  }
  
  status = helicsFederateEnterExecutionModeComplete(user.vfed);
  status = helicsFederateFinalize(user.vfed);

  PetscFinalize();
  return 0;
}
  
