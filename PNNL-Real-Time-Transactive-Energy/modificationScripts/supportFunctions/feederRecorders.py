"""
This file contains a fuction to add recorders to a feeder based on the use flags defined

	add_recorders(recorder_dict, config_file, file_path, feeder_name, last_key=0):
		This fuction add recorders based on the configuration of the feeder


Created December 20, 2016 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2016 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""

import os, random

def add_recorders(recorder_dict, config_file, file_path, selectedFeederDict, last_key=0):	
	"""
	This fuction adds recorders based on the configuration of the feeder

	Inputs
		recorder_dict - dictionary containing the full feeder
		config_file - dictionary that contains the configurations of the feeder
		file_path - file path to where you created the modified GLM
		feeder_name - name of the feeder we are working with
		last_object_key - Last object key

	Outputs
		recorder_dict -  dictionary containing the full feeder
	"""

	# feeder and node number used as identifiers for the mysql.recorder 
	feeder_name=selectedFeederDict['desiredName']
	feeder_id=feeder_name.split("feeder_")[1]
	# if not a co-simulation then the node number for the mysql.recorder is defaulted to -1
	if ('substationBus' in selectedFeederDict):
		node=selectedFeederDict['substationBus']
	else:
		node=-1

	# Initialize psuedo-random seed
	random.seed(8)
    
    # determine if we need to create an output folder
	if not config_file['sequelLogging']:
		if not os.path.isdir(file_path / 'output'):
			os.makedirs(file_path / 'output')
			
    # Check if last_key is already in glm dictionary
	def unused_key(key):
		if key in recorder_dict:
			while key in recorder_dict:
				key += 1
		return key

	# let's determine the next available key
	last_key = unused_key(last_key)

	# flags to ensure we are not deploying recorders for technology that is not in the dictionary
	have_resp_zips = 0
	have_houses = 0
	have_res_houses = 0
	have_unresp_zips = 0
	have_waterheaters = 0
	have_auction = 0
	have_EVs = 0
	have_EBs = 0
	have_UEBs = 0
	have_ResourceControllers = 0
	swing_node = None
	climate_name = None
	regulator_parents = []
	regulator_names = []


	# min and max queue for mysql
	minSql = 2000
	maxSql = 4000

	for x in list(recorder_dict.keys()):
		if 'object' in list(recorder_dict[x].keys()):
			if recorder_dict[x]['object'] == 'transformer' and recorder_dict[x]['name'] == 'substation_transformer':
				swing_node = recorder_dict[x]['to']

			if recorder_dict[x]['object'] == 'house':
				have_houses = 1

			if recorder_dict[x]['object'] == 'climate':
				climate_name = recorder_dict[x]['name']

			if recorder_dict[x]['object'] == 'house':
				if 'groupid' in list(recorder_dict[x].keys()):
					if recorder_dict[x]['groupid'] == 'Residential':
						have_res_houses = 1

			if recorder_dict[x]['object'] == 'ZIPload':
				if 'groupid' in list(recorder_dict[x].keys()):
					if recorder_dict[x]['groupid'] == 'Responsive_load':
						have_resp_zips = 1

					if recorder_dict[x]['groupid'] == 'Unresponsive_load':
						have_unresp_zips = 1

			if recorder_dict[x]['object'] == 'waterheater':
				have_waterheaters = 1

			if recorder_dict[x]['object'] == 'auction_ccsi':
				have_auction = 1
				
			if recorder_dict[x]['object'] == 'evcharger_det':
				have_EVs = 1	

			if recorder_dict[x]['object'] == 'battery':
				if recorder_dict[x]['groupid'] == 'residential_storage':
					have_EBs = 1
				if recorder_dict[x]['groupid'] == 'utility_storage':
					have_UEBs = 1

			if recorder_dict[x]['object'] == 'regulator':
				regulator_parents.append(recorder_dict[x]['to'])
				regulator_names.append(recorder_dict[x]['name'])

			if recorder_dict[x]['object'] == 'resource_controller':
				have_ResourceControllers = 1


	# time to add those recorders
	if config_file['sequelLogging']:
		if 'VBM_calibration' in config_file['recorders']:
			if have_waterheaters == 1 and have_houses == 1 and climate_name != None and config_file['recorders']['VBM_calibration']:
				print('WARNING: not implemented yet')
			else:
				if config_file['recorders']['VBM_calibration']:
					print('You asked to record data for VBM calibration, however the dictionary did not meet the requirements for doing so')


		if 'responsive_load' in config_file['recorders']:
			if have_resp_zips == 1 and config_file['recorders']['responsive_load']:
				print('WARNING: not implemented yet')
			else:
				if config_file['recorders']['responsive_load']:
					print('You asked to record responsive zip load, however I did not find any in the dictionary')

		if 'unresponsive_load' in config_file['recorders']:
			if have_unresp_zips == 1 and config_file['recorders']['unresponsive_load']:
				print('WARNING: not implemented yet')
			else:
				if config_file['recorders']['unresponsive_load']:
					print('You asked to record non responsive zip load, however I did not find any in the dictionary')
		if 'water_heaters' in config_file['recorders']:
			if have_waterheaters == 1 and config_file['recorders']['water_heaters']:
				print('WARNING: not implemented yet')
			else:
				if config_file['recorders']['water_heaters']:
					print('You asked to record water heaters, however I did not find any in the dictionary')

		if 'swing_node' in config_file['recorders']:
			if config_file['recorders']['swing_node']:
				if swing_node is not None:
					recorder_dict[last_key] = {'object': 'mysql.recorder',
												'parent': '{:s}'.format(swing_node),
												'table': 'swing_node',
												'interval': '{:d}'.format(config_file['measure_interval']),
												'in': '"{:s}"'.format(config_file['record_in']),
												'out': '"{:s}"'.format(config_file['record_out']),
												'query_buffer_limit': '{:d}'.format(random.randint(minSql, maxSql)),	
												#'header_fieldnames': '"name"',
												'mode': '"a"',
												'with_primary_key': 'true',
												'minimize_data': 'true',
												'custom_sql': '"FID MEDIUMINT {:s}, NID SMALLINT {:d}"'.format(feeder_id,node),                                                            
												#'recorder_name': '"{:s}"'.format(feeder_name),
												'property': 'measured_current_A,measured_current_B,measured_current_C,measured_voltage_A,measured_voltage_B,measured_voltage_C,measured_power'}
												#'property': 'measured_current_A.real,measured_current_A.imag,measured_current_B.real,measured_current_B.imag,measured_current_C.real,measured_current_C.imag,measured_voltage_A.real,measured_voltage_A.imag,measured_voltage_B.real,measured_voltage_B.imag,measured_voltage_C.real,measured_voltage_C.imag,measured_real_power,measured_reactive_power'}

					last_key = unused_key(last_key)
				else:
					print('You asked to record the swing node, however I did not find any in the dictionary')

		if 'climate' in config_file['recorders']:
			if config_file['recorders']['climate']:
				if climate_name is not None:
					recorder_dict[last_key] = {'object': 'mysql.recorder',
											   'parent': '{:s}'.format(climate_name),
											   'table': 'climate',
											   'interval': '{:d}'.format(config_file['measure_interval']),
											   'in': '"{:s}"'.format(config_file['record_in']),
											   'out': '"{:s}"'.format(config_file['record_out']),
											   'query_buffer_limit': '{:d}'.format(random.randint(minSql, maxSql)),
											   #'header_fieldnames': '"name"',
											   'mode': '"a"',
											   'with_primary_key': 'true',
											   'minimize_data': 'true',
											   'custom_sql': '"FID MEDIUMINT {:s}, NID SMALLINT {:d}"'.format(feeder_id,node),                                                                             
											   #'recorder_name': '"{:s}"'.format(feeder_name),
											   'property': 'temperature,humidity'}
					last_key = unused_key(last_key)
				else:
					print('You asked to record the climate, however I did not find any in the dictionary')

		if 'HVAC' in config_file['recorders']:
			if have_res_houses == 1 and config_file['recorders']['HVAC']:
				recorder_dict[last_key] = {'object': 'mysql.recorder',
											   'group': '"class=house AND groupid=Residential"',
											   'table': 'residential_houses',
											   'interval': '{:d}'.format(config_file['measure_interval']),
											   'in': '"{:s}"'.format(config_file['record_in']),
											   'out': '"{:s}"'.format(config_file['record_out']),
											   'query_buffer_limit': '{:d}'.format(random.randint(minSql, maxSql)),
											   'header_fieldnames': '"name"',
											   'mode': '"a"',
											   'with_primary_key': 'true',
											   'minimize_data': 'true',
									           'custom_sql': '"FID MEDIUMINT {:s}, NID SMALLINT {:d}"'.format(feeder_id,node),                                                                             
											   #'recorder_name': '"{:s}"'.format(feeder_name),
											   'property': 'hvac_load,air_temperature'}
				last_key = unused_key(last_key)         
			else:
				if config_file['recorders']['HVAC']:
					print('You asked to record HVAC, however I did not find any in the dictionary')

		if 'load_composition' in config_file['recorders']:
			if config_file['recorders']['load_composition']:
				print('WARNING: not implemented yet')


		if 'customer_meter' in config_file['recorders']:
			if config_file['recorders']['customer_meter']:
				print('WARNING: not implemented yet')
				
		if 'voltage_regulators' in config_file['recorders']:
			if regulator_parents and config_file['recorders']['voltage_regulators']:
				for idx, regulator in enumerate(regulator_parents):
					print('WARNING: not implemented yet')

				for idx, regulator in enumerate(regulator_names):
					print('WARNING: not implemented yet')
			else:
				if config_file['recorders']['voltage_regulators']:
					print('You asked to record regulators, however I did not find any in the dictionary')

		if 'market' in config_file['recorders']:
			if have_auction == 1 and config_file['recorders']['market']:
				recorder_dict[last_key] = {'object': 'mysql.recorder',
											   'parent': 'retailMarket',
											   'table': 'retail_market',
											   'interval': '{:d}'.format(config_file['measure_interval']*10),
											   'in': '"{:s}"'.format(config_file['record_in']),
											   'out': '"{:s}"'.format(config_file['record_out']),
											   'query_buffer_limit': '{:d}'.format(random.randint(minSql, maxSql)),
											   #'header_fieldnames': '"name"',
											   'mode': '"a"',
											   'with_primary_key': 'true',
                                               'minimize_data': 'true',
                                               'custom_sql': '"FID MEDIUMINT {:s}, NID SMALLINT {:d}"'.format(feeder_id,node),                                                                             
											   #'recorder_name': '"{:s}"'.format(feeder_name),
											   'property': 'current_price_mean_24h,current_price_stdev_24h,fixed_price,market_id'}
				last_key = unused_key(last_key)
			else:
				if config_file['recorders']['market']:
					print('You asked to record auction, however I did not find any in the dictionary')

		if 'TSEControllers' in config_file['recorders']:
			if have_auction == 1 and config_file['recorders']['TSEControllers']:
				recorder_dict[last_key] = {'object': 'mysql.recorder',
											   'group': '"class=controller_ccsi"',
											   'table': 'transactive_controllers',
											   'interval': '{:d}'.format(config_file['measure_interval']*10),
											   'in': '"{:s}"'.format(config_file['record_in']),
											   'out': '"{:s}"'.format(config_file['record_out']),
											   'query_buffer_limit': '{:d}'.format(random.randint(minSql, maxSql)),
											   'header_fieldnames': '"name"',
											   'mode': '"a"',
											   'with_primary_key': 'true',
											   'minimize_data': 'true',
											   'custom_sql': '"FID MEDIUMINT {:s}, NID SMALLINT {:d}"'.format(feeder_id,node),                                                                             
											   #'recorder_name': '"{:s}"'.format(feeder_name),
											   'property': 'bid_quantity,bid_price'}
				last_key = unused_key(last_key)              	                  
			else:
				if config_file['recorders']['TSEControllers']:
					print('You asked to record TSE controllers, however I did not find any in the dictionary')



		if 'EVChargers' in config_file['recorders']:
			if have_EVs == 1 and config_file['recorders']['EVChargers']:
				print('WARNING: not implemented yet')
			else:
				if config_file['recorders']['EVChargers']:
					print('You asked to record EV chargers, however I did not find any in the dictionary')			
		

		if 'residentialStorage' in config_file['recorders']:
			if have_EBs == 1 and config_file['recorders']['residentialStorage']:
				print('WARNING: not implemented yet')
			else:
				if config_file['recorders']['residentialStorage']:
					print('You asked to record residential battery storage, however I did not find any in the dictionary')


		if 'utilityStorage' in config_file['recorders']:
			if have_UEBs == 1 and config_file['recorders']['utilityStorage']:
				print('WARNING: not implemented yet')
			else:
				if config_file['recorders']['utilityStorage']:
					print('You asked to record utility battery storage, however I did not find any in the dictionary')				

		
		if 'violationRecorder' in config_file['recorders']:
			if config_file['recorders']['violationRecorder']:
				print('WARNING: not implemented yet')


		if 'resourceControllers' in config_file['recorders']:
			if have_ResourceControllers == 1 and config_file['recorders']['resourceControllers']:
				print('WARNING: not implemented yet')

		else:
			if config_file['recorders']['resourceControllers']:
				print('You asked to record resource controllers, however I did not find any in the dictionary')	

	else:
		if 'VBM_calibration' in config_file['recorders']:
			if have_waterheaters == 1 and have_houses == 1 and climate_name != None and config_file['recorders']['VBM_calibration']:
				recorder_dict[last_key] = {'object': 'recorder',
										   'parent': '{:s}'.format(climate_name),
										   'file': 'output/{:s}_climate.csv'.format(feeder_name),
										   'interval': '60',
										   'property': 'temperature,humidity'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=waterheater"',
										   'file': 'output/{:s}_waterheater_temperature.csv'.format(feeder_name),
										   'interval': '60',
										   'property': 'temperature'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=waterheater"',
										   'file': 'output/{:s}_waterheater_actual_load.csv'.format(feeder_name),
										   'interval': '60',
										   'property': 'actual_load'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=waterheater"',
										   'file': 'output/{:s}_waterheater_is_waterheater_on.csv'.format(feeder_name),
										   'interval': '60',
										   'property': 'is_waterheater_on'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=waterheater"',
										   'file': 'output/{:s}_waterheater_water_demand.csv'.format(feeder_name),
										   'interval': '60',
										   'property': 'water_demand'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=house"',
										   'file': 'output/{:s}_residential_house_air_temperature.csv'.format(feeder_name),
										   'interval': '60',
										   'property': 'air_temperature'}
				last_key = unused_key(last_key)
				recorder_dict[last_key] = {'object': 'group_recorder',
									   	   'group': '"class=house"',
										   'file': 'output/{:s}_residential_house_hvac_load.csv'.format(feeder_name),
										   'interval': '60',
										   'property': 'hvac_load'}
				last_key = unused_key(last_key)

			else:
				if config_file['recorders']['VBM_calibration']:
					print('You asked to record data for VBM calibration, however the dictionary did not meet the requirements for doing so')


		if 'responsive_load' in config_file['recorders']:
			if have_resp_zips == 1 and config_file['recorders']['responsive_load']:
				recorder_dict[last_key] = {'object': 'collector',
										   'group': '"class=ZIPload AND groupid=Responsive_load"',
										   'file': 'output/{:s}_residential_responsive_load.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(base_power)'}
				last_key = unused_key(last_key)
			else:
				if config_file['recorders']['responsive_load']:
					print('You asked to record responsive zip load, however I did not find any in the dictionary')

		if 'unresponsive_load' in config_file['recorders']:
			if have_unresp_zips == 1 and config_file['recorders']['unresponsive_load']:
				recorder_dict[last_key] = {'object': 'collector',
										   'group': '"class=ZIPload AND groupid=Unresponsive_load"',
										   'file': 'output/{:s}_residential_unresponsive_load.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(base_power)'}
				last_key = unused_key(last_key)
			else:
				if config_file['recorders']['unresponsive_load']:
					print('You asked to record non responsive zip load, however I did not find any in the dictionary')
		if 'water_heaters' in config_file['recorders']:
			if have_waterheaters == 1 and config_file['recorders']['water_heaters']:
				# recorder_dict[last_key] = {'object': 'collector',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_total_load.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'sum(actual_load)'}
				# last_key = unused_key(last_key)
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=waterheater"',
										   'file': 'output/{:s}_waterheater_load.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'actual_load'}
				last_key = unused_key(last_key)
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=waterheater"',
										   'file': 'output/{:s}_waterheater_temperature.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'temperature'}
				last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_control_temperature.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'Tcontrol'}
				# last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_tank_setpoint.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'tank_setpoint'}
				# last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_thermostat_deadband.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'thermostat_deadband'}
				# last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_override.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 're_override'}
				# last_key = unused_key(last_key)
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=waterheater"',
										   'file': 'output/{:s}_waterheater_water_draw.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'water_demand'}
				last_key = unused_key(last_key)

				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_load_state.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'load_state'}
				# last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_thermo_height.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'height'}
				# last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_model.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'waterheater_model'}
				# last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_height.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'tank_height'}
				# last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=waterheater"',
				# 						   'file': 'output/{:s}_waterheater_tank_state.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'current_tank_status'}
				# last_key = unused_key(last_key)
			else:
				if config_file['recorders']['water_heaters']:
					print('You asked to record water heaters, however I did not find any in the dictionary')

		if 'swing_node' in config_file['recorders']:
			if config_file['recorders']['swing_node']:
				if swing_node is not None:
					recorder_dict[last_key] = {'object': 'recorder',
												'parent': '{:s}'.format(swing_node),
												'file': 'output/{:s}_swing_node.csv'.format(feeder_name),
												'interval': '{:d}'.format(config_file['measure_interval']),
												'in': '"{:s}"'.format(config_file['record_in']),
												'out': '"{:s}"'.format(config_file['record_out']),
												'property': 'measured_current_A,measured_current_B,measured_current_C,measured_voltage_A,measured_voltage_B,measured_voltage_C,measured_power'}
												#'property': 'measured_current_A.real,measured_current_A.imag,measured_current_B.real,measured_current_B.imag,measured_current_C.real,measured_current_C.imag,measured_voltage_A.real,measured_voltage_A.imag,measured_voltage_B.real,measured_voltage_B.imag,measured_voltage_C.real,measured_voltage_C.imag,measured_real_power,measured_reactive_power'}

					last_key = unused_key(last_key)
				else:
					print('You asked to record the swing node, however I did not find any in the dictionary')

		if 'climate' in config_file['recorders']:
			if config_file['recorders']['climate']:
				if climate_name is not None:
					recorder_dict[last_key] = {'object': 'recorder',
											   'parent': '{:s}'.format(climate_name),
											   'file': 'output/{:s}_climate.csv'.format(feeder_name),
											   'interval': '{:d}'.format(config_file['measure_interval']),
											   'in': '"{:s}"'.format(config_file['record_in']),
											   'out': '"{:s}"'.format(config_file['record_out']),
											   'property': 'temperature,humidity'}
					last_key = unused_key(last_key)
				else:
					print('You asked to record the climate, however I did not find any in the dictionary')

		if 'HVAC' in config_file['recorders']:
			if have_houses == 1 and config_file['recorders']['HVAC']:
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=house"',
										   'file': 'output/{:s}_residential_house_temperature.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'air_temperature'}
				last_key = unused_key(last_key)
				recorder_dict[last_key] = {'object': 'group_recorder',
									   	   'group': '"class=house"',
										   'file': 'output/{:s}_residential_HVAC_load.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'hvac_load'}
				last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=house"',
				# 						   'file': 'output/{:s}_residential_HVAC_heating_setpoint.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'heating_setpoint'}
				# last_key = unused_key(last_key)
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=house"',
										   'file': 'output/{:s}_residential_HVAC_cooling_setpoint.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'cooling_setpoint'}
				last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=house"',
				# 						   'file': 'output/{:s}_residential_HVAC_deadband.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 'thermostat_deadband'}
				# last_key = unused_key(last_key)
				# recorder_dict[last_key] = {'object': 'group_recorder',
				# 						   'group': '"class=house"',
				# 						   'file': 'output/{:s}_residential_HVAC_override.csv'.format(feeder_name),
				# 						   'interval': '{:d}'.format(config_file['measure_interval']),
				# 						   'in': '"{:s}"'.format(config_file['record_in']),
				# 						   'out': '"{:s}"'.format(config_file['record_out']),
				# 						   'property': 're_override'}
				# last_key = unused_key(last_key)

			else:
				if config_file['recorders']['HVAC']:
					print('You asked to record HVAC, however I did not find any in the dictionary')

		if 'load_composition' in config_file['recorders']:
			if config_file['recorders']['load_composition']:

				recorder_dict[last_key] = {'object': 'collector',
										   'group': 'class=triplex_meter AND groupid=Residential_Meter',
										   'file': 'output/{:s}_Residential_meter.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(measured_real_power)'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'collector',
										   'group': 'class=triplex_meter AND groupid=Commercial_Meter',
										   'file': 'output/{:s}_Commercial_meter.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(measured_real_power)'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'collector',
										   'group': 'class=house AND groupid=Residential',
										   'file': 'output/{:s}_Residential_building.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(total_load)'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'collector',
										   'group': 'class=house AND groupid=Commercial',
										   'file': 'output/{:s}_Commercial_building.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(total_load)'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'collector',
										   'group': 'class=house AND groupid=Residential',
										   'file': 'output/{:s}_Residential_hvac.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(hvac_load)'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'collector',
										   'group': 'class=house AND groupid=Commercial',
										   'file': 'output/{:s}_Commercial_hvac.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(hvac_load)'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'collector',
										   'group': 'class=ZIPload AND groupid=Residential_zip',
										   'file': 'output/{:s}_Residential_zip.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(actual_power.real)'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'collector',
										   'group': 'class=ZIPload AND groupid=Commercial_zip',
										   'file': 'output/{:s}_Commercial_zip.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(actual_power.real)'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'collector',
										   'group': 'class=waterheater AND groupid=water_heater',
										   'file': 'output/{:s}_Residential_water_heater.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'sum(actual_load)'}
				last_key = unused_key(last_key)

		if 'customer_meter' in config_file['recorders']:
			if config_file['recorders']['customer_meter']:

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"groupid=Residential_Meter"',
										   'file': 'output/{:s}_AMI_residential_phase12_power.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'measured_power'}
				last_key = unused_key(last_key)


				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"groupid=Residential_Meter"',
										   'file': 'output/{:s}_AMI_residential_phase12_voltage.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'voltage_12'}
				last_key = unused_key(last_key)

		if 'voltage_regulators' in config_file['recorders']:
			if regulator_parents and config_file['recorders']['voltage_regulators']:
				for idx, regulator in enumerate(regulator_parents):
					recorder_dict[last_key] = {'object': 'recorder',
											   'parent': '{:s}'.format(regulator),
											   'file': 'output/{:s}_regulator_{:d}_output.csv'.format(feeder_name, idx+1),
											   'interval': '{:d}'.format(config_file['measure_interval']),
											   'in': '"{:s}"'.format(config_file['record_in']),
											   'out': '"{:s}"'.format(config_file['record_out']),
											   #'property': 'voltage_A.real,voltage_A.imag,voltage_B.real,voltage_B.imag,voltage_C.real,voltage_C.imag'}
											   'property': 'voltage_A,voltage_B,voltage_C'}
					last_key = unused_key(last_key)

				for idx, regulator in enumerate(regulator_names):
					recorder_dict[last_key] = {'object': 'recorder',
											   'parent': '{:s}'.format(regulator),
											   'file': 'output/{:s}_regulator_{:d}_tab.csv'.format(feeder_name, idx + 1),
											   'interval': '{:d}'.format(config_file['measure_interval']),
											   'in': '"{:s}"'.format(config_file['record_in']),
											   'out': '"{:s}"'.format(config_file['record_out']),
											   'property': 'tap_A,tap_B,tap_C'}
					last_key = unused_key(last_key)
			else:
				if config_file['recorders']['voltage_regulators']:
					print('You asked to record regulators, however I did not find any in the dictionary')

		if 'market' in config_file['recorders']:
			if have_auction == 1 and config_file['recorders']['market']:
				recorder_dict[last_key] = {'object': 'recorder',
										   'parent': 'retailMarket',
										   'file': 'output/{:s}_retail_market.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'current_price_mean_24h,current_price_stdev_24h,fixed_price,market_id'}
				last_key = unused_key(last_key)
			else:
				if config_file['recorders']['market']:
					print('You asked to record auction, however I did not find any in the dictionary')

		if 'TSEControllers' in config_file['recorders']:
			if have_auction == 1 and config_file['recorders']['TSEControllers']:
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=controller_ccsi"',
										   'file': 'output/{:s}_controller_bid_price.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'bid_price'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=controller_ccsi"',
										   'file': 'output/{:s}_controller_bid_quantity.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'bid_quantity'}
				last_key = unused_key(last_key)

			else:
				if config_file['recorders']['TSEControllers']:
					print('You asked to record TSE controllers, however I did not find any in the dictionary')

		if 'EVChargers' in config_file['recorders']:
			if have_EVs == 1 and config_file['recorders']['EVChargers']:
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=evcharger_det"',
										   'file': 'output/{:s}_EV_battery_SOC.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'battery_SOC'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=evcharger_det"',
										   'file': 'output/{:s}_EV_charge_rate.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'charge_rate'}
				last_key = unused_key(last_key)
			else:
				if config_file['recorders']['EVChargers']:
					print('You asked to record EV chargers, however I did not find any in the dictionary')			
		

		if 'residentialStorage' in config_file['recorders']:
			if have_EBs == 1 and config_file['recorders']['residentialStorage']:
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"groupid=residential_storage"',
										   'file': 'output/{:s}_residential_storage_SOC.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'state_of_charge'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"groupid=residential_storage"',
										   'file': 'output/{:s}_residential_storage_power.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'battery_load'}
				last_key = unused_key(last_key)
			else:
				if config_file['recorders']['residentialStorage']:
					print('You asked to record residential battery storage, however I did not find any in the dictionary')


		if 'utilityStorage' in config_file['recorders']:
			if have_UEBs == 1 and config_file['recorders']['utilityStorage']:
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"groupid=utility_storage"',
										   'file': 'output/{:s}_utility_storage_SOC.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'state_of_charge'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"groupid=utility_storage"',
										   'file': 'output/{:s}_utility_storage_power.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'battery_load'}
				last_key = unused_key(last_key)
			else:
				if config_file['recorders']['utilityStorage']:
					print('You asked to record utility battery storage, however I did not find any in the dictionary')				

		
		if 'violationRecorder' in config_file['recorders']:
			if config_file['recorders']['violationRecorder']:
				recorder_dict[last_key] = {'object': 'violation_recorder',
										   'violation_flag': 'ALLVIOLATIONS',
										   'strict': 'false',
										   'echo': 'false',
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'summary': 'output/{:s}_violation_summary.csv'.format(feeder_name),
										   'file': 'output/{:s}_violation_log.csv'.format(feeder_name),

									       # Violation 1 - Exceeding device thermal limit
									       'line_thermal_limit_lower': '0',
									       'line_thermal_limit_upper': '1',
									       'xfrmr_thermal_limit_lower': '0',
									       'xfrmr_thermal_limit_upper': '2',
									      
									       # Violation 2 - Instantaneous voltage of node over X pu
									       'node_instantaneous_voltage_limit_lower': '0.94',
									       'node_instantaneous_voltage_limit_upper': '1.06',
									      
									       # Violation 3 - Voltage of node over X pu or under Y pu for Z minutes or more
									       'node_continuous_voltage_limit_lower': '0.96',
									       'node_continuous_voltage_limit_upper': '1.04',
									       'node_continuous_voltage_interval': '300',
									      
									       # Violation 4 / 5 - Reverse power exceeds 50% / 75% of the minimum trip setting of the substation breaker (fuse) or a recloser
									       'substation_breaker_A_limit': '480',
									       'substation_breaker_B_limit': '480',
									       'substation_breaker_C_limit': '480',
									       'virtual_substation': '{:s}'.format(swing_node),
									      
									       # Violation 6 - Any voltage change at a PV POC that is greater than X % between two Y-minute simulation time-steps
									       'inverter_v_chng_per_interval_lower_bound': '-0.025',
									       'inverter_v_chng_per_interval_upper_bound': '0.025',
									       'inverter_v_chng_interval': '60',
									      
									       # Violation 7 - X V (%) rise/fall across the secondary distribution system
									       'secondary_dist_voltage_rise_lower_limit': '-0.030',
									       'secondary_dist_voltage_rise_upper_limit': '0.030',

									  	   # Violation 8 - Power factor limits
									       'substation_pf_lower_limit': '0.85',

										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out'])}

				last_key = unused_key(last_key)


		if 'resourceControllers' in config_file['recorders']:
			if have_ResourceControllers == 1 and config_file['recorders']['resourceControllers']:
				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_response.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'response_signal'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_regulation.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'regulation_signal'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_ramping.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'ramping_signal'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_tracking_signal.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'tracking_signal'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_device_consumption.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'device_consumption'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_device_command.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'device_command'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_device_status.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'device_status'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_service_category.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'service_category'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_threshold_up.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'threshold_up'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_threshold_down.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'threshold_down'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_control_status.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'control_status'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_service_multiplier.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'service_multiplier'}
				last_key = unused_key(last_key)

				recorder_dict[last_key] = {'object': 'group_recorder',
										   'group': '"class=resource_controller"',
										   'file': 'output/{:s}_RC_status_change_time.csv'.format(feeder_name),
										   'interval': '{:d}'.format(config_file['measure_interval']),
										   'in': '"{:s}"'.format(config_file['record_in']),
										   'out': '"{:s}"'.format(config_file['record_out']),
										   'property': 'status_change_time'}
				last_key = unused_key(last_key)

		else:
			if config_file['recorders']['resourceControllers']:
				print('You asked to record resource controllers, however I did not find any in the dictionary')	

	return recorder_dict

if __name__ == '__main__':
	pass
