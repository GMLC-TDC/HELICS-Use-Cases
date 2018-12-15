"""
This file contains functions to add FNCS configurations to the simulation

Created April 23, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""
import os
import pprint

def dso_fncs_config(selectedFeederDict):
	"""
	This function adds FNCS capabilities to the feeder in question

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
	substationBus = str(selectedFeederDict['substationBus'])

	# we only want the feeder number from the name
	feederNum = feederName.split('_')[-1]

	if not os.path.exists(experimentFilePath / experimentName / str('dso_bus_' + substationBus) / 'fncs.yaml'):
		file = open(experimentFilePath / experimentName / str('dso_bus_' + substationBus) / 'fncs.yaml','w')
		file.write('name: {:s}\n'.format(str('dso_bus_' + substationBus)))
		file.write('time_delta: 10s\n')
		file.write('broker: tcp://localhost:5570\n')
		file.write('values:\n')
		file.write('    {:s}:\n'.format('bus_' + substationBus + '_allocatedConsumption'))
		file.write('        topic: {:s}/{:s}\n'.format('matpower', 'DispLoad_B' + str(selectedFeederDict['substationBus'])))
		file.write('        default: 0\n')
		file.write('        type: double\n')
		file.write('        list: false\n')
		file.write('    {:s}:\n'.format('bus_' + substationBus + '_receivedLMP'))
		file.write('        topic: {:s}/{:s}\n'.format('matpower', 'LMP_B' + str(selectedFeederDict['substationBus'])))
		file.write('        default: 0\n')
		file.write('        type: double\n')
		file.write('        list: false\n')
		file.close()

		file = open(experimentFilePath / experimentName / 'matpower' / 'fncs.yaml', 'a')
		file.write('    {:s}:\n'.format('Bus_' + str(substationBus) + '_dispLoad'))
		file.write('        topic: {:s}/{:s}\n'.format('dso_bus_' + str(substationBus), 'maxDispLoad'))
		file.write('        default: 0\n')
		file.write('        type: double\n')
		file.write('        list: false\n')
		file.write('    {:s}:\n'.format('Bus_' + str(substationBus) + '_unrespLoad'))
		file.write('        topic: {:s}/{:s}\n'.format('dso_bus_' + str(substationBus), 'unresponsiveLoad'))
		file.write('        default: 0\n')
		file.write('        type: double\n')
		file.write('        list: false\n')
		file.write('    {:s}:\n'.format('Bus_' + str(substationBus) + '_dispLoadDemandCurve'))
		file.write('        topic: {:s}/{:s}\n'.format('dso_bus_' + str(substationBus), 'dispLoadDemandCurve'))
		file.write('        default: 0\n')
		file.write('        type: double\n')
		file.write('        list: false\n')
		file.close()


	file = open(experimentFilePath / experimentName / str('dso_bus_' + substationBus) / 'fncs.yaml','a')

	file.write('    {:s}:\n'.format('lse_bus_' + substationBus + '_feeder_' + feederNum + '_currUnresponsiveLoad'))
	file.write('        topic: {:s}/{:s}\n'.format('lse_bus_' + substationBus + '_feeder_' + feederNum, 'unresponsiveLoad'))
	file.write('        default: 0\n')
	file.write('        type: double\n')
	file.write('        list: false\n')
	file.write('    {:s}:\n'.format('lse_bus_' + substationBus + '_feeder_' + feederNum + '_MinMaxCumQuant'))
	file.write('        topic: {:s}/{:s}\n'.format('lse_bus_' + substationBus + '_feeder_' + feederNum, 'min-maxQbids'))
	file.write('        default: 0\n')
	file.write('        type: double\n')
	file.write('        list: false\n')
	file.write('    {:s}:\n'.format('lse_bus_' + substationBus + '_feeder_' + feederNum + '_mdCurveCoeff'))
	file.write('        topic: {:s}/{:s}\n'.format('lse_bus_' + substationBus + '_feeder_' + feederNum, 'dispLoadMarginalDemandCurve'))
	file.write('        default: 0\n')
	file.write('        type: double\n')
	file.write('        list: false\n')

	file.close()


