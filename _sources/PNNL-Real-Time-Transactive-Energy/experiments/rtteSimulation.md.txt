Real Time Transactive Energy Co-Simulation Example
==================================================

This is an example of a Transactive Energy Use case. This example will take a simple static power system model and add a detailed secondary side with individual residences with a collection of devices such a HVAC, Water heater, Pool pumps, etc. Then also add a Transmission system using MATPOWER while also adding a Hierachical control structure with LSE and DSO constructs.

To get started nagivate to the following folder within the main script base and open the `coSimulationRTTE.py` script.

.. code-block:: bash
	
	# navigate to the repositories folder
	cd $HOME/repositories

	# from here navigate to main landing for experiment runs
	cd modificationScipts
	nano coSimulationTD.py


This script will contain all of the setting you have available for the experiment. The following will explain the settings:

.. code-block:: bash

	# ---------------------------------------------------------------
	# ----------------------- Settings ------------------------------
	# ---------------------------------------------------------------
	
	# name of the experiment
	experimentName = 'rtteSimTest'
	
	# number of distribution systems in the experiment
	distributionSystemNumber = 2
	
	# create simple bash run scipt that will start a GridLAB-D instance per feeder
	createRunScripts = True
	
	# create HPC run scipt that will work with the Co-Simulation launcher capability
	createHPCScripts = False
	
	# this assumes that everything associated with this experiment is in a certain folder structure. This is the path to the root folder
	rootPath = '/people/hans464/helicsUseCaseScripts'
	
	# path to where you want the experiment outputs (if left empty we assume /experiments)
	experimentFilePath = ''
	
	# file path that contains the GLMs to extract (if left empty we assume /modelDependency/feeders)
	feederFilePath = ''
	
	# file path that contains include files for the experiment (if left empty we assume /modelDependency)
	includeFilePath = ''
	
	# dictionary that holds all the log level information for each type of federate
	simulatorLogLevels = dict()
	simulatorLogLevels['fncs'] = 'WARNING'
	simulatorLogLevels['matpower'] = 'LMACTIME'
	simulatorLogLevels['dso'] = 'INFO'
	simulatorLogLevels['lse'] = 'INFO'
	
	# specify the port fncs will use to communicate on
	fncsPort = '7777'
	
	# list of distribution systems models and their population distribution for the experiment (feeder : [percent [.], region [#])
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
	useFlags['use_FNCS'] = 0
	useFlags['use_HELICS'] = 1
	useFlags['core_type_HELICS'] = 'zmq'
	useFlags['add_real_time_transactive_control'] = 1
	useFlags['house_thermostat_mode'] = 'COOL'
	
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
	# edit the files being recorder and the interval
	feederConfig['measure_interval'] = 30
	feederConfig['recorders'] = {'TSEControllers': True, 'HVAC': True, 'market': True}
	feederConfig['short_names'] = True
	feederConfig['suppress_repeat_messages'] = 'True'
	feederConfig['tmy_higher_fidelity'] = False
	feederConfig['tmy_higher_fidelity_path'] = Path(rootPath) / 'modelDependency' / 'transmission' / 'tmy_higher_fidelity.csv'
	
	# createing a dict for the transmission system
	transmissionConfig = {}
	transmissionConfig['sequelLogging'] = False
	transmissionConfig['matpowerFilePath'] = Path(rootPath) / 'modelDependency' / 'transmission'
	transmissionConfig['matpowerSystem'] = 'case9'	# transmission system to use
	transmissionConfig['matpowerPFTime'] = 15 		# time between power flow solutions in MATPOWER in seconds. OPF need to be a multiple of PF
	transmissionConfig['matpowerOPFTime'] = 300		# time between optimal power flow solutions in MATPOWER in seconds. OPF need to be a multiple of PF
	transmissionConfig['matpowerAmpFactor'] = 1		# MATPOWER distribution load amplification factor
	transmissionConfig['wholesaleTimeShift'] = 15 	# lead time at which the OPF is solved
	
	# These are the specific settings for the NODES control
	controlConfig = dict()
	controlConfig["controlDependencyFilePath"] = Path(rootPath) / 'modelDependency' / 'realTimeTransactiveEnergy'
	controlConfig['quantityPrioritization'] = True # If true quantity is used though the control levels. If false price is used
	controlConfig['transactivepenetration'] = 1 # Penetration of transactive control (percent of distribution system that will have control active)
	# settings for Transactive Energy Controllers
	controlConfig['TSEmarketName'] = 'retailMarket'
	controlConfig['TSEmarketUnit'] = 'W'
	controlConfig['TSEmarketPeriod'] = 300
	controlConfig['TSEcontrolTechnology'] = 'DOUBLE_PRICE'  # at the moment we only support modes that does either cooling or heating
	controlConfig['TSEresolveMode'] = 'DEADBAND'
	controlConfig['TSEbidMode'] = 'ON'
	controlConfig['TSEbidDelay'] = 30
	controlConfig['TSEsliderSetting'] = 1
	controlConfig['TSEauctionStatistics'] = 24
	controlConfig['TSEinitPrice'] = 18
	controlConfig['TSEinitStdev'] = 4
	controlConfig['TSEpriceCap'] = 1000
	controlConfig['TSEuseFutureMeanPrice'] = 'FALSE'
	controlConfig['TSEwarmUp'] = 0
	
	controlConfig['dsoISORelativeTimeShift'] = 5
	controlConfig['lseISORelativeTimeShift'] = 10


After modifying the setting for this script you can create and run the experiment by doing the following:
 
.. code-block:: bash 

	# navigate to the repositories folder
	cd $HOME/repositories/HELICS-Use-Cases/PNNL-Real-Time-Transactive-Energy/modificationScripts
	
	# run scripts to populate feeders
	python coSimulationRTTE.py
	
	# execute experiment
	cd ../experiments/rtteExample
	./runAll.sh