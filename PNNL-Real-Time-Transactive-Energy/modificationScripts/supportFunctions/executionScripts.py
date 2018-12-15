"""
This file contains functions to add execution scripts that can run the experiment 

Created April 7, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""
from . import feederConfiguration
import subprocess, os, math, datetime, itertools

def add_simple_run_script(experimentFilePath, experimentName):
	"""
	This function creates convenience scripts for running the experiment that consists only of GridLAB-D systems

	Inputs
		experimentFilePath - path to where we want to save the experiment
		experimentName - name of the experiment
	Outputs
		None
	"""

	processFolderNames = [name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('feeder' in name)]

	if os.name == 'nt': # if running on windows
		print('WARNING: execution scripts are not supported for the windows platform at this time')
	else:
		# open the files we need
		runFile = open(experimentFilePath / experimentName / 'runAll.sh', 'w')
		killFile = open(experimentFilePath / experimentName / 'killAll.sh', 'w')

		# create the run all script. This script will run the experiment. if we only have one resource we do not have to do anything fancy and the script is easy to create
		runFile.write('#!/bin/bash\n\n')
		runFile.write('clear\n')

		runFile.write('\necho "Executing experiment..."\n\n')

		runFile.write('experimentPath="{:}"\n\n'.format(experimentFilePath / experimentName))

		for process in sorted(processFolderNames):
			runFile.write('cd $experimentPath/{:s} && gridlabd {:s}.glm &> simLog.out &\n'.format(process, process))

		runFile.write('\necho "Waiting for processes to finish..."\n\n')
		runFile.write('wait\n')
		runFile.write('\necho "Done..."\n\n')

		#runFile.write('\nexit 0')

		# create the kill all script. This script will terminate an experiment
		killFile.write('#!/bin/bash\n\n')
		killFile.write('clear\n\n')
		killFile.write('pkill -9 runAll\n')
		killFile.write('pkill -9 gridlab\n')
		killFile.write('\nexit 0')

		runFile.close()
		killFile.close()

		termProcess = subprocess.Popen(['chmod', '+x', 'runAll.sh'], cwd=experimentFilePath / experimentName, stdout=subprocess.PIPE)
		if termProcess.wait() != 0:
			raise Exception('something went wrong when doing "chmod" on runAll.sh')
		termProcess = subprocess.Popen(['chmod', '+x', 'killAll.sh'], cwd=experimentFilePath / experimentName, stdout=subprocess.PIPE)
		if termProcess.wait() != 0:
			raise Exception('something went wrong when doing "chmod" on killAll.sh')


def add_fncs_run_script(populationDict, transmissionDict, simulatorLogLevels, fncsPort):
	"""
	This function creates convenience scripts for running the experiment

	Inputs
		populationDict - dictionary containing properties for all the feeders we are using
		transmissionDict - dictionary containing properties for the transmission system we are using
		simulatorLogLevels - log level for each type of federate
		fncsPort - the port to run FNCS on
	Outputs
		None
	"""

	experimentFilePath = populationDict[0]['experimentFilePath']
	experimentName = populationDict[0]['experimentName']
	feederConfig = populationDict[0]['feederConfig']
	useFlags = populationDict[0]['useFlags']
	fncsLogLevel = simulatorLogLevels['fncs']
	matpowerLogLevel = simulatorLogLevels['matpower']
	matpowerSystem = transmissionDict['matpowerSystem']
	wholesaleMarketPeriod = int(transmissionDict['matpowerOPFTime'])
	matpowerAmpFactor = transmissionDict['matpowerAmpFactor']
	wholesaleTimeShift = int(transmissionDict['wholesaleTimeShift'])
	withTE = '0'

	if transmissionDict['sequelLogging']:
		sequelLogging = '1'
	else:
		sequelLogging = '0'

	if useFlags['add_real_time_transactive_control']:
		withTE = '1'
		dsoLogLevel = simulatorLogLevels['dso']
		lseLogLevel = simulatorLogLevels['lse']
		dsoISORelativeTimeShift = int(populationDict[0]['controlConfig']['dsoISORelativeTimeShift'])
		lseISORelativeTimeShift = int(populationDict[0]['controlConfig']['lseISORelativeTimeShift'])
		quantityPrioritization = int(populationDict[0]['controlConfig']['quantityPrioritization'])
	elif useFlags['add_nodes_control']:
		allocationPeriod = int(populationDict[0]['controlConfig']['allocationPeriod'])
		aggregatorControllerLogLevel = simulatorLogLevels['aggregatorController']
		drcLogLevel = simulatorLogLevels['drc']
		usePriorityStack = int(populationDict[0]['controlConfig']['usePriorityStack'])

	simFullTime = int((datetime.datetime.strptime(feederConfig['stopdate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(feederConfig['startdate'], '%Y-%m-%d %H:%M:%S')).total_seconds())

	processFolderNames = os.listdir(experimentFilePath / experimentName)
	#processFolderNames = [name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('feeder' in name or 'matpower' in name or 'dso' in name or 'lse' in name)]

	if os.name == 'nt': # if running on windows
		print('WARNING: execution scripts are not supported for the windows platform at this time')
	else:
		# open the files we need
		runFile = open(experimentFilePath / experimentName / 'runAll.sh', 'w')

		# create the run all script. This script will run the experiment. if we only have one resource we do not have to do anything fancy and the script is easy to create
		runFile.write('#!/bin/bash\n\n')
		runFile.write('clear\n')

		runFile.write('\necho "Executing experiment..."\n\n')

		runFile.write('logFile="fncs.out"\n')
		runFile.write('fncsConfigFile="fncs.yaml"\n')
		runFile.write('fncsLogLevel="{:s}"\n'.format(fncsLogLevel))
		runFile.write('matpowerLogLevel="{:s}"\n'.format(matpowerLogLevel))
		
		if useFlags['add_real_time_transactive_control']:
			runFile.write('dsoLogLevel="{:s}"\n'.format(dsoLogLevel))
			runFile.write('lseLogLevel="{:s}"\n'.format(lseLogLevel))

		if useFlags['add_nodes_control']:
			runFile.write('aggregatorControllerLogLevel="{:s}"\n'.format(aggregatorControllerLogLevel))
			runFile.write('drcLogLevel="{:s}"\n'.format(drcLogLevel))
		
		runFile.write('experimentPath="{:}"\n'.format(experimentFilePath / experimentName))
		runFile.write('fncsBrokerPort="tcp://*:{:s}"\n'.format(fncsPort))
		runFile.write('fncsBrokerIP="tcp://localhost:{:s}"\n\n'.format(fncsPort))

		# Do the exports so FNCS and other software behave the way we want
		runFile.write('export FNCS_LOG_STDOUT=yes\n')
		runFile.write('export FNCS_CONFIG_FILE=$fncsConfigFile\n')
		runFile.write('export FNCS_LOG_LEVEL=$fncsLogLevel\n')
		runFile.write('export MATPOWER_LOG_LEVEL=$matpowerLogLevel\n')
		
		if useFlags['add_real_time_transactive_control']:
			runFile.write('export DSO_LOG_LEVEL=$dsoLogLevel\n')
			runFile.write('export LSE_LOG_LEVEL=$lseLogLevel\n')
		
		if useFlags['add_nodes_control']:
			runFile.write('export AGGREGATORCONTROLLER_LOG_LEVEL=$aggregatorControllerLogLevel\n')
			runFile.write('export DRC_LOG_LEVEL=$drcLogLevel\n')

		runFile.write('export FNCS_BROKER=$fncsBrokerIP\n\n')

		processCount = 0
		for process in sorted(processFolderNames):
			if 'matpower' in process:
				if withTE == '1':
					runFile.write('cd $experimentPath/matpower && start_MATPOWER {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json dispatchable_load_data.json &> $logFile &\n'.format(matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate']))
				else:
					runFile.write('cd $experimentPath/matpower && start_MATPOWER {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json &> $logFile &\n'.format(matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate']))
				#runFile.write('echo $! > $experimentPath/killAll.sh')
				processCount += 1
			elif 'feeder' in process and 'lse' not in process:
				runFile.write('cd $experimentPath/{:s} && gridlabd {:s}.glm &> $logFile &\n'.format(process, process))
				processCount += 1
			elif 'include' in process:
				pass

			# these are for the CCSI control
			elif 'dso' in process:
				runFile.write('cd $experimentPath/{:s} && dso {:d} {:d} {:d} {:d} {:d} &> $logFile &\n'.format(process, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, dsoISORelativeTimeShift, quantityPrioritization))
				processCount += 1
			elif 'lse' in process:	
				runFile.write('cd $experimentPath/{:s} && lse {:d} {:0.3f} {:d} {:d} {:d} {:d} &> $logFile &\n'.format(process, simFullTime, matpowerAmpFactor, wholesaleMarketPeriod, wholesaleTimeShift, lseISORelativeTimeShift, quantityPrioritization))		
				processCount += 1
			# these are for the nodes control
			elif 'ISO' in process:
				runFile.write('export FNCS_NAME="ISO"\n')
				runFile.write('cd $experimentPath/ISO && fncs_player {:d}s isoPlayer.txt &> $logFile &\n'.format(int(simFullTime)))
				runFile.write('unset FNCS_NAME\n')
				processCount += 1
			elif 'distributionReliabilityCoordinator' in process:
				runFile.write('cd $experimentPath/distributionReliabilityCoordinator && distributionReliabilityCoordinator {:d} {:d} &> $logFile &\n'.format(allocationPeriod, int(simFullTime)))
				processCount += 1
			elif 'aggregator' in process:	
				runFile.write('cd $experimentPath/{:s} && aggregatorController {:d} {:d} {:d} &> $logFile &\n'.format(process, allocationPeriod, int(simFullTime), usePriorityStack))
				processCount += 1

			else:
				print("WARNING: something went wrong in creating the execution script (Unknown federate ->", process, ")")


		runFile.write('export FNCS_BROKER=$fncsBrokerPort\n')
		runFile.write('fncs_broker {:d} &> $logFile &\n'.format(processCount))
		runFile.write('export FNCS_BROKER=$fncsBrokerIP\n\n')

		runFile.write('\necho "Waiting for processes to finish..."\n\n')
		runFile.write('wait\n')

		runFile.write('\necho "Done..."\n\n')
		runFile.write('\nexit 0')

		# create the kill all script. This script will terminate an experiment
		killFile = open(experimentFilePath / experimentName / 'killAll.sh', 'w')
		killFile.write('#!/bin/bash\n\n')
		killFile.write('var=$(pgrep -o runAll.sh)\n')
		killFile.write('if [ -z "$var" ]\n')
		killFile.write('then\n')
		killFile.write('    echo "No processes are running"\n')
		killFile.write('else\n')
		killFile.write('    echo "Killing all processes of runAll.sh"\n')
		killFile.write('    kill -9 -$var >/dev/null\n')
		killFile.write('fi\n')

		runFile.close()
		killFile.close()

		termProcess = subprocess.Popen(['chmod', '+x', 'runAll.sh'], cwd=experimentFilePath / experimentName, stdout=subprocess.PIPE)
		if termProcess.wait() != 0:
			raise Exception('something went wrong when doing "chmod" on runAll.sh')
		termProcess = subprocess.Popen(['chmod', '+x', 'killAll.sh'], cwd=experimentFilePath / experimentName, stdout=subprocess.PIPE)
		if termProcess.wait() != 0:
			raise Exception('something went wrong when doing "chmod" on killAll.sh')	


def add_helics_run_script(populationDict, transmissionDict, simulatorLogLevels):
	"""
	This function creates convenience scripts for running the experiment

	Inputs
		populationDict - dictionary containing properties for all the feeders we are using
		transmissionDict - dictionary containing properties for the transmission system we are using
		simulatorLogLevels - log level for each type of federate
	Outputs
		None
	"""

	experimentFilePath = populationDict[0]['experimentFilePath']
	experimentName = populationDict[0]['experimentName']
	feederConfig = populationDict[0]['feederConfig']
	useFlags = populationDict[0]['useFlags']
	fncsLogLevel = simulatorLogLevels['fncs']
	matpowerLogLevel = simulatorLogLevels['matpower']
	matpowerSystem = transmissionDict['matpowerSystem']
	wholesaleMarketPeriod = int(transmissionDict['matpowerOPFTime'])
	matpowerAmpFactor = transmissionDict['matpowerAmpFactor']
	wholesaleTimeShift = int(transmissionDict['wholesaleTimeShift'])
	withTE = '0'

	if transmissionDict['sequelLogging']:
		sequelLogging = '1'
	else:
		sequelLogging = '0'

	if useFlags['add_real_time_transactive_control']:
		withTE = '1'
		dsoLogLevel = simulatorLogLevels['dso']
		lseLogLevel = simulatorLogLevels['lse']
		dsoISORelativeTimeShift = int(populationDict[0]['controlConfig']['dsoISORelativeTimeShift'])
		lseISORelativeTimeShift = int(populationDict[0]['controlConfig']['lseISORelativeTimeShift'])
		quantityPrioritization = int(populationDict[0]['controlConfig']['quantityPrioritization'])

	simFullTime = int((datetime.datetime.strptime(feederConfig['stopdate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(feederConfig['startdate'], '%Y-%m-%d %H:%M:%S')).total_seconds())

	processFolderNames = os.listdir(experimentFilePath / experimentName)

	if os.name == 'nt': # if running on windows
		print('WARNING: execution scripts are not supported for the windows platform at this time')
	else:
		# open the files we need
		runFile = open(experimentFilePath / experimentName / 'runAll.sh', 'w')

		# create the run all script. This script will run the experiment. if we only have one resource we do not have to do anything fancy and the script is easy to create
		runFile.write('#!/bin/bash\n\n')
		runFile.write('clear\n')

		runFile.write('\necho "Executing experiment..."\n\n')

		runFile.write('logFile="helics.out"\n')
		runFile.write('configFile="helics.json"\n')
		runFile.write('matpowerLogLevel="{:s}"\n'.format(matpowerLogLevel))
		
		if useFlags['add_real_time_transactive_control']:
			runFile.write('dsoLogLevel="{:s}"\n'.format(dsoLogLevel))
			runFile.write('lseLogLevel="{:s}"\n'.format(lseLogLevel))
		
		runFile.write('experimentPath="{:}"\n'.format(experimentFilePath / experimentName))
		
		if useFlags['add_real_time_transactive_control']:
			runFile.write('export DSO_LOG_LEVEL=$dsoLogLevel\n')
			runFile.write('export LSE_LOG_LEVEL=$lseLogLevel\n')

		# Do the exports so FNCS and other software behave the way we want
		runFile.write('export MATPOWER_LOG_LEVEL=$matpowerLogLevel\n\n')
		
		processCount = 0
		for process in sorted(processFolderNames):
			if 'matpower' in process:
				if withTE == '1':
					runFile.write('cd $experimentPath/matpower && start_MATPOWER $configFile {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json dispatchable_load_data.json &> $logFile &\n'.format(matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate']))
				else:
					runFile.write('cd $experimentPath/matpower && start_MATPOWER $configFile {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json &> $logFile &\n'.format(matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate']))
				#runFile.write('echo $! > $experimentPath/killAll.sh')
				processCount += 1
			elif 'feeder' in process and 'lse' not in process:
				runFile.write('cd $experimentPath/{:s} && gridlabd {:s}.glm &> $logFile &\n'.format(process, process))
				processCount += 1
			elif 'include' in process:
				pass

			# these are for the CCSI control
			elif 'dso' in process:
				runFile.write('cd $experimentPath/{:s} && dso $configFile {:d} {:d} {:d} {:d} {:d} &> $logFile &\n'.format(process, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, dsoISORelativeTimeShift, quantityPrioritization))
				processCount += 1
			elif 'lse' in process:	
				runFile.write('cd $experimentPath/{:s} && lse $configFile {:d} {:0.3f} {:d} {:d} {:d} {:d} &> $logFile &\n'.format(process, simFullTime, matpowerAmpFactor, wholesaleMarketPeriod, wholesaleTimeShift, lseISORelativeTimeShift, quantityPrioritization))		
				processCount += 1

			else:
				print("WARNING: something went wrong in creating the execution script (Unknown federate ->", process, ")")

		runFile.write('helics_broker --federates {:d} --log_level=3 &> $logFile &\n'.format(processCount))

		runFile.write('\necho "Waiting for processes to finish..."\n\n')
		runFile.write('wait\n')

		runFile.write('\necho "Done..."\n')
		runFile.write('\nexit 0')

		# create the kill all script. This script will terminate an experiment
		killFile = open(experimentFilePath / experimentName / 'killAll.sh', 'w')
		killFile.write('#!/bin/bash\n\n')
		killFile.write('var=$(pgrep -o runAll.sh)\n')
		killFile.write('if [ -z "$var" ]\n')
		killFile.write('then\n')
		killFile.write('    echo "No processes are running"\n')
		killFile.write('else\n')
		killFile.write('    echo "Killing all processes of runAll.sh"\n')
		killFile.write('    kill -9 -$var >/dev/null\n')
		killFile.write('fi\n')

		runFile.close()
		killFile.close()

		termProcess = subprocess.Popen(['chmod', '+x', 'runAll.sh'], cwd=experimentFilePath / experimentName, stdout=subprocess.PIPE)
		if termProcess.wait() != 0:
			raise Exception('something went wrong when doing "chmod" on runAll.sh')
		termProcess = subprocess.Popen(['chmod', '+x', 'killAll.sh'], cwd=experimentFilePath / experimentName, stdout=subprocess.PIPE)
		if termProcess.wait() != 0:
			raise Exception('something went wrong when doing "chmod" on killAll.sh')


def add_fncs_HPC_script(populationDict, transmissionDict, simulatorLogLevels):
	"""
	This function creates convenience scripts for running the experiment on HPC resource

	Inputs
		populationDict - dictionary containing properties for all the feeders we are using
		transmissionDict - dictionary containing properties for the transmission system we are using
		simulatorLogLevels - log level for each type of federate
	Outputs
		None
	"""

	experimentFilePath = populationDict[0]['experimentFilePath']
	experimentName = populationDict[0]['experimentName']
	feederConfig = populationDict[0]['feederConfig']
	fncsLogLevel = simulatorLogLevels['fncs']
	matpowerLogLevel = simulatorLogLevels['matpower']
	matpowerSystem = transmissionDict['matpowerSystem']
	wholesaleMarketPeriod = int(transmissionDict['matpowerOPFTime'])
	matpowerAmpFactor = transmissionDict['matpowerAmpFactor']
	wholesaleTimeShift = int(transmissionDict['wholesaleTimeShift'])
	withTE = '0'
	versionNumber = '0'

	if transmissionDict['sequelLogging']:
		sequelLogging = '1'
	else:
		sequelLogging = '0'

	if 'controlConfig' in populationDict[0]:
		withTE = '1'
		dsoLogLevel = simulatorLogLevels['dso']
		lseLogLevel = simulatorLogLevels['lse']
		dsoISORelativeTimeShift = int(populationDict[0]['controlConfig']['dsoISORelativeTimeShift'])
		lseISORelativeTimeShift = int(populationDict[0]['controlConfig']['lseISORelativeTimeShift'])
		quantityPrioritization = int(populationDict[0]['controlConfig']['quantityPrioritization'])

	simFullTime = int((datetime.datetime.strptime(feederConfig['stopdate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(feederConfig['startdate'], '%Y-%m-%d %H:%M:%S')).total_seconds())

	# unique list for federates
	matpowerNamesTemp = sorted([name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('matpower' in name)])
	feederNamesTemp = sorted([name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('feeder' in name and 'lse' not in name)], key = lambda x: x.split('_')[-1])
	dsoNamesTemp = sorted([name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('dso' in name)])
	lseNamesTemp = sorted([name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('lse' in name)])
	#processFolderNames = [name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('feeder' in name or 'matpower' in name or 'dso' in name or 'lse' in name)]

	if os.name == 'nt': # if running on windows
		print('WARNING: execution scripts are not supported for the windows platform at this time')
	else:
		# open the files we need
		runFile = open(experimentFilePath / experimentName / 'launcher.cfg', 'w')

		maxListLength = max(len(matpowerNamesTemp), len(feederNamesTemp), len(dsoNamesTemp), len(lseNamesTemp))
		#print(maxListLength)

		#shiftFactor = 100

		matpowerNames = [None]*maxListLength
		if len(matpowerNamesTemp)>0:
			#matpowerNames[:(math.floor(maxListLength/len(matpowerNamesTemp))*len(matpowerNamesTemp)):math.floor(maxListLength/len(matpowerNamesTemp))] = matpowerNamesTemp
			matpowerNames[-1] = matpowerNamesTemp[0]
		#feederNames = [None]*(maxListLength+shiftFactor)
		feederNames = [None]*maxListLength
		if len(feederNamesTemp)>0:
			feederNames[:(math.floor(maxListLength/len(feederNamesTemp))*len(feederNamesTemp)):math.floor(maxListLength/len(feederNamesTemp))] = feederNamesTemp
			#feederNames[-1:(math.floor((maxListLength)/len(feederNamesTemp))*len(feederNamesTemp)):math.floor((maxListLength)/len(feederNamesTemp))] = feederNamesTemp
		dsoNames = [None]*maxListLength
		if len(dsoNamesTemp)>0:
			dsoNames[:(math.floor(maxListLength/len(dsoNamesTemp))*len(dsoNamesTemp)):math.floor(maxListLength/len(dsoNamesTemp))] = dsoNamesTemp
			#dsoNames = dsoNamesTemp
		lseNames = [None]*maxListLength
		if len(lseNamesTemp)>0:
			lseNames[:(math.floor(maxListLength/len(lseNamesTemp))*len(lseNamesTemp)):math.floor(maxListLength/len(lseNamesTemp))] = lseNamesTemp		

		#print(matpowerNames)
		#print(feederNames)
		#print(dsoNames)
		#print(lseNames)

		# create a list that is alternating between federate types
		processFolderNames = [x for x in itertools.chain.from_iterable(itertools.zip_longest(matpowerNames,feederNames,dsoNames,lseNames)) if x]
		#print(processFolderNames)

		for process in processFolderNames:
			if 'matpower' in process:
				if withTE == '1':
					runFile.write('{:}/{:s} FNCS_LOG_LEVEL={:s} FNCS_CONFIG_FILE=fncs.yaml MATPOWER_LOG_LEVEL={:s} nice -5 start_MATPOWER {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json dispatchable_load_data.json\n'.format(experimentFilePath / experimentName, process, fncsLogLevel, matpowerLogLevel, matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate']))
				else:
					runFile.write('{:}/{:s} FNCS_LOG_LEVEL={:s} FNCS_CONFIG_FILE=fncs.yaml MATPOWER_LOG_LEVEL={:s} nice -5 start_MATPOWER {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json\n'.format(experimentFilePath / experimentName, process, fncsLogLevel, matpowerLogLevel, matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate']))
				# This is for running with experimental wrapper code
				#runFile.write('{:}/{:s} FNCS_LOG_LEVEL={:s} FNCS_CONFIG_FILE=fncs.yaml MATPOWER_LOG_LEVEL={:s} start_MATPOWER {:s}.m real_power_demand.txt reactive_power_demand.txt {:d} {:d} {:d} "{:s}" {:s} {:s} {:s}\n'.format(experimentFilePath / experimentName, process, fncsLogLevel, matpowerLogLevel, matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate'], withTE, sequelLogging, versionNumber))
			elif 'dso' in process:
				runFile.write('{:}/{:s} FNCS_LOG_LEVEL={:s} FNCS_CONFIG_FILE=fncs.yaml DSO_LOG_LEVEL={:s} nice -5 dso {:d} {:d} {:d} {:d} {:d}\n'.format(experimentFilePath / experimentName, process, fncsLogLevel, dsoLogLevel, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, dsoISORelativeTimeShift, quantityPrioritization))
			elif 'lse' in process:	
				runFile.write('{:}/{:s} FNCS_LOG_LEVEL={:s} FNCS_CONFIG_FILE=fncs.yaml LSE_LOG_LEVEL={:s} nice -5 lse {:d} {:0.3f} {:d} {:d} {:d} {:d}\n'.format(experimentFilePath / experimentName, process, fncsLogLevel, lseLogLevel, simFullTime, matpowerAmpFactor, wholesaleMarketPeriod, wholesaleTimeShift, lseISORelativeTimeShift, quantityPrioritization))		
			else:
				runFile.write('{:}/{:s} FNCS_LOG_LEVEL={:s} nice -5 gridlabd {:s}.glm\n'.format(experimentFilePath / experimentName, process, fncsLogLevel, process))		


def add_helics_HPC_script(populationDict, transmissionDict, simulatorLogLevels):
	"""
	This function creates convenience scripts for running the experiment on HPC resource

	Inputs
		populationDict - dictionary containing properties for all the feeders we are using
		transmissionDict - dictionary containing properties for the transmission system we are using
		simulatorLogLevels - log level for each type of federate
	Outputs
		None
	"""

	experimentFilePath = populationDict[0]['experimentFilePath']
	experimentName = populationDict[0]['experimentName']
	feederConfig = populationDict[0]['feederConfig']
	useFlags = populationDict[0]['useFlags']
	fncsLogLevel = simulatorLogLevels['fncs']
	matpowerLogLevel = simulatorLogLevels['matpower']
	matpowerSystem = transmissionDict['matpowerSystem']
	wholesaleMarketPeriod = int(transmissionDict['matpowerOPFTime'])
	matpowerAmpFactor = transmissionDict['matpowerAmpFactor']
	wholesaleTimeShift = int(transmissionDict['wholesaleTimeShift'])
	withTE = '0'
	versionNumber = '0'

	if transmissionDict['sequelLogging']:
		sequelLogging = '1'
	else:
		sequelLogging = '0'

	if 'controlConfig' in populationDict[0]:
		withTE = '1'
		dsoLogLevel = simulatorLogLevels['dso']
		lseLogLevel = simulatorLogLevels['lse']
		dsoISORelativeTimeShift = int(populationDict[0]['controlConfig']['dsoISORelativeTimeShift'])
		lseISORelativeTimeShift = int(populationDict[0]['controlConfig']['lseISORelativeTimeShift'])
		quantityPrioritization = int(populationDict[0]['controlConfig']['quantityPrioritization'])

	simFullTime = int((datetime.datetime.strptime(feederConfig['stopdate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(feederConfig['startdate'], '%Y-%m-%d %H:%M:%S')).total_seconds())

	# unique list for federates
	matpowerNamesTemp = sorted([name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('matpower' in name)])
	feederNamesTemp = sorted([name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('feeder' in name and 'lse' not in name)], key = lambda x: x.split('_')[-1])
	dsoNamesTemp = sorted([name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('dso' in name)])
	lseNamesTemp = sorted([name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('lse' in name)])
	#processFolderNames = [name for name in os.listdir(experimentFilePath / experimentName) if os.path.isdir(experimentFilePath / experimentName / name) and ('feeder' in name or 'matpower' in name or 'dso' in name or 'lse' in name)]

	if os.name == 'nt': # if running on windows
		print('WARNING: execution scripts are not supported for the windows platform at this time')
	else:
		# open the files we need
		runFile = open(experimentFilePath / experimentName / 'launcher.cfg', 'w')

		maxListLength = max(len(matpowerNamesTemp), len(feederNamesTemp), len(dsoNamesTemp), len(lseNamesTemp))
		#print(maxListLength)

		#shiftFactor = 100

		matpowerNames = [None]*maxListLength
		if len(matpowerNamesTemp)>0:
			#matpowerNames[:(math.floor(maxListLength/len(matpowerNamesTemp))*len(matpowerNamesTemp)):math.floor(maxListLength/len(matpowerNamesTemp))] = matpowerNamesTemp
			matpowerNames[-1] = matpowerNamesTemp[0]
		#feederNames = [None]*(maxListLength+shiftFactor)
		feederNames = [None]*maxListLength
		if len(feederNamesTemp)>0:
			feederNames[:(math.floor(maxListLength/len(feederNamesTemp))*len(feederNamesTemp)):math.floor(maxListLength/len(feederNamesTemp))] = feederNamesTemp
			#feederNames[-1:(math.floor((maxListLength)/len(feederNamesTemp))*len(feederNamesTemp)):math.floor((maxListLength)/len(feederNamesTemp))] = feederNamesTemp
		dsoNames = [None]*maxListLength
		if len(dsoNamesTemp)>0:
			dsoNames[:(math.floor(maxListLength/len(dsoNamesTemp))*len(dsoNamesTemp)):math.floor(maxListLength/len(dsoNamesTemp))] = dsoNamesTemp
			#dsoNames = dsoNamesTemp
		lseNames = [None]*maxListLength
		if len(lseNamesTemp)>0:
			lseNames[:(math.floor(maxListLength/len(lseNamesTemp))*len(lseNamesTemp)):math.floor(maxListLength/len(lseNamesTemp))] = lseNamesTemp		

		#print(matpowerNames)
		#print(feederNames)
		#print(dsoNames)
		#print(lseNames)

		# create a list that is alternating between federate types
		processFolderNames = [x for x in itertools.chain.from_iterable(itertools.zip_longest(matpowerNames,feederNames,dsoNames,lseNames)) if x]
		#print(processFolderNames)

		if "mpi" in useFlags['core_type_HELICS']:
			runFile.write('-np 1 -wd {:} helicsWrapperMPI.sh helics_broker --federates {:d} --type=mpi --loglevel=4\n'.format(experimentFilePath / experimentName, len(processFolderNames)))
			for process in processFolderNames:
				if 'matpower' in process:
					if withTE == '1':
						runFile.write('-np 1 -wd {:}/{:s} helicsWrapperMPI.sh nice -5 start_MATPOWER helics.json {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json dispatchable_load_data.json\n'.format(experimentFilePath / experimentName, process, matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate'].replace(" ", "-")))
					else:
						runFile.write('-np 1 -wd {:}/{:s} helicsWrapperMPI.sh nice -5 start_MATPOWER helics.json {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json\n'.format(experimentFilePath / experimentName, process, matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate'].replace(" ", "-")))
					# This is for running with experimental wrapper code
					#runFile.write('{:}/{:s} FNCS_LOG_LEVEL={:s} FNCS_CONFIG_FILE=fncs.yaml MATPOWER_LOG_LEVEL={:s} start_MATPOWER {:s}.m real_power_demand.txt reactive_power_demand.txt {:d} {:d} {:d} "{:s}" {:s} {:s} {:s}\n'.format(experimentFilePath / experimentName, process, fncsLogLevel, matpowerLogLevel, matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate'], withTE, sequelLogging, versionNumber))
				elif 'dso' in process:
					runFile.write('-np 1 -wd {:}/{:s} helicsWrapperMPI.sh nice -5 dso helics.json {:d} {:d} {:d} {:d} {:d}\n'.format(experimentFilePath / experimentName, process, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, dsoISORelativeTimeShift, quantityPrioritization))
				elif 'lse' in process:	
					runFile.write('-np 1 -wd {:}/{:s} helicsWrapperMPI.sh nice -5 lse helics.json {:d} {:0.3f} {:d} {:d} {:d} {:d}\n'.format(experimentFilePath / experimentName, process, simFullTime, matpowerAmpFactor, wholesaleMarketPeriod, wholesaleTimeShift, lseISORelativeTimeShift, quantityPrioritization))		
				else:
					runFile.write('-np 1 -wd {:}/{:s} helicsWrapperMPI.sh nice -5 gridlabd {:s}.glm\n'.format(experimentFilePath / experimentName, process, process))		
		else:
			for process in processFolderNames:
				if 'matpower' in process:
					if withTE == '1':
						runFile.write('{:}/{:s} MATPOWER_LOG_LEVEL={:s} nice -5 start_MATPOWER helics.json {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json dispatchable_load_data.json\n'.format(experimentFilePath / experimentName, process, matpowerLogLevel, matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate']))
					else:
						runFile.write('{:}/{:s} MATPOWER_LOG_LEVEL={:s} nice -5 start_MATPOWER helics.json {:s}.m real_power_demand.txt reactive_power_demand.txt renewable_power_generation.txt {:d} {:d} {:d} "{:s}" load_data.json generator_data.json\n'.format(experimentFilePath / experimentName, process, matpowerLogLevel, matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate']))
					# This is for running with experimental wrapper code
					#runFile.write('{:}/{:s} FNCS_LOG_LEVEL={:s} FNCS_CONFIG_FILE=fncs.yaml MATPOWER_LOG_LEVEL={:s} start_MATPOWER {:s}.m real_power_demand.txt reactive_power_demand.txt {:d} {:d} {:d} "{:s}" {:s} {:s} {:s}\n'.format(experimentFilePath / experimentName, process, fncsLogLevel, matpowerLogLevel, matpowerSystem, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, feederConfig['startdate'], withTE, sequelLogging, versionNumber))
				elif 'dso' in process:
					runFile.write('{:}/{:s} DSO_LOG_LEVEL={:s} nice -5 dso helics.json {:d} {:d} {:d} {:d} {:d}\n'.format(experimentFilePath / experimentName, process, dsoLogLevel, simFullTime, wholesaleMarketPeriod, wholesaleTimeShift, dsoISORelativeTimeShift, quantityPrioritization))
				elif 'lse' in process:	
					runFile.write('{:}/{:s} LSE_LOG_LEVEL={:s} nice -5 lse helics.json {:d} {:0.3f} {:d} {:d} {:d} {:d}\n'.format(experimentFilePath / experimentName, process, lseLogLevel, simFullTime, matpowerAmpFactor, wholesaleMarketPeriod, wholesaleTimeShift, lseISORelativeTimeShift, quantityPrioritization))		
				else:
					runFile.write('{:}/{:s} nice -5 gridlabd {:s}.glm\n'.format(experimentFilePath / experimentName, process, process))		


if __name__ == '__main__':
	pass