def lse_fncs_config(feeder_dict, selectedFeederDict):
	"""
	This function adds FNCS capabilities to the feeder in question

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

	if not os.path.exists(experimentFilePath / experimentName / str('lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + feederNum) / 'fncs.yaml'):
		file = open(experimentFilePath / experimentName / str('lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + feederNum) / 'fncs.yaml','w')
		file.write('name: {:s}\n'.format(str('lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + feederNum)))
		file.write('time_delta: 5s\n')
		file.write('broker: tcp://localhost:5570\n')
		file.write('values:\n')
		file.close()

	file = open(experimentFilePath / experimentName / str('lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + feederNum) / 'fncs.yaml','a')
  # subscribing to the head-of-the-feeder total load
	file.write('    {:s}:\n'.format('feeder_' + feederNum + '_headLoad'))
	file.write('        topic: {:s}/{:s}\n'.format(feederName, 'distribution_load'))
	file.write('        default: 0\n')
	file.write('        type: double\n')
	file.write('        list: false\n')
	# subscribing to the corresponding DSO load allocation value
	file.write('    {:s}:\n'.format( 'dso_bus_' + str(selectedFeederDict['substationBus']) + '_allocatedConsumption'))
	file.write('        topic: {:s}/{:s}\n'.format('dso_bus_' + str(selectedFeederDict['substationBus']), 'lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + feederNum + '_allocatedConsumption'))
	file.write('        default: 0\n')
	file.write('        type: double\n')
	file.write('        list: false\n')
	# subscribing to the corresponding DSO locally calculated LMP value
	file.write('    {:s}:\n'.format( 'dso_bus_' + str(selectedFeederDict['substationBus']) + '_receivedLMP'))
	file.write('        topic: {:s}/{:s}\n'.format('dso_bus_' + str(selectedFeederDict['substationBus']), 'LMP'))
	file.write('        default: 0\n')
	file.write('        type: double\n')
	file.write('        list: false\n')
	# we also need to publish the bid price and quantity
	for x in feeder_dict:
		if 'object' in feeder_dict[x] and feeder_dict[x]['object'] == 'controller_ccsi':

			fncsName = 'feeder_' + feederName.split('_')[-1] + '_node_' + feeder_dict[x]['name'].split('_')[-2] + '_' + feeder_dict[x]['name'].split('_')[0]

			file.write('    {:s}:\n'.format(fncsName + '_bid_price'))
			file.write('        topic: {:s}/{:s}\n'.format(feederName, fncsName + '_bid_price'))
			file.write('        default: 0\n')
			file.write('        type: double\n')
			file.write('        list: false\n')
			file.write('    {:s}:\n'.format(fncsName + '_bid_quantity'))
			file.write('        topic: {:s}/{:s}\n'.format(feederName, fncsName + '_bid_quantity'))
			file.write('        default: 0\n')
			file.write('        type: double\n')
			file.write('        list: false\n')
			file.write('    {:s}:\n'.format(fncsName + '_actual_load'))
			file.write('        topic: {:s}/{:s}\n'.format(feederName, fncsName + '_actual_load'))
			file.write('        default: 0\n')
			file.write('        type: double\n')
			file.write('        list: false\n')

	file.close()


def residential_controllers_fncs_config(feeder_dict, selectedFeederDict, transactiveActive):
	"""
	This function adds FNCS capabilities to the feeder in question

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

	file = open(experimentFilePath / experimentName / feederName / 'fncs_configure.cfg', 'a')
	
	for x in list(feeder_dict.keys()):
		if 'object' in list(feeder_dict[x].keys()):
			if feeder_dict[x]['object'] == 'auction_ccsi':
				file.write('subscribe "precommit:{:s}.fixed_price <- {:s}";\n'.format(controlConfig['TSEmarketName'], 'lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + str(feederName.split('_')[-1]) + '/LMP'))
				break

	# we also need to publish the bid price and quantity
	for x in feeder_dict:
		if 'object' in feeder_dict[x] and feeder_dict[x]['object'] == 'controller_ccsi':

			fncsName = 'feeder_' + feederName.split('_')[-1] + '_node_' + feeder_dict[x]['name'].split('_')[-2] + '_' + feeder_dict[x]['name'].split('_')[0]
			#print(feederName)
			#print(feeder_dict[x]['name'])
			#print(fncsName)
			if transactiveActive:
				file.write('publish "commit:{:s}.bid_price -> {:s}; 0.0001";\n'.format(feeder_dict[x]['name'], fncsName + '_bid_price'))
				file.write('publish "commit:{:s}.bid_quantity -> {:s}; 0.0001";\n'.format(feeder_dict[x]['name'], fncsName + '_bid_quantity'))
			
			#file.write('publish "commit:{:s}.hvac_load -> {:s}; 0.0001";\n'.format(feeder_dict[x]['name'].strip('_controller'), fncsName + '_actual_load'))
			file.write('publish "commit:{:s}.hvac_load -> {:s}; 0.0001";\n'.format(feeder_dict[x]['parent'], fncsName + '_actual_load'))

	file.close()

if __name__ == '__main__':
	pass