"""
This file contains functions to add Transactive Control to the simulation
"""
##################################################################################################################
# Created April 23, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

# Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
# worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
# Government, including the right to distribute to other Government contractors.
##################################################################################################################

import random, os


def add_dso(selectedFeederDict):
	"""
	This function adds DSO capabilities to the simulation in question

	Inputs
		selectedFeederDict - dictionary containing properties for feeders we are using

	Outputs
		None

	"""	
	# Get information about the co-sim we are working on
	feederConfig = selectedFeederDict['feederConfig']
	useFlags = selectedFeederDict['useFlags']
	controlConfig = selectedFeederDict['controlConfig']
	experimentFilePath = selectedFeederDict['experimentFilePath']
	experimentName = selectedFeederDict['experimentName']
	feederName = selectedFeederDict['desiredName']
	substationBus = str(selectedFeederDict['substationBus'])

	if not os.path.isdir(experimentFilePath / experimentName / str('dso_bus_' + substationBus)):
		os.makedirs(experimentFilePath / experimentName / str('dso_bus_' + substationBus))
		file = open(experimentFilePath / experimentName / str('dso_bus_' + substationBus) / 'feeder_list.txt','w')
		file.write('List of feeders attached to DSO:\n')
		file.write('{:s}\n'.format(feederName))
		file.close()
	else:
		file = open(experimentFilePath / experimentName / str('dso_bus_' + substationBus) / 'feeder_list.txt','a')
		file.write('{:s}\n'.format(feederName))
		file.close()				


