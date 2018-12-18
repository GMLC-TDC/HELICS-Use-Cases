Populate Feeders Example
========================

This is an example of populating feeders with technologies. This example will take a simple static power system model and add a detailed secondary side with individual residences with a collection of devices such a HVAC, Water heater, Pool pumps, etc.

To get started nagivate to the following folder within the main script base and open the `populateFeeders.py` script.

``` bash	
# navigate to the repositories folder
cd $HOME/repositories

# from here navigate to main landing for experiment runs
cd modificationScipts
nano populateFeeders.py
```


This script will contain all of the setting you have available for the experiment. The following will explain the settings:

``` bash	
# ---------------------------------------------------------------
# ----------------------- Settings ------------------------------
# ---------------------------------------------------------------
	
# name of the experiment
experimentName = 'populateExample'
	
# number of distribution systems in the experiment
distributionSystemNumber = 2
	
# create simple bash run scipt that will start a GridLAB-D instance per feeder
createRunScripts = True
	
# this assumes that everything associated with this experiment is in a certain folder structure. This is the path to the root folder
rootPath = '/people/hans464/helicsUseCaseScripts'
	
# path to where you want the experiment outputs (if left empty we assume /experiments)
experimentFilePath = ''
	
# file path that contains the GLMs to extract (if left empty we assume /modelDependency/feeders)
feederFilePath = ''
	
# file path that contains include files for the experiment (if left empty we assume /modelDependency)
includeFilePath = ''
	
# list of distribution systems models and their population distribution for the experiment (feeder : [percent [.])
inputGLM = dict()
inputGLM['small4BusSystem.glm'] = [1, 1]
# inputGLM['R1-12.47-1.glm'] = [0.14, 1]
# inputGLM['R1-12.47-2.glm'] = [0.14, 1]
# inputGLM['R1-12.47-3.glm'] = [0.14, 1]
# inputGLM['R2-12.47-1.glm'] = [0.08, 2]
# inputGLM['R2-12.47-2.glm'] = [0.07, 2]
# inputGLM['R2-12.47-3.glm'] = [0.07, 2]
# inputGLM['R3-12.47-1.glm'] = [0.12, 3]
# inputGLM['R3-12.47-2.glm'] = [0.12, 3]
# inputGLM['R3-12.47-3.glm'] = [0.12, 3]
	
	
# This specifies what technologies to use. What is specified here will overwrite the defaults in the technologyConfiguration.py
useFlags = dict()
	
# This specifies what feeder configuration to use. What is specified here will overwrite the defaults in the feederConfiguration.py	
feederConfig = dict()
# this can enable logging to a mysql database instead of csv files
feederConfig['sequelLogging'] = False
feederConfig["sequelSettings"] = ['localhost','gridlabd','passGLD123','3306','0']
# some settings to upgrade the equipment of the feeders
feederConfig['fuses_upgrade_level'] = 2
feederConfig['transformer_upgrade_level'] = 1
feederConfig['transformer_upgrade_cutoff'] = 100
# start and stop time for the simulation
feederConfig['startdate'] = '2013-08-28 00:00:00'
feederConfig['stopdate'] = '2013-08-29 00:00:00'
```

After modifying the setting for this script you can create and run the experiment by doing the following:
 
``` bash	
# navigate to the repositories folder
cd $HOME/repositories/HELICS-Use-Cases/PNNL-Real-Time-Transactive-Energy/modificationScripts
	
# run scripts to populate feeders
python populateFeeders.py
	
# execute experiment
cd ../experiments/populateExample
./runAll.sh
```