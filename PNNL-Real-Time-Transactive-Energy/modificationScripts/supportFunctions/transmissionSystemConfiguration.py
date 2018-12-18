"""
This file contains functions that help configure the transmission system 
"""
##################################################################################################################
# Created April 16, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

# Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
# worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
# Government, including the right to distribute to other Government contractors.
##################################################################################################################

import numpy as np
import scipy.io as sio
import random, os, math

def create_transmission_system(populationDict, transmissionDict, haveMATLAB=False):
	"""
	This function creates the MATPOWER simulator according the user specified settings

	Inputs
		populationDict - dictionary containing properties for all the feeders we are using

		transmissionDict - - dictionary containing properties for the transmission system we are using

		haveMATLAB - setting to tell the script if you have MATLAB installed

	Outputs
		populationDict - modified dictionary containing properties for all the feeders we are using
	"""

	# Get information about the co-sim we are working on
	feederConfig = populationDict[0]['feederConfig']
	useFlags = populationDict[0]['useFlags']

	experimentFilePath = populationDict[0]['experimentFilePath']
	experimentName = populationDict[0]['experimentName']

	matpowerFilePath = transmissionDict['matpowerFilePath']
	matpowerSystem = transmissionDict['matpowerSystem']
	matpowerAmpFactor = transmissionDict['matpowerAmpFactor']
	
	# Initialize psuedo-random seed
	random.seed(10, version=1)

	# create folder for MATPOWER simulator
	os.makedirs(experimentFilePath / experimentName / 'matpower')

	if haveMATLAB is True:
		# open matlab engine and add MATPOWER to the path
		import matlab.engine as MatlabEngine
		eng = MatlabEngine.start_matlab('-nojvm -nodisplay -nosplash')
		eng.addpath(matpowerFilePath)

		# load the MATPOWER case struct
		matpowerCaseStruct = eng.loadcase(matpowerFilePath / str(matpowerSystem + '.m'))
	else:
		matpowerCaseStruct = pythonLoadCase(matpowerFilePath / str(matpowerSystem + '.m'))

	# pull out the bus data as we need it to adjust the case
	busData = np.asarray(matpowerCaseStruct['bus'])

	# determine the total distribution load along with the total matpower load
	totalDistributionLoad = sum([(populationDict[dist]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15 for dist in populationDict])
	totalMatpowerLoad = sum(busData[:, 2])

	# warn the user if the distribution load is larger than the matpower load
	if (totalMatpowerLoad - totalDistributionLoad) < 0:
		print('WARNING: you are trying to attach more load than the transmission system can support (' + str(int(totalMatpowerLoad/1000)) + 'GW vs ' + str(int(totalDistributionLoad/1000)) + 'GW)')

	# determine buses that contain load and take the bus number, these will be used to attach distribution systems
	matpowerLoadBuses = busData[busData[:, 2] > 0, 0]
	matpowerLoadBuskV = busData[busData[:, 2] > 0, 9]
	matpowerLoad = busData[busData[:, 2] > 0, 2]

	# this calculates the percentage of system out of the total that should be attached at each bus. This is then multiplied by the user specified number of systems
	# We use ceil() to ensure that the sum will always be greater than or equal to number of distribution systems
	matpowerDistributionCountAtBuses = []
	for load in matpowerLoad:
		matpowerDistributionCountAtBuses.append(math.ceil((load / totalMatpowerLoad) * len(list(populationDict.keys()))))

	# determine the number of regions specified in the MATPOWER case file contains region specification
	if 'region' in matpowerCaseStruct:
		regionFlag = True
		regionData = np.asarray(matpowerCaseStruct['region'])
		regionData = regionData[busData[:, 2] > 0, 1]
		#print regionData
	else:
		regionFlag = False

	# loop through the population dictionary and start placing the distribution systems
	for idx, feeder in enumerate(populationDict):
		# print('==== ', idx, ' ==== ', feeder , ' ====\n')
		success = False
		count = 0
		while success is False:
			if regionFlag is True:
				# pull region from the feeder info
				feederRegion = populationDict[feeder]['region']
				feederRegionIdx = np.nonzero(regionData == feederRegion)[0]
				busIdx = random.choice(feederRegionIdx)  # pick a random bus to use
			else:
				busIdx = random.randint(0, len(matpowerLoadBuses)-1) # pick a random bus to use
			# we will try 20 times to find a bus
			if matpowerDistributionCountAtBuses[busIdx] > 0 and matpowerLoad[busIdx] >= (populationDict[feeder]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15:
				success = True
				populationDict[feeder]['substationkV'] = matpowerLoadBuskV[busIdx]
				populationDict[feeder]['substationBus'] = int(matpowerLoadBuses[busIdx])
				#populationDict[feeder]['matpowerSubscriptions'] = ['matpower', 'three_phase_voltage_B', 'LMP_B']
				matpowerLoad[busIdx] -= (populationDict[feeder]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15
				matpowerDistributionCountAtBuses[busIdx] -= 1


			if count > 20 and success is False:
				# let's find an alternative bus for the system!
				if matpowerLoad[busIdx] >= (populationDict[feeder]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15:
					success = True
					populationDict[feeder]['substationkV'] = matpowerLoadBuskV[busIdx]
					populationDict[feeder]['substationBus'] = int(matpowerLoadBuses[busIdx])
					#populationDict[feeder]['matpowerSubscriptions'] = ['matpower', 'three_phase_voltage_B', 'LMP_B']
					matpowerLoad[busIdx] -= (populationDict[feeder]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15
					matpowerDistributionCountAtBuses[busIdx] -= 1
				else:
					# let's find an alternative bus for the system!
					for secondaryIdx, load in enumerate(matpowerLoad):
						if load >= (populationDict[feeder]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15:
							if regionFlag is True:
								if regionData[secondaryIdx] == populationDict[feeder]['region']:
									success = True
									populationDict[feeder]['substationkV'] = matpowerLoadBuskV[secondaryIdx]
									populationDict[feeder]['substationBus'] = int(matpowerLoadBuses[secondaryIdx])
									#populationDict[feeder]['matpowerSubscriptions'] = ['matpower', 'three_phase_voltage_B', 'LMP_B']
									matpowerLoad[secondaryIdx] -= (populationDict[feeder]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15
									matpowerDistributionCountAtBuses[secondaryIdx] -= 1
									break
							else:
								success = True
								populationDict[feeder]['substationkV'] = matpowerLoadBuskV[secondaryIdx]
								populationDict[feeder]['substationBus'] = int(matpowerLoadBuses[secondaryIdx])
								#populationDict[feeder]['matpowerSubscriptions'] = ['matpower', 'three_phase_voltage_B', 'LMP_B']
								matpowerLoad[secondaryIdx] -= (populationDict[feeder]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15
								matpowerDistributionCountAtBuses[secondaryIdx] -= 1
								break

					if success is False:
						# still didn't find a spot so we will just attach it where we find the biggest load!
						if regionFlag is True:
							tempLoadVec = matpowerLoad[regionData == feederRegion]
							third_idx = np.where(matpowerLoad==np.amax(tempLoadVec))[0][0]
						else:
							third_idx = np.argmax(matpowerLoad)
						
						success = True
						populationDict[feeder]['substationkV'] = matpowerLoadBuskV[third_idx]
						populationDict[feeder]['substationBus'] = int(matpowerLoadBuses[third_idx])
						#populationDict[feeder]['matpowerSubscriptions'] = ['matpower', 'three_phase_voltage_B', 'LMP_B']
						matpowerLoad[third_idx] = 0
						#matpowerLoad[third_idx] -= (populationDict[feeder]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15
						matpowerDistributionCountAtBuses[third_idx] -= 1

					# if success is False:
					# 	# still didn't find a spot so we will just attach it where we first intended it!
					# 	success = True
					# 	populationDict[feeder]['substationkV'] = matpowerLoadBuskV[busIdx]
					# 	populationDict[feeder]['substationBus'] = int(matpowerLoadBuses[busIdx])
					# 	populationDict[feeder]['matpowerSubscriptions'] = ['matpower', 'three_phase_voltage_B', 'LMP_B']
					# 	print('hmm')
					# 	#matpowerLoad[busIdx] = 0
					# 	matpowerLoad[busIdx] -= (populationDict[feeder]['feederConfig']['feeder_rating']*matpowerAmpFactor)/1.15
					# 	matpowerDistributionCountAtBuses[busIdx] -= 1
			count += 1
		# print populationDict[feeder]
	#print(matpowerLoad)

	# now we just need to update the matpower case struct
	for rowIdx, row in enumerate(matpowerCaseStruct['bus']):
		if row[0] in matpowerLoadBuses:
			matpowerCaseStruct['bus'][rowIdx][2] = matpowerLoad[np.where(matpowerLoadBuses==row[0])]
			# we will also adjust the reactive load to be 25% of the real load. Should probably be changed in the future
			matpowerCaseStruct['bus'][rowIdx][3] = matpowerLoad[np.where(matpowerLoadBuses==row[0])]*0.25

	# loop through the population dictionary to find unique substation buses
	uniqueSubstationBus = []
	for feeder in populationDict:
		if not populationDict[feeder]['substationBus'] in uniqueSubstationBus:
			uniqueSubstationBus.append(populationDict[feeder]['substationBus'])

	# adding the dispatchable load part to the generation matrix, and to the generator cost matrix when CCSI transactive is in place
	if useFlags['add_real_time_transactive_control'] == 1:
		for substBus in uniqueSubstationBus:
			tempDispLoadRow = np.zeros((1, len(matpowerCaseStruct['gen'][0])))
			tempDispLoadRow[0][0] = substBus
			tempDispLoadRow[0][16:20] = 9999
			tempDispLoadRow[0][6] = matpowerCaseStruct['gen'][0][6]
			matpowerCaseStruct['gen'] = np.vstack([matpowerCaseStruct['gen'], tempDispLoadRow])
			tempDispLoadCostRow = np.zeros((1, len(matpowerCaseStruct['gencost'][0])))
			tempDispLoadCostRow[0][0] = 2
			tempDispLoadCostRow[0][3] = 3
			matpowerCaseStruct['gencost'] = np.vstack([matpowerCaseStruct['gencost'], tempDispLoadCostRow])

	if haveMATLAB is True:
		# save the adjusted MATPOWER case struct
		eng.savecase(experimentFilePath / experimentName / 'matpower' / str(matpowerSystem + '.m'), matpowerCaseStruct)
	else:
		pythonSaveCase(experimentFilePath / experimentName / 'matpower' / str(matpowerSystem + '.m'), matpowerCaseStruct)

	# open the case file again to add in FNCS specific information
	matpowerFile = open(experimentFilePath / experimentName / 'matpower' / str(matpowerSystem + '.m'), 'a')

	# this section add all the setting for the FNCS related matrices for MATPOWER
	matpowerFile.write('\n%% ======================================================================\n')
	matpowerFile.write('%% Co-Simulation communication interface\n')
	matpowerFile.write('%% This has been added to simplify the set-up process\n')
	matpowerFile.write('%% ======================================================================\n')
	matpowerFile.write('%% Number of buses where distribution networks are going to be connected to\n')
	matpowerFile.write('mpc.BusCoSimNum = {:d};\n'.format(len(uniqueSubstationBus)))
	matpowerFile.write('%% Buses where distribution networks are going to be connected to\n')
	matpowerFile.write('mpc.BusCoSim = [\n')
	# loop through the unique bus list
	for bus in uniqueSubstationBus:
		matpowerFile.write('\t{:d}\n'.format(int(bus)))

	matpowerFile.write('];\n')
	matpowerFile.write('%% Number of distribution feeders (GridLAB-D instances)\n')
	matpowerFile.write('mpc.FeederNumCoSim = {:d}\n'.format(int(len(list(populationDict.keys())))))
	matpowerFile.write('mpc.FeederNameCoSim = [\n')
	# loop through the population dictionary and start placing the distribution systems
	for feeder in populationDict:
		matpowerFile.write('\t{:s}\t{:d}\n'.format(populationDict[feeder]['desiredName'], int(populationDict[feeder]['substationBus'])))

	matpowerFile.write('];\n')
	matpowerFile.write('%% ======================================================================\n')
	matpowerFile.write('%% For creating scenarios for visualization\n')
	matpowerFile.write('%% Setting up the matrix of generators that could become off-line\n')
	matpowerFile.write('%% Number of generators that might be turned off-line\n')
	matpowerFile.write('mpc.offlineGenNum = 0;\n')
	matpowerFile.write('%% Matrix contains the bus number of the corresponding off-line generators\n')
	matpowerFile.write('mpc.offlineGenBus = [ ];\n')

	matpowerFile.write('%% ======================================================================\n')
	matpowerFile.write('%% An amplification factor is used to simulate a higher load at the feeder end\n')
	matpowerFile.write('mpc.ampFactor = {:0.3f};\n'.format(matpowerAmpFactor))
	matpowerFile.write('%% ======================================================================\n')

	# add some extra information about matrix sizes that is needed by the MATPOWER wrapper
	for key in matpowerCaseStruct:
		if not (key == 'baseMVA' or key == 'version' or key == 'function' or key == 'governor' or key == 'genfuel'):
			i = len(matpowerCaseStruct[key])
			j = len(matpowerCaseStruct[key][0])
			matpowerFile.write('mpc.{:s}Data = [{:d} {:d}];\n'.format(key, i, j))

	matpowerFile.close()

	# open the file we want to add the load profiles too
	loadprofilerealFile = open(experimentFilePath / experimentName / 'matpower' / 'real_power_demand.txt', 'w')
	loadprofilereacFile = open(experimentFilePath / experimentName / 'matpower' / 'reactive_power_demand.txt', 'w')
	loadprofilererFile = open(experimentFilePath / experimentName / 'matpower' / 'renewable_power_generation.txt', 'w')

	if haveMATLAB is True:
		# construct the real power load for matpower. The normalized_load_data.mat contains some normalized load profiles given by Jason
		normalizedLoadData = eng.load(matpowerFilePath / 'normalized_load_data.mat')
		normalizedLoadData = np.asarray(normalizedLoadData['my_data'])
	else:
		# construct the real power load for matpower. The normalized_load_data.mat contains some normalized load profiles given by Jason
		normalizedLoadData = pythonLoadMat(matpowerFilePath / 'normalized_load_data.mat')
		normalizedLoadData = np.asarray(normalizedLoadData['my_data'])

	# this section assigns a random load profile to each bus in the transmission system
	numberOfBuses = len(matpowerCaseStruct['bus'])
	for idx, busRow in enumerate(matpowerCaseStruct['bus']):
		busLoadReal = busRow[2]
		busLoadReac = busRow[3]
		profile = random.randint(0, 8) # we have 9 profiles and we want to pick one at random
		for loadLen in range(0, 288):
			if not loadLen == 287:
				loadprofilerealFile.write('{:0.2f} '.format(busLoadReal * normalizedLoadData[loadLen, profile]))
				loadprofilereacFile.write('{:0.2f} '.format(busLoadReac * normalizedLoadData[loadLen, profile]))
			elif idx == numberOfBuses-1:
				loadprofilerealFile.write('{:0.2f}'.format(busLoadReal * normalizedLoadData[loadLen, profile]))
				loadprofilereacFile.write('{:0.2f}'.format(busLoadReac * normalizedLoadData[loadLen, profile]))
			else:
				loadprofilerealFile.write('{:0.2f}\n'.format(busLoadReal * normalizedLoadData[loadLen, profile]))
				loadprofilereacFile.write('{:0.2f}\n'.format(busLoadReac * normalizedLoadData[loadLen, profile]))

	# this section assigns a generation schedule for renewable assets in the transmission system
	if os.path.isfile(matpowerFilePath / (matpowerSystem + '.mat')):
		# we have an actual profile for the renewables
		if haveMATLAB is True:
			renewableGenData = eng.load(matpowerFilePath / (matpowerSystem + '.mat'))
			#normalizedLoadData = np.asarray(normalizedLoadData['my_data'])
		else:
			renewableGenData = pythonLoadMat(matpowerFilePath / (matpowerSystem + '.mat'))
			#normalizedLoadData = np.asarray(normalizedLoadData['my_data'])

		renewableGenIdx = renewableGenData['idx']
		renewableGenData = renewableGenData['data']

		numberOfGens = len(matpowerCaseStruct['gen'])
		for idx, genRow in enumerate(matpowerCaseStruct['gen']):
			if idx+1 in renewableGenIdx:
				for genLen in range(0, 288):
					if not genLen == 287:
						loadprofilererFile.write('{:0.2f} '.format(renewableGenData[np.where(renewableGenIdx[0] == idx+1)[0][0], genLen]))
					elif idx == numberOfGens-1:
						loadprofilererFile.write('{:0.2f}'.format(renewableGenData[np.where(renewableGenIdx[0] == idx+1)[0][0], genLen]))
					else:
						loadprofilererFile.write('{:0.2f}\n'.format(renewableGenData[np.where(renewableGenIdx[0] == idx+1)[0][0], genLen]))
			else:
				for genLen in range(0, 288):
					if not genLen == 287:
						loadprofilererFile.write('{:d} '.format(-1))
					elif idx == numberOfGens-1:
						loadprofilererFile.write('{:d}'.format(-1))
					else:
						loadprofilererFile.write('{:d}\n'.format(-1))

	else:
		# no profile available. We will disable any schedule
		numberOfGens = len(matpowerCaseStruct['gen'])
		for idx, genRow in enumerate(matpowerCaseStruct['gen']):
			for genLen in range(0, 288):
				if not genLen == 287:
					loadprofilererFile.write('{:d} '.format(-1))
				elif idx == numberOfGens-1:
					loadprofilererFile.write('{:d}'.format(-1))
				else:
					loadprofilererFile.write('{:d}\n'.format(-1))


	loadprofilerealFile.close()
	loadprofilereacFile.close()
	loadprofilererFile.close()

	if haveMATLAB is True:
		# close the matlab engine
		eng.quit()


	return populationDict


def pythonLoadMat(loadProfilePath):
	"""
	This funciton is used to load .mat files in python without using MATLAB

	Inputs
		loadProfilePath - path for the load profile file

	Outputs
		loadprofiles
	"""

	return sio.loadmat(loadProfilePath)


def pythonLoadCase(casePath):
	"""
	This funciton is used to load a MATPOWER case file without using MATLAB

	Inputs
		casePath - path for the MATPOWER case file

	Outputs
		matpowerCaseStruct - MATPOWER case struct
	"""

	# open the case file
	caseFile = open(casePath,'r')

	# parse the case file
	matpowerCaseStruct = {}
	while True:
		line = caseFile.readline()
		# print "line is -> ", line
		if not line:
			break
		elif line == '\n':
			continue
		else:
			splitLine = line.split()
			if splitLine[0] == 'function':
				matpowerCaseStruct['function'] = splitLine[3]
			elif splitLine[0] == 'mpc.version':
				matpowerCaseStruct['version'] = splitLine[2]
			elif splitLine[0] == 'mpc.baseMVA':
				matpowerCaseStruct['baseMVA'] = float(splitLine[2].strip(';'))
			elif splitLine[0] == 'mpc.bus':
				array = np.empty((0, 0))
				count = 0
				while True:
					newLine = caseFile.readline()
					if newLine.split()[0] == '];' or newLine.split()[0] == ']':
						matpowerCaseStruct['bus'] = np.reshape(array, [-1, numberCol]).astype(np.float)
						break
					elif count > 100000:
						raise Exception('not able to read the matpower case file format!')
					newLine = newLine.split(';', 1)[0] # remove comments if they are present
					newLine = newLine.split('%', 1)[0]  # remove comments if they are present
					array = np.append(array, newLine.split())
					numberCol = len(newLine.split())
					count += 1
			elif splitLine[0] == 'mpc.branch':
				array = np.empty((0, 0))
				count = 0
				while True:
					newLine = caseFile.readline()
					if newLine.split()[0] == '];' or newLine.split()[0] == ']':
						matpowerCaseStruct['branch'] = np.reshape(array, [-1, numberCol]).astype(np.float)
						break
					elif count > 100000:
						raise Exception('not able to read the matpower case file format!')
					newLine = newLine.split(';', 1)[0] # remove comments if they are present
					newLine = newLine.split('%', 1)[0]  # remove comments if they are present
					array = np.append(array, newLine.split())
					numberCol = len(newLine.split())
					count += 1
			elif splitLine[0] == 'mpc.gen':
				array = np.empty((0, 0))
				count = 0
				while True:
					newLine = caseFile.readline()
					if newLine.split()[0] == '];' or newLine.split()[0] == ']':
						matpowerCaseStruct['gen'] = np.reshape(array, [-1, numberCol]).astype(np.float)
						break
					elif count > 100000:
						raise Exception('not able to read the matpower case file format!')
					newLine = newLine.split(';', 1)[0] # remove comments if they are present
					newLine = newLine.split('%', 1)[0]  # remove comments if they are present
					array = np.append(array, newLine.split())
					numberCol = len(newLine.split())
					count += 1
			elif splitLine[0] == 'mpc.gencost':
				array = np.empty((0, 0))
				count = 0
				while True:
					newLine = caseFile.readline()
					if newLine.split()[0] == '];' or newLine.split()[0] == ']':
						matpowerCaseStruct['gencost'] = np.reshape(array, [-1, numberCol]).astype(np.float)
						break
					elif count > 100000:
						raise Exception('not able to read the matpower case file format!')
					newLine = newLine.split(';', 1)[0] # remove comments if they are present
					newLine = newLine.split('%', 1)[0]  # remove comments if they are present
					array = np.append(array, newLine.split())
					numberCol = len(newLine.split())
					count += 1
			elif splitLine[0] == 'mpc.region':
				array = np.empty((0, 0))
				count = 0
				while True:
					newLine = caseFile.readline()
					if newLine.split()[0] == '];' or newLine.split()[0] == ']':
						matpowerCaseStruct['region'] = np.reshape(array, [-1, numberCol]).astype(np.float)
						break
					elif count > 100000:
						raise Exception('not able to read the matpower case file format!')
					newLine = newLine.split(';', 1)[0] # remove comments if they are present
					newLine = newLine.split('%', 1)[0]  # remove comments if they are present
					array = np.append(array, newLine.split())
					numberCol = len(newLine.split())
					count += 1
			elif splitLine[0] == 'mpc.genfuel':
				array = []
				count = 0
				while True:
					newLine = caseFile.readline()
					if newLine.split()[0] == '};' or newLine.split()[0] == '}':
						matpowerCaseStruct['genfuel'] = array
						break
					elif count > 100000:
						raise Exception('not able to read the matpower case file format!')
					newLine = newLine.split(';', 1)[0] # remove comments if they are present
					newLine = newLine.split('%', 1)[0]  # remove comments if they are present
					array.append(newLine.split()[0])
					numberCol = len(newLine.split())
					count += 1
			elif splitLine[0] == 'mpc.governor':
				array = {}
				count = 0
				while True:
					newLine = caseFile.readline()
					if newLine.split()[0] == '};' or newLine.split()[0] == '}':
						matpowerCaseStruct['governor'] = array
						break
					elif count > 100000:
						raise Exception('not able to read the matpower case file format!')
					newLine = newLine.split(';', 1)[0] # remove comments if they are present
					newLine = newLine.split('%', 1)[0]  # remove comments if they are present
					array[newLine.split()[0]] = newLine.split()[1]
					numberCol = len(newLine.split())
					count += 1		

	caseFile.close()
	return matpowerCaseStruct


def pythonSaveCase(casePath, matpowerCaseStruct):
	"""
	This funciton is used to save a MATPOWER case file without using MATLAB

	Inputs
		casePath - path where you want to save the modified MATPOWER case file
		
		matpowerCaseStruct - MATPOWER case struct

	Outputs
		None
	"""

	# open the case file
	caseFile = open(casePath,'w')

	# write out the case file
	caseFile.write('function mpc = {:s}\n'.format(matpowerCaseStruct['function']))
	caseFile.write('% This is -> {:s}\n\n'.format(matpowerCaseStruct['function']))
	caseFile.write('%% MATPOWER Case Format : Version {:s}\n'.format(matpowerCaseStruct['version']))
	caseFile.write('mpc.version = {:s}\n\n'.format(matpowerCaseStruct['version']))
	caseFile.write('%%-----  Power Flow Data  -----%%\n%% system MVA base\n')
	caseFile.write('mpc.baseMVA = {:g};\n\n'.format(matpowerCaseStruct['baseMVA']))
	caseFile.write('%% bus data\n%	bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin\nmpc.bus = [\n')
	for row in matpowerCaseStruct['bus']:
		for data in row:
			caseFile.write('\t{:g}'.format(data))
		caseFile.write(';\n')
	caseFile.write('];\n\n')
	caseFile.write('%% generator data\n%	bus	Pg	Qg	Qmax	Qmin	Vg	mBase	status	Pmax	Pmin	Pc1	Pc2	Qc1min	Qc1max	Qc2min	Qc2max	ramp_agc	ramp_10	ramp_30	ramp_q	apf\nmpc.gen = [\n')
	for row in matpowerCaseStruct['gen']:
		for data in row:
			caseFile.write('\t{:g}'.format(data))
		caseFile.write(';\n')
	caseFile.write('];\n\n')
	caseFile.write('%% branch data\n%	fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax\nmpc.branch = [\n')
	for row in matpowerCaseStruct['branch']:
		for data in row:
			caseFile.write('\t{:g}'.format(data))
		caseFile.write(';\n')
	caseFile.write('];\n\n')
	caseFile.write('%%-----  OPF Data  -----%%\n%% generator cost data\n%	1	startup	shutdown	n	x1	y1	...	xn	yn\n%	2	startup	shutdown	n	c(n-1)	...	c0\nmpc.gencost = [\n')
	for row in matpowerCaseStruct['gencost']:
		for data in row:
			caseFile.write('\t{:g}'.format(data))
		caseFile.write(';\n')
	caseFile.write('];\n\n')

	if 'region' in matpowerCaseStruct:
		caseFile.write('%% region data\n%	bus region\nmpc.region = [\n')
		for row in matpowerCaseStruct['region']:
			for data in row:
				caseFile.write('\t{:g}'.format(data))
			caseFile.write(';\n')
		caseFile.write('];\n\n')

	if 'genfuel' in matpowerCaseStruct:
		caseFile.write('%% fuel type data\nmpc.genfuel = {\n')
		for row in matpowerCaseStruct['genfuel']:
			caseFile.write('\t{:s};\n'.format(row))
		caseFile.write('};\n\n')

	if 'governor' in matpowerCaseStruct:
		caseFile.write('%% governor data\nmpc.governor = {\n')
		for row in matpowerCaseStruct['governor']:
			caseFile.write('\t{:s}, {:s};\n'.format(row, matpowerCaseStruct['governor'][row]))
		caseFile.write('};\n\n')

	caseFile.close()

if __name__ == '__main__':
	pass		