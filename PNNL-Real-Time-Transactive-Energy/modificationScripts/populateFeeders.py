"""
Created April 11, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""

from supportFunctions import parseGLM
from supportFunctions import createDistributionFeeder
from supportFunctions import executionScripts
from supportFunctions import feederConfiguration
from supportFunctions import technologyConfiguration
from supportFunctions import upgradeEquipment
from pathlib import Path
import time, os, shutil, math, tqdm, multiprocessing, platform, sys

# ---------------------------------------------------------------
# ----------------------- Settings ------------------------------
# ---------------------------------------------------------------
start = time.time()

# name of the experiment
experimentName = 'populateExample'

# number of distribution systems in the experiment
distributionSystemNumber = 2

# create simple bash run scipt that will start a GridLAB-D instance per feeder
createRunScripts = True

# this assumes that everything associated with this experiment is in a certain folder structure. This is the path to the root folder
rootPath = '<path to your repository>/HELICS-Use-Cases/PNNL-Real-Time-Transactive-Energy'

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
feederConfig['sequelLogging'] = False
feederConfig["sequelSettings"] = ['localhost','gridlabd','passGLD123','3306','0']
feederConfig['fuses_upgrade_level'] = 2
feederConfig['transformer_upgrade_level'] = 1
feederConfig['transformer_upgrade_cutoff'] = 100
feederConfig['startdate'] = '2013-08-28 00:00:00'
feederConfig['stopdate'] = '2013-08-29 00:00:00'

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
	else:
		raise Exception('Correct amount of command line arguments are not specified')

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
								 'experimentName': experimentName}
		#print 'key offset -> ', keyOffset, 'control -> ',advancedControlBool
		count += 1
		
# create all the distribution systems
# code to show the user progress in creating the experiment
print('creating distribution systems')

success = True
#if True:
if os.name == 'nt': # if running on windows
	for randomSeed, feeder in enumerate(populationDict):
		# print populationDict[feeder]
		result = createDistributionFeeder.createDistributionSystem(parsedDict[populationDict[feeder]['originalName']]['model'], populationDict[feeder], False, False)
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
		pool.apply_async(createDistributionFeeder.createDistributionSystem, args=(parsedDict[populationDict[feeder]['originalName']]['model'], populationDict[feeder], False, True, ), callback=poolResults.append)

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
		executionScripts.add_simple_run_script(experimentFilePath, experimentName)

	end = time.time()
	print('successfully completed experiment creation on "', platform.uname()[1], '" in {:0.1f} seconds'.format(end - start))
