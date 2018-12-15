"""
This file contains functions that help build specific distribution feeders:

Created April 11, 2018 by Jacob Hansen (jacob.hansen@pnnl.gov)

Copyright (c) 2018 Battelle Memorial Institute.  The Government retains a paid-up nonexclusive, irrevocable
worldwide license to reproduce, prepare derivative works, perform publicly and display publicly by or for the
Government, including the right to distribute to other Government contractors.
"""
from . import feederConfiguration
from . import technologyConfiguration
from . import feederGenerator
from . import feederRecorders
from . import upgradeEquipment
from . import parseGLM
from . import fncsConfiguration
from . import helicsConfiguration
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

		# add recorders to the GLM
		modifiedGLM = feederRecorders.add_recorders(modifiedGLM, feederConfig, filePath, selectedFeederDict)

		# we need to do extra stuff if we are working with FNCS
		if useFlags['use_FNCS']:
			modifiedGLM = fncsConfiguration.gridlabd_fncs_config(modifiedGLM, selectedFeederDict)

		# we need to do extra stuff if we are working with HELICS
		if useFlags['use_HELICS']:
			modifiedGLM = helicsConfiguration.gridlabd_config(modifiedGLM, selectedFeederDict)	

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
