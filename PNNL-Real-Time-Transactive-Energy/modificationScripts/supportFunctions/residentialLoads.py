"""
This file contains four fuctions to add residential load types to a feeder based on the use flags and cofiguration defined
"""
##################################################################################################################
# Modified April 11, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)
# Created April 13, 2013 by Andy Fisher (andy.fisher@pnnl.gov)

# Copyright (c) 2013 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
# worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
# Government, including the right to distribute to other Government contractors.
##################################################################################################################

import math, random

def append_residential(ResTechDict, use_flags, residential_dict, last_object_key, config_data):
	"""
	This fucntion appends residential houses to a feeder based on existing triplex loads

	Inputs
		ResTechDict - dictionary containing the full feeder

		use_flags - dictionary that contains the use flags

		residential_dict - dictionary that contains information about residential loads spots

		last_object_key - Last object key

		configuration_file - dictionary that contains the configurations of the feeder

	Outputs
		ResTechDict -  dictionary containing the full feeder

		last_object_key - Last object key
	"""

	# Initialize psuedo-random seed
	# random.seed(3)

	# Check if last_object_key exists in glmCaseDict
	if last_object_key in ResTechDict:
		while last_object_key in ResTechDict:
			last_object_key += 1
	
	# Begin adding residential house dictionaries
	if use_flags['use_homes'] == 1 and len(residential_dict) > 0:
		count_house = 0
		fl_area = []

		# In order to ensure we follow the thermal integrity distribution we will need to base it off the total populations of houses to be attached
		total_no_houses = 0
		for x in residential_dict:
			total_no_houses += residential_dict[x]['number_of_houses']

		# Create a histogram of what the thermal integrity of the houses should be
		thermal_integrity = [[math.ceil(x * total_no_houses) for x in config_data['thermal_percentages'][y]] for y in range(0,len(config_data['thermal_percentages']))]

		# list of how many house per type
		total_houses_by_type = [sum(x) for x in thermal_integrity] #[sum(x) for x in zip(*thermal_integrity)]

		# only allow pool pumps on single family homes
		no_pool_pumps = total_houses_by_type[0]

		# number of water heater to implement
		no_water_heaters = math.ceil(total_no_houses * config_data['wh_electric'])

		# Create a histogram of what the heating and cooling schedules of the houses should be
		cool_sp = [[math.ceil(x * total_houses_by_type[y]) for x in config_data['cooling_setpoint'][y][0]] for y in range(0,len(config_data['cooling_setpoint']))]
		heat_sp = [[math.ceil(x * total_houses_by_type[y]) for x in config_data['heating_setpoint'][y][0]] for y in range(0, len(config_data['heating_setpoint']))]

		# Create a histogram of what the water heater sizes should be
		wh_sp = [math.ceil(x * no_water_heaters) for x in config_data['wh_size'] ]

		# counter for total number of houses
		uniqueHouses = -1

		#print('iterating over residential_dict')
		# Begin attaching houses to designated triplex_meters
		for x in residential_dict:
			if residential_dict[x]['number_of_houses'] > 0:
				if residential_dict[x]['parent'] != 'None':
					my_name = residential_dict[x]['parent'] #+ '_' + residential_dict[x]['name']
					my_parent = residential_dict[x]['parent']
				else:
					my_name = residential_dict[x]['name']
					my_parent = residential_dict[x]['name']

				no_houses = residential_dict[x]['number_of_houses']
				phase = residential_dict[x]['phases']
				lg_vs_sm = residential_dict[x]['large_vs_small']

				#print('iterating over number of houses')
				# Start adding house dictionaries
				for y in range(no_houses):
					# increase the house counter
					uniqueHouses +=1
					
					ResTechDict[last_object_key] = {'object' : 'triplex_meter',
													'phases' : '{:s}'.format(phase),
													'name' : 'tpm{:d}_{:s}'.format(y,my_name),
													'parent' : '{:s}'.format(my_parent),
													'groupid' : 'Residential_Meter',
													'nominal_voltage' : '120'}
					
					if config_data['short_names']:
						ResTechDict[last_object_key]['name'] = 'tm{:d}_h{:d}'.format(y,uniqueHouses)

					last_object_key += 1

					# Create the house dictionary
					ResTechDict[last_object_key] = {'object' : 'house',
													'name' : 'house{:d}_{:s}'.format(y,my_name),
													'parent' : 'tpm{:d}_{:s}'.format(y,my_name),
													'groupid' : 'Residential'}

					if config_data['short_names']:
						ResTechDict[last_object_key]['name'] = 'h{:d}_m{:d}'.format(uniqueHouses,y)
						ResTechDict[last_object_key]['parent'] = 'tm{:d}_h{:d}'.format(y,uniqueHouses)

					# Calculate the  residential schedule skew value
					skew_value = config_data['residential_skew_std']*random.normalvariate(0,1)

					if skew_value < -1*config_data['residential_skew_max']:
						skew_value = -1*config_data['residential_skew_max']
					elif skew_value > config_data['residential_skew_max']:
						skew_value = config_data['residential_skew_max']

					# Additional skew outside the residential skew max
					skew_value = skew_value + config_data['residential_skew_shift']

					# Calculate the waterheater schedule skew
					wh_skew_value = 3*config_data['residential_skew_std']*random.normalvariate(0,1)

					if wh_skew_value < -6*config_data['residential_skew_max']:
						wh_skew_value = -6*config_data['residential_skew_max']
					elif wh_skew_value > 6*config_data['residential_skew_max']:
						wh_skew_value = 6*config_data['residential_skew_max']

					# Scale this skew up to weeks
					pp_skew_value = 128*config_data['residential_skew_std']*random.normalvariate(0,1)

					if pp_skew_value < -128*config_data['residential_skew_max']:
						pp_skew_value = -128*config_data['residential_skew_max']
					elif pp_skew_value > 128*config_data['residential_skew_max']:
						pp_skew_value = 128*config_data['residential_skew_max']

					ResTechDict[last_object_key]['schedule_skew'] = '{:.0f}'.format(skew_value)

					# Choose what type of building we are going to use
					# and set the thermal integrity of said building
					size_a = len(thermal_integrity)
					size_b = len(thermal_integrity[0])

					therm_int = int(math.ceil(size_a * size_b * random.random()))

					row_ti = therm_int % size_a
					col_ti = therm_int % size_b

					# print thermal_integrity

					while thermal_integrity[row_ti][col_ti] < 1:
						therm_int = int(math.ceil(size_a * size_b * random.random()))
						row_ti = therm_int % size_a
						col_ti = therm_int % size_b

					thermal_integrity[row_ti][col_ti] -= 1
					thermal_temp = config_data['thermal_properties'][row_ti][col_ti]

					f_area_base = config_data['floor_area'][row_ti]
					f_area_dist = config_data['floor_area_scalar'][row_ti]
					story_rand = random.random()
					height_rand = random.randint(0,1) # add aither 0, or 1 feet to the base heigth
					fa_rand = random.random()

					# Manipulate the floor area based on age
					floor_area = (f_area_base*f_area_dist[col_ti]) + ((f_area_base*f_area_dist[col_ti]) / 2.) * (0.5 - fa_rand) # +- 25%

					# Determine one story vs. two story house along with ceiling height
					if row_ti == 0:
						# single family home
						if story_rand < config_data['one_story']:
							stories = 1
						else:
							stories = 2
					else:
						# apartment of mobile home
						stories = 1
						height_rand = 0

					# Now also adjust square footage as a factor of whether
					# the load modifier (avg_house) rounded up or down
					floor_area *= (1 + lg_vs_sm)

					if floor_area > 4000:
						floor_area = 3800 + fa_rand*200
					elif floor_area < 300:
						floor_area = 300 + fa_rand*100

					fl_area.append(floor_area)
					count_house += 1

					ResTechDict[last_object_key]['floor_area'] = '{:.0f}'.format(floor_area)
					ResTechDict[last_object_key]['number_of_stories'] = '{:.0f}'.format(stories)

					ceiling_height = 8 + height_rand
					ResTechDict[last_object_key]['ceiling_height'] = '{:.0f}'.format(ceiling_height)

					building_type = ['Single Family','Apartment','Mobile Home']
					ResTechDict[last_object_key]['comment'] = '//Thermal integrity -> {:s} {:d}'.format(building_type[row_ti],col_ti)

					rroof = thermal_temp[0] * (0.8 + (0.4 * random.random()))
					ResTechDict[last_object_key]['Rroof'] = '{:.2f}'.format(rroof)

					rwall =  thermal_temp[1] * (0.8 + (0.4 * random.random()))
					ResTechDict[last_object_key]['Rwall'] = '{:.2f}'.format(rwall)

					rfloor =  thermal_temp[2] * (0.8 + (0.4 * random.random()))
					ResTechDict[last_object_key]['Rfloor'] = '{:.2f}'.format(rfloor)
					ResTechDict[last_object_key]['glazing_layers'] = '{:.0f}'.format(thermal_temp[3])
					ResTechDict[last_object_key]['glass_type'] = '{:.0f}'.format(thermal_temp[4])
					ResTechDict[last_object_key]['glazing_treatment'] = '{:.0f}'.format(thermal_temp[5])
					ResTechDict[last_object_key]['window_frame'] = '{:.0f}'.format(thermal_temp[6])

					rdoor =  thermal_temp[7] * (0.8 + (0.4 * random.random()))
					ResTechDict[last_object_key]['Rdoors'] = '{:.2f}'.format(rdoor)

					airchange =  thermal_temp[8] * (0.8 + (0.4 * random.random()))
					ResTechDict[last_object_key]['airchange_per_hour'] = '{:.2f}'.format(airchange)

					c_COP =  thermal_temp[10] + (random.random() * (thermal_temp[9] - thermal_temp[10]))
					ResTechDict[last_object_key]['cooling_COP'] = '{:.2f}'.format(c_COP)


					ResTechDict[last_object_key]['window_wall_ratio'] = '{:.2f}'.format(config_data['window_wall_ratio'])

					# This is a bit of a guess from Rob's estimates
					mass_floor = 2.5 + (1.5 * random.random())
					ResTechDict[last_object_key]['total_thermal_mass_per_floor_area'] = '{:.3f}'.format(mass_floor)

					#ResTechDict[last_object_key]['include_solar_quadrant'] = 'W|S|E'
					 

					heat_type = random.random()
					cool_type = random.random()
					h_COP = c_COP

					# ct = 'NONE'
					if heat_type <= config_data['perc_gas']:
						ResTechDict[last_object_key]['heating_system_type'] = 'GAS'

						if cool_type <= config_data['perc_AC']:
							ResTechDict[last_object_key]['cooling_system_type'] = 'ELECTRIC'
							ResTechDict[last_object_key]['motor_model'] = 'BASIC'
							ResTechDict[last_object_key]['motor_efficiency'] = 'GOOD'
							# ct = 'ELEC'
						else:
							ResTechDict[last_object_key]['cooling_system_type'] = 'NONE'

						# ht = 'GAS'
					elif heat_type <= (config_data['perc_gas'] + config_data['perc_pump']):
						ResTechDict[last_object_key]['heating_system_type'] = 'HEAT_PUMP'
						ResTechDict[last_object_key]['heating_COP'] = '{:.1f}'.format(h_COP)
						ResTechDict[last_object_key]['cooling_system_type'] = 'ELECTRIC'
						ResTechDict[last_object_key]['auxiliary_strategy'] = 'DEADBAND'
						ResTechDict[last_object_key]['auxiliary_system_type'] = 'ELECTRIC'
						ResTechDict[last_object_key]['motor_model'] = 'BASIC'
						ResTechDict[last_object_key]['motor_efficiency'] = 'AVERAGE'
						# ht = 'HP'
						# ct = 'ELEC'
					elif (floor_area * ceiling_height) > 12000: # No resistive homes with large volumes
						ResTechDict[last_object_key]['heating_system_type'] = 'GAS'

						if cool_type <= config_data['perc_AC']:
							ResTechDict[last_object_key]['cooling_system_type'] = 'ELECTRIC'
							ResTechDict[last_object_key]['motor_model'] = 'BASIC'
							ResTechDict[last_object_key]['motor_efficiency'] = 'GOOD'
							# ct = 'ELEC'
						else:
							ResTechDict[last_object_key]['cooling_system_type'] = 'NONE'

						# ht = 'GAS'
					else:
						ResTechDict[last_object_key]['heating_system_type'] = 'RESISTANCE'

						if cool_type <= config_data['perc_AC']:
							ResTechDict[last_object_key]['cooling_system_type'] = 'ELECTRIC'
							ResTechDict[last_object_key]['motor_model'] = 'BASIC'
							ResTechDict[last_object_key]['motor_efficiency'] = 'GOOD'
							# ct = 'ELEC'
						else:
							ResTechDict[last_object_key]['cooling_system_type'] = 'NONE'

						# ht = 'ELEC'

					ResTechDict[last_object_key]['heating_cop_curve'] = 'LINEAR'
					ResTechDict[last_object_key]['heating_cap_curve'] = 'FLAT'
					ResTechDict[last_object_key]['cooling_cop_curve'] = 'LINEAR'
					ResTechDict[last_object_key]['cooling_cap_curve'] = 'FLAT'

					#os_rand = config_data['over_sizing_factor'] * (0.8 + (0.4 * random.random()))
					os_rand = config_data['over_sizing_factor'] * (random.random())
					ResTechDict[last_object_key]['over_sizing_factor'] = '{:.1f}'.format(os_rand)
					ResTechDict[last_object_key]['latent_load_fraction'] = '0.0001'

					ResTechDict[last_object_key]['breaker_amps'] = '1000'
					ResTechDict[last_object_key]['hvac_breaker_rating'] = '1000'

					# Choose a cooling and heating schedule
					cooling_set = int(math.ceil(config_data['no_cool_sch'] * random.random()))
					heating_set = int(math.ceil(config_data['no_heat_sch'] * random.random()))

					# Choose a cooling bin
					coolsp = config_data['cooling_setpoint'][row_ti]
					no_cool_bins = len(coolsp[0])

					# See if we have that bin left
					cool_bin = random.randint(0,no_cool_bins - 1)

					while cool_sp[row_ti][cool_bin] < 1:
						cool_bin = random.randint(0,no_cool_bins - 1)

					cool_sp[row_ti][cool_bin] -= 1

					# Choose a heating bin
					heatsp = config_data['heating_setpoint'][row_ti]
					no_heat_bins = len(heatsp[0])
					find = False

					# we have already choosen a cool bing and since they allign with the heating bins we will first check to see if the coresponding heat bin is available
					heat_bin = cool_bin
					while heat_sp[row_ti][heat_bin] < 1 or heatsp[2][heat_bin] >= coolsp[3][cool_bin]:
						if heat_bin <= 0:
							# we ended up with the lowest bin. We make one more attempt to find another bin by random search
							heat_bin = random.randint(0,no_heat_bins - 1)
							heat_count = 1

							while heat_sp[row_ti][heat_bin] < 1 or heatsp[2][heat_bin] >= coolsp[3][cool_bin]:
								heat_bin = random.randint(0,no_heat_bins - 1)

								# if we tried a few times, give up and take an extra
								# draw from the lowest bin
								if heat_count > 20:
									heat_bin = 0
									find = True
									break

								heat_count += 1

						if find:
							break
						heat_bin -= 1

					heat_sp[row_ti][heat_bin] -= 1

					# Randomly choose within the bin, then +/- one
					# degree to seperate the deadbands
					cool_night = (coolsp[2][cool_bin] - coolsp[3][cool_bin]) * random.random() + coolsp[3][cool_bin] + 1
					heat_night = (heatsp[2][heat_bin] - heatsp[3][heat_bin]) * random.random() + heatsp[3][heat_bin] - 1

					# 1-15-2013: made a change so that cool and heat
					# diff's are based off same random value -JLH
					diff_rand = random.random()
					cool_night_diff = coolsp[1][cool_bin] * 2. * diff_rand
					heat_night_diff = heatsp[1][heat_bin] * 2. * diff_rand

					#heat_night += config_data['addtl_heat_degrees']

					if use_flags['use_schedules'] == 1:
						if use_flags['house_thermostat_mode'] == 'COOL': # cooling only
							ResTechDict[last_object_key]['cooling_setpoint'] = 'cooling{:d}*{:.2f}+{:.2f}'.format(cooling_set,cool_night_diff,cool_night)
							ResTechDict[last_object_key]['heating_setpoint'] = '40'
							init_temp = cool_night - 1 + (2 * random.random())
							ResTechDict[last_object_key]['air_temperature'] = '{:.2f}'.format(init_temp)
							ResTechDict[last_object_key]['mass_temperature'] = '{:.2f}'.format(init_temp)
						elif use_flags['house_thermostat_mode'] == 'HEAT': # heating only
							ResTechDict[last_object_key]['cooling_setpoint'] = '110'
							ResTechDict[last_object_key]['heating_setpoint'] = 'heating{:d}*{:.2f}+{:.2f}'.format(heating_set,heat_night_diff,heat_night)
							init_temp = heat_night - 1 + (2 * random.random())
							ResTechDict[last_object_key]['air_temperature'] = '{:.2f}'.format(init_temp)
							ResTechDict[last_object_key]['mass_temperature'] = '{:.2f}'.format(init_temp)
						else: # auto so both cooling and heating
							ResTechDict[last_object_key]['cooling_setpoint'] = 'cooling{:d}*{:.2f}+{:.2f}'.format(cooling_set,cool_night_diff,cool_night)
							ResTechDict[last_object_key]['heating_setpoint'] = 'heating{:d}*{:.2f}+{:.2f}'.format(heating_set,heat_night_diff,heat_night)
							init_temp = abs(cool_night-heat_night)/2 + min(cool_night, heat_night) - 1 + (2 * random.random())
							ResTechDict[last_object_key]['air_temperature'] = '{:.2f}'.format(init_temp)
							ResTechDict[last_object_key]['mass_temperature'] = '{:.2f}'.format(init_temp)
					else:
						ResTechDict[last_object_key]['cooling_setpoint'] = '{:.2f}'.format(cool_night)
						ResTechDict[last_object_key]['heating_setpoint'] = '{:.2f}'.format(heat_night)
						init_temp = abs(cool_night-heat_night)/2 + min(cool_night, heat_night) - 1 + (2 * random.random())
						ResTechDict[last_object_key]['air_temperature'] = '{:.2f}'.format(init_temp)
						ResTechDict[last_object_key]['mass_temperature'] = '{:.2f}'.format(init_temp)

					# add some randomness to the compressor lock time, range will be 1-3 minutes
					onLock = random.randint(30,90)
					offLock = random.randint(30,90)

					ResTechDict[last_object_key]['thermostat_off_cycle_time'] = '{:d}'.format(offLock)
					ResTechDict[last_object_key]['thermostat_on_cycle_time'] = '{:d}'.format(onLock)


					last_object_key += 1

					# Add the end-use ZIPload objects to the house
					# Scale all of the end-use loads
					scalar_base = config_data['base_load_scalar']
					scalar1 = ((324.9 / 8907.) * pow(floor_area,0.442)) * scalar_base
					scalar2 = 0.8 + 0.4 * random.random()
					scalar3 = 0.8 + 0.4 * random.random()
					resp_scalar = scalar1 * scalar2
					unresp_scalar = scalar1 * scalar3

					# average size is 1.36 kW
					# Energy Savings through Automatic Seasonal Run-Time Adjustment of Pool Filter Pumps
					# Stephen D Allen, B.S. Electrical Engineering
					pool_pump_power = 1.36 + .36*random.random()
					pool_pump_perc = random.random()

					# average 4-12 hours / day -> 1/6-1/2 duty cycle
					# typically run for 2 - 4 hours at a time
					pp_dutycycle = 1./6. + (1./2. - 1./6.)*random.random()
					pp_period = 4. + 4.*random.random()
					pp_init_phase = random.random()

					# Add responsive ZIPload

					ResTechDict[last_object_key] = {'object' : 'ZIPload',
													'name' : 'house{:d}_resp_{:s}'.format(y,my_name),
													'parent' : 'house{:d}_{:s}'.format(y,my_name),
													'comment' : '// Responsive load',
													'groupid' : 'Responsive_load',
													# 'groupid': 'Residential_zip',
													'schedule_skew' : '{:.0f}'.format(skew_value),
													'base_power' : 'responsive_loads*{:.2f}'.format(resp_scalar),
													'heatgain_fraction' : '{:.3f}'.format(config_data['r_heat_fraction']),
													'power_pf' : '{:.3f}'.format(config_data['r_p_pf']),
													'current_pf' : '{:.3f}'.format(config_data['r_i_pf']),
													'impedance_pf' : '{:.3f}'.format(config_data['r_z_pf']),
													'impedance_fraction' : '{:f}'.format(config_data['r_zfrac']),
													'current_fraction' : '{:f}'.format(config_data['r_ifrac']),
													'power_fraction' : '{:f}'.format(config_data['r_pfrac'])}

					# if we do not use schedules we will assume resp_scalar is the fixed value
					if use_flags['use_schedules'] == 0:
						ResTechDict[last_object_key]['base_power'] = '{:.2f}'.format(resp_scalar)

					if config_data['short_names']:
						ResTechDict[last_object_key]['name'] = 'h{:d}_m{:d}_resp'.format(uniqueHouses,y)
						ResTechDict[last_object_key]['parent'] = 'h{:d}_m{:d}'.format(uniqueHouses,y)

					last_object_key += 1

					# Add unresponsive ZIPload object
					ResTechDict[last_object_key] = {'object' : 'ZIPload',
													'name' : 'house{:d}_unresp_{:s}'.format(y,my_name),
													'parent' : 'house{:d}_{:s}'.format(y,my_name),
													'comment' : '// Unresponsive load',
													'groupid' : 'Unresponsive_load',
													# 'groupid': 'Residential_zip',
													'schedule_skew' : '{:.0f}'.format(skew_value),
													'base_power' : 'unresponsive_loads*{:.2f}'.format(unresp_scalar),
													'heatgain_fraction' : '{:.3f}'.format(config_data['r_heat_fraction']),
													'power_pf' : '{:.3f}'.format(config_data['r_p_pf']),
													'current_pf' : '{:.3f}'.format(config_data['r_i_pf']),
													'impedance_pf' : '{:.3f}'.format(config_data['r_z_pf']),
													'impedance_fraction' : '{:f}'.format(config_data['r_zfrac']),
													'current_fraction' : '{:f}'.format(config_data['r_ifrac']),
													'power_fraction' : '{:f}'.format(config_data['r_pfrac'])}

					# if we do not use schedules we will assume unresp_scalar is the fixed value
					if use_flags['use_schedules'] == 0:
						ResTechDict[last_object_key]['base_power'] = '{:.2f}'.format(unresp_scalar)

					if config_data['short_names']:
						ResTechDict[last_object_key]['name'] = 'h{:d}_m{:d}_uresp'.format(uniqueHouses,y)
						ResTechDict[last_object_key]['parent'] = 'h{:d}_m{:d}'.format(uniqueHouses,y)

					last_object_key += 1
					#print('finished unresponsive zipload')
					# Add pool pumps only on single-family homes
					if pool_pump_perc < (2.*config_data['perc_poolpumps']) and no_pool_pumps >= 1 and row_ti == 0:
						ResTechDict[last_object_key] = {'object' : 'ZIPload',
														'name' : 'house{:d}_ppump_{:s}'.format(y,my_name),
														'parent' : 'house{:d}_{:s}'.format(y,my_name),
														'comment' : '// Pool Pump',
														'groupid' : 'Pool_Pump',
														# 'groupid': 'Residential_zip',
														'schedule_skew' : '{:.0f}'.format(pp_skew_value),
														'base_power' : 'pool_pump_season*{:.2f}'.format(pool_pump_power),
														'duty_cycle' : '{:.2f}'.format(pp_dutycycle),
														'phase' : '{:.2f}'.format(pp_init_phase),
														'period' : '{:.2f}'.format(pp_period),
														'heatgain_fraction' : '0.0',
														'power_pf' : '{:.3f}'.format(config_data['r_p_pf']),
														'current_pf' : '{:.3f}'.format(config_data['r_i_pf']),
														'impedance_pf' : '{:.3f}'.format(config_data['r_z_pf']),
														'impedance_fraction' : '{:f}'.format(config_data['r_zfrac']),
														'current_fraction' : '{:f}'.format(config_data['r_ifrac']),
														'power_fraction' : '{:f}'.format(config_data['r_pfrac']),
														'is_240' : 'TRUE'}

						# if we do not use schedules we will assume the pool pump never running
						if use_flags['use_schedules'] == 0:
							ResTechDict[last_object_key]['base_power'] = '0'

						if config_data['short_names']:
							ResTechDict[last_object_key]['name'] = 'h{:d}_m{:d}_pp'.format(uniqueHouses,y)
							ResTechDict[last_object_key]['parent'] = 'h{:d}_m{:d}'.format(uniqueHouses,y)

						no_pool_pumps -= 1
						last_object_key += 1

					# Add Water heater objects
					heat_element = 3.0 + (0.5 * random.randint(1,5))
					tank_height = 3.78
					tank_set = 120. + (16 * random.random())
					tank_temp = 130. + (12 * random.random())
					therm_dead = 4. + (4. * random.random())
					tank_UA = 2. + (2. * random.random())
					water_sch = math.ceil(config_data['no_water_sch'] * random.random())
					water_var = 0.95 + (random.random() * 0.1)
					wh_size_test = random.random()
					wh_size_rand = random.randint(0,2)

					# waterDemandScale = 0.245 * (1 + 0.331555 * random.random())
					# waterEnergy = 2 + (0.25 * random.random())
					# waterPeriod = 160 + (30 * random.random())
					# waterCount = 5 + (3 * random.random())
					# waterDemandScale = 0.245 * (1 + 0.331555 * random.random())
					# waterEnergy = 2 + (0.25 * random.random())
					# waterCount = 5 + (3 * random.random())
					# waterDuration = 160 #+ (30 * random.random())
					# waterQOFF = 2
					# waterQON = 4

					if heat_type <= config_data['wh_electric']:
						ResTechDict[last_object_key] = {'object' : 'waterheater',
														'groupid': 'water_heater',
														'name' : 'house{:d}_wh_{:s}'.format(y,my_name),
														'parent' : 'house{:d}_{:s}'.format(y,my_name),
														'schedule_skew' : '{:.0f}'.format(wh_skew_value),
														'heating_element_capacity' : '{:.1f} kW'.format(heat_element),
														'tank_setpoint' : '{:.1f}'.format(tank_set),
														'temperature': '{:.1f}'.format(tank_temp),
														'thermostat_deadband' : '{:.1f}'.format(therm_dead),
														'location' : 'INSIDE',
														'tank_UA' : '{:.1f}'.format(tank_UA),
														'tank_height': '{:.2f}'.format(tank_height)}#,
														#'water_demand' : 'this.myshape*{:.3f}'.format(waterDemandScale),
														#'myshape' : '"type: modulated; schedule: WATERHEATER; energy: {:.3f} kWh; period: {:.3f} s; count: {:.3f}; modulation: amplitude"'.format(waterEnergy, waterPeriod, waterCount)}
														#'myshape' : '"type: queued; schedule: WATERHEATER; energy: {:.3f} kWh; count: {:.3f}; duration: {:.3f} s; q_on: {:.3f}; q_off: {:.3f}";'.format(waterEnergy, waterCount, waterDuration, waterQON, waterQOFF)}
														#'myshape': '"type: pulsed; schedule: WATERHEATER; energy: {:.3f} kWh; count: {:.3f}; duration: {:.3f} s;"'.format(waterEnergy, waterCount, waterDuration)}

						# determine tank size and schedule to use
						if wh_size_test < config_data['wh_size'][0]:
							ResTechDict[last_object_key]['water_demand'] = 'small_{:.0f}*{:.02f}'.format(water_sch,water_var)
							whsize = 20. + (5. * wh_size_rand)
							wh_sp[0] -= 1
						elif wh_size_test < (config_data['wh_size'][0] + config_data['wh_size'][1]):
							if floor_area < 2000:
								ResTechDict[last_object_key]['water_demand'] = 'small_{:.0f}*{:.02f}'.format(water_sch,water_var)
							else:
								ResTechDict[last_object_key]['water_demand'] = 'large_{:.0f}*{:.02f}'.format(water_sch,water_var)
							whsize = 30. + (10. * wh_size_rand)
							wh_sp[1] -= 1
						else:
							ResTechDict[last_object_key]['water_demand'] = 'large_{:.0f}*{:.02f}'.format(water_sch,water_var)
							whsize = 50. + (10. * wh_size_rand)
							wh_sp[2] -= 1

						ResTechDict[last_object_key]['tank_volume'] = '{:.0f}'.format(whsize)

						# if we do not use schedules we will assume the water heater is just a storage tank
						if use_flags['use_schedules'] == 0:
							ResTechDict[last_object_key]['water_demand'] = '0'

						if config_data['short_names']:
							ResTechDict[last_object_key]['name'] = 'h{:d}_m{:d}_wh'.format(uniqueHouses,y)
							ResTechDict[last_object_key]['parent'] = 'h{:d}_m{:d}'.format(uniqueHouses,y)

						last_object_key += 1

				#print('finished water heater')
			#print('finished iterating over number of houses')
		#print('finished iterating over residential dict')
	return ResTechDict, last_object_key

