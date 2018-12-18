"""
This file contains four fuctions to add commercial load types to a feeder based on the use flags and cofiguration defined
"""
##################################################################################################################
# Modified April 11, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)
# Created April 13, 2013 by Andy Fisher (andy.fisher@pnnl.gov)

# Copyright (c) 2013 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
# worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
# Government, including the right to distribute to other Government contractors.
##################################################################################################################

import math, random


def append_commercial(glmCaseDict, use_flags, commercial_dict, last_object_key, config_data):
	"""
	This fucntion appends commercial houses to a feeder based on existing loads

	Inputs
		glmCaseDict - dictionary containing the full feeder

		use_flags - dictionary that contains the use flags
		
		commercial_dict - dictionary that contains information about commercial loads spots
		
		last_object_key - Last object key
		
		use_config_file - dictionary that contains the configurations of the feeder

	Outputs
		glmCaseDict -  dictionary containing the full feeder

		last_object_key - Last object key
	"""

	# Initialize psuedo-random seed
	# random.seed(4)

	# Phase ABC - convert to "commercial buildings"
	#  if number of "houses" > 15, then create a large office
	#  if number of "houses" < 15 but > 6, create a big box commercial
	#  else, create a residential strip mall

	# If using Configuration.m and load classifications,
	#  building type is chosen according to classification
	#  regardless of number of "houses"


	# Check if last_object_key exists in glmCaseDict
	if last_object_key in glmCaseDict:
		while last_object_key in glmCaseDict:
			last_object_key += 1

	if len(commercial_dict) > 0 and use_flags["use_commercial"] == 1:
		# setup all of the line configurations we may need
		glmCaseDict[last_object_key] = {"object": "triplex_line_conductor",
										"name": "comm_line_cfg_cnd1",
										"resistance": "0.48",
										"geometric_mean_radius": "0.0158"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "triplex_line_conductor",
										"name": "comm_line_cfg_cnd2",
										"resistance": "0.48",
										"geometric_mean_radius": "0.0158"}

		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "triplex_line_conductor",
										"name": "comm_line_cfg_cndN",
										"resistance": "0.48",
										"geometric_mean_radius": "0.0158"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "triplex_line_configuration",
										"name": "commercial_line_config",
										"conductor_1": "comm_line_cfg_cnd1",
										"conductor_2": "comm_line_cfg_cnd2",
										"conductor_N": "comm_line_cfg_cndN",
										"insulation_thickness": "0.08",
										"diameter": "0.522"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "line_spacing",
										"name": "line_spacing_commABC",
										"distance_AB": "53.19999999996 in",
										"distance_BC": "53.19999999996 in",
										"distance_AC": "53.19999999996 in",
										"distance_AN": "69.80000000004 in",
										"distance_BN": "69.80000000004 in",
										"distance_CN": "69.80000000004 in"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "overhead_line_conductor",
										"name": "overhead_line_conductor_comm",
										"rating.summer.continuous": "443.0",
										"geometric_mean_radius": "0.02270 ft",
										"resistance": "0.05230"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "line_configuration",
										"name": "line_configuration_commABC",
										"conductor_A": "overhead_line_conductor_comm",
										"conductor_B": "overhead_line_conductor_comm",
										"conductor_C": "overhead_line_conductor_comm",
										"conductor_N": "overhead_line_conductor_comm",
										"spacing": "line_spacing_commABC"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "line_configuration",
										"name": "line_configuration_commAB",
										"conductor_A": "overhead_line_conductor_comm",
										"conductor_B": "overhead_line_conductor_comm",
										"conductor_N": "overhead_line_conductor_comm",
										"spacing": "line_spacing_commABC"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "line_configuration",
										"name": "line_configuration_commAC",
										"conductor_A": "overhead_line_conductor_comm",
										"conductor_C": "overhead_line_conductor_comm",
										"conductor_N": "overhead_line_conductor_comm",
										"spacing": "line_spacing_commABC"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "line_configuration",
										"name": "line_configuration_commBC",
										"conductor_B": "overhead_line_conductor_comm",
										"conductor_C": "overhead_line_conductor_comm",
										"conductor_N": "overhead_line_conductor_comm",
										"spacing": "line_spacing_commABC"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "line_configuration",
										"name": "line_configuration_commA",
										"conductor_A": "overhead_line_conductor_comm",
										"conductor_N": "overhead_line_conductor_comm",
										"spacing": "line_spacing_commABC"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "line_configuration",
										"name": "line_configuration_commB",
										"conductor_B": "overhead_line_conductor_comm",
										"conductor_N": "overhead_line_conductor_comm",
										"spacing": "line_spacing_commABC"}
		last_object_key += 1

		glmCaseDict[last_object_key] = {"object": "line_configuration",
										"name": "line_configuration_commC",
										"conductor_C": "overhead_line_conductor_comm",
										"conductor_N": "overhead_line_conductor_comm",
										"spacing": "line_spacing_commABC"}
		last_object_key += 1

		# initializations for the commercial "house" list

		# print('iterating over commercial_dict')
		for iii in commercial_dict:
			total_comm_houses = commercial_dict[iii]['number_of_houses'][0] + commercial_dict[iii]['number_of_houses'][1] + commercial_dict[iii]['number_of_houses'][2]

			my_phases = 'ABC'

			# read through the phases and do some bit-wise math
			has_phase_A = 0
			has_phase_B = 0
			has_phase_C = 0
			ph = ''
			if "A" in commercial_dict[iii]['phases']:
				has_phase_A = 1
				ph += 'A'
			if "B" in commercial_dict[iii]['phases']:
				has_phase_B = 1
				ph += 'B'
			if "C" in commercial_dict[iii]['phases']:
				has_phase_C = 1
				ph += 'C'

			no_of_phases = has_phase_A + has_phase_B + has_phase_C

			if no_of_phases == 0:
				raise Exception('The phases in commercial buildings did not add up right.')

			# name of original load object
			if commercial_dict[iii]['parent'] != 'None':
				my_name = commercial_dict[iii]['parent'] #+ '_' + commercial_dict[iii]['name']
				my_parent = commercial_dict[iii]['parent']
			else:
				my_name = commercial_dict[iii]['name']
				my_parent = commercial_dict[iii]['name']

			nom_volt = int(float(commercial_dict[iii]['nom_volt']))

			# Same for everyone
			# air_heat_fraction = 0
			# mass_solar_gain_fraction = 0.5
			# mass_internal_gain_fraction = 0.5
			fan_type = 'ONE_SPEED'
			heat_type = 'GAS'
			cool_type = 'ELECTRIC'
			aux_type = 'NONE'
			# cooling_design_temperature = 100
			# heating_design_temperature = 1
			# over_sizing_factor = 0.3
			no_of_stories = 1
			surface_heat_trans_coeff = 0.59

			# Office building - must have all three phases and enough load for 15 zones
			#                     *or* load is classified to be office buildings
			if total_comm_houses > 15 and no_of_phases == 3:
				no_of_offices = int(round(total_comm_houses / 15))

				glmCaseDict[last_object_key] = {"object": "transformer_configuration",
												"name": "CTTF_config_A_{:s}".format(my_name),
												"connect_type": "SINGLE_PHASE_CENTER_TAPPED",
												"install_type": "POLETOP",
												"impedance": "0.00033+0.0022j",
												"shunt_impedance": "10000+10000j",
												"primary_voltage": "{:.3f}".format(nom_volt),
												"secondary_voltage": "120",
												"powerA_rating": "100 kVA"}
				last_object_key += 1

				glmCaseDict[last_object_key] = {"object": "transformer_configuration",
												"name": "CTTF_config_B_{:s}".format(my_name),
												"connect_type": "SINGLE_PHASE_CENTER_TAPPED",
												"install_type": "POLETOP",
												"impedance": "0.00033+0.0022j",
												"shunt_impedance": "10000+10000j",
												"primary_voltage": "{:.3f}".format(nom_volt),
												"secondary_voltage": "120",
												"powerB_rating": "100 kVA"}
				last_object_key += 1

				glmCaseDict[last_object_key] = {"object": "transformer_configuration",
												"name": "CTTF_config_C_{:s}".format(my_name),
												"connect_type": "SINGLE_PHASE_CENTER_TAPPED",
												"install_type": "POLETOP",
												"impedance": "0.00033+0.0022j",
												"shunt_impedance": "10000+10000j",
												"primary_voltage": "{:.3f}".format(nom_volt),
												"secondary_voltage": "120",
												"powerC_rating": "100 kVA"}
				last_object_key += 1
				# print('iterating over number of offices')
				for jjj in range(no_of_offices):
					floor_area_choose = 40000. * (0.5 * random.random() + 0.5)  # up to -50# #config_data.floor_area
					ceiling_height = 13.
					airchange_per_hour = 0.69
					Rroof = 19.
					Rwall = 18.3
					Rfloor = 46.
					Rdoors = 3.
					glazing_layers = 'TWO'
					glass_type = 'GLASS'
					glazing_treatment = 'LOW_S'
					window_frame = 'NONE'
					int_gains = 3.24  # W/sf

					glmCaseDict[last_object_key] = {"object": "overhead_line",
													"from": "{:s}".format(my_parent),
													"to": "{:s}_office_meter{:.0f}".format(my_name, jjj),
													"phases": "{:s}".format(commercial_dict[iii]['phases']),
													"length": "50ft",
													"configuration": "line_configuration_comm{:s}".format(ph)}
					last_object_key += 1

					glmCaseDict[last_object_key] = {"object": "meter",
													"phases": "{:s}".format(commercial_dict[iii]['phases']),
													"name": "{:s}_office_meter{:.0f}".format(my_name, jjj),
													"groupid": "Commercial_Meter",
													"nominal_voltage": "{:f}".format(nom_volt)}
					last_object_key += 1

					# for phind = 1:3 #for each of three floors (5 zones each)
					# for phind = 1:no_of_phases #jlh
					for phind in range(1,4):
						glmCaseDict[last_object_key] = {"object": "transformer",
														"name": "{:s}_CTTF_{:s}_{:.0f}".format(my_name, ph[phind-1], jjj),
														"phases": "{:s}S".format(ph[phind-1]),
														"from": "{:s}_office_meter{:.0f}".format(my_name, jjj),
														"to": "{:s}_tm_{:s}_{:.0f}".format(my_name, ph[phind-1], jjj),
														"groupid": "Distribution_Trans",
														"configuration": "CTTF_config_{:s}_{:s}".format(ph[phind-1], my_name)}
						last_object_key += 1

						glmCaseDict[last_object_key] = {"object": "triplex_meter",
														"name": "{:s}_tm_{:s}_{:.0f}".format(my_name, ph[phind-1], jjj),
														"phases": "{:s}S".format(ph[phind-1]),
														"nominal_voltage": "120"}
						last_object_key += 1

						# skew each office zone identically per floor
						sk = round(2 * random.normalvariate(0, 1))
						skew_value = config_data["commercial_skew_std"] * sk
						if skew_value < -config_data["commercial_skew_max"]:
							skew_value = -config_data["commercial_skew_max"]
						elif skew_value > config_data["commercial_skew_max"]:
							skew_value = config_data["commercial_skew_max"]

						for zoneind in range(1, 6):
							total_depth = math.sqrt(floor_area_choose / (3. * 1.5))
							total_width = 1.5 * total_depth

							if phind < 3:
								exterior_ceiling_fraction = 0
							else:
								exterior_ceiling_fraction = 1

							if zoneind == 5:
								exterior_wall_fraction = 0
								w = total_depth - 30.
								d = total_width - 30.
								floor_area = w * d
								aspect_ratio = w / d
							else:
								window_wall_ratio = 0.33

								if zoneind == 1 or zoneind == 3:
									w = total_width - 15.
									d = 15.
									floor_area = w * d
									exterior_wall_fraction = w / (2. * (w + d))
									aspect_ratio = w / d
								else:
									w = total_depth - 15.
									d = 15.
									floor_area = w * d
									exterior_wall_fraction = w / (2. * (w + d))
									aspect_ratio = w / d

							if phind > 1:
								exterior_floor_fraction = 0
							else:
								exterior_floor_fraction = w / (2. * (w + d)) / (floor_area / (floor_area_choose / 3.))

							thermal_mass_per_floor_area = 3.9 * (0.5 + 1. * random.random())  # +/- 50#
							interior_exterior_wall_ratio = (floor_area * (2. - 1.) + 0. * 20.) / (no_of_stories * ceiling_height * 2. * (w + d)) - 1. + window_wall_ratio * exterior_wall_fraction
							no_of_doors = 0.1  # will round to zero

							init_temp = 68. + 4. * random.random()
							os_rand = config_data["over_sizing_factor"] * (0.8 + 0.4 * random.random())
							COP_A = config_data["cooling_COP"] * (0.8 + 0.4 * random.random())
							glmCaseDict[last_object_key] = {"object": "house",
															"name": "office{:s}_{:s}{:.0f}_zone{:.0f}".format(my_name, my_phases[phind-1], jjj, zoneind),
															"parent": "{:s}_tm_{:s}_{:.0f}".format(my_name, my_phases[phind-1], jjj),
															"groupid": "Commercial",
															"motor_model" : "BASIC",
															"schedule_skew": "{:.0f}".format(skew_value),
															"floor_area": "{:.0f}".format(floor_area),
															"design_internal_gains": "{:.0f}".format(int_gains * floor_area * 3.413),
															"number_of_doors": "{:.0f}".format(no_of_doors),
															"aspect_ratio": "{:.2f}".format(aspect_ratio),
															"total_thermal_mass_per_floor_area": "{:1.2f}".format(thermal_mass_per_floor_area),
															"interior_surface_heat_transfer_coeff": "{:1.2f}".format(surface_heat_trans_coeff),
															"interior_exterior_wall_ratio": "{:2.1f}".format(interior_exterior_wall_ratio),
															"exterior_floor_fraction": "{:.3f}".format(exterior_floor_fraction),
															"exterior_ceiling_fraction": "{:.3f}".format(exterior_ceiling_fraction),
															"Rwall": "{:2.1f}".format(Rwall),
															"Rroof": "{:2.1f}".format(Rroof),
															"Rfloor": "{:.2f}".format(Rfloor),
															"Rdoors": "{:2.1f}".format(Rdoors),
															"exterior_wall_fraction": "{:.2f}".format(exterior_wall_fraction),
															"glazing_layers": "{:s}".format(glazing_layers),
															"glass_type": "{:s}".format(glass_type),
															"glazing_treatment": "{:s}".format(glazing_treatment),
															"window_frame": "{:s}".format(window_frame),
															"airchange_per_hour": "{:.2f}".format(airchange_per_hour),
															"window_wall_ratio": "{:0.3f}".format(window_wall_ratio),
															"heating_system_type": "{:s}".format(heat_type),
															"auxiliary_system_type": "{:s}".format(aux_type),
															"fan_type": "{:s}".format(fan_type),
															"cooling_system_type": "{:s}".format(cool_type),
															"air_temperature": "{:.2f}".format(init_temp),
															"mass_temperature": "{:.2f}".format(init_temp),
															"over_sizing_factor": "{:.1f}".format(os_rand),
															"cooling_COP": "{:2.2f}".format(COP_A),
															"cooling_setpoint" : "office_cooling",
															"heating_setpoint" : "office_heating"}
							parent_house = glmCaseDict[last_object_key]

							# if we do not use schedules we will assume the initial temp is the setpoint
							if use_flags['use_schedules'] == 0:
								del glmCaseDict[last_object_key]['cooling_setpoint']
								del glmCaseDict[last_object_key]['heating_setpoint']

							last_object_key += 1

							# Need all of the "appliances"
							# Lights
							adj_lights = (0.9 + 0.1 * random.random()) * floor_area / 1000.  # randomize 10# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "lights_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, my_phases[phind-1], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Lights",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "1.0",
															"power_fraction": "{:.2f}".format(config_data["c_pfrac"]),
															"impedance_fraction": "{:.2f}".format(config_data["c_zfrac"]),
															"current_fraction": "{:.2f}".format(config_data["c_ifrac"]),
															"power_pf": "{:.2f}".format(config_data["c_p_pf"]),
															"current_pf": "{:.2f}".format(config_data["c_i_pf"]),
															"impedance_pf": "{:.2f}".format(config_data["c_z_pf"]),
															"base_power": "office_lights*{:.2f}".format(adj_lights)}

							# if we do not use schedules we will assume adj_lights is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_lights)

							last_object_key += 1

							# Plugs
							adj_plugs = (0.9 + 0.2 * random.random()) * floor_area / 1000.  # randomize 20# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "plugs_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, my_phases[phind-1], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Plugs",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "1.0",
															"power_fraction": "{:.2f}".format(config_data["c_pfrac"]),
															"impedance_fraction": "{:.2f}".format(config_data["c_zfrac"]),
															"current_fraction": "{:.2f}".format(config_data["c_ifrac"]),
															"power_pf": "{:.2f}".format(config_data["c_p_pf"]),
															"current_pf": "{:.2f}".format(config_data["c_i_pf"]),
															"impedance_pf": "{:.2f}".format(config_data["c_z_pf"]),
															"base_power": "office_plugs*{:.2f}".format(adj_plugs)}

							# if we do not use schedules we will assume adj_plugs is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_plugs)

							last_object_key += 1

							# Gas Waterheater
							adj_gas = (0.9 + 0.2 * random.random()) * floor_area / 1000. # randomize 20# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "wh_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, my_phases[phind-1], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Gas_waterheater",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "1.0",
															"power_fraction": "0.0",
															"impedance_fraction": "0.0",
															"current_fraction": "0.0",
															"power_pf": "1.0",
															"base_power": "office_gas*{:.2f}".format(adj_gas)}

							# if we do not use schedules we will assume adj_gas is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_gas)

							last_object_key += 1

							# Exterior Lighting
							adj_ext = (0.9 + 0.1 * random.random()) * floor_area / 1000.  # randomize 10# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "ext_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, my_phases[phind-1], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Exterior_lighting",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "0.0",
															"power_fraction": "{:.2f}".format(config_data["c_pfrac"]),
															"impedance_fraction": "{:.2f}".format(config_data["c_zfrac"]),
															"current_fraction": "{:.2f}".format(config_data["c_ifrac"]),
															"power_pf": "{:.2f}".format(config_data["c_p_pf"]),
															"current_pf": "{:.2f}".format(config_data["c_i_pf"]),
															"impedance_pf": "{:.2f}".format(config_data["c_z_pf"]),
															"base_power": "office_exterior*{:.2f}".format(adj_ext)}

							# if we do not use schedules we will assume adj_ext is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_ext)

							last_object_key += 1

							# Occupancy
							adj_occ = (0.9 + 0.1 * random.random()) * floor_area / 1000.  # randomize 10# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "occ_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, my_phases[phind-1], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Occupancy",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "1.0",
															"power_fraction": "0.0",
															"impedance_fraction": "0.0",
															"current_fraction": "0.0",
															"power_pf": "1.0",
															"base_power": "office_occupancy*{:.2f}".format(adj_occ)}

							# if we do not use schedules we will assume adj_occ is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_occ)

							last_object_key += 1

						# end of house object
						# end # office zones (1-5)
						# end  #office floors (1-3)
						# end # total offices needed
						# print('finished iterating over number of offices')
			# Big box - has at least 2 phases and enough load for 6 zones
			#            *or* load is classified to be big boxes
			elif total_comm_houses > 6 and no_of_phases >= 2:
				no_of_bigboxes = int(round(total_comm_houses / 6.))

				if has_phase_A == 1:
					glmCaseDict[last_object_key] = {"object": "transformer_configuration",
													"name": "CTTF_config_A_{:s}".format(my_name),
													"connect_type": "SINGLE_PHASE_CENTER_TAPPED",
													"install_type": "POLETOP",
													"impedance": "0.00033+0.0022j",
													"shunt_impedance": "10000+10000j",
													"primary_voltage": "{:.3f}".format(nom_volt),
													"secondary_voltage": "120",
													"powerA_rating": "100 kVA"}
					last_object_key += 1

				if has_phase_B == 1:
					glmCaseDict[last_object_key] = {"object": "transformer_configuration",
													"name": "CTTF_config_B_{:s}".format(my_name),
													"connect_type": "SINGLE_PHASE_CENTER_TAPPED",
													"install_type": "POLETOP",
													"impedance": "0.00033+0.0022j",
													"shunt_impedance": "10000+10000j",
													"primary_voltage": "{:.3f}".format(nom_volt),
													"secondary_voltage": "120",
													"powerB_rating": "100 kVA"}
					last_object_key += 1

				if has_phase_C == 1:
					glmCaseDict[last_object_key] = {"object": "transformer_configuration",
													"name": "CTTF_config_C_{:s}".format(my_name),
													"connect_type": "SINGLE_PHASE_CENTER_TAPPED",
													"install_type": "POLETOP",
													"impedance": "0.00033+0.0022j",
													"shunt_impedance": "10000+10000j",
													"primary_voltage": "{:.3f}".format(nom_volt),
													"secondary_voltage": "120",
													"powerC_rating": "100 kVA"}
					last_object_key += 1
				# print('iterating over number of big boxes')
				for jjj in range(no_of_bigboxes):
					floor_area_choose = 20000. * (0.5 + 1. * random.random())  # +/- 50#
					ceiling_height = 14.
					airchange_per_hour = 1.5
					Rroof = 19.
					Rwall = 18.3
					Rfloor = 46.
					Rdoors = 3.
					glazing_layers = 'TWO'
					glass_type = 'GLASS'
					glazing_treatment = 'LOW_S'
					window_frame = 'NONE'
					int_gains = 3.6  # W/sf

					glmCaseDict[last_object_key] = {"object": "overhead_line",
													"from": "{:s}".format(my_parent),
													"to": "{:s}_bigbox_meter{:.0f}".format(my_name, jjj),
													"phases": "{:s}".format(commercial_dict[iii]["phases"]),
													"length": "50ft",
													"configuration": "line_configuration_comm{:s}".format(ph)}
					last_object_key += 1

					glmCaseDict[last_object_key] = {"object": "meter",
													"phases": "{:s}".format(commercial_dict[iii]["phases"]),
													"name": "{:s}_bigbox_meter{:.0f}".format(my_name, jjj),
													"groupid": "Commercial_Meter",
													"nominal_voltage": "{:f}".format(nom_volt)}

					last_object_key += 1

					# skew each big box zone identically
					sk = round(2 * random.normalvariate(0, 1))
					skew_value = config_data["commercial_skew_std"] * sk
					if skew_value < -config_data["commercial_skew_max"]:
						skew_value = -config_data["commercial_skew_max"]
					elif skew_value > config_data["commercial_skew_max"]:
						skew_value = config_data["commercial_skew_max"]

					total_index = 0

					for phind in range(no_of_phases):
						glmCaseDict[last_object_key] = {"object": "transformer",
														"name": "{:s}_CTTF_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"phases": "{:s}S".format(ph[phind]),
														"from": "{:s}_bigbox_meter{:.0f}".format(my_name, jjj),
														"to": "{:s}_tm_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"groupid": "Distribution_Trans",
														"configuration": "CTTF_config_{:s}_{:s}".format(ph[phind],
																										my_name)}
						last_object_key += 1

						glmCaseDict[last_object_key] = {"object": "triplex_meter",
														"name": "{:s}_tm_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"phases": "{:s}S".format(ph[phind]),
														"nominal_voltage": "120"}
						last_object_key += 1

						zones_per_phase = int(6. / no_of_phases)
						for zoneind in range(1,zones_per_phase+1):
							total_index += 1
							thermal_mass_per_floor_area = 3.9 * (0.8 + 0.4 * random.random())  # +/- 20#
							floor_area = floor_area_choose / 6.
							exterior_ceiling_fraction = 1.
							aspect_ratio = 1.28301275561855

							total_depth = math.sqrt(floor_area_choose / aspect_ratio)
							total_width = aspect_ratio * total_depth
							d = total_width / 3.
							w = total_depth / 2.
							if total_index == 2 or total_index == 5:
								exterior_wall_fraction = d / (2. * (d + w))
								exterior_floor_fraction = (0. + d) / (2. * (total_width + total_depth)) / (floor_area / floor_area_choose)
							else:
								exterior_wall_fraction = 0.5
								exterior_floor_fraction = (w + d) / (2. * (total_width + total_depth)) / (floor_area / floor_area_choose)

							if total_index == 2:
								window_wall_ratio = 0.76
							else:
								window_wall_ratio = 0.

							if total_index < 4:
								no_of_doors = 0.1  # this will round to 0
							elif total_index == 4 or total_index == 6:
								no_of_doors = 1.
							else:
								no_of_doors = 24.

							interior_exterior_wall_ratio = (floor_area * (2. - 1.) + no_of_doors * 20.) / (no_of_stories * ceiling_height * 2. * (w + d)) - 1. + window_wall_ratio * exterior_wall_fraction

							if total_index > 6:
								raise Exception('Something wrong in the indexing of the retail strip.')

							init_temp = 68. + 4. * random.random()
							os_rand = config_data["over_sizing_factor"] * (0.8 + 0.4 * random.random())
							COP_A = config_data["cooling_COP"] * (0.8 + 0.4 * random.random())
							glmCaseDict[last_object_key] = {"object": "house",
															"name": "bigbox{:s}_{:s}{:.0f}_zone{:.0f}".format(my_name, ph[phind], jjj, zoneind),
															"groupid": "Commercial",
															"motor_model": "BASIC",
															"schedule_skew": "{:.0f}".format(skew_value),
															"parent": "{:s}_tm_{:s}_{:.0f}".format(my_name, ph[phind],jjj),
															"floor_area": "{:.0f}".format(floor_area),
															"design_internal_gains": "{:.0f}".format(int_gains * floor_area * 3.413),
															"number_of_doors": "{:.0f}".format(no_of_doors),
															"aspect_ratio": "{:.2f}".format(aspect_ratio),
															"total_thermal_mass_per_floor_area": "{:1.2f}".format(thermal_mass_per_floor_area),
															"interior_surface_heat_transfer_coeff": "{:1.2f}".format(surface_heat_trans_coeff),
															"interior_exterior_wall_ratio": "{:2.1f}".format(interior_exterior_wall_ratio),
															"exterior_floor_fraction": "{:.3f}".format(exterior_floor_fraction),
															"exterior_ceiling_fraction": "{:.3f}".format(exterior_ceiling_fraction),
															"Rwall": "{:2.1f}".format(Rwall),
															"Rroof": "{:2.1f}".format(Rroof),
															"Rfloor": "{:.2f}".format(Rfloor),
															"Rdoors": "{:2.1f}".format(Rdoors),
															"exterior_wall_fraction": "{:.2f}".format(exterior_wall_fraction),
															"glazing_layers": "{:s}".format(glazing_layers),
															"glass_type": "{:s}".format(glass_type),
															"glazing_treatment": "{:s}".format(glazing_treatment),
															"window_frame": "{:s}".format(window_frame),
															"airchange_per_hour": "{:.2f}".format(airchange_per_hour),
															"window_wall_ratio": "{:0.3f}".format(window_wall_ratio),
															"heating_system_type": "{:s}".format(heat_type),
															"auxiliary_system_type": "{:s}".format(aux_type),
															"fan_type": "{:s}".format(fan_type),
															"cooling_system_type": "{:s}".format(cool_type),
															"air_temperature": "{:.2f}".format(init_temp),
															"mass_temperature": "{:.2f}".format(init_temp),
															"over_sizing_factor": "{:.1f}".format(os_rand),
															"cooling_COP": "{:2.2f}".format(COP_A),
															"cooling_setpoint": "bigbox_cooling",
															"heating_setpoint": "bigbox_heating"}
							parent_house = glmCaseDict[last_object_key]  # cache this for a second...

							# if we do not use schedules we will assume the initial temp is the setpoint
							if use_flags['use_schedules'] == 0:
								del glmCaseDict[last_object_key]['cooling_setpoint']
								del glmCaseDict[last_object_key]['heating_setpoint']

							last_object_key += 1

							# Need all of the "appliances"
							# Lights
							adj_lights = 1.2 * (0.9 + 0.1 * random.random()) * floor_area / 1000.  # randomize 10# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "lights_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, ph[phind], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Lights",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "1.0",
															"power_fraction": "{:.2f}".format(config_data["c_pfrac"]),
															"impedance_fraction": "{:.2f}".format(config_data["c_zfrac"]),
															"current_fraction": "{:.2f}".format(config_data["c_ifrac"]),
															"power_pf": "{:.2f}".format(config_data["c_p_pf"]),
															"current_pf": "{:.2f}".format(config_data["c_i_pf"]),
															"impedance_pf": "{:.2f}".format(config_data["c_z_pf"]),
															"base_power": "bigbox_lights*{:.2f}".format(adj_lights)}

							# if we do not use schedules we will assume adj_lights is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_lights)

							last_object_key += 1

							# Plugs
							adj_plugs = (0.9 + 0.2 * random.random()) * floor_area / 1000.  # randomize 20# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "plugs_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, ph[phind], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Plugs",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "1.0",
															"power_fraction": "{:.2f}".format(config_data["c_pfrac"]),
															"impedance_fraction": "{:.2f}".format(config_data["c_zfrac"]),
															"current_fraction": "{:.2f}".format(config_data["c_ifrac"]),
															"power_pf": "{:.2f}".format(config_data["c_p_pf"]),
															"current_pf": "{:.2f}".format(config_data["c_i_pf"]),
															"impedance_pf": "{:.2f}".format(config_data["c_z_pf"]),
															"base_power": "bigbox_plugs*{:.2f}".format(adj_plugs)}

							# if we do not use schedules we will assume adj_plugs is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_plugs)

							last_object_key += 1

							# Gas Waterheater
							adj_gas = (0.9 + 0.2 * random.random()) * floor_area / 1000.  # randomize 20# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "wh_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, ph[phind], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Gas_waterheater",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "1.0",
															"power_fraction": "0.0",
															"impedance_fraction": "0.0",
															"current_fraction": "0.0",
															"power_pf": "1.0",
															"base_power": "bigbox_gas*{:.2f}".format(adj_gas)}

							# if we do not use schedules we will assume adj_gas is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_gas)

							last_object_key += 1

							# Exterior Lighting
							adj_ext = (0.9 + 0.1 * random.random()) * floor_area / 1000.  # randomize 10# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "ext_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, ph[phind], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Exterior_lighting",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "0.0",
															"power_fraction": "{:.2f}".format(config_data["c_pfrac"]),
															"impedance_fraction": "{:.2f}".format(config_data["c_zfrac"]),
															"current_fraction": "{:.2f}".format(config_data["c_ifrac"]),
															"power_pf": "{:.2f}".format(config_data["c_p_pf"]),
															"current_pf": "{:.2f}".format(config_data["c_i_pf"]),
															"impedance_pf": "{:.2f}".format(config_data["c_z_pf"]),
															"base_power": "bigbox_exterior*{:.2f}".format(adj_ext)}

							# if we do not use schedules we will assume adj_ext is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_ext)

							last_object_key += 1

							# Occupancy
							adj_occ = (0.9 + 0.1 * random.random()) * floor_area / 1000.  # randomize 10# then convert W/sf -> kW
							glmCaseDict[last_object_key] = {"object": "ZIPload",
															"name": "occ_{:s}_{:s}_{:.0f}_zone{:.0f}".format(my_name, ph[phind], jjj, zoneind),
															"parent": parent_house["name"],
															"groupid": "Occupancy",
															# "groupid": "Commercial_zip",
															"schedule_skew": "{:.0f}".format(skew_value),
															"heatgain_fraction": "1.0",
															"power_fraction": "0.0",
															"impedance_fraction": "0.0",
															"current_fraction": "0.0",
															"power_pf": "1.0",
															"base_power": "bigbox_occupancy*{:.2f}".format(adj_occ)}

							# if we do not use schedules we will assume adj_occ is the fixed value
							if use_flags['use_schedules'] == 0:
								glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_occ)

							last_object_key += 1

						# end #zone index
						# end #phase index
						# end #number of big boxes
						# print('finished iterating over number of big boxes')
			# Strip mall
			elif total_comm_houses > 0:  # unlike for big boxes and offices, if total house number = 0, just don't populate anything.
				no_of_strip = total_comm_houses
				strip_per_phase = int(math.ceil(no_of_strip / no_of_phases))

				if has_phase_A == 1:
					glmCaseDict[last_object_key] = {"object": "transformer_configuration",
													"name": "CTTF_config_A_{:s}".format(my_name),
													"connect_type": "SINGLE_PHASE_CENTER_TAPPED",
													"install_type": "POLETOP",
													"impedance": "0.00033+0.0022j",
													"shunt_impedance": "100000+100000j",
													"primary_voltage": "{:.3f}".format(nom_volt),
													"secondary_voltage": "120",
													"powerA_rating": "{:.0f} kVA".format(100. * strip_per_phase)}

					last_object_key += 1

				if has_phase_B == 1:
					glmCaseDict[last_object_key] = {"object": "transformer_configuration",
													"name": "CTTF_config_B_{:s}".format(my_name),
													"connect_type": "SINGLE_PHASE_CENTER_TAPPED",
													"install_type": "POLETOP",
													"impedance": "0.00033+0.0022j",
													"shunt_impedance": "100000+100000j",
													"primary_voltage": "{:.3f}".format(nom_volt),
													"secondary_voltage": "120",
													"powerB_rating": "{:.0f} kVA".format(100. * strip_per_phase)}

					last_object_key += 1

				if has_phase_C == 1:
					glmCaseDict[last_object_key] = {"object": "transformer_configuration",
													"name": "CTTF_config_C_{:s}".format(my_name),
													"connect_type": "SINGLE_PHASE_CENTER_TAPPED",
													"install_type": "POLETOP",
													"impedance": "0.00033+0.0022j",
													"shunt_impedance": "100000+100000j",
													"primary_voltage": "{:.3f}".format(nom_volt),
													"secondary_voltage": "120",
													"powerC_rating": "{:.0f} kVA".format(100. * strip_per_phase)}

					last_object_key += 1

				glmCaseDict[last_object_key] = {"object": "overhead_line",
												"from": "{:s}".format(my_parent),
												"to": "{:s}_strip_node".format(my_name),
												"phases": "{:s}".format(commercial_dict[iii]["phases"]),
												"length": "50ft",
												"configuration": "line_configuration_comm{:s}".format(ph)}
				last_object_key += 1

				glmCaseDict[last_object_key] = {"object": "node",
												"phases": "{:s}".format(commercial_dict[iii]["phases"]),
												"name": "{:s}_strip_node".format(my_name),
												"nominal_voltage": "{:f}".format(nom_volt)}
				last_object_key += 1

				# print('iterating over number of stripmalls')
				for phind in range(no_of_phases):
					floor_area_choose = 2400. * (0.7 + 0.6 * random.random())  # +/- 30#
					# ceiling_height = 12
					airchange_per_hour = 1.76
					Rroof = 19.
					Rwall = 18.3
					Rfloor = 40.
					Rdoors = 3.
					glazing_layers = 'TWO'
					glass_type = 'GLASS'
					glazing_treatment = 'LOW_S'
					window_frame = 'NONE'
					int_gains = 3.6  # W/sf
					thermal_mass_per_floor_area = 3.9 * (0.5 + 1. * random.random())  # +/- 50#
					exterior_ceiling_fraction = 1.

					for jjj in range(1, strip_per_phase+1):
						# skew each office zone identically per floor
						sk = round(2 * random.normalvariate(0, 1))
						skew_value = config_data["commercial_skew_std"] * sk
						if skew_value < -config_data["commercial_skew_max"]:
							skew_value = -config_data["commercial_skew_max"]
						elif skew_value > config_data["commercial_skew_max"]:
							skew_value = config_data["commercial_skew_max"]

						if jjj == 1 or jjj == (math.floor(strip_per_phase / 2.) + 1.):
							floor_area = floor_area_choose
							aspect_ratio = 1.5
							window_wall_ratio = 0.05

							# if (j == jjj):
							#    exterior_wall_fraction = 0.7;
							#    exterior_floor_fraction = 1.4;
							# else:
							exterior_wall_fraction = 0.4
							exterior_floor_fraction = 0.8

							interior_exterior_wall_ratio = -0.05
						else:
							floor_area = floor_area_choose / 2.
							aspect_ratio = 3.0
							window_wall_ratio = 0.03

							if jjj == strip_per_phase:
								exterior_wall_fraction = 0.63
								exterior_floor_fraction = 2.
							else:
								exterior_wall_fraction = 0.25
								exterior_floor_fraction = 0.8

							interior_exterior_wall_ratio = -0.40

						no_of_doors = 1

						glmCaseDict[last_object_key] = {"object": "transformer",
														"name": "{:s}_CTTF_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"phases": "{:s}S".format(ph[phind]),
														"from": "{:s}_strip_node".format(my_name),
														"to": "{:s}_tn_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"groupid": "Distribution_Trans'",
														"configuration": "CTTF_config_{:s}_{:s}".format(ph[phind], my_name)}
						last_object_key += 1

						glmCaseDict[last_object_key] = {"object": "triplex_node",
														"name": "{:s}_tn_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"phases": "{:s}S".format(ph[phind]),
														"nominal_voltage": "120"}
						last_object_key += 1

						glmCaseDict[last_object_key] = {"object": "triplex_meter",
														"parent": "{:s}_tn_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"name": "{:s}_tm_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"phases": "{:s}S".format(ph[phind]),
														"groupid": "Commercial_Meter",
														# was 'real(my_var), imag(my_var), but it's an int above
														"nominal_voltage": "120"}
						last_object_key += 1

						init_temp = 68. + 4. * random.random()
						os_rand = config_data["over_sizing_factor"] * (0.8 + 0.4 * random.random())
						COP_A = config_data["cooling_COP"] * (0.8 + 0.4 * random.random())
						glmCaseDict[last_object_key] = {"object": "house",
														"name": "stripmall{:s}_{:s}{:.0f}".format(my_name, ph[phind], jjj),
														"groupid": "Commercial",
														"motor_model": "BASIC",
														"schedule_skew": "{:.0f}".format(skew_value),
														"parent": "{:s}_tm_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"floor_area": "{:.0f}".format(floor_area),
														"design_internal_gains": "{:.0f}".format(int_gains * floor_area * 3.413),
														"number_of_doors": "{:.0f}".format(no_of_doors),
														"aspect_ratio": "{:.2f}".format(aspect_ratio),
														"total_thermal_mass_per_floor_area": "{:1.2f}".format(thermal_mass_per_floor_area),
														"interior_surface_heat_transfer_coeff": "{:1.2f}".format(surface_heat_trans_coeff),
														"interior_exterior_wall_ratio": "{:2.1f}".format(interior_exterior_wall_ratio),
														"exterior_floor_fraction": "{:.3f}".format(exterior_floor_fraction),
														"exterior_ceiling_fraction": "{:.3f}".format(exterior_ceiling_fraction),
														"Rwall": "{:2.1f}".format(Rwall),
														"Rroof": "{:2.1f}".format(Rroof),
														"Rfloor": "{:.2f}".format(Rfloor),
														"Rdoors": "{:2.1f}".format(Rdoors),
														"exterior_wall_fraction": "{:.2f}".format(exterior_wall_fraction),
														"glazing_layers": "{:s}".format(glazing_layers),
														"glass_type": "{:s}".format(glass_type),
														"glazing_treatment": "{:s}".format(glazing_treatment),
														"window_frame": "{:s}".format(window_frame),
														"airchange_per_hour": "{:.2f}".format(airchange_per_hour),
														"window_wall_ratio": "{:0.3f}".format(window_wall_ratio),
														"heating_system_type": "{:s}".format(heat_type),
														"auxiliary_system_type": "{:s}".format(aux_type),
														"fan_type": "{:s}".format(fan_type),
														"cooling_system_type": "{:s}".format(cool_type),
														"air_temperature": "{:.2f}".format(init_temp),
														"mass_temperature": "{:.2f}".format(init_temp),
														"over_sizing_factor": "{:.1f}".format(os_rand),
														"cooling_COP": "{:2.2f}".format(COP_A),
														"cooling_setpoint": "stripmall_cooling",
														"heating_setpoint": "stripmall_heating"}
						parent_house = glmCaseDict[last_object_key]

						# if we do not use schedules we will assume the initial temp is the setpoint
						if use_flags['use_schedules'] == 0:
							del glmCaseDict[last_object_key]['cooling_setpoint']
							del glmCaseDict[last_object_key]['heating_setpoint']

						last_object_key += 1

						# Need all of the "appliances"
						# Lights
						adj_lights = (0.8 + 0.4 * random.random()) * floor_area / 1000.  # randomize 10# then convert W/sf -> kW
						glmCaseDict[last_object_key] = {"object": "ZIPload",
														"name": "lights_{:s}_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"parent": parent_house["name"],
														"groupid": "Lights",
														# "groupid": "Commercial_zip",
														"schedule_skew": "{:.0f}".format(skew_value),
														"heatgain_fraction": "1.0",
														"power_fraction": "{:.2f}".format(config_data["c_pfrac"]),
														"impedance_fraction": "{:.2f}".format(config_data["c_zfrac"]),
														"current_fraction": "{:.2f}".format(config_data["c_ifrac"]),
														"power_pf": "{:.2f}".format(config_data["c_p_pf"]),
														"current_pf": "{:.2f}".format(config_data["c_i_pf"]),
														"impedance_pf": "{:.2f}".format(config_data["c_z_pf"]),
														"base_power": "stripmall_lights*{:.2f}".format(adj_lights)}

						# if we do not use schedules we will assume adj_lights is the fixed value
						if use_flags['use_schedules'] == 0:
							glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_lights)

						last_object_key += 1

						# Plugs
						adj_plugs = (0.8 + 0.4 * random.random()) * floor_area / 1000.  # randomize 20# then convert W/sf -> kW
						glmCaseDict[last_object_key] = {"object": "ZIPload",
														"name": "plugs_{:s}_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"parent": parent_house["name"],
														"groupid": "Plugs",
														# "groupid": "Commercial_zip",
														"schedule_skew": "{:.0f}".format(skew_value),
														"heatgain_fraction": "1.0",
														"power_fraction": "{:.2f}".format(config_data["c_pfrac"]),
														"impedance_fraction": "{:.2f}".format(config_data["c_zfrac"]),
														"current_fraction": "{:.2f}".format(config_data["c_ifrac"]),
														"power_pf": "{:.2f}".format(config_data["c_p_pf"]),
														"current_pf": "{:.2f}".format(config_data["c_i_pf"]),
														"impedance_pf": "{:.2f}".format(config_data["c_z_pf"]),
														"base_power": "stripmall_plugs*{:.2f}".format(adj_plugs)}

						# if we do not use schedules we will assume adj_plugs is the fixed value
						if use_flags['use_schedules'] == 0:
							glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_plugs)

						last_object_key += 1

						# Gas Waterheater
						adj_gas = (0.8 + 0.4 * random.random()) * floor_area / 1000.  # randomize 20# then convert W/sf -> kW
						glmCaseDict[last_object_key] = {"object": "ZIPload",
														"name": "wh_{:s}_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"parent": parent_house["name"],
														"groupid": "Gas_waterheater",
														# "groupid": "Commercial_zip",
														"schedule_skew": "{:.0f}".format(skew_value),
														"heatgain_fraction": "1.0",
														"power_fraction": "0.0",
														"impedance_fraction": "0.0",
														"current_fraction": "0.0",
														"power_pf": "1.0",
														"base_power": "stripmall_gas*{:.2f}".format(adj_gas)}

						# if we do not use schedules we will assume adj_gas is the fixed value
						if use_flags['use_schedules'] == 0:
							glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_gas)

						last_object_key += 1

						# Exterior Lighting
						adj_ext = (0.8 + 0.4 * random.random()) * floor_area / 1000.  # randomize 10# then convert W/sf -> kW
						glmCaseDict[last_object_key] = {"object": "ZIPload",
														"name": "ext_{:s}_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"parent": parent_house["name"],
														"groupid": "Exterior_lighting",
														# "groupid": "Commercial_zip",
														"schedule_skew": "{:.0f}".format(skew_value),
														"heatgain_fraction": "0.0",
														"power_fraction": "{:.2f}".format(config_data["c_pfrac"]),
														"impedance_fraction": "{:.2f}".format(config_data["c_zfrac"]),
														"current_fraction": "{:.2f}".format(config_data["c_ifrac"]),
														"power_pf": "{:.2f}".format(config_data["c_p_pf"]),
														"current_pf": "{:.2f}".format(config_data["c_i_pf"]),
														"impedance_pf": "{:.2f}".format(config_data["c_z_pf"]),
														"base_power": "stripmall_exterior*{:.2f}".format(adj_ext)}

						# if we do not use schedules we will assume adj_ext is the fixed value
						if use_flags['use_schedules'] == 0:
							glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_ext)

						last_object_key += 1

						# Occupancy
						adj_occ = (0.8 + 0.4 * random.random()) * floor_area / 1000.  # randomize 10# then convert W/sf -> kW
						glmCaseDict[last_object_key] = {"object": "ZIPload",
														"name": "occ_{:s}_{:s}_{:.0f}".format(my_name, ph[phind], jjj),
														"parent": parent_house["name"],
														"groupid": "Occupancy",
														# "groupid": "Commercial_zip",
														"schedule_skew": "{:.0f}".format(skew_value),
														"heatgain_fraction": "1.0",
														"power_fraction": "0.0",
														"impedance_fraction": "0.0",
														"current_fraction": "0.0",
														"power_pf": "1.0",
														"base_power": "stripmall_occupancy*{:.2f}".format(adj_occ)}

						# if we do not use schedules we will assume adj_occ is the fixed value
						if use_flags['use_schedules'] == 0:
							glmCaseDict[last_object_key]['base_power'] = "{:.2f}".format(adj_occ)

						last_object_key += 1
					# end
					# end #number of strip zones
					# end #phase index
					# end #commercial selection
					# print('finished iterating over number of stripmalls')
			# add the "street light" loads
			# parent them to the METER as opposed to the node, so we don't
			# have any "grandchildren"
			elif total_comm_houses == 0 and sum(commercial_dict[iii]['load']) > 0:
				# print('writing street_light')
				glmCaseDict[last_object_key] = {"object": "load",
												"parent": "{:s}".format(my_parent),
												"name": "str_light_{:s}{:s}".format(ph, commercial_dict[iii]['name']),
												"nominal_voltage": "{:.2f}".format(nom_volt),
												"phases": "{:s}".format(ph)
												}
				if has_phase_A == 1 and commercial_dict[iii]['load'][0] > 0:
					if use_flags['use_schedules'] == 1:
						glmCaseDict[last_object_key]["base_power_A"] = "street_lighting*{:f}".format(config_data["light_scalar_comm"] * commercial_dict[iii]['load'][0])
					else:
						glmCaseDict[last_object_key]["base_power_A"] = "{:f}".format(config_data["light_scalar_comm"] * commercial_dict[iii]['load'][0])
					glmCaseDict[last_object_key]["power_pf_A"] = "{:f}".format(config_data["c_p_pf"])
					glmCaseDict[last_object_key]["current_pf_A"] = "{:f}".format(config_data["c_i_pf"])
					glmCaseDict[last_object_key]["impedance_pf_A"] = "{:f}".format(config_data["c_z_pf"])
					glmCaseDict[last_object_key]["power_fraction_A"] = "{:f}".format(config_data["c_pfrac"])
					glmCaseDict[last_object_key]["current_fraction_A"] = "{:f}".format(config_data["c_ifrac"])
					glmCaseDict[last_object_key]["impedance_fraction_A"] = "{:f}".format(config_data["c_zfrac"])

				if has_phase_B == 1 and commercial_dict[iii]['load'][1] > 0:
					if use_flags['use_schedules'] == 1:
						glmCaseDict[last_object_key]["base_power_B"] = "street_lighting*{:f}".format(config_data["light_scalar_comm"] * commercial_dict[iii]['load'][1])
					else:
						glmCaseDict[last_object_key]["base_power_B"] = "{:f}".format(config_data["light_scalar_comm"] * commercial_dict[iii]['load'][1])
					glmCaseDict[last_object_key]["power_pf_B"] = "{:f}".format(config_data["c_p_pf"])
					glmCaseDict[last_object_key]["current_pf_B"] = "{:f}".format(config_data["c_i_pf"])
					glmCaseDict[last_object_key]["impedance_pf_B"] = "{:f}".format(config_data["c_z_pf"])
					glmCaseDict[last_object_key]["power_fraction_B"] = "{:f}".format(config_data["c_pfrac"])
					glmCaseDict[last_object_key]["current_fraction_B"] = "{:f}".format(config_data["c_ifrac"])
					glmCaseDict[last_object_key]["impedance_fraction_B"] = "{:f}".format(config_data["c_zfrac"])

				if has_phase_C == 1 and commercial_dict[iii]['load'][2] > 0:
					if use_flags['use_schedules'] == 1:
						glmCaseDict[last_object_key]["base_power_C"] = "street_lighting*{:f}".format(config_data["light_scalar_comm"] * commercial_dict[iii]['load'][2])
					else:
						glmCaseDict[last_object_key]["base_power_C"] = "{:f}".format(config_data["light_scalar_comm"] * commercial_dict[iii]['load'][2])
					glmCaseDict[last_object_key]["power_pf_C"] = "{:f}".format(config_data["c_p_pf"])
					glmCaseDict[last_object_key]["current_pf_C"] = "{:f}".format(config_data["c_i_pf"])
					glmCaseDict[last_object_key]["impedance_pf_C"] = "{:f}".format(config_data["c_z_pf"])
					glmCaseDict[last_object_key]["power_fraction_C"] = "{:f}".format(config_data["c_pfrac"])
					glmCaseDict[last_object_key]["current_fraction_C"] = "{:f}".format(config_data["c_ifrac"])
					glmCaseDict[last_object_key]["impedance_fraction_C"] = "{:f}".format(config_data["c_zfrac"])

				last_object_key += 1
			# end 'for each load'

	return glmCaseDict, last_object_key


