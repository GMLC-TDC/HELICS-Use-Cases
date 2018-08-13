"""
Copyright (C) 2017-2018, Argonne National Laboratory
All rights reserved.

This software was developed by Argonne National Laboratory,
A U.S. Department of Energy laboratory managed by UChicago Argonne, LLC.
"""

from __future__ import division
import os
import json
import copy
import string
import socket
import math
import shlex
import six
from subprocess import Popen

import numpy as np
from catchException import PrintException

BUFFER_SIZE=1024

if 'HELICSVVO_DIR' in os.environ.keys():
	dirName=os.environ['HELICSVVO_DIR']
else:
	dirName=os.path.abspath('../')

class PyGldWorker():
	def __init__(self):
		self.sync_ackMsg='1'
		self.sync_endMsg='2'
		a=math.cos(2*math.pi/3)+1j*math.sin(2*math.pi/3)
		self.T=np.array([[1,1,1],[1,a,a*a],[1,a*a,a]])*(1/3)
		self.a=a
		return None

	#========================INIT=======================
	def init(self,host='127.0.0.1',portNum=10500):
		try:
			self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.s.bind((host,portNum))
			self.s.listen(0)
			self.syncConn={}
			self.gldConn={}
			self.IDs=[]
			self.syncServerPortNum=portNum
		except:
			PrintException()
	
	#========================SETUP=======================
	def setup(self,host='127.0.0.1',portNum=12000,\
	fname=dirName+'/data/IEEE13_solar.glm',ID=5,debug=False):
		try:
			if debug:
				self.f_gld_out=open('gld_out_'+str(ID)+'.txt','w')
				self.f_gld_err=open('gld_err_'+str(ID)+'.txt','w')
			else:
				self.f_gld_out=open('/dev/null','w')
				self.f_gld_err=open('/dev/null','w')
			
			gld_directive='gridlabd -D run_realtime=1 -D client_portnum='+\
			str(self.syncServerPortNum)+' -D server_portnum='
			
			self.proc=Popen(shlex.split(gld_directive+str(portNum)+\
			' '+fname+' --server -v'),stdout=self.f_gld_out,stderr=self.f_gld_err,\
			close_fds=True)
			
			self.syncConn[ID]=self.s.accept()# accept connection from gld (sync connection)
			self.gldConn[ID]=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.gldConn[ID].connect((host,portNum))
			self.IDs.append(ID)# add each interface bus ID
		except:
			PrintException()
	
	#========================RUN=======================
	def run(self,Vpu,tol=10**-8,ID=5,monitor=False,iterMax=20):
		"""Gets the complex power injection at PCC for a given PCC voltage setpoint."""
		try:
			Sinj=[0,1]; iteration=0
			while abs(Sinj[0]-Sinj[1])>tol and iteration<iterMax:
				convergence_flg=self.setV(Vpu,ID=ID)
				iteration+=1
				if convergence_flg==1:
					temp,status=self.getS(Vpu,ID=ID)
					if status==1:
						Sinj[1]=Sinj[0]
						Sinj[0]=temp
			
			if monitor==True:
				res=self.monitor(ID)
			else:
				res={}

			return Sinj[0],res,convergence_flg
		except:
			PrintException()

	#========================CLOSE=======================
	def close(self,ID=5):
		try:
			# send msg to gridlabd server and client for graceful shutdown
			qry_shutdown="GET /control/shutdown HTTP/1.1"
			if six.PY2:
				self.gldConn[ID].send(qry_shutdown)
				self.syncConn[ID][0].send(self.sync_endMsg)
			elif six.PY3:
				self.gldConn[ID].send(qry_shutdown.encode())
				self.syncConn[ID][0].send(self.sync_endMsg.encode())

			self.s.shutdown(0)
			self.s.close()
			self.gldConn[ID].shutdown(0)
			self.gldConn[ID].close()
		except:
			PrintException()

	#========================SET VOLTAGE=======================
	def setV(self,VPu,VNominal=2400,ID=5):
		try:
			V=VPu*VNominal
			Vabc=np.complex(V)*np.array([[1],[self.a*self.a],[self.a]])# pos seq to abc

			msg='GET /xml/Node650/voltage_A/'+str(Vabc[0][0].real)+'+0j/'\
			+'/Node650/voltage_B/'+str(Vabc[1][0]).strip('()')\
			+'/Node650/voltage_C/'+str(Vabc[2][0]).strip('()')+' HTTP/1.1\r\n'

			if six.PY2:
				self.gldConn[ID].send(msg)# send msg to gridlabd server
				self.syncConn[ID][0].send(self.sync_ackMsg)# inform gridlabd sync client that we are done setting V
				convergence_flg=int(self.syncConn[ID][0].recv(BUFFER_SIZE))
				reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE)# reply from gridlabd server
			elif six.PY3:
				self.gldConn[ID].send(msg.encode())# send msg to gridlabd server
				self.syncConn[ID][0].send(self.sync_ackMsg.encode())# inform gridlabd sync client that we are done setting V
				convergence_flg=int(self.syncConn[ID][0].recv(BUFFER_SIZE).decode())
				reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE).decode()# reply from gridlabd server

			return convergence_flg
		except:
			PrintException()

	#========================GET COMPLEX POWER INJECTION=======================
	def getS(self,VPu,VNominal=2400,ID=5):
		try:
			V=VPu*VNominal
			Sinj_pos=0+0j
			msg="GET /xml/Reg1/current_in_A/none/Reg1/current_in_B/none/Reg1/current_in_C/none HTTP/1.1\r\n"

			if six.PY2:
				self.gldConn[ID].send(msg)# send msg to gridlabd server
				self.syncConn[ID][0].send(self.sync_ackMsg)# inform gridlabd sync client that we are done setting V
				convergence_flg=int(self.syncConn[ID][0].recv(BUFFER_SIZE))
				reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE)# reply from gridlabd server
			elif six.PY3:
				self.gldConn[ID].send(msg.encode())# send msg to gridlabd server
				self.syncConn[ID][0].send(self.sync_ackMsg.encode())# inform gridlabd sync client that we are done setting V
				convergence_flg=int(self.syncConn[ID][0].recv(BUFFER_SIZE).decode())
				reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE).decode()# reply from gridlabd server
			
			if convergence_flg==1:
				Iabc_str=self.parseHTTPResponse(reply_from_server)

				if len(Iabc_str)>0:
					# now convert to np.complex
					Iabc_list=Iabc_str.split(',')
					Iinj_abc=np.array([np.complex(Iabc_list[2].strip(' A').replace('i','j')),\
					np.complex(Iabc_list[5].strip(' A').replace('i','j')),\
					np.complex(Iabc_list[8].strip(' A').replace('i','j'))])
					Iinj_seq=self.abc2seq(Iinj_abc)
					Sinj_pos=3*np.complex(V)*Iinj_seq[1].conjugate()
				else:# try to request again if an empty string is returned by gridlabd
					self.getS(VPu,VNominal,ID)

			return Sinj_pos,convergence_flg
		except:
			PrintException()

	#=========================PARSE HTTP RESPONSE==================
	def parseHTTPResponse(self,msg):
		try:
			flg=0
			if msg.find("\r\n\r\n")>0: #then CRLF is used as line ending
				startInd=msg.find("\r\n\r\n")+4 # +4 for CRLF CRLF
				flg=1
			elif msg.find("\n\n")>0:#then LF is used as line ending
				startInd=msg.find("\n\n")+2 # +2 for LF LF
				flg=1
			if flg==1:
				msg=msg[startInd::]
			else: # will return empty msg
				msg=''
			return msg
		except:
			PrintException()