def add_normalized_residential_ziploads(loadshape_dict, residenntial_dict, config_data, last_key):
	"""
	This fucntion appends residential zip loads to a feeder based on existing triplex loads

	Inputs
		loadshape_dict - dictionary containing the full feeder

		residenntial_dict - dictionary that contains information about residential loads spots

		last_key - Last object key

		config_data - dictionary that contains the configurations of the feeder

	Outputs
		loadshape_dict -  dictionary containing the full feeder

		last_key - Last object key
	"""

	for x in list(residenntial_dict.keys()):
		tpload_name = residenntial_dict[x]['name']
		tpload_parent = residenntial_dict[x].get('parent', 'None')
		tpphases = residenntial_dict[x]['phases']
		tpnom_volt = '120.0'
		bp = residenntial_dict[x]['load'] * config_data['normalized_loadshape_scalar']

		loadshape_dict[last_key] = {'object': 'triplex_load',
									'name': '{:s}_loadshape'.format(tpload_name),
									'phases': tpphases,
									'nominal_voltage': tpnom_volt}
		if tpload_parent != 'None':
			loadshape_dict[last_key]['parent'] = tpload_parent
		else:
			loadshape_dict[last_key]['parent'] = tpload_name

		if bp > 0.0:
			loadshape_dict[last_key]['base_power_12'] = 'norm_feeder_loadshape.value*{:f}'.format(bp)
			loadshape_dict[last_key]['power_pf_12'] = '{:f}'.format(config_data['r_p_pf'])
			loadshape_dict[last_key]['current_pf_12'] = '{:f}'.format(config_data['r_i_pf'])
			loadshape_dict[last_key]['impedance_pf_12'] = '{:f}'.format(config_data['r_z_pf'])
			loadshape_dict[last_key]['power_fraction_12'] = '{:f}'.format(config_data['r_pfrac'])
			loadshape_dict[last_key]['current_fraction_12'] = '{:f}'.format(config_data['r_ifrac'])
			loadshape_dict[last_key]['impedance_fraction_12'] = '{:f}'.format(config_data['r_zfrac'])

		last_key += last_key

	return loadshape_dict, last_key


