"""
Created April 11, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""

from supportFunctions import parseGLM
from supportFunctions import createDistributionFeeder
from supportFunctions import executionScripts
from supportFunctions import transmissionSystemConfiguration
from supportFunctions import feederConfiguration
from supportFunctions import technologyConfiguration
from supportFunctions import fncsConfiguration
from supportFunctions import helicsConfiguration
from supportFunctions import upgradeEquipment
from pathlib import Path
import time, os, shutil, math, tqdm, multiprocessing, platform, sys

# ---------------------------------------------------------------
# ----------------------- Settings ------------------------------
# ---------------------------------------------------------------
start = time.time()

# name of the experiment
experimentName = 'tdExample'

# number of distribution systems in the experiment
distributionSystemNumber = 2

# create simple bash run scipt that will start a GridLAB-D instance per feeder
createRunScripts = True		

# create HPC run scipt that will work with the Co-Simulation launcher capability
createHPCScripts = False

# this assumes that everything associated with this experiment is in a certain folder structure. This is the path to the root folder
rootPath = '<path to your repository>/HELICS-Use-Cases/PNNL-Real-Time-Transactive-Energy'

# path to where you want the experiment outputs (if left empty we assume /experiments)
experimentFilePath = ''

# file path that contains the GLMs to extract (if left empty we assume /modelDependency/feeders)
feederFilePath = ''

# file path that contains include files for the experiment (if left empty we assume /modelDependency)
includeFilePath = ''

# dictionary that holds all the log level information for each type of federate
simulatorLogLevels = dict()
simulatorLogLevels['fncs'] = 'WARNING'
simulatorLogLevels['matpower'] = 'INFO'

# specify the port fncs will use to communicate on
fncsPort = '7777'

# list of distribution systems models and their population distribution for the experiment (feeder : [percent [.], region [#])
inputGLM = dict()
inputGLM['small4BusSystem.glm'] = [1, 1]
#inputGLM['R1-12.47-1.glm'] = [0.14, 1]
#inputGLM['R1-12.47-2.glm'] = [0.14, 1]
#inputGLM['R1-12.47-3.glm'] = [0.14, 1]
#inputGLM['R2-12.47-1.glm'] = [0.08, 2]
#inputGLM['R2-12.47-2.glm'] = [0.07, 2]
#inputGLM['R2-12.47-3.glm'] = [0.07, 2]
#inputGLM['R3-12.47-1.glm'] = [0.12, 3]
#inputGLM['R3-12.47-2.glm'] = [0.12, 3]
#inputGLM['R3-12.47-3.glm'] = [0.12, 3]


# This specifies what technologies to use. What is specified here will overwrite the defaults in the technologyConfiguration.py
useFlags = dict()
useFlags['use_FNCS'] = 0
useFlags['use_HELICS'] = 1
useFlags['core_type_HELICS'] = 'zmq'

# This specifies what feeder configuration to use. What is specified here will overwrite the defaults in the feederConfiguration.py	
feederConfig = dict()
feederConfig['sequelLogging'] = False
feederConfig["sequelSettings"] = ['localhost','gridlabd','passGLD123','3306','0']
feederConfig['fuses_upgrade_level'] = 2
feederConfig['transformer_upgrade_level'] = 1
feederConfig['transformer_upgrade_cutoff'] = 100
feederConfig['startdate'] = '2013-08-28 00:00:00'
feederConfig['stopdate'] = '2013-08-29 00:00:00'
feederConfig['measure_interval'] = 30
feederConfig['recorders'] = {'HVAC': True}
feederConfig['short_names'] = False
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

# -------------------------------------------------------------------------------------------
# ----------------------- No modification beyond this point ---------------------------------
# -------------------------------------------------------------------------------------------

# combine paths
if feederFilePath == '':
	feederFilePath = Path(rootPath) / 'modelDependency' / 'feeders'
else:
	feederFilePath = Path(feederFilePath)
if includeFilePath == '':
	includeFilePath = Path(rootPath) / 'modelDependency'
else:
	includeFilePath = Path(includeFilePath)	
if experimentFilePath == '':
	experimentFilePath = Path(rootPath) / 'experiments'
else:
	experimentFilePath = Path(experimentFilePath)

# For certain application is it useful to be able to specify the experiment name and number of distribution system at execution time
if len(sys.argv) > 1:
	# we have extra arguments, let check if we got the two we needed
	if len(sys.argv) == 3:
		experimentName = str(sys.argv[1])
		distributionSystemNumber = int(sys.argv[2])
	elif len(sys.argv) == 4:
		experimentName = str(sys.argv[1])
		distributionSystemNumber = int(sys.argv[2])
		if "helics" in str(sys.argv[3]):
			useFlags['use_FNCS'] = 0
			useFlags['use_HELICS'] = 1
		elif "fncs" in str(sys.argv[3]):
			useFlags['use_FNCS'] = 1
			useFlags['use_HELICS'] = 0
		else:
			raise Exception('The third argument speicfied is not valid')
	elif len(sys.argv) == 5:
		experimentName = str(sys.argv[1])
		distributionSystemNumber = int(sys.argv[2])
		if "helics" in str(sys.argv[3]):
			useFlags['use_FNCS'] = 0
			useFlags['use_HELICS'] = 1
		elif "fncs" in str(sys.argv[3]):
			useFlags['use_FNCS'] = 1
			useFlags['use_HELICS'] = 0
		else:
			raise Exception('The third argument speicfied is not valid')
		if "zmq" in str(sys.argv[4]):
			useFlags['core_type_HELICS'] = 'zmq'
		elif "mpi" in str(sys.argv[4]):
			useFlags['core_type_HELICS'] = 'mpi'
		else:
			raise Exception('The fourth argument speicfied is not valid')				
	else:
		raise Exception('Correct amount of command line arguments are not specified')

if createRunScripts and createHPCScripts:
	print('WARNING: you asked to two different run script technologies')

# some user info
print('creating experiment "{:s}" with a total of "{:0.0f}" distribution systems'.format(experimentName, distributionSystemNumber))

# ensure that the input GLM specification makes sense (i.e percentages sum to one). We only warn the user as it won't break anything
if abs(sum([inputGLM[key][0] for key in list(inputGLM.keys())]) - 1) > 0.001:
	print('WARNING: your distribution system population sums to {:0.2f}, should be 1'.format(sum([inputGLM[key][0] for key in list(inputGLM.keys())])))


# We need to create the experiment folder. If it already exists we delete it and then create it
if os.path.isdir(experimentFilePath / experimentName):
	print("experiment folder already exists, deleting and moving on...")
	shutil.rmtree(experimentFilePath / experimentName)
os.makedirs(experimentFilePath / experimentName)

# then we need to copy over all the include files for the experiment
shutil.copytree(includeFilePath / 'players', experimentFilePath / experimentName / 'include' / 'players')
shutil.copytree(includeFilePath / 'schedules', experimentFilePath / experimentName / 'include' / 'schedules')
shutil.copytree(includeFilePath / 'weather', experimentFilePath / experimentName / 'include' / 'weather')

# it is assumed that the list of feeders will be much less than the actual amount of distribution system.
# instead of parsing the same system over an over we will parse all of them once.
parsedDict = {}
for feeder in inputGLM:
	# Parse the feeder model into a nice dictionary
	originalGLM = parseGLM.parse(feederFilePath / feeder)
	configGLM = feederConfiguration.feederConfiguration(os.path.splitext(feeder)[0], feederConfig)
	# upgrade fuses and transformers
	originalGLM = upgradeEquipment.upgrade_transformers(originalGLM, configGLM['transformer_upgrade_level'], configGLM['transformer_upgrade_cutoff'])
	originalGLM = upgradeEquipment.upgrade_fuses(originalGLM, configGLM['fuses_upgrade_level'], configGLM['fuses_upgrade_cutoff'])
	

	parsedDict[os.path.splitext(feeder)[0]] = {'model': originalGLM.copy(),
											   'feederConfig': configGLM.copy()}

# find the appropiate number of distribution system of each to implement. We need this to create the full distribution system dictionary
temp = [inputGLM[key][0]*distributionSystemNumber for key in list(inputGLM.keys())]
distributionNumberVector = [math.floor(x) for x in temp]
temp2 = [a_i - b_i for a_i, b_i in zip(temp, distributionNumberVector)]
for remain in range(int(distributionSystemNumber - sum(distributionNumberVector))):
	idx = temp2.index(max(temp2))
	distributionNumberVector[idx] += 1
	temp2[idx] = 0

#print distributionNumberVector

# pull the technology list to use
useFlags = technologyConfiguration.technologyConfiguration(useFlags)

# create the full list of distribution systems to implement (key : {'name' , 'feeder' , 'peakLoad', 'substationkV', 'substationBus'})
populationDict = {}
count = 0
for key, number in enumerate(distributionNumberVector):
	for keyOffset in range(0, int(number)):
		populationDict[count] = {'originalName': os.path.splitext(list(inputGLM.keys())[key])[0],
								 'desiredName' : os.path.splitext(list(inputGLM.keys())[key])[0].replace('-','_').replace('.','_') + '_feeder_' + str(count) ,
								 'useFlags': useFlags.copy(),
								 'feederConfig': parsedDict[os.path.splitext(list(inputGLM.keys())[key])[0]]['feederConfig'].copy(),
								 'experimentFilePath': experimentFilePath,
								 'experimentName': experimentName,
								 'region': inputGLM[list(inputGLM.keys())[key]][1]}
		#print 'key offset -> ', keyOffset, 'control -> ',advancedControlBool
		count += 1

# some user info
print('creating MATPOWER simulator')

# this function will add the transmission system to our co-simulation
populationDict = transmissionSystemConfiguration.create_transmission_system(populationDict, transmissionConfig)

# we need to do extra stuff if we are working with FNCS
if useFlags['use_FNCS']:
	fncsConfiguration.matpower_fncs_config(populationDict, transmissionConfig)

# we need to do extra stuff if we are working with HELICS
if useFlags['use_HELICS']:
	helicsConfiguration.matpower_config(populationDict, transmissionConfig)
	
# create all the distribution systems
# code to show the user progress in creating the experiment
print('creating distribution systems')

success = True
#if True:
if os.name == 'nt': # if running on windows
	for randomSeed, feeder in enumerate(populationDict):
		# print populationDict[feeder]
		result = createDistributionFeeder.createDistributionSystem(parsedDict[populationDict[feeder]['originalName']]['model'], populationDict[feeder], createHPCScripts, False)
		if not result == True:
			print ('The script failed with the following trace:')
			print (result)
			success = False
			break
else:
	l = multiprocessing.Lock()
	#multiprocessing.set_start_method('forkserver', force=True)
	pool = multiprocessing.Pool(initializer=createDistributionFeeder.initLock, initargs=(l,), processes=multiprocessing.cpu_count())
	poolResults = []
	for randomSeed, feeder in enumerate(populationDict):
		# print populationDict[feeder]
		pool.apply_async(createDistributionFeeder.createDistributionSystem, args=(parsedDict[populationDict[feeder]['originalName']]['model'], populationDict[feeder], createHPCScripts, True, ), callback=poolResults.append)

	time.sleep(1) # seems to be needed
	pbar = tqdm.tqdm(desc='processing: ',total=len(list(populationDict.keys())), bar_format='{desc}|{bar}| {percentage:3.0f}%', ncols=50)
	oldLen = 0
	updateLeft = len(list(populationDict.keys()))
	while len(poolResults) != len(list(populationDict.keys())):
		if len(poolResults)-oldLen > (len(list(populationDict.keys()))/20):
			updateLeft -= len(poolResults)-oldLen
			pbar.update(len(poolResults)-oldLen)
			oldLen = len(poolResults)
		time.sleep(1)
		if any(item != True for item in poolResults):
			print ('The script failed with the following trace:')
			print (poolResults[0])
			success = False
			break
	pbar.update(updateLeft)
	pbar.close()

	# ensure that all workers are finished before we continue
	pool.close()
	pool.join()

	# it can happen that the previous loop exists fine even when an error is present. Let's double check that here
	if any(item != True for item in poolResults):
		print ('The script failed with the following trace:')
		print (poolResults[0])
		success = False

if success:
	# this function will create the run template for running the cases
	if createRunScripts:
		# some user info
		print('creating convenience scripts for user')
		if useFlags['use_FNCS'] == 1:
			executionScripts.add_fncs_run_script(populationDict, transmissionConfig, simulatorLogLevels, fncsPort)
		elif useFlags['use_HELICS'] == 1:	
			executionScripts.add_helics_run_script(populationDict, transmissionConfig, simulatorLogLevels)
		else:
			print('WARNING: you asked for a run script but that only works with either HELICS or FNCS')	

	if createHPCScripts:
		# some user info
		print('creating HPC scripts for user')
		if useFlags['use_FNCS'] == 1:
			executionScripts.add_fncs_HPC_script(populationDict, transmissionConfig, simulatorLogLevels)
		elif useFlags['use_HELICS'] == 1:	
			executionScripts.add_helics_HPC_script(populationDict, transmissionConfig, simulatorLogLevels)
		else:
			print('WARNING: you asked for a run script but that only works with either HELICS or FNCS')	
			
	end = time.time()
	print('successfully completed experiment creation on "', platform.uname()[1], '" in {:0.1f} seconds'.format(end - start))
