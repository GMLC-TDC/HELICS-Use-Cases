
"""
This file contains functions to create HELICS config files for each simulator. This time with Transactive Enegy simulators
"""
##################################################################################################################
# Created October 20, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

# Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
# worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
# Government, including the right to distribute to other Government contractors.
##################################################################################################################

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

	#	dsoName = 'dsoBus' + str(selectedFeederDict['substationBus'])
	#lseName = 'lseBus' + str(selectedFeederDict['substationBus']) + 'Feeder' + feederNum
	#gldName = 'feeder' + feederNum

	# Add subscription per feeder
	for feeder in populationDict:
		gldName = populationDict[feeder]['desiredName']
		temp = {'key':  gldName + '/' + 'distLoad',
				'type': 'complex',
				'unit': 'MVA',
				'required': True}
		configData['subscriptions'].append(temp)

	# Add subscriptions per substation bus
	for bus in uniqueSubstationBus:
		dsoName = 'dsoBus' + str(bus)
		temp = {'key': dsoName + '/' + 'unRespLoad',
				'type': 'double',
				'unit': 'MW',
				'required': True}
		configData['subscriptions'].append(temp)

		temp = {'key': dsoName + '/' + 'maxQ',
				'type': 'double',
				'unit': 'MW',
				'required': True}
		configData['subscriptions'].append(temp)					

		temp = {'key': dsoName + '/' + 'demandCurve',
				'type': 'string',
				'unit': '',
				'required': True}
		configData['subscriptions'].append(temp)

	# Add publication per substation bus
	for bus in uniqueSubstationBus:
		temp = {'key': 'voltageB' + str(bus),
				'type': 'complex',
				'unit': 'V',
				'global': False}
		configData['publications'].append(temp)	

	# Add publication per substation bus
	for bus in uniqueSubstationBus:
		temp = {'key': 'dispLoadB' + str(bus),
				'type': 'double',
				'unit': 'MW',
				'global': False}
		configData['publications'].append(temp)

		temp = {'key': 'lmpB' + str(bus),
				'type': 'double',
				'unit': '$/MW',
				'global': False}
		configData['publications'].append(temp)					

	write_config(configData)


def dso_config(populationDict):
	"""
	This function adds HELICS capabilities to the dso in question

	Inputs
		populationDict - dictionary containing properties for the feeders we are using

	Outputs
		None

	"""

	experimentFilePath = populationDict[0]['experimentFilePath']
	experimentName = populationDict[0]['experimentName']
	useFlags = populationDict[0]['useFlags']

	# loop through the population dictionary to find unique substation buses
	uniqueSubstationBus = []
	for feeder in populationDict:
		if not populationDict[feeder]['substationBus'] in uniqueSubstationBus:
			uniqueSubstationBus.append(populationDict[feeder]['substationBus'])

	# for every substation bus we will create a DSO configuration
	for substationBus in uniqueSubstationBus:
		dsoName = 'dsoBus' + str(substationBus)

		# get a list of the LSEs attached to this DSO
		lseNames = []
		for feeder in populationDict:
			if populationDict[feeder]['substationBus'] == substationBus:
				lseNames.append('lseBus' + str(substationBus) + 'Feeder' + populationDict[feeder]['desiredName'].split('_')[-1])

		#print(lseNames)

		configData = dict()
		configData['outputFolder'] = experimentFilePath / experimentName / str('dso_bus_' + str(substationBus)) / 'helics.json'
		configData['name'] = dsoName
		configData['log_level'] = 2
		configData['observer'] = False
		configData['rollback'] =  False
		configData['only_update_on_change'] = False
		configData['only_transmit_on_change'] = False
		configData['source_only'] = False
		configData['uninterruptible'] = True
		configData['coreType'] = useFlags['core_type_HELICS']
		configData['coreName'] = ''
		if "mpi" in useFlags['core_type_HELICS']:
			configData['coreInit'] = '--broker_adress=0:0'
		else:
			configData['coreInit'] = '1'
		configData['maxIterations'] = 1
		configData['period'] =  10.0
		configData['offset'] =  0.0
		configData['timeDelta'] = 10.0
		configData['outputDelay'] = 0
		configData['inputDelay'] = 0

		configData['publications'] = []
		configData['subscriptions'] = []

		# subscribe to values from LSEs
		for lse in lseNames:
			# subscribe to LSE unresponsive load 
			temp = {'key': lse + '/' + 'unRespLoad',
					'type': 'double',
					'unit': 'MW',
					'required': True}
			configData['subscriptions'].append(temp)	

			# subscribe to the LSE min max quantity
			temp = {'key': lse + '/' + 'minMaxQ',
					'type': 'string',
					'unit': 'MW',
					'required': True}
			configData['subscriptions'].append(temp)	

			# subscribe to the LSE marginal demand curve
			temp = {'key': lse + '/' + 'demandCurve',
					'type': 'string ',
					'unit': '',
					'required': True}
			configData['subscriptions'].append(temp)	

		# subscribe to the matpower LMP 
		temp = {'key': 'matpower' + '/' + 'lmpB' + str(substationBus),
				'type': 'double',
				'unit': '$/MW',
				'required': True}
		configData['subscriptions'].append(temp)

		# subscribe to the matpower dispatchable load
		temp = {'key': 'matpower' + '/' + 'dispLoadB' + str(substationBus),
				'type': 'double',
				'unit': 'MW',
				'required': True}
		configData['subscriptions'].append(temp)	

		# publish values from each LSEs
		for lse in lseNames:
			# publish the DSO calculated dispatchable load
			temp = {'key': lse + '_dispLoad',
					'type': 'double',
					'unit': 'MW',
					'global': False}
			configData['publications'].append(temp)	

		# publish the DSO calculated lmp
		temp = {'key': 'lmp',
				'type': 'double',
				'unit': '$/MW',
				'global': False}
		configData['publications'].append(temp)	

		# publish the DSO unresponsive load 
		temp = {'key': 'unRespLoad',
				'type': 'double',
				'unit': 'MW',
				'global': False}
		configData['publications'].append(temp)	

		# publish the LSE max quantity
		temp = {'key': 'maxQ',
				'type': 'string',
				'unit': 'MW',
				'global': False}
		configData['publications'].append(temp)	

		# publish the DSO marginal demand curve
		temp = {'key': 'demandCurve',
				'type': 'string ',
				'unit': '',
				'global': False}
		configData['publications'].append(temp)	



		write_config(configData)