def add_residential_EVs(glmCaseDict, config_file, use_flags, last_key=0):
	"""
	This fucntion appends residential EVs to a feeder

	Inputs
		glmCaseDict - dictionary containing the full feeder

		config_file - dictionary that contains the configurations of the feeder

		use_flags - dictionary that contains the use flags

		last_key - Last object key

	Outputs
		glmCaseDict -  dictionary containing the full feeder
	"""

	# Initialize psuedo-random seed
	# random.seed(4)

	if use_flags['use_electric_vehicles'] != 0 and use_flags['use_homes'] != 0:

		# Check if last_key is already in glm dictionary
		def unused_key(key):
			if key in glmCaseDict:
				while key in glmCaseDict:
					key += 1
			return key

		# let's determine the next available key
		last_key = unused_key(last_key)

		# determine the total number of homes in the feeder
		control_dict = []
		for x in glmCaseDict:
			if 'object' in glmCaseDict[x] and glmCaseDict[x]['object'] == 'house' and glmCaseDict[x]['groupid'] == 'Residential':
				control_dict.append(glmCaseDict[x]['name'])

		# determine how many EVs to implement
		total_num_EVs = round(float(config_file["perc_EV"])*len(control_dict))

		# adjust the house list with the appropiate number to be implemented at random
		control_dict = random.sample(control_dict, int(total_num_EVs))

		for controlObject in control_dict:
			# random variables for each EV
			mileageClassification = 50 + random.randint(0, 200)  # between 50-250
			mileageEfficiency = 3.35 + 0.5 * random.random()  # between 3.35-3.85
			maximumChargeRate = math.floor(1500 + 200 * random.random())  # between 1500-1700
			chargingEfficiency = 0.85 + 0.1 * random.random()  # between 0.85-0.95
			vehicleIndex = random.randint(1, 35200)  # we have 35200 entries in the trip log

			# adding the EV charger
			glmCaseDict[last_key] = {'object': 'evcharger_det',
									 'parent': '{:s}'.format(controlObject),
									 'name': '{:s}_ev_charger'.format(controlObject),
									 'variation_mean' : '0.0',
									 'variation_std_dev' : '0.0',
									 'variation_trip_mean' : '0.0',
									 'variation_trip_std_dev' : '0.0',
									 'mileage_classification' : '{:.2f}'.format(mileageClassification),
									 'work_charging_available' : 'false',
									 'mileage_efficiency' : '{:.2f}'.format(mileageEfficiency),
									 'maximum_charge_rate' : '{:.2f}'.format(maximumChargeRate),
									 'charging_efficiency' : '{:.2f}'.format(chargingEfficiency),
									 'data_file' : '{:s}/schedules/EV_trips.csv'.format(config_file['includePath']),
									 'vehicle_index' : '{:d}'.format(vehicleIndex)}

			last_key = unused_key(last_key)

	else:
		if use_flags['use_EVs'] != 0:
			print("You asked for EVs but you did not implement residential houses so this setting was ignored")

	return glmCaseDict


