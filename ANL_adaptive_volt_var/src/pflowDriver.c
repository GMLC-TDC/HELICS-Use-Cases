/*
Copyright (C) 2017-2018, Argonne National Laboratory
All rights reserved.

This software was developed by Argonne National Laboratory,
A U.S. Department of Energy laboratory managed by UChicago Argonne, LLC.
*/

static char help[] = "PFLOW interface to pyPflow through ZEROMQ.\n\n";

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>

#include <pflow.h>
#include <zmq.h>
#include "cJSON.h"

#define MAX_DEPTH 10

char tree_path_set[MAX_DEPTH][128];
char tree_path_get[MAX_DEPTH][128];
int count_set=0;int count_get=0;

#define NUMBER_SET_COMMANDS 4  // Pd,Qd,Pg,VSetPoint
#define NUMBER_GET_COMMANDS 3  // Pg,Qg,V


#undef __FUNCT__
#define __FUNCT__ "get_schemaopt"

int get_schemaopt(){

	FILE *fp_set,*fp_get;
	char desc[512]="";

	fp_set=fopen("data/schemaopt_set","r");
	fp_get=fopen("data/schemaopt_get","r");

	//======================SET============================
	if (fp_set == NULL) {
		fprintf(stderr,"Cannot open schemaopt_set for reading\n");
	}
	else{
		while (fgets(desc, sizeof(desc), fp_set) != NULL) /* put data in array*/
		{
				strtok(desc,"\n");
				strncpy(tree_path_set[count_set],desc,sizeof(desc)); /* get the result */
			count_set++;
		}
	}

	//======================GET============================
	if (fp_get == NULL) {
		fprintf(stderr,"Cannot open schemaopt_get for reading\n");
	}
	else{
		while (fgets(desc, sizeof(desc), fp_get) != NULL) /* put data in array*/
		{
			strtok(desc,"\n");
			strncpy(tree_path_get[count_get],desc,sizeof(desc)); /* get the result */
			count_get++;
		}
	}
	
	fclose(fp_set);
	fclose(fp_get);
	return 0;
}

#undef __FUNCT__
#define __FUNCT__ "main"

