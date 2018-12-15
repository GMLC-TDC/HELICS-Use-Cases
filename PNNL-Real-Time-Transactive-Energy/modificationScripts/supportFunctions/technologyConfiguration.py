"""
This file contains functions to define user specifications for feeder models

	technologyConfiguration():
		Creates the complete configuration dictionary needed to populate the feeder

Modified April 11, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)
Created December 20, 2016 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2016 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""




def technologyConfiguration(use_flags=0):
	"""
	Creates the specific settings for each feeder needed to populate the feeder

	Inputs
		feederName - name of the specific feeder we are working on
	Outputs
		data - dictionary with full configuration specifications
	"""
	if use_flags == 0:
		use_flags = dict()


	# Specific flags for what technology you want implemented (these are meant as defaults and should be modified from main script)
	if 'use_homes' not in use_flags:
		use_flags["use_homes"] = 1			# 0= no homes, 1= individual homes, 2= normalized load shapes
	
	if 'use_commercial' not in use_flags:
		use_flags["use_commercial"] = 1		# 0= no commercial, 1= individual commercial, 2= normalized load shapes

	if 'use_electric_vehicles' not in use_flags:
		use_flags["use_electric_vehicles"] = 0			# add Electric vehicles to the simulation

	if 'use_residential_storage' not in use_flags:
		use_flags["use_residential_storage"] = 0	# add battery storage at the residential level

	if 'use_utility_storage' not in use_flags:
		use_flags["use_utility_storage"] = 0	# add battery storage at the residential level

	if 'use_schedules' not in use_flags:
		use_flags["use_schedules"] = 1 				# ALWAYS keep at 1 unless you know what you are doing!!

	if 'use_FNCS' not in use_flags:
		use_flags['use_FNCS'] = 0 					# if true the connection module will be added

	if 'use_HELICS' not in use_flags:
		use_flags['use_HELICS'] = 0 					# determine the core type used in HELICS, defaults to ZMQn module will be added	

	if 'core_type_HELICS' not in use_flags:
		use_flags['core_type_HELICS'] = 'zmq' 					# if true the connection module will be added		

	if 'house_thermostat_mode' not in use_flags:
		use_flags['house_thermostat_mode'] = 'AUTO'  	# setting to specify how house thermostats should behave, 'COOL', 'HEAT', 'AUTO'

	if 'add_nodes_control' not in use_flags:
		use_flags['add_nodes_control'] = 0  	# by default we will not use the nodes control

	if 'add_real_time_transactive_control' not in use_flags:
		use_flags['add_real_time_transactive_control'] = 0  	# by default we will not use the nodes control

	return use_flags


if __name__ == '__main__':
	pass