def lse_config(feeder_dict, selectedFeederDict):
	"""
	This function adds FNCS capabilities to the lse in question

	Inputs
		feeder_dict - dictionary containing the full feeder

		selectedFeederDict - dictionary containing properties for the feeders we are using

	Outputs

	"""

	# Get information about the co-sim we are working on
	feederConfig = selectedFeederDict['feederConfig']
	useFlags = selectedFeederDict['useFlags']
	controlConfig = selectedFeederDict['controlConfig']
	experimentFilePath = selectedFeederDict['experimentFilePath']
	experimentName = selectedFeederDict['experimentName']
	feederName = selectedFeederDict['desiredName']
	# we only want the feeder number from the name
	feederNum = feederName.split('_')[-1]

	dsoName = 'dsoBus' + str(selectedFeederDict['substationBus'])
	lseName = 'lseBus' + str(selectedFeederDict['substationBus']) + 'Feeder' + feederNum
	gldName = feederName

	if not os.path.exists(experimentFilePath / experimentName / str('lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + feederNum) / 'helics.json'):
		configData = dict()
		configData['outputFolder'] = experimentFilePath / experimentName / str('lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + feederNum) / 'helics.json'
		configData['name'] = lseName
		configData['log_level'] = 2
		configData['observer'] = False
		configData['rollback'] =  False
		configData['only_update_on_change'] = False
		configData['only_transmit_on_change'] = False
		configData['source_only'] = False
		configData['uninterruptible'] = True
		configData['coreType'] = useFlags['core_type_HELICS']
		configData['coreName'] = ''
		if "mpi" in useFlags['core_type_HELICS']:
			configData['coreInit'] = '--broker_adress=0:0'
		else:
			configData['coreInit'] = '1'
		configData['maxIterations'] = 1
		configData['period'] =  5.0
		configData['offset'] =  0.0
		configData['timeDelta'] = 5.0
		configData['outputDelay'] = 0
		configData['inputDelay'] = 0

		configData['publications'] = []
		configData['subscriptions'] = []

		# subscribing to the head-of-the-feeder total load
		temp = {'key': gldName + '/distLoad',
				'type': 'complex',
				'unit': 'VA',
				'required': True}
		configData['subscriptions'].append(temp)

		# subscribe to all the individual DER parameters
		for x in feeder_dict:
			if 'object' in feeder_dict[x] and feeder_dict[x]['object'] == 'controller_ccsi':

				derName = 'feeder_' + feederName.split('_')[-1] + '_node_' + feeder_dict[x]['name'].split('_')[-2] + '_' + feeder_dict[x]['name'].split('_')[0]

				temp = {'key': gldName + '/' + derName + '_bidP',
						'type': 'double',
						'unit': '$/MW',
						'required': True}
				configData['subscriptions'].append(temp)

				temp = {'key': gldName + '/' + derName + '_bidQ',
						'type': 'double',
						'unit': 'W',
						'required': True}
				configData['subscriptions'].append(temp)

				temp = {'key': gldName + '/' + derName + '_actualQ',
						'type': 'double',
						'unit': 'kW',
						'required': True}
				configData['subscriptions'].append(temp)

		# subscribing to the corresponding DSO load allocation value
		temp = {'key': dsoName + '/' + lseName + '_dispLoad',
				'type': 'double',
				'unit': 'MW',
				'required': True}
		configData['subscriptions'].append(temp)

		# subscribing to the corresponding DSO locally calculated LMP value
		temp = {'key': dsoName + '/' + 'lmp',
				'type': 'double',
				'unit': '$/MW',
				'required': True}
		configData['subscriptions'].append(temp)

		# publish the LSE calculated lmp
		temp = {'key': 'lmp',
				'type': 'double',
				'unit': '$/MW',
				'global': False}
		configData['publications'].append(temp)	

		# publish the LSE unresponsive load 
		temp = {'key': 'unRespLoad',
				'type': 'double',
				'unit': 'MW',
				'global': False}
		configData['publications'].append(temp)	

		# publish the LSE min max qunatity
		temp = {'key': 'minMaxQ',
				'type': 'string',
				'unit': 'MW',
				'global': False}
		configData['publications'].append(temp)	

		# publish the LSE marginal demand curve
		temp = {'key': 'demandCurve',
				'type': 'string ',
				'unit': '',
				'global': False}
		configData['publications'].append(temp)	

		write_config(configData)


def gridlabd_config(glmDict, selectedFeederDict, transactiveActive):
	"""
	This function adds HELICS capabilities to the feeder in question

	Inputs
		glmDict - dictionary of the feeder

		selectedFeederDict - settings for the specific feeder

		transactiveActive - add transactive control to the feeder
		
	Outputs
		glmDict - the modified feeder dictionary
	"""	

	# Get information about the co-sim we are working on
	feederConfig = selectedFeederDict['feederConfig']
	useFlags = selectedFeederDict['useFlags']
	controlConfig = selectedFeederDict['controlConfig']
	experimentFilePath = selectedFeederDict['experimentFilePath']
	experimentName = selectedFeederDict['experimentName']
	feederName = selectedFeederDict['desiredName']

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

	gldName = selectedFeederDict['desiredName']

	# add the fncs object
	glmDict[last_key] = {'object': 'helics_msg',
						 'name': '{:s}'.format(gldName),
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

	for x in list(glmDict.keys()):
		if 'object' in list(glmDict[x].keys()):
			if glmDict[x]['object'] == 'auction_ccsi':
				temp = {'key': 'lseBus' + str(selectedFeederDict['substationBus']) + 'Feeder' + str(feederName.split('_')[-1]) + '/lmp',
						'type': 'double',
						'unit': '$/MW',
						'required': True,
						'info': "{\"object\": \"" + controlConfig['TSEmarketName'] + "\", \"property\": \"fixed_price\"}"}
				configData['subscriptions'].append(temp)

	# we also need to publish the bid price, bid quantity, and actual load
	for x in glmDict:
		if 'object' in glmDict[x] and glmDict[x]['object'] == 'controller_ccsi':

			derName = 'feeder_' + feederName.split('_')[-1] + '_node_' + glmDict[x]['name'].split('_')[-2] + '_' + glmDict[x]['name'].split('_')[0]
			#print(feederName)
			#print(glmDict[x]['name'])
			#print(derName)
			if transactiveActive:
				temp = {'key': derName + '_bidP',
					'type': 'double',
					'unit': '$/MW',
					'global': False,
					'info': "{\"object\": \"" + glmDict[x]['name'] + "\", \"property\": \"bid_price\"}"} 
				configData['publications'].append(temp)
				temp = {'key': derName + '_bidQ',
					'type': 'double',
					'unit': 'W',
					'global': False,
					'info': "{\"object\": \"" + glmDict[x]['name'] + "\", \"property\": \"bid_quantity\"}"} 
				configData['publications'].append(temp)

			temp = {'key': derName + '_actualQ',
					'type': 'double',
					'unit': 'kW',
					'global': False,
					'info': "{\"object\": \"" + glmDict[x]['parent'] + "\", \"property\": \"hvac_load\"}"} 
			configData['publications'].append(temp)

	write_config(configData)

	return glmDict


if __name__ == '__main__':
	pass