def add_residential_storage(glmCaseDict, config_file, use_flags, last_key=0):
	"""
	This fucntion appends residential battery storage to a feeder

	Inputs
		glmCaseDict - dictionary containing the full feeder

		config_file - dictionary that contains the configurations of the feeder

		use_flags - dictionary that contains the use flags

		last_key - Last object key

	Outputs
		glmCaseDict -  dictionary containing the full feeder
	"""

	if use_flags['use_residential_storage'] != 0 and use_flags['use_homes'] != 0:

		# Check if last_key is already in glm dictionary
		def unused_key(key):
			if key in glmCaseDict:
				while key in glmCaseDict:
					key += 1
			return key

		# let's determine the next available key
		last_key = unused_key(last_key)

		# determine the total number of homes in the feeder
		control_dict = []
		for x in glmCaseDict:
			if 'object' in glmCaseDict[x] and glmCaseDict[x]['object'] == 'house' and glmCaseDict[x]['groupid'] == 'Residential':
				control_dict.append([glmCaseDict[x]['name'],glmCaseDict[x]['parent']])

		# determine how many EVs to implement
		total_num_EBs = round(float(config_file["perc_EB"])*len(control_dict))

		# adjust the house list with the appropiate number to be implemented at random
		control_dict = random.sample(control_dict, int(total_num_EBs))

		for controlObject in control_dict:
			# random variables for each EB

			batterySOC = 0.7 + 0.2 * random.random() 

			# adding the external controller
			glmCaseDict[last_key] = {'object': 'inverter',
									'parent': '{:s}'.format(controlObject[1]),
									'name': '{:s}_eb_inveter'.format(controlObject[0]),
								    'inverter_type': 'FOUR_QUADRANT', # Must be in FOUR_QUADRANT to use the load following control scheme.
								    'generator_status': 'ONLINE', # set the status of the inverter to online
								    'charge_lockout_time': '30', # lockout time for charging
								    'discharge_lockout_time': '30', # lockout time for dischargeing
								    'four_quadrant_control_mode': 'LOAD_FOLLOWING', # The only mode that works with the battery object.
								    'sense_object': '{:s}'.format(controlObject[1]), # the sense_object must be a meter, triplex_meter, or transformer.
								    'rated_power': '3000.0', # The per phase power output rating of the inverter in VA.
								    'inverter_efficiency': '0.95',
								    'charge_on_threshold': '1.3 kW', # when the load at the sense_object drops below this value the inverter starts to charge the battery.
								    'charge_off_threshold': '2.7 kW', # when the battery is charging and the load at the sense_object rises above this value the inverter stops charging the battery.
								    'discharge_off_threshold': '3.0 kW', # when the battery is discharging and the load at the sense_object drops below this value the inverter stops discharging the battery.
								    'discharge_on_threshold': '4.5 kW', # when the load at the sense_object rises above this value the inverter starts to discharge the battery.
								    'max_discharge_rate': '1 kW', # The maximum power output to demand from the battery when discharging.
								    'max_charge_rate': '1 kW'} # The maximum power input to the battery when charging.


			last_key = unused_key(last_key)
			
			glmCaseDict[last_key] = {'object': 'battery',
									 'groupid': 'residential_storage',
									 'parent': '{:s}_eb_inveter'.format(controlObject[0]),
									 'name': '{:s}_eb_battery'.format(controlObject[0]),
									 'use_internal_battery_model': 'true',
									 'battery_type': 'LI_ION',
									 'state_of_charge': '{:.2f}'.format(batterySOC),
									 'generator_mode': 'SUPPLY_DRIVEN',
									 'rfb_size': 'HOUSEHOLD'}

			last_key = unused_key(last_key)
	else:
		if use_flags['use_residential_storage'] != 0:
			print("You asked for residential battery storage, but you did not implement residential houses so this setting was ignored")

	return glmCaseDict


