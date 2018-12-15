
"""
This file contains functions to create HELICS config files for each simulator

Created October 20, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""

import os, json

def write_config(configString):
	"""
	This function writes the HELICS configuration file to disk
	Inputs
		configString - Python dictionary that hold the JSON config information to write to disk
	Outputs
		None
	"""	

	# the config dictionary contains the output folder. THis will read it and the delete as it should not be part of the config
	outFolder = configString['outputFolder']
	del configString['outputFolder']

	# write the JSON config to disk
	with open(outFolder, 'w') as outfile:
	    json.dump(configString, outfile, ensure_ascii=False, indent = 4)


def gridlabd_config(glmDict, selectedFeederDict):
	"""
	This function adds HELICS capabilities to the feeder in question

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

	useFlags = selectedFeederDict['useFlags']

	# add the connection module to our file
	glmDict[last_key] = {'module': 'connection',
						 'security': 'STANDARD',
						 'lockout': '1 min'}

	last_key = unused_key(last_key)

	# add the fncs object
	glmDict[last_key] = {'object': 'helics_msg',
						 'name': '{:s}'.format(selectedFeederDict['desiredName']),
						 'configure': 'helics.json'}

	configData = dict()
	configData['outputFolder'] = selectedFeederDict['experimentFilePath'] / selectedFeederDict['experimentName'] / selectedFeederDict['desiredName'] / 'helics.json'
	configData['name'] = selectedFeederDict['desiredName']
	configData['log_level'] = 2
	configData['observer'] = False
	configData['rollback'] =  False
	configData['only_update_on_change'] = False
	configData['only_transmit_on_change'] = False
	configData['source_only'] = False
	configData['uninterruptible'] = False
	configData['coreType'] = useFlags['core_type_HELICS']
	configData['coreName'] = ''
	if "mpi" in useFlags['core_type_HELICS']:
		configData['coreInit'] = '--broker_adress=0:0'
	else:
		configData['coreInit'] = '1'
	configData['maxIterations'] = 1
	configData['period'] =  1.0
	configData['offset'] =  0.0
	configData['timeDelta'] = 1.0
	configData['outputDelay'] = 0
	configData['inputDelay'] = 0

	configData['publications'] = []
	configData['subscriptions'] = []

	temp = {'key': 'matpower/voltageB' + str(selectedFeederDict['substationBus']),
			'type': 'complex',
			'unit': 'V',
			'required': True,
			'info': "{\"object\": \"network_node\", \"property\": \"positive_sequence_voltage\"}"}
	configData['subscriptions'].append(temp)

	temp = {'key': 'distLoad',
			'type': 'complex',
			'unit': 'VA',
			'global': False,
			'info': "{\"object\": \"network_node\", \"property\": \"distribution_load\"}"}
	configData['publications'].append(temp)	

	write_config(configData)

	return glmDict


def matpower_config(populationDict, transmissionDict):
	"""
	This function adds HELICS capabilities to matpower
	Inputs
		populationDict - dictionary containing properties for all the feeders we are using
		transmissionDict - - dictionary containing properties for the transmission system we are using
	Outputs
		None
	"""	

	experimentFilePath = populationDict[0]['experimentFilePath']
	experimentName = populationDict[0]['experimentName']
	useFlags = populationDict[0]['useFlags']
	matpowerPFTime = transmissionDict['matpowerPFTime']


	# loop through the population dictionary to find unique substation buses
	uniqueSubstationBus = []
	for feeder in populationDict:
		if not populationDict[feeder]['substationBus'] in uniqueSubstationBus:
			uniqueSubstationBus.append(populationDict[feeder]['substationBus'])

	# we also need to create the json file for the matpower simulator
	configData = dict()
	configData['outputFolder'] = experimentFilePath / experimentName / 'matpower' / 'helics.json'
	configData['name'] = 'matpower'
	configData['log_level'] = 2
	configData['observer'] = False
	configData['rollback'] =  False
	configData['only_update_on_change'] = False
	configData['only_transmit_on_change'] = False
	configData['source_only'] = False
	configData['uninterruptible'] = False
	configData['coreType'] = useFlags['core_type_HELICS']
	configData['coreName'] = ''
	if "mpi" in useFlags['core_type_HELICS']:
		configData['coreInit'] = '--broker_adress=0:0'
	else:
		configData['coreInit'] = '1'
	configData['maxIterations'] = 1
	configData['period'] =  15.0
	configData['offset'] =  0.0
	configData['timeDelta'] = 15.0
	configData['outputDelay'] = 0
	configData['inputDelay'] = 0

	configData['publications'] = []
	configData['subscriptions'] = []

	# loop through all feeders and add subscriptions for feeder load
	for feeder in populationDict:
		temp = {'key':  populationDict[feeder]['desiredName'] + '/distLoad',
				'type': 'complex',
				'unit': 'VA',
				'required': True}
		configData['subscriptions'].append(temp)

	# loop through all unique substation busses to add publications
	for bus in uniqueSubstationBus:
		temp = {'key': 'voltageB' + str(bus),
				'type': 'complex',
				'unit': 'V',
				'global': False}
		configData['publications'].append(temp)	
	
	write_config(configData)
