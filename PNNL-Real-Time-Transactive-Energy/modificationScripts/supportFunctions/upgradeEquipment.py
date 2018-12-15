"""
This file contains functions to upgrade transformers

Created April 16, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""


from . import feederConfiguration
import subprocess, os, math

# kva, %r, %x, %nll, %imag
three_phase = [[30,1.90,1.77,0.79,4.43],
[45,1.75,2.12,0.70,3.94],
[75,1.60,2.42,0.63,3.24],
[112.5,1.45,2.85,0.59,2.99],
[150,1.30,3.25,0.54,2.75],
[225,1.30,3.52,0.50,2.50],
[300,1.30,4.83,0.46,2.25],
[500,1.10,4.88,0.45,2.26],
[750,0.97,5.11,0.44,1.89],
[1000,0.85,5.69,0.43,1.65],
[1500,0.78,5.70,0.39,1.51],
[2000,0.72,5.70,0.36,1.39],
[2500,0.70,5.71,0.35,1.36],
[3750,0.62,5.72,0.31,1.20],
[5000,0.55,5.72,0.28,1.07],
[7500,0.55,5.72,0.28,1.07],
[10000,0.55,5.72,0.28,1.07]]

# kva, %r, %x, %nll, %imag
single_phase = [[5,2.10,1.53,0.90,3.38],
[10,1.90,1.30,0.68,2.92],
[15,1.70,1.47,0.60,2.53],
[25,1.60,1.51,0.52,1.93],
[37.5,1.45,1.65,0.47,1.74],
[50,1.30,1.77,0.45,1.54],
[75,1.25,1.69,0.42,1.49],
[100,1.20,2.19,0.40,1.45],
[167,1.15,2.77,0.38,1.66],
[250,1.10,3.85,0.36,1.81],
[333,1.00,4.90,0.34,1.97],
[500,1.00,4.90,0.29,1.98]]

# leave off intermediate fuse sizes 8, 12, 20, 30, 50, 80, 140
# leave off 6, 10, 15, 25 from the smallest sizes, too easily blown
standard_fuses = [40, 65, 100, 200]
standard_reclosers = [280, 400, 560, 630, 800]
standard_breakers = [600, 1200, 2000]

def FindFuseLimit (amps):
    for row in standard_fuses:
        if row >= amps:
            return row
    for row in standard_reclosers:
        if row >= amps:
            return row
    for row in standard_breakers:
        if row >= amps:
            return row
    return 999999

def Find1PhaseXfmrKva (kva):
	for row in single_phase:
		if row[0] >= kva:
			return row[0], True
	print('WARNING: unable to upgrade single phase transformer anymore')
	return single_phase[-1][0], False

def Find3PhaseXfmrKva (kva):
	for row in three_phase:
		if row[0] >= kva:
			return row[0], True
	print('WARNING: unable to upgrade three phase transformer anymore')		
	return three_phase[-1][0], False

def Find1PhaseXfmr (kva):
	for row in single_phase:
		if row[0] >= kva:
			return row[0], 0.01 * row[1], 0.01 * row[2], 0.01 * row[3], 0.01 * row[4]
	return 0,0,0,0,0

def Find3PhaseXfmr (kva):
	for row in three_phase:
		if row[0] >= kva:
			return row[0], 0.01 * row[1], 0.01 * row[2], 0.01 * row[3], 0.01 * row[4]
	return 0,0,0,0,0

def upgrade_transformers(feederDict, upgradeLevel, upgradeCutOff=1e6):
	"""
	This function upgrades transformers in the feeder

	Inputs
		feederDict - The dictionary that hold the feeder information
		upgradeLevel - a number that describes the levels of upgrade you want to make
		upgradeCutOff - a value for when to not upgrade transformers, smaller number means that only small transformers are upgraded
	Outputs
		feederDict
	"""

	# loop the feeder to find transformer configurations
	for x in feederDict:
		if 'object' in feederDict[x] and feederDict[x]['object'] == 'transformer_configuration':
			# get the current rating
			kvat = float(feederDict[x]['power_rating'])
			originalKvat = kvat

			if kvat < upgradeCutOff and upgradeLevel > 0:
				if 'SINGLE_PHASE_CENTER_TAPPED' in feederDict[x]['connect_type']:
					for idx in range(0, int(upgradeLevel)):
						kvat, flag = Find1PhaseXfmrKva (kvat+1)
						if flag == False:
							break
				else:
					for idx in range(0, int(upgradeLevel)):
						kvat, flag = Find3PhaseXfmrKva (kvat+1)
						if flag == False:
							break
				# adding a comment so that the user can see the change
				feederDict[x]['comment'] = '\t//Upgraded from {:.1f}kva to {:.1f}kva'.format(originalKvat, kvat)

				# get the phases
				phs = ''
				numPhs = 0
				if 'powerA_rating' in feederDict[x] and float(feederDict[x]['powerA_rating']) > 0.:
					phs = phs + 'A'
					numPhs += 1
				if 'powerB_rating' in feederDict[x] and float(feederDict[x]['powerB_rating']) > 0.:
					phs = phs + 'B'
					numPhs += 1
				if 'powerC_rating' in feederDict[x] and float(feederDict[x]['powerC_rating']) > 0.:
					phs = phs + 'C'
					numPhs += 1				

				# adjust the per phase rating
				if numPhs > 0:
					kvaphase = kvat / numPhs
				else:
					kvaphase = kvat

				feederDict[x]['power_rating'] = '{:.2f}'.format(kvat)
				if 'A' in phs:
					feederDict[x]['powerA_rating'] = '{:.2f}'.format(kvaphase)
				if 'B' in phs:
					feederDict[x]['powerB_rating'] = '{:.2f}'.format(kvaphase)
				if 'C' in phs:
					feederDict[x]['powerC_rating'] = '{:.2f}'.format(kvaphase)

				if 'SINGLE_PHASE_CENTER_TAPPED' in feederDict[x]['connect_type']:
					row = Find1PhaseXfmr (kvat)
					feederDict[x]['resistance'] = '{:.5f}'.format(row[1] * 0.5)
					feederDict[x]['resistance1'] = '{:.5f}'.format(row[1])
					feederDict[x]['resistance2'] = '{:.5f}'.format(row[1])
					feederDict[x]['reactance'] = '{:.5f}'.format(row[2] * 0.8)
					feederDict[x]['reactance1'] = '{:.5f}'.format(row[2] * 0.4)
					feederDict[x]['reactance2'] = '{:.5f}'.format(row[2] * 0.4)
					feederDict[x]['shunt_resistance'] = '{:.5f}'.format(1.0 / row[3])
					feederDict[x]['shunt_reactance'] = '{:.5f}'.format(1.0 / row[4])
				else:
					row = Find3PhaseXfmr (kvat)
					feederDict[x]['resistance'] = '{:.5f}'.format(row[1])
					feederDict[x]['reactance'] = '{:.5f}'.format(row[2])
					feederDict[x]['shunt_resistance'] = '{:.5f}'.format(1.0 / row[3])
					feederDict[x]['shunt_reactance'] = '{:.5f}'.format(1.0 / row[4])
	
	return feederDict


def upgrade_fuses(feederDict, upgradeLevel, upgradeCutOff=1e6):
	"""
	This function upgrades fuses in the feeder

	Inputs
		feederDict - The dictionary that hold the feeder information
		upgradeLevel - a number that describes the levels of upgrade you want to make
		upgradeCutOff - a value for when to not upgrade transformers, smaller number means that only small transformers are upgraded
	Outputs
		feederDict
	"""

	# loop the feeder to find transformer configurations
	for x in feederDict:
		if 'object' in feederDict[x] and feederDict[x]['object'] == 'fuse':
			amps = float(feederDict[x]['current_limit'])
			originalAmps = amps

			if amps < upgradeCutOff and upgradeLevel > 0:
				for idx in range(0, int(upgradeLevel)):
					amps = FindFuseLimit (amps+1)

			# adding a comment so that the user can see the change
			feederDict[x]['comment'] = '\t//Upgraded from {:.1f}amps to {:.1f}amps'.format(originalAmps, amps)
			feederDict[x]['current_limit'] = '{:.2f}'.format(amps)

	return feederDict

if __name__ == '__main__':
	pass