def add_utility_storage(glmCaseDict, config_file, use_flags, peakLoad, last_key=0):
	"""
	This fucntion appends utility battery storage to a feeder

	Inputs
		glmCaseDict - dictionary containing the full feeder

		config_file - dictionary that contains the configurations of the feeder

		use_flags - dictionary that contains the use flags

		last_key - Last object key

	Outputs
		glmCaseDict -  dictionary containing the full feeder
	"""

	# Check if last_key is already in glm dictionary
	def unused_key(key):
		if key in glmCaseDict:
			while key in glmCaseDict:
				key += 1
		return key

	# let's determine the next available key
	last_key = unused_key(last_key)

	foundNode = False
	# determine the total number of homes in the feeder
	for x in glmCaseDict:
		if 'object' in glmCaseDict[x] and glmCaseDict[x]['object'] == 'transformer' and glmCaseDict[x]['name'] == 'substation_transformer':
			foundNode = True
			UEBParent = glmCaseDict[x]['to']
			break

	if foundNode:
		for count in range(0,int(config_file["utility_EB"])): # we have to create the correct amount of batteries
			# random variables for each EB

			batterySOC = 0.7 + 0.2 * random.random() 

			charge_on_threshold = (peakLoad*1000)*0.65
			charge_off_threshold = (peakLoad*1000)*0.73
			discharge_off_threshold = (peakLoad*1000)*0.77
			discharge_on_threshold = (peakLoad*1000)*0.85

			# adding the external controller
			glmCaseDict[last_key] = {'object': 'inverter',
									'parent': '{:s}'.format(UEBParent),
									'name': 'utility_eb_inveter_{:d}'.format(count),
								    'inverter_type': 'FOUR_QUADRANT', # Must be in FOUR_QUADRANT to use the load following control scheme.
								    'generator_status': 'ONLINE', # set the status of the inverter to online
								    'charge_lockout_time': '30', # lockout time for charging
								    'discharge_lockout_time': '30', # lockout time for dischargeing
								    'four_quadrant_control_mode': 'LOAD_FOLLOWING', # The only mode that works with the battery object.
								    'sense_object': '{:s}'.format(UEBParent), # the sense_object must be a meter, triplex_meter, or transformer.
								    'rated_power': '240000.0', # The per phase power output rating of the inverter in VA.
								    'inverter_efficiency': '0.95',
								    'charge_on_threshold': '{:.2f} kW'.format(charge_on_threshold), # when the load at the sense_object drops below this value the inverter starts to charge the battery.
								    'charge_off_threshold': '{:.2f} kW'.format(charge_off_threshold), # when the battery is charging and the load at the sense_object rises above this value the inverter stops charging the battery.
								    'discharge_off_threshold': '{:.2f} kW'.format(discharge_off_threshold), # when the battery is discharging and the load at the sense_object drops below this value the inverter stops discharging the battery.
								    'discharge_on_threshold': '{:.2f} kW'.format(discharge_on_threshold), # when the load at the sense_object rises above this value the inverter starts to discharge the battery.
								    'max_discharge_rate': '200 kW', # The maximum power output to demand from the battery when discharging.
								    'max_charge_rate': '200 kW'} # The maximum power input to the battery when charging.


			last_key = unused_key(last_key)
			
			glmCaseDict[last_key] = {'object': 'battery',
									 'groupid': 'utility_storage',
									 'parent': 'utility_eb_inveter_{:d}'.format(count),
									 'name': 'utility_eb_battery_{:d}'.format(count),
									 'use_internal_battery_model': 'true',
									 'battery_type': 'LI_ION',
									 'state_of_charge': '{:.2f}'.format(batterySOC),
									 'generator_mode': 'SUPPLY_DRIVEN',
									 'rfb_size': 'LARGE'}

			last_key = unused_key(last_key)

	else:
		print("Unable to find the nodes to connect the utility scale battery storage")
	
	return glmCaseDict

if __name__ == '__main__':
	pass