int main(int argc,char **argv)
{
	PetscErrorCode ierr;
	PFLOW             pflow;
	char              file[PETSC_MAX_PATH_LEN];
	PetscBool         flg;
	PetscInt          rank;

	PetscInitialize(&argc,&argv,"petscopt",help);
	ierr = MPI_Comm_rank(PETSC_COMM_WORLD,&rank);CHKERRQ(ierr);
	ierr = PFLOWCreate(PETSC_COMM_WORLD,&pflow);CHKERRQ(ierr);//Create PFLOW object 

	ierr = PetscOptionsGetString(NULL,NULL,"-netfile",file,PETSC_MAX_PATH_LEN,&flg);CHKERRQ(ierr);
	if(flg) {//Read Network Data file 
		ierr = PFLOWReadMatPowerData(pflow,file);CHKERRQ(ierr);
	}else {
		ierr = PFLOWReadMatPowerData(pflow,"data/case9.m");CHKERRQ(ierr);
	}

	//==============================GET THE SCHEMA DEFINITION==========================
	get_schemaopt();

	//==============================SET UP ZEROMQ SERVER==========================
	int buffer_size=2048;
	char *buffer = malloc(buffer_size);
	char ID[4];

	void *context = zmq_ctx_new ();
	void *responder = zmq_socket (context, ZMQ_REP);
	zmq_msg_t message;
	size_t msg_size;

	if(rank==0){//start server on node 0
		//Socket to talk to clients
		int rc = zmq_bind (responder, "tcp://*:10000");// for now port 10000 is used
		assert (rc == 0);
	}

	// processes query and reply
	PetscBool comm_flg=1;
	while (comm_flg){

		if(rank==0){//get data from client
			zmq_msg_init (&message);//create an empty msg object and pass it to recv
			zmq_msg_recv (&message,responder, 0);
			msg_size = zmq_msg_size (&message);//get msg size

			if (msg_size>buffer_size){
				buffer = malloc(msg_size);
				buffer_size=msg_size;
			}

			memcpy (buffer,zmq_msg_data (&message), msg_size);// get msg
		}

		MPI_Bcast(&msg_size,1,MPI_INT,0,PETSC_COMM_WORLD);// broadcast size to all processors

		if(msg_size>buffer_size && rank>0){
			buffer = malloc(msg_size);
			buffer_size=msg_size;
		}

		MPI_Bcast(buffer,buffer_size,MPI_CHAR,0,PETSC_COMM_WORLD);// broadcast data to all processors

		if (!strstr(buffer,"COMM_END")){

			//=======================PARSE DATA AND MAKE CHANGES===========================
			cJSON * date_time, *date_time_get;
			cJSON * root = cJSON_Parse(buffer);

			int depth_level;

			//we preserve the root node definition for later use when we traverse the tree for get
			date_time = cJSON_GetObjectItem(root,tree_path_set[0]);

			for(depth_level=1;depth_level<count_set;depth_level++){
				date_time = cJSON_GetObjectItem(date_time,tree_path_set[depth_level]);
			}

			//------------set relevant info in PS structure----------------------
			int nVal,nChanges,n,m;
			double *setVal;
			const char *set_command[NUMBER_SET_COMMANDS];
			set_command[0]="Pd"; set_command[1]="Qd";
			set_command[2]="Pg"; set_command[3]="VSetPoint";

			for(n=0;n<NUMBER_SET_COMMANDS;n++){//cycle through all set commands
				nVal=PFLOWParserGetVal(date_time,set_command[n],NULL,0);// dry run to find out mem req
				setVal = malloc(sizeof(double)*nVal);
				nVal=PFLOWParserGetVal(date_time,set_command[n],setVal,1);// set read values in setVal
			
				if (nVal>0){// set only when requested
					nChanges=nVal/3;
					for(m=0;m<nChanges;m++){//cycle through all changes
						sprintf(ID,"%d",(int)setVal[3*m+1]);
						PFLOWParserSet(pflow,(int)setVal[m*3],ID,setVal[m*3+2],set_command[n]);
					}
				}
				free(setVal);
			}

			//==================================SOLVE=======================================
			ierr = PFLOWSolve(pflow);CHKERRQ(ierr);
			ierr = PFLOWPostSolve(pflow);CHKERRQ(ierr);

			//============================GET DATA TO REPLY=============================
			date_time_get = cJSON_GetObjectItem(root,tree_path_get[0]);

			for(depth_level=1;depth_level<count_get;depth_level++){
				date_time_get = cJSON_GetObjectItem(date_time_get,tree_path_get[depth_level]);
			}

			//------------get relevant info from PS structure----------------------
			double *getVal;int nRequests;double *currentItemVal;
			const char *get_command[NUMBER_GET_COMMANDS];
			get_command[0]="Pg"; get_command[1]="Qg"; get_command[2]="V";

			for(n=0;n<NUMBER_GET_COMMANDS;n++){//cycle through all set commands
				nVal=PFLOWParserGetVal(date_time_get,get_command[n],NULL,0);// dry run to find out mem req
				getVal = malloc(sizeof(double)*nVal);
				nVal=PFLOWParserGetVal(date_time_get,get_command[n],getVal,1);// set read values in setVal

				if (nVal>0){// only when requested
					nRequests=nVal/3;

					for(m=0;m<nRequests;m++){//cycle through all requests
						if (strcmp(get_command[n],"V")!=0){
							currentItemVal = malloc(sizeof(double)*3);
							currentItemVal[0]=getVal[3*m];
							currentItemVal[1]=getVal[3*m+1];
							sprintf(ID,"%d",(int)getVal[3*m+1]);
							currentItemVal[2]=PFLOWParserGet(pflow,(int)getVal[3*m],ID,get_command[n]);
							cJSON_ReplaceItemInArray(cJSON_GetObjectItem(date_time_get,get_command[n]),m,cJSON_CreateDoubleArray(currentItemVal,3));
						}
						else{
							currentItemVal = malloc(sizeof(double)*3);

							currentItemVal[0]=(int)getVal[3*m];
							currentItemVal[1]=PFLOWParserGet(pflow,(int)getVal[3*m],NULL,"Vmag");
							currentItemVal[2]=PFLOWParserGet(pflow,(int)getVal[3*m],NULL,"Vang");

							cJSON_ReplaceItemInArray(cJSON_GetObjectItem(date_time_get,get_command[n]),m,cJSON_CreateDoubleArray(currentItemVal,3));
						}
					}
				}
				free(getVal);
			}
			//--------------------reply-------------------------
			if(rank==0) {
				zmq_send (responder,cJSON_Print(root),strlen(cJSON_Print(root)),0);// string without null byte
			}
				cJSON_Delete(root);//delete root
		}
		else{//if COMM_END
			comm_flg=0;
			if(rank==0)  zmq_send (responder,"COMM_END",8,0);
		}
	}// will continually repeat the process until COMM_END flag is recv

	free(buffer);// free memory

	if(rank==0){ // delete zmq context
		zmq_msg_close(&message);
		zmq_close(responder);
		zmq_ctx_destroy(context);
	}

	/* Destroy PFLOW object */
	ierr = PFLOWDestroy(&pflow);CHKERRQ(ierr);

	PetscFinalize();
	return 0;
}

