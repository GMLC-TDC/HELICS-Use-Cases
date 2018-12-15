#!/bin/bash

MYHOST=`hostname -s`
MYRANK=$OMPI_COMM_WORLD_RANK       # this variable may depend on your execution environment

OUT_FILE=helics_${MYHOST}_${MYRANK}.out 

storageLocation=$HELICS_STORAGE_LOCATION
experimentName=$HELICS_EXPERIMENT_NAME

if [ $3 == "gridlabd" ]
then
	echo "Rank $MYRANK on host $MYHOST unzipping model"
	#echo "unzip -qq *.zip"
	unzip -qq *.zip
fi

echo "Rank $MYRANK on host $MYHOST starting $*"
"$@" 1> $OUT_FILE

echo "Rank $MYRANK on host $MYHOST zipping data"
if [ $MYRANK -eq 0 ]
then
	#echo "cp $OUT_FILE $storageLocation/$experimentName"
	cp $OUT_FILE $storageLocation/$experimentName
else
	#echo "zip -rq ${PWD##*/}.zip *"
	#echo "mv ${PWD##*/}.zip $storageLocation/$experimentName"
	zip -rq ${PWD##*/}.zip *
	mv ${PWD##*/}.zip $storageLocation/$experimentName
fi
