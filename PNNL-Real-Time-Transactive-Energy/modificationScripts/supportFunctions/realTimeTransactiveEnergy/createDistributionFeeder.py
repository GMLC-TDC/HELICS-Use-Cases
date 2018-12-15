"""
This file contains functions that help build specific distribution feeders:

Created April 11, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""
from supportFunctions import feederConfiguration
from supportFunctions import technologyConfiguration
from supportFunctions import feederGenerator
from supportFunctions import feederRecorders
from supportFunctions import upgradeEquipment
from supportFunctions import parseGLM
from supportFunctions import fncsConfiguration
from supportFunctions import helicsConfiguration
from supportFunctions.realTimeTransactiveEnergy import controlConfiguration
from supportFunctions.realTimeTransactiveEnergy import fncsConfiguration as rtteFncsConfiguration
from supportFunctions.realTimeTransactiveEnergy import helicsConfiguration as rtteHelicsConfiguration
import os, traceback, zipfile

def initLock(l):
    global lock
    lock = l

def createDistributionSystem(feederModel, selectedFeederDict, hpc, parallel, randomSeed=10):
	"""
	This function is used to create distribution systems according the user specified settings

	Inputs
		feederModel - the model file for the feeder
		selectedFeederDict - dictionary with the information of the feeder
		randomSeed - this is the random seed so we can reproduce the results

	Outputs
		None
	"""
	try:
		# path for this specific system
		filePath =	selectedFeederDict['experimentFilePath'] / selectedFeederDict['experimentName'] / selectedFeederDict['desiredName']

		# create a folder for the feeder
		os.makedirs(filePath)

		# Get information about the feeder we are working with
		feederConfig = selectedFeederDict['feederConfig']
		useFlags = selectedFeederDict['useFlags']

		# if we are part of a co-simulation then we need to pull our assigned base voltage
		if 'substationkV' in selectedFeederDict:
			feederConfig['substationkV'] = selectedFeederDict['substationkV']

		# Using the settings above we will modify feeder
		modifiedGLM = feederGenerator.modifyFeeder(feederModel, selectedFeederDict, randomSeed)

		# we need to do extra stuff if we are working with FNCS
		if useFlags['use_FNCS']:
			modifiedGLM = fncsConfiguration.gridlabd_fncs_config(modifiedGLM, selectedFeederDict)

		if useFlags['add_real_time_transactive_control']: 
			if selectedFeederDict['add_real_time_transactive_control']:
				modifiedGLM = controlConfiguration.add_residential_controller(modifiedGLM, selectedFeederDict)
			
			if useFlags['use_FNCS']:
				if parallel:
					lock.acquire()
				controlConfiguration.add_lse(selectedFeederDict)
				controlConfiguration.add_dso(selectedFeederDict)
				rtteFncsConfiguration.residential_controllers_fncs_config(modifiedGLM, selectedFeederDict, selectedFeederDict['add_real_time_transactive_control'])
				rtteFncsConfiguration.lse_fncs_config(modifiedGLM, selectedFeederDict)
				rtteFncsConfiguration.dso_fncs_config(selectedFeederDict)
				if parallel:
					lock.release()

			if useFlags['use_HELICS']:
				if parallel:
					lock.acquire()
				controlConfiguration.add_lse(selectedFeederDict)
				controlConfiguration.add_dso(selectedFeederDict)
				rtteHelicsConfiguration.gridlabd_config(modifiedGLM, selectedFeederDict, selectedFeederDict['add_real_time_transactive_control'])	
				rtteHelicsConfiguration.lse_config(modifiedGLM, selectedFeederDict)
				if parallel:
					lock.release()

		# add recorders to the GLM
		modifiedGLM = feederRecorders.add_recorders(modifiedGLM, feederConfig, filePath, selectedFeederDict)

		# write the new feeder model to a file
		glmString = parseGLM.sortedWrite(modifiedGLM)

		if hpc:
			# write to zip
			zipf = zipfile.ZipFile(filePath / str(selectedFeederDict['desiredName'] + '.zip'), 'w', zipfile.ZIP_DEFLATED)
			zipf.writestr(selectedFeederDict['desiredName'] + '.glm', glmString)
			zipf.close()
		else:
			# write the glm to a file
			glmFile = open(filePath / str(selectedFeederDict['desiredName'] + '.glm'), 'w')
			glmFile.write(glmString)
			glmFile.close()
	except:
		return traceback.format_exc()
	else:
		return True
