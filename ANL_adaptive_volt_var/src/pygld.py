"""
Copyright (C) 2017-2018, Argonne National Laboratory
All rights reserved.

This software was developed by Argonne National Laboratory,
A U.S. Department of Energy laboratory managed by UChicago Argonne, LLC.
"""

from __future__ import division
import os
import sys
import math
import json

import helics as h
from pygld_worker import PyGldWorker
from catchException import PrintException

if 'HELICSVVO_DIR' in os.environ.keys():
	dirName=os.environ['HELICSVVO_DIR']
else:
	dirName=os.path.abspath('../')

class PyGld():
	def __init__(self):
		self.pyGldWorker=PyGldWorker()
		return None

	#========================INIT=======================
	def init(self,host='127.0.0.1',portNum=10500):
		try:
			self.pyGldWorker.init(host=host,portNum=portNum)
		except:
			PrintException()

	#========================SETUP=======================
	def setup(self,fedName='pyGld',portNum=12000,ID=5):
		try:
			fedName+='_'+str(ID)
			self.fedName=fedName
			
			# setup helics
			self.fi=fi=h.helicsFederateInfoCreate() # create info obj
			status = h.helicsFederateInfoSetFederateName(fi,fedName)
			status = h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
			status = h.helicsFederateInfoSetCoreInitString(fi,"--federates=1")
			status = h.helicsFederateInfoSetTimeDelta(fi,300)# 5 min dispatch interval
			self.vf=vf=h.helicsCreateValueFederate(fi)
			self.pub = h.helicsFederateRegisterGlobalPublication(vf,fedName, "string", "")
			self.sub=h.helicsFederateRegisterSubscription(vf,"adaptive_volt_var", "string", "")
			status = h.helicsFederateEnterExecutionMode(vf)

			# setup worker
			self.pyGldWorker.setup(portNum=portNum,ID=ID)
		except:
			PrintException()

	#========================RUN=======================
	def run(self,dt=300.0,ID=5,\
	scale={5:0.0000009, 7:0.000001, 9:0.00000125},monitor=False,\
	inv_nominalV={5:480.0, 7:480.0, 9:480.0},msgSize=1024):
		try:
			Res=[];res={}
			simTime=0.0; comm_end=0
			while comm_end==0:
				grantedTime=h.helicsFederateRequestTime(self.vf,simTime)
				status,msg=h.helicsSubscriptionGetString(self.sub)# receive from pyPflow
				simTime+=dt
				
				if 'setpoint' in msg:
					msg=eval(msg)

					if ID in msg['setpoint']:
						propVal=[]
						for entry in msg['setpoint'][ID]:
							propVal.append(entry[0])
							propVal.append(entry[1])

						objName=['solar_inv']*8
						propName=['V1','Q1','V2','Q2','V3','Q3','V4','Q4']
						self.pyGldWorker.objVal(ID,objName,propName,propVal,flg='send')# set new QV curve
						self.pyGldWorker.objVal(ID,objName,propName,['none']*len(propVal),flg='recv')# set new QV curve

					status = h.helicsPublicationPublishString(self.pub,'Received QV curve')
					grantedTime=h.helicsFederateRequestTime(self.vf,simTime)# sync at this point
					simTime+=dt
				else:
					msg=eval(msg)
					if 'comm_end' in msg:
						if msg['comm_end']==1:
							comm_end=1
							if len(res)>0:
								Res.append(res)

					if comm_end==0:
						# set load if requested
						if 'set' in msg['mpc'].keys():
							if 'loadShape' in msg['mpc']['set'].keys():
								self.pyGldWorker.setLoad(msg['mpc']['set']['loadShape'],ID=ID)
								self.pyGldWorker.setSolar(msg['mpc']['set']['solarShape'],ID=ID)
								if len(res)>0:
									Res.append(res)

						Vpu=0
						for entry in msg['mpc']['get']['V']:
							if entry[0]==ID:
								Vpu=entry[1]

						Pd=0; Qd=0
						if Vpu!=0:
							Sinj,res,convergence_flg=self.pyGldWorker.run(Vpu,ID=ID,monitor=monitor) # will call gridlabd server
							if convergence_flg==1:
								Pd=Sinj.real*scale[ID]
								Qd=Sinj.imag*scale[ID]

						msg={}; msg['mpc']={}
						msg['mpc']['set']={}; msg['mpc']['get']={}
						if Pd!=0 and Qd!=0:
							msg['mpc']['set']['Pd']=[[ID,1,math.ceil(Pd*10**6)*10**-6]]
							msg['mpc']['set']['Qd']=[[ID,1,math.ceil(Qd*10**6)*10**-6]]
							msg['mpc']['get']['V']=[[ID,0,0]]
							msg['mpc']['set']['solar_V']=math.ceil(min([\
							res[ID]['solar_meter']['measured_voltage_A_mag']/inv_nominalV[ID]*math.sqrt(3),\
							res[ID]['solar_meter']['measured_voltage_B_mag']/inv_nominalV[ID]*math.sqrt(3),\
							res[ID]['solar_meter']['measured_voltage_C_mag']/inv_nominalV[ID]*math.sqrt(3)\
							])*10**4)*10**-4
							msg['mpc']['set']['solar_Q']=\
							math.ceil(-res[ID]['solar_meter']['measured_reactive_power']/\
							(res[ID]['solar_inv']['rated_power']*3)*10**2)*10**-2 # rated power is per phase

						# send
						status = h.helicsPublicationPublishString(self.pub,str(msg))# publish Sinj as fedName
						grantedTime=h.helicsFederateRequestTime(self.vf,simTime)# sync at this point
						simTime+=dt
			if monitor==True:
				json.dump(Res,open(dirName+'/results/res_'+str(ID)+'.json','w'))
		except:
			PrintException()

	#========================CLOSE=======================
	def close(self,ID=5):
		try:
			h.helicsFederateFree(self.vf)
			h.helicsCloseLibrary()
			self.pyGldWorker.close(ID=ID)
		except:
			PrintException()

#========================RUN AS SCRIPT=======================
if __name__=="__main__":
	"""Sample call: python pyGld.py ID=5 client_portNum=10500 server_portNum=12000"""
	try:
		options={}; options['ID']=5; options['client_portNum']=10500; options['server_portNum']=12000
		for n in range(1,len(sys.argv)):
			arg,val=sys.argv[n].split('=')
			if arg in options:
				options[arg]=int(val)

		ID,client_portNum,server_portNum=options['ID'],options['client_portNum'],options['server_portNum']

		gld=PyGld()
		gld.init(portNum=client_portNum)
		gld.setup(portNum=server_portNum,ID=ID)
		gld.run(ID=ID,monitor=True)
		gld.close(ID=ID)
	except:
		PrintException()