#=========================ABC TO SEQUENCE==================
	def abc2seq(self,x_abc):
		try:
			x_seq=self.T.dot(x_abc) # T*x_abc
			return x_seq # seq
		except:
			PrintException()

	#========================SET LOAD=======================
	def setLoad(self,scale,fname=dirName+'/data/loadMap.json',ID=5):
		"""Scales Feeder load."""
		try:
			loadMap=json.load(open(fname))
			msg='GET /xml'

			for loadObj in loadMap:
				for prop in loadMap[loadObj]:
					msg+='/'+loadObj+'/'+prop+'/'+str(math.ceil(loadMap[loadObj][prop]*scale))

			msg+=' HTTP/1.1\r\n'
			
			if six.PY2:
				self.gldConn[ID].send(msg)# send msg to gridlabd server
				self.syncConn[ID][0].send(self.sync_ackMsg)# inform gridlabd sync client that we are done setting V
				convergence_flg=int(self.syncConn[ID][0].recv(BUFFER_SIZE))
				reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE)# reply from gridlabd server
			elif six.PY3:
				self.gldConn[ID].send(msg.encode())# send msg to gridlabd server
				self.syncConn[ID][0].send(self.sync_ackMsg.encode())# inform gridlabd sync client that we are done setting V
				convergence_flg=int(self.syncConn[ID][0].recv(BUFFER_SIZE).decode())
				reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE).decode()# reply from gridlabd server
		except:
			PrintException()

	#=================SET MSG TO SET/GET PROPERTY VALUES=================
	def objVal(self,ID,objName,propName,propVal=['none'],flg='send'):
		"""Send msg to gridlabd server to set/get an object property value.
		if propVal is none, then it is a get operation if not it is a set operation.
		ID - interface_bus_number/id
		objName - object name (should be a list)
		propName - property name (should be a list)
		propVal - value to be set (should be a list)
		flg - 'send' or 'recv'
		"""
		try:
			if isinstance(objName,str):
				objName=list(objName)
			if isinstance(propName,str):
				propName=list(propName)
			if isinstance(propVal,str):
				propVal=list(propVal)

			if flg=='send':
				msg="GET /xml"
				for obj,prop,val in zip(objName,propName,propVal):
					msg+='/'+obj+'/'+prop+'/'+str(val)
				msg+=' HTTP/1.1\r\n'

				if six.PY2:
					self.gldConn[ID].send(msg)# send msg to gridlabd server
					self.syncConn[ID][0].send(self.sync_ackMsg)# inform gridlabd sync client that we are done setting V
				elif six.PY3:
					self.gldConn[ID].send(msg.encode())# send msg to gridlabd server
					self.syncConn[ID][0].send(self.sync_ackMsg.encode())# inform gridlabd sync client that we are done setting V
				reply_from_server=''
			
			elif flg=='recv':
				if six.PY2:
					ack_from_sync_client=int(self.syncConn[ID][0].recv(BUFFER_SIZE))
					reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE)# reply from gridlabd server
				elif six.PY3:
					ack_from_sync_client=int(self.syncConn[ID][0].recv(BUFFER_SIZE).decode())
					reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE).decode()# reply from gridlabd server

			return reply_from_server
		except:
			PrintException()

	#=================GET PROPERTY VALUES=================
	def monitor(self,ID,monMap=dirName+'/data/monitorMap.json'):
		"""Send msg to gridlabd server to set/get an object property value.
		if propVal is none, then it is a get operation if not it is a set operation.
		ID - interface_bus_number/id
		objName - object name (should be a list)
		propName - property name (should be a list)
		flg - 'send' or 'recv'
		"""
		try:
			if isinstance(monMap,str): # then a template file is given
				data=json.load(open(monMap))
			elif isinstance(monMap,dict):
				data=copy.deepcopy(monMap)

			if ID not in data:
				data[ID]=copy.deepcopy(data['1'])

			res={}; res[ID]={}; objName=[]; propName=[]
			for entry in data[ID].keys():
				for item in data[ID][entry]:
					objName.append(entry)
					propName.append(item)

			self.objVal(ID,objName,propName,\
			propVal=['none']*len(propName),flg='send')
			reply=self.parseHTTPResponse(self.objVal(ID,\
			objName,propName,propVal=['none']*len(propName),\
			flg='recv')).split(',')
			
			reply=np.array(reply[0:-1]).reshape(\
			int((len(reply)-1)/3),3)#last entry is an empty value
			
			for obj,prop,val in reply:
				if obj not in res[ID]:
					res[ID][obj]={}
				try:
					if six.PY2:
						res[ID][obj][prop]=float(val.translate(None,\
						string.ascii_letters))
					elif six.PY3:
						res[ID][obj][prop]=float(val.translate(\
						{ord(entry):None for entry in string.ascii_letters}))
				except ValueError:#if translation to float is not possible
					val,debugInfo=self.str2complex(val)
					res[ID][obj][prop+'_mag']=np.abs(val)
					res[ID][obj][prop+'_ang']=np.angle(val)

			return res
		except:
			PrintException()

	#================CONVERT STRING TO COMPLEX NUMBER====================
	def str2complex(self,strData,precision=2):
		"""Converts string returned by gridlabd to a complex number.
		The string can be in polar or rectangular form."""
		try:
			val=0.0; debugInfo=[]
			# first check if the string is in rectangular or polar form
			if 'd' in strData:# string likely contains polar form
				strValue=strData.split(' ')[0]
				dInd=strValue.find('d')
				if 'e' in strValue:# e+- form
					eInd=strValue.find('e')
					try:
						scale=float('1'+strValue[eInd:dInd])#1e+-x form
					except ValueError:
						debugInfo.append([strData,strValue,dInd,eInd])
				else:
					eInd=-1
					scale=1
				strValue=strValue[0:eInd]
				degreeInd=strValue[1::].rfind('+')
				if degreeInd==-1:
					degreeInd=strValue[1::].rfind('-')

				if degreeInd!=-1:
					degreeInd+=1#offset due to str[1::]
					degree=float(strValue[degreeInd::])*scale
					theta=degree*(math.pi/180)# in radians
					magnitude=float(strValue[0:degreeInd])
					val=math.ceil(magnitude*math.cos(theta)*10**precision)*10**-precision+\
					1j*math.ceil(magnitude*math.sin(theta)*10**precision)*10**-precision
				else:
					val=0.0
			elif 'i' in strData: # string likely contains rectangular form
				val=complex(strData.replace('i','j'))
				val=math.ceil(val.real*10**precision)*10**-precision+\
				1j*math.ceil(val.imag*10**precision)*10**-precision

			return val,debugInfo
		except:
			PrintException()

	#========================SET SOLAR=======================
	def setSolar(self,val,ID=5):
		try:
			msg='GET /xml/solar_weather/solar_diffuse/'+str(val)+\
			'/solar_weather/solar_direct/'+str(val)+\
			'/solar_weather/solar_global/'+str(val)+' HTTP/1.1\r\n'
			
			if six.PY2:
				self.gldConn[ID].send(msg)# send msg to gridlabd server
				self.syncConn[ID][0].send(self.sync_ackMsg)# inform gridlabd sync client that we are done setting V
				ack_from_sync_client=int(self.syncConn[ID][0].recv(BUFFER_SIZE))
				reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE)# reply from gridlabd server
			elif six.PY3:
				self.gldConn[ID].send(msg.encode())# send msg to gridlabd server
				self.syncConn[ID][0].send(self.sync_ackMsg.encode())# inform gridlabd sync client that we are done setting V
				ack_from_sync_client=int(self.syncConn[ID][0].recv(BUFFER_SIZE).decode())
				reply_from_server=self.gldConn[ID].recv(BUFFER_SIZE).decode()# reply from gridlabd server
		except:
			PrintException()