def add_normalized_commercial_ziploads(loadshape_dict, commercial_dict, config_data, last_key):
	"""
	This fucntion appends commercial zip loads to a feeder based on existing loads

	Inputs
		loadshape_dict - dictionary containing the full feeder

		commercial_dict - dictionary that contains information about commercial loads spots

		last_key - Last object key

		config_data - dictionary that contains the configurations of the feeder

	Outputs
		loadshape_dict -  dictionary containing the full feeder

		last_key - Last object key
	"""

	for x in list(commercial_dict.keys()):
		load_name = commercial_dict[x]['name']
		load_parent = commercial_dict[x].get('parent', 'None')
		phases = commercial_dict[x]['phases']
		#nom_volt = commercial_dict[x]['nom_volt']
		nom_volt = '120.0'
		bp_A = commercial_dict[x]['load'][0] * config_data['normalized_loadshape_scalar']
		bp_B = commercial_dict[x]['load'][1] * config_data['normalized_loadshape_scalar']
		bp_C = commercial_dict[x]['load'][2] * config_data['normalized_loadshape_scalar']

		loadshape_dict[last_key] = {'object': 'load',
									'name': '{:s}_loadshape'.format(load_name),
									'phases': phases,
									'nominal_voltage': nom_volt}
		if load_parent != 'None':
			loadshape_dict[last_key]['parent'] = load_parent
		else:
			loadshape_dict[last_key]['parent'] = load_parent

		if 'A' in phases and bp_A > 0.0:
			loadshape_dict[last_key]['base_power_A'] = 'norm_feeder_loadshape.value*{:f}'.format(bp_A)
			loadshape_dict[last_key]['power_pf_A'] = '{:f}'.format(config_data['c_p_pf'])
			loadshape_dict[last_key]['current_pf_A'] = '{:f}'.format(config_data['c_i_pf'])
			loadshape_dict[last_key]['impedance_pf_A'] = '{:f}'.format(config_data['c_z_pf'])
			loadshape_dict[last_key]['power_fraction_A'] = '{:f}'.format(config_data['c_pfrac'])
			loadshape_dict[last_key]['current_fraction_A'] = '{:f}'.format(config_data['c_ifrac'])
			loadshape_dict[last_key]['impedance_fraction_A'] = '{:f}'.format(config_data['c_zfrac'])

		if 'B' in phases and bp_B > 0.0:
			loadshape_dict[last_key]['base_power_B'] = 'norm_feeder_loadshape.value*{:f}'.format(bp_B)
			loadshape_dict[last_key]['power_pf_B'] = '{:f}'.format(config_data['c_p_pf'])
			loadshape_dict[last_key]['current_pf_B'] = '{:f}'.format(config_data['c_i_pf'])
			loadshape_dict[last_key]['impedance_pf_B'] = '{:f}'.format(config_data['c_z_pf'])
			loadshape_dict[last_key]['power_fraction_B'] = '{:f}'.format(config_data['c_pfrac'])
			loadshape_dict[last_key]['current_fraction_B'] = '{:f}'.format(config_data['c_ifrac'])
			loadshape_dict[last_key]['impedance_fraction_B'] = '{:f}'.format(config_data['c_zfrac'])

		if 'C' in phases and bp_C > 0.0:
			loadshape_dict[last_key]['base_power_C'] = 'norm_feeder_loadshape.value*{:f}'.format(bp_C)
			loadshape_dict[last_key]['power_pf_C'] = '{:f}'.format(config_data['c_p_pf'])
			loadshape_dict[last_key]['current_pf_C'] = '{:f}'.format(config_data['c_i_pf'])
			loadshape_dict[last_key]['impedance_pf_C'] = '{:f}'.format(config_data['c_z_pf'])
			loadshape_dict[last_key]['power_fraction_C'] = '{:f}'.format(config_data['c_pfrac'])
			loadshape_dict[last_key]['current_fraction_C'] = '{:f}'.format(config_data['c_ifrac'])
			loadshape_dict[last_key]['impedance_fraction_C'] = '{:f}'.format(config_data['c_zfrac'])

		last_key += last_key

	return loadshape_dict, last_key