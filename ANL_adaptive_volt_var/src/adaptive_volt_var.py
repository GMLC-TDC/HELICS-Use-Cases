"""Python interface for PFLOW. Both pyPflow and pyGld (python interface for gridlabd) runs with same
dispatch interval (dt). A tight-coupling scheme is used where information exchange between T&D
interface is iterated until stable boundary condition is obtained. HELICS is used to pass messages
between T&D systems. Time-management is handled internally by pyPflow and pyGld.

Copyright (C) 2017-2018, Argonne National Laboratory
All rights reserved.

This software was developed by Argonne National Laboratory,
A U.S. Department of Energy laboratory managed by UChicago Argonne, LLC.
"""

from __future__ import division
import os
import sys
import json
import six

import zmq
import helics as h
import numpy as np

from catchException import PrintException


if 'HELICSVVO_DIR' in os.environ.keys():
	dirName=os.environ['HELICSVVO_DIR']
else:
	dirName=os.path.abspath('../')

class PyPflow():
	def __init__(self):
		return None

#========================INIT=======================
	def init(self,portNum=10000):
		try:
			# connect to pflow
			context = zmq.Context()
			socket = context.socket(zmq.REQ)
			socket.connect("tcp://localhost:"+str(portNum))
			self.socket=socket
		except:
			PrintException()

	#========================SETUP=======================
	def setup(self,ID):
		"""ID needs to be a list that contains all the T&D interface nodes."""
		try:
			# read solar mapping
			self.solarData=np.genfromtxt(dirName+'/data/solar_diffusion_map.csv',\
			delimiter=',')

			self.ID=ID
		
			# set up comm with helics
			self.fi=fi = h.helicsFederateInfoCreate() # create info obj
			status = h.helicsFederateInfoSetFederateName(fi,"pyPflow")
			status = h.helicsFederateInfoSetCoreTypeFromString(fi, "zmq")
			status = h.helicsFederateInfoSetCoreInitString(fi,"--federates=1")
			status = h.helicsFederateInfoSetTimeDelta(fi,300)# 5 min dispatch interval
			status = h.helicsFederateInfoSetLoggingLevel(fi,1)
			self.vf=vf=h.helicsCreateValueFederate(fi)
			self.pub=pub = h.helicsFederateRegisterGlobalPublication(vf, "adaptive_volt_var", "string", "")
			
			self.sub=sub={}
			for entry in ID:# subscribe to all IDs
				sub['pyGld_'+str(entry)]= h.helicsFederateRegisterSubscription(vf,'pyGld_'+str(entry), "string", "")

			status = h.helicsFederateEnterExecutionMode(vf)

			# Read schema
			f=open(dirName+'/data/schema_case9.json')
			self.data = eval(f.read())
			f.close()
			
			# add V in schema for all subscriptions
			for entry in ID:
				self.data['mpc']['get']['V'].append([entry,0,0])
			
			# run initial PFLOW (base case condition as read from .m file)
			self.socket.send_string(json.dumps(self.data))# send instructions to pflow
			self.msgFromPflow = eval(self.socket.recv())# receive data from pflow
			
		except:
			PrintException()

	#========================RUN=======================
	def run(self,dt=300.0,nDis=5,tol=10**-3,\
	pflowFname=dirName+'/results/pflowRes.json',adaptive=False,iterMax=10,\
	msgSize=1024):
		try:
			simTime=0.0; comm_end=0; pflowRes=[]; setPoint={}; sensitivity_info={}
			sensitivity_info['inv']={5:0.025,7:0.025,9:0.025}
			sensitivity_info['pcc']={5:0.01,7:0.01,9:0.01}
			iteration=0
			dispatchNo=1

			while comm_end==0:
				#send (set V at distribution side)
				self.msgFromPflow['mpc'].pop('set')
				self.msgFromPflow['mpc']['set']={}
				
				if iteration==0:#set load at iteration 0
					self.__setDcopfData(self.msgFromPflow,dispatchNo,'gld')
					boundaryConditionCheck=np.zeros(shape=(len(self.ID),2))

				if adaptive and 'flg' in setPoint and setPoint['flg']==1:# change QV curve if needed
					setPoint.pop('flg'); temp_setpoint={}; temp_setpoint['setpoint']=setPoint
					temp_setpoint=str(temp_setpoint).replace(' ',''); setPoint={}

					status = h.helicsPublicationPublishString(self.pub,temp_setpoint)
					grantedTime=h.helicsFederateRequestTime(self.vf,simTime)
					simTime+=dt
					grantedTime=h.helicsFederateRequestTime(self.vf,simTime)

					for ID in self.ID:# receive from GLD
						errFlg,temp=h.helicsSubscriptionGetString(self.sub['pyGld_'+str(ID)])
						temp=eval(temp)
					simTime+=dt
				else:
					status = h.helicsPublicationPublishString(self.pub,str(self.msgFromPflow))# will send msg i.e. Vpcc to all 
					# distribution feeders that are subscribers of publisher called pyPflow
					grantedTime=h.helicsFederateRequestTime(self.vf,simTime)
					simTime+=dt

					#recv (getS from distribution side)
					grantedTime=h.helicsFederateRequestTime(self.vf,simTime)
				
					msgFromGld={}; msgFromGld['mpc']={}
					msgFromGld['mpc']['set']={}; msgFromGld['mpc']['get']={}
					setData=msgFromGld['mpc']['set']; getData=msgFromGld['mpc']['get']
					setData['Pd']=[]; setData['Qd']=[]; getData['V']=[];

					inv_volt={}; inv_Q={};
					for ID in self.ID:
						errFlg,temp=h.helicsSubscriptionGetString(self.sub['pyGld_'+str(ID)])
						temp=eval(temp)

						setData['Pd'].append(temp['mpc']['set']['Pd'][0])
						setData['Qd'].append(temp['mpc']['set']['Qd'][0])
						getData['V'].append(temp['mpc']['get']['V'][0])
						inv_volt[ID]=temp['mpc']['set']['solar_V']
						inv_Q[ID]=temp['mpc']['set']['solar_Q']
					simTime+=dt

					# run PFLOW (setS and getV from transmission side)
					if iteration==0:#set load at iteration 0
						self.__setDcopfData(msgFromGld,dispatchNo,'pflow')

					self.socket.send_string(json.dumps(msgFromGld))# send instructions to pflow
					self.msgFromPflow = eval(self.socket.recv())# receive data from pflow
					iteration+=1

					# check boundary condition
					V=np.array(self.msgFromPflow['mpc']['get']['V'])

					pcc_volt={}
					for ID in self.ID:
						pcc_volt[ID]=V[V[:,0]==ID,1][0]

					count=0
					for ID in self.ID:
						boundaryConditionCheck[count,1]=boundaryConditionCheck[count,0]
						boundaryConditionCheck[count,0]=V[V[:,0]==ID,1][0]
						count+=1

					if np.all(abs(boundaryConditionCheck[:,0]-boundaryConditionCheck[:,1])<tol):
						# check for QV setting
						if adaptive:
							setPoint=self.setQvCurve(pcc_volt,inv_volt,inv_Q,sensitivity_info)
						else:
							setPoint={};setPoint['flg']=0

						# implies no adaptive changes are required or max iterations have been exceeded
						if setPoint['flg']==0 or iteration>iterMax:
							six.print_("Completed Dispath Number: ",dispatchNo)
							pflowRes.append([self.msgFromPflow,msgFromGld])# store pflow result
							iteration=0 # reset iteration for the new dispatch
							if dispatchNo==nDis:
								comm_end=1
								commEndMsg={}; commEndMsg['comm_end']=1
								status = h.helicsPublicationPublishString(self.pub,str(commEndMsg))# send shutdown signal
								grantedTime=h.helicsFederateRequestTime(self.vf,simTime)
								self.socket.send_string("COMM_END")
								msgFromPflow = self.socket.recv()
							else:
								dispatchNo+=1

			# save results
			json.dump(pflowRes,open(pflowFname,'w'))
		except:
			PrintException()

	#========================CLOSE=======================
	def close(self):
		try:
			h.helicsFederateFree(self.vf)
			h.helicsCloseLibrary()
		except:
			PrintException()

	#========================SET DATA=======================
	def __setDcopfData(self,msg,dispatchNo,destination,\
	fname=dirName+'/data/multiperiod_dcopf_res.json',maxSolar=95348.0):
		"""Reads dcopf data from matpower in .json format and packs the data in a 
		format that is understood by PFLOW (contained in msg) for a given dispatch."""
		try:
			data=json.load(open(fname))
			if destination.lower()=='pflow':
				dispatchData=data['dispatch_'+str(dispatchNo)]
				msg['mpc']['set']['Pg']=dispatchData['Pg']
			elif destination.lower()=='gld':
				#data['loadShape'][dispatchNo-1] is total load seen at T side i.e.
				# load-solar. data['dispatch_'+str(dispatchNo)]['solar'] is 
				# solar power.
				msg['mpc']['set']['loadShape']=data['loadShape'][dispatchNo-1]+\
				data['solarShape'][dispatchNo-1]

				ind=np.where(self.solarData[:,1]>=data['solarShape']\
				[dispatchNo-1]*(1/max(data['solarShape']))*maxSolar)[0][0]
				msg['mpc']['set']['solarShape']=self.solarData[ind,0]
		except:
			PrintException()

	#========================QV CURVE=======================
	def setQvCurve(self,pcc_volt,inv_volt,inv_Q,sensitivity_info,minV=0.95,maxV=1.05,tol=0.01):
		try:
			# check current voltage levels
			setPoint={}; setPoint['flg']=0
			# TODO: json.encoder.FLOAT_REPR did not work. need a better workaround.
			float_repr=lambda x: [round(entry,2) for entry in x]

			for ID in pcc_volt:
				if pcc_volt[ID]<minV:
					violation_lower=minV-pcc_volt[ID]
					Q=inv_Q[ID] # current Q. All phases produce same Q

					if Q<1:# if current Q gen is already at max inverter rating nothing more can be done
						Vreq=inv_volt[ID]+(sensitivity_info['inv'][ID]/sensitivity_info['pcc'][ID])*violation_lower
						V1,V2,V3,V4=inv_volt[ID]-tol,Vreq+tol,Vreq+tol,1.1
						Qsetpoint=min(1.0,(violation_lower/sensitivity_info['pcc'][ID])+Q)
						Q1,Q2,Q3,Q4=Qsetpoint,Qsetpoint,Qsetpoint,-0.25
						setPoint[ID]=[float_repr([V1,Q1]),float_repr([V2,Q2]),\
						float_repr([V3,Q3]),float_repr([V4,Q4])]
						setPoint['flg']=1

			return setPoint
		except:
			PrintException()

#========================RUN AS SCRIPT=======================
if __name__=="__main__":
	"""Sample call: python pyPflow.py nDis=4 adaptive=1 ID=5,7,9
	will run the 9-bus test case with loads 5,7 and 9 replaced by distribution feeders for 4 dispatches
	with dt=5 minute and with adaptive volt/var setting."""
	try:
		options={}; options['nDis']=6; options['ID']=[]; options['adaptive']=1
		for n in range(1,len(sys.argv)):
			arg,val=sys.argv[n].split('=')
			if arg in options:
				if arg=='ID':
					for entry in val.split(","):
						options[arg].append(int(entry))
				else:
					options[arg]=int(val)
		
		if options['adaptive']==1:
			options['adaptive']=True
		else:
			options['adaptive']=False
			
		nDis,ID,adaptive=options['nDis'],options['ID'],options['adaptive']

		six.print_('\nStarting Co-sim with tight coupling protocol for {} dispatches.'.format(nDis))
		six.print_('Interfaced {} feeders to T side.\n'.format(len(ID)))

		pflow=PyPflow()
		pflow.init()
		pflow.setup(ID=ID)
		pflow.run(nDis=nDis,adaptive=adaptive)
		pflow.close()
	except:
		PrintException()

