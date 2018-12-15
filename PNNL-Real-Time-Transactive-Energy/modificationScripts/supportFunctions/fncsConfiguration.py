
"""
This file contains functions to create FNCS config files for each simulator

Created April 16, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""

import os

def gridlabd_fncs_config(glmDict, selectedFeederDict):
	"""
	This function adds FNCS capabilities to the feeder in question

	Inputs
		glmDict - dictionary of the feeder
		selectedFeederDict - settings for the specific feeder
	Outputs
		glmDict - the modified feeder dictionary
	"""	

	# Check if last_key is already in glm dictionary
	def unused_key(key):
		if key in glmDict:
			while key in glmDict:
				key += 1
		return key

	# let's determine the next available key
	last_key = unused_key(0)

	# add the connection module to our file
	glmDict[last_key] = {'module': 'connection',
						 'security': 'STANDARD',
						 'lockout': '1 min'}

	last_key = unused_key(last_key)

	# add the fncs object
	glmDict[last_key] = {'object': 'fncs_msg',
						 'name': '{:s}'.format(selectedFeederDict['desiredName']),
						 'configure': 'fncs_configure.cfg'}

	configFilePath = selectedFeederDict['experimentFilePath'] / selectedFeederDict['experimentName'] / selectedFeederDict['desiredName']

	# create the fncs configure file
	if not os.path.exists(configFilePath / 'fncs_configure.cfg'):
		fncsFile = open(configFilePath / 'fncs_configure.cfg', 'w')
		fncsFile.write('option "transport:hostname localhost, port 5570";\n')
		fncsFile.close()
	
	fncsFile = open(configFilePath / 'fncs_configure.cfg', 'a')
	#fncsFile.write('publish "commit:network_node.distribution_load -> distribution_load; 20000";\n')
	fncsFile.write('publish "commit:network_node.distribution_load -> distribution_load";\n')
	fncsFile.write('subscribe "precommit:network_node.positive_sequence_voltage <- matpower/three_phase_voltage_B{:s}";\n'.format(str(selectedFeederDict['substationBus'])))
	fncsFile.close()

	return glmDict


def matpower_fncs_config(populationDict, transmissionDict):
	"""
	This function adds FNCS capabilities to matpower
	Inputs
		populationDict - dictionary containing properties for all the feeders we are using
		transmissionDict - - dictionary containing properties for the transmission system we are using
	Outputs
		None
	"""	

	experimentFilePath = populationDict[0]['experimentFilePath']
	experimentName = populationDict[0]['experimentName']
	matpowerPFTime = transmissionDict['matpowerPFTime']

	# we also need to create the yaml file for the matpower simulator
	matpowerFNCSConfigFile = open(experimentFilePath / experimentName / 'matpower' / 'fncs.yaml', 'w')

	# create the header for the file
	matpowerFNCSConfigFile.write('name: matpower\n')
	matpowerFNCSConfigFile.write('time_delta: {:d}s\n'.format(int(matpowerPFTime)))
	matpowerFNCSConfigFile.write('broker: tcp://localhost:5570\n')
	matpowerFNCSConfigFile.write('values:\n')

	# loop through the population dictionary and start placing the distribution systems
	for idx, feeder in enumerate(populationDict):
		matpowerFNCSConfigFile.write('    {:s}:\n'.format(populationDict[feeder]['desiredName']))
		matpowerFNCSConfigFile.write('        topic: {:s}/distribution_load\n'.format(populationDict[feeder]['desiredName']))
		matpowerFNCSConfigFile.write('        default: 0 + 0 j MVA\n')
		matpowerFNCSConfigFile.write('        type: complex\n')
		matpowerFNCSConfigFile.write('        list: false\n')

	matpowerFNCSConfigFile.close()