def add_lse(selectedFeederDict):
	"""
	This function adds LSE capabilities to the simulation in question

	Inputs
		selectedFeederDict - dictionary containing properties for feeders we are using

	Outputs
		None

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

	if not os.path.isdir(experimentFilePath / experimentName / str('lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + feederNum)):
		os.makedirs(experimentFilePath / experimentName / str('lse_bus_' + str(selectedFeederDict['substationBus']) + '_feeder_' + feederNum))		


def add_residential_controller(feeder_dict, selectedFeederDict, last_key=0):
	"""
	This function adds residential controllers based on the configuration of the feeder

	Inputs
		feeder_dict - dictionary containing the full feeder

		selectedFeederDict - settings for the specific feeder
		
		last_object_key - Last object key

	Outputs
		feeder_dict -  dictionary containing the full feeder
	"""

	# Get information about the co-sim we are working on
	feederConfig = selectedFeederDict['feederConfig']
	useFlags = selectedFeederDict['useFlags']
	controlConfig = selectedFeederDict['controlConfig']


	# let's check that the control mode specified by the user makes sense.
	if not (useFlags['house_thermostat_mode'] == 'HEAT' or useFlags['house_thermostat_mode'] == 'COOL'):
		print ('WARNING: control mode is ill defined. These controllers will only work with either cooling or heating! -> ', useFlags['house_thermostat_mode'])

	# Check if last_key is already in glm dictionary
	def unused_key(key):
		if key in feeder_dict:
			while key in feeder_dict:
				key += 1
		return key

	# let's determine the next available key
	last_key = unused_key(last_key)

	# loop through the feeder dictionary to find residential houses that we can attach controllers to
	controllerDict = {}
	counter = 0
	for x in feeder_dict:
		if 'object' in feeder_dict[x] and feeder_dict[x]['object'] == 'house' and feeder_dict[x]['groupid'] == 'Residential':
			# if we are in heating mode we need to ensure that
			if (useFlags['house_thermostat_mode'] == 'HEAT' and feeder_dict[x]['heating_system_type'] != 'GAS') or (useFlags['house_thermostat_mode'] == 'COOL' and feeder_dict[x]['cooling_system_type'] != 'NONE'):
				controllerDict[counter] = {'parent' : '{:s}'.format(feeder_dict[x]['name']),
										   'name': '{:s}_controller'.format(feeder_dict[x]['name']),
										   'schedule_skew': '{:s}'.format(feeder_dict[x]['schedule_skew']),
										   'heating_setpoint': '{:s}'.format(feeder_dict[x]['heating_setpoint']),
										   'cooling_setpoint': '{:s}'.format(feeder_dict[x]['cooling_setpoint']),}

				if useFlags['house_thermostat_mode'] == 'COOL': # very important to remove the cooling setpoint from the house! it will not be handled by the controller
					del feeder_dict[x]['cooling_setpoint']
				elif useFlags['house_thermostat_mode'] == 'HEAT': # very important to remove the heating setpoint from the house! it will not be handled by the controller
					del feeder_dict[x]['heating_setpoint']

				counter += 1
			# else:
				# print "we passed on controller -> ", feeder_dict[x]['name']


	if controllerDict:
		# Add class auction to dictionary
		feeder_dict[last_key] = {'class': 'auction_ccsi',
								 'variable_types': ['double', 'double'],
								 'variable_names': ['current_price_mean_{:.0f}h'.format(controlConfig['TSEauctionStatistics']), 'current_price_stdev_{:.0f}h'.format(controlConfig['TSEauctionStatistics'])]}

		# let's determine the next available key
		last_key = unused_key(last_key)

		# Add object auction to dictionary
		feeder_dict[last_key] = {'object': 'auction_ccsi',
								 'name': "{:s}".format(controlConfig['TSEmarketName']),
								 'unit': "{:s}".format(controlConfig['TSEmarketUnit']),
								 'period': "{:.0f}".format(controlConfig['TSEmarketPeriod']),
								 'special_mode': 'BUYERS_ONLY',
								 'init_price': '{:.2f}'.format(controlConfig['TSEinitPrice']),
								 'init_stdev': '{:.2f}'.format(controlConfig['TSEinitStdev']),
								 'price_cap': '{:.2f}'.format(controlConfig['TSEpriceCap']),
								 'use_future_mean_price': '{:s}'.format(controlConfig['TSEuseFutureMeanPrice']),
								 'warmup': '{:.0f}'.format(controlConfig['TSEwarmUp'])}

		# let's determine the next available key
		last_key = unused_key(last_key)

	# now we just need to add the controllers
	for x in controllerDict:
		# limit slider randomization to Olypen style
		## slider = random.normalvariate(0.45, 0.2)
		slider = random.normalvariate(0.6, 0.2)
		if slider > controlConfig['TSEsliderSetting']:
			slider = controlConfig['TSEsliderSetting']
		if slider < 0:
			#slider = 0
			slider = 0.1

		# set the pre-cool / pre-heat xrange to really small
		# to get rid of it.
		s_rampstat = 2
		s_rangestat = 5
		#s_rampstat = 2.1
		#s_rangestat = 10

		hrh = s_rangestat - s_rangestat * (1 - slider)
		crh = s_rangestat - s_rangestat * (1 - slider)
		hrl = -s_rangestat - s_rangestat * (1 - slider)
		crl = -s_rangestat + s_rangestat * (1 - slider)

		hrh2 = -s_rampstat - (1 - slider)
		crh2 = s_rampstat + (1 - slider)
		hrl2 = -s_rampstat - (1 - slider)
		crl2 = s_rampstat + (1 - slider)

		feeder_dict[last_key] = {'object': 'controller_ccsi',
									'name': '{:s}'.format(controllerDict[x]['name']),
									'parent': '{:s}'.format(controllerDict[x]['parent']),
									'schedule_skew': '{:s}'.format(controllerDict[x]['schedule_skew']),
									'market': '{:s}'.format(controlConfig['TSEmarketName']),
									'bid_mode': '{:s}'.format(controlConfig['TSEbidMode']),
								    'bid_delay': '{:d}'.format(controlConfig['TSEbidDelay']),
									'control_mode': '{:s}'.format(controlConfig['TSEcontrolTechnology']),
									'resolve_mode': '{:s}'.format(controlConfig['TSEresolveMode']),
									'period': '{:.0f}'.format(controlConfig['TSEmarketPeriod']),
									'average_target': 'current_price_mean_{:.0f}h'.format(controlConfig['TSEauctionStatistics']),
									'standard_deviation_target': 'current_price_stdev_{:.0f}h'.format(controlConfig['TSEauctionStatistics']),
									'target': 'air_temperature',
									'deadband': 'thermostat_deadband',
									'total': 'total_load',
									'load': 'hvac_load',
									'state': 'power_state'}

		# if we are in heating mode
		if useFlags['house_thermostat_mode'] == 'HEAT':
			feeder_dict[last_key]['range_high'] = hrh
			feeder_dict[last_key]['range_low'] = hrl
			feeder_dict[last_key]['ramp_high'] = hrh2
			feeder_dict[last_key]['ramp_low'] = hrl2
			feeder_dict[last_key]['base_setpoint'] = controllerDict[x]['heating_setpoint']
			feeder_dict[last_key]['setpoint'] = 'heating_setpoint'
			feeder_dict[last_key]['demand'] = 'last_heating_load' # rated_heating_demand' # could also use last_heating_load

		# if we are in cooling mode
		if useFlags['house_thermostat_mode'] == 'COOL':
			feeder_dict[last_key]['range_high'] = crh
			feeder_dict[last_key]['range_low'] = crl
			feeder_dict[last_key]['ramp_high'] = crh2
			feeder_dict[last_key]['ramp_low'] = crl2
			feeder_dict[last_key]['base_setpoint'] = controllerDict[x]['cooling_setpoint']
			feeder_dict[last_key]['setpoint'] = 'cooling_setpoint'
			feeder_dict[last_key]['demand'] = 'last_cooling_load' # rated_cooling_demand'  # could also use last_cooling_load

		if feederConfig['short_names']:
			feeder_dict[last_key]['name'] = '{:s}_c'.format(feeder_dict[last_key]['parent'])

		# find the next available key
		last_key = unused_key(last_key)

	return feeder_dict

if __name__ == '__main__':
	pass