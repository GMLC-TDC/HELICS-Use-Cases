import static org.junit.Assert.assertTrue;

import java.util.Hashtable;
import java.util.Map.Entry;
import java.util.logging.Level;

import org.apache.commons.math3.complex.Complex;
import org.ieee.odm.adapter.IODMAdapter.NetType;
import org.interpss.numeric.datatype.Complex3x1;
import org.interpss.numeric.datatype.Complex3x3;
import org.interpss.numeric.datatype.ComplexFunc;
import org.interpss.pssl.plugin.IpssAdapter.FileImportDSL;
import org.interpss.pssl.plugin.cmd.AclfDslRunner;
import org.interpss.pssl.plugin.cmd.json.BaseJSONBean;
import org.interpss.pssl.plugin.cmd.json.DstabRunConfigBean;
import org.interpss.pssl.simu.IpssDStab;
import org.interpss.util.FileUtil;
import org.ipss.threePhase.basic.Branch3Phase;
import org.ipss.threePhase.basic.Bus3Phase;
import org.ipss.threePhase.dynamic.DStabNetwork3Phase;
import org.ipss.threePhase.dynamic.algo.DynamicEventProcessor3Phase;
import org.ipss.threePhase.powerflow.DistributionPowerFlowAlgorithm;
import org.ipss.threePhase.powerflow.impl.DistPowerFlowOutFunc;
import org.ipss.threePhase.test.Test_GC_12_47_1_Feeder;
import org.ipss.threePhase.util.ThreePhaseAclfOutFunc;
import org.ipss.threePhase.util.ThreePhaseObjectFactory;
import org.pnnl.gov.pssl.CoSimConfigBean;

import com.interpss.common.exp.InterpssException;
import com.interpss.common.util.IpssLogger;
import com.interpss.core.net.Branch;
import com.interpss.dstab.cache.StateMonitor;
import com.interpss.dstab.common.IDStabSimuOutputHandler;
import com.interpss.dstab.mach.EConstMachine;
import com.java.helics.SWIGTYPE_p_void;
import com.java.helics.helics;

public class DistCoSimDslRunner extends CoSimDslRunner{
	
	@Override
	public <T> T run(BaseJSONBean bean) throws InterpssException {
        if(!(bean instanceof DstabRunConfigBean))
			try {
				throw new Exception("The input bean is not of DstabRunConfigBean type!");
			} catch (Exception e1) {
				
				e1.printStackTrace();
			}
		
        dstabBean = (DstabRunConfigBean) bean;
		
//		FileImportDSL inDsl =  new FileImportDSL();
//		inDsl.setFormat(dstabBean.acscConfigBean.runAclfConfig.format)
//			 .setPsseVersion(dstabBean.acscConfigBean.runAclfConfig.version)
//		     .load(NetType.DStabNet,new String[]{dstabBean.acscConfigBean.runAclfConfig.aclfCaseFileName,
//		    		 dstabBean.acscConfigBean.seqFileName,
//		    		 dstabBean.dynamicFileName});
//		
//		// map ODM to InterPSS model object
//		try {
//			net = inDsl.getImportedObj();
//		} catch (InterpssException e) {
//			e.printStackTrace();
//			return (T)null;
//		}	
        Test_GC_12_47_1_Feeder feeder = new Test_GC_12_47_1_Feeder();
        String feederDefPath = "testData/gldFeeders/GC-12.47-1_impedance_dump.xml";
		
        this.net = feeder.createTestFeeder(feederDefPath, 12470,480,28,3,"",100.0);
					
		IDStabSimuOutputHandler outputHdler =null;
		try {
			outputHdler = runDstab(dstabBean);
			
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
		
		//output the result
        
		if(!dstabBean.dstabOutputFileName.equals("")){
			FileUtil.write2File(dstabBean.dstabOutputFileName, outputHdler.toString().getBytes());
			IpssLogger.getLogger().info("Ouput written to " + dstabBean.dstabOutputFileName);
		}
		

		return (T) outputHdler;
	}
	
	
	@Override
	protected IDStabSimuOutputHandler runDstab(DstabRunConfigBean configBean) throws Exception {
	    
		
	   // read simulation configuration
		coSimConfigBean = (CoSimConfigBean) configBean;
		
		String federateName = coSimConfigBean.federateName;
		
		if(federateName==null || federateName.equals(""))
			federateName = DEFAULT_FEDERATE_NAME;
		
		double timeStep = coSimConfigBean.simuTimeStepSec;
		String[] boundaryBuses =coSimConfigBean.boundaryBusAry;
		
		
		//----------------------------------------------------------
		// step-1 set up helics federate
		//-----------------------------------------------------------

	   // !! all helics functions are accessed with static
		
	   // create the federate infomation object
		IpssLogger.getLogger().info("calling create helics federateInfo object");
	   SWIGTYPE_p_void fi= helics.helicsFederateInfoCreate();
	   
	   // set core_type
	   helics.helicsFederateInfoSetCoreTypeFromString(fi, DEFAULT_CORE_TYPE);
	   
	   // set timeDelta, unit in second
	   helics.helicsFederateInfoSetTimeDelta(fi, timeStep);
	   
	   helics.helicsFederateInfoSetCoreName(fi, federateName);
	   
	   //TODO refer to tutorial slide #26
	  
	   //int coreNum = 1;
	   helics.helicsFederateInfoSetCoreInitString(fi, Integer.toString(coSimConfigBean.numberOfCores));//Integer.toString(coreNum));//
	   
	   
	   // create the value federate 
	   IpssLogger.getLogger().info("calling create helics value federate object");
	   SWIGTYPE_p_void vFed1 = helics.helicsCreateValueFederate(fi);
	   
	   String publishedParameter = coSimConfigBean.publishedParamters;
	   String subscribedParameter = coSimConfigBean.subscribedParamters;
	   
	   for (int i = 0; i<coSimConfigBean.boundaryBusAry.length;i++) {
		   String busId = coSimConfigBean.boundaryBusAry[i];
		   
		   if( this.net.getBus(busId)!=null){
			   this.boundaryBusIds.add(busId);
			   
			   HelicsPublication hp = new HelicsPublication();
			   HelicsSubscription hs = new HelicsSubscription();
			   
			   hp.setBusId(busId);
			   hp.setObjectName(publishedParameter);
			   hp.setParameterType(coSimConfigBean.publishedParamterType);
			   hp.setTopicName(coSimConfigBean.publishedTopicNames[i]);
			   
			   helicsPublications.put(hp.getTopicName(), hp);
			   
			   
			   hs.setBusId(busId);
			   hs.setObjectName(subscribedParameter);
			   hs.setParameterType(coSimConfigBean.subscribedParamterType);
			   hs.setTopicName(coSimConfigBean.subscribedTopicNames[i]);
			   
			   helicsSubscriptions.put(hs.getTopicName(), hs);
			   
		   }
		   else {
			   throw new Error("The boundary busId in the boundaryBusAry of coSim configuration file is not found in the system :"+busId);
		   }
	   }
	   
	   //assertTrue(helics.)
	   
	   //register helics publications
	   
	   //NOte: follow https://github.com/gridlab-d/gridlab-d/blob/feature/1024/connection/helics_msg.cpp 
	   //       starting at line #290
	   IpssLogger.getLogger().info("start to register helics publications");
	   
	   for(HelicsPublication hp :helicsPublications.values()) {
		   SWIGTYPE_p_void  pubId = helics.helicsFederateRegisterPublication(vFed1, hp.getTopicName(), hp.getParameterType(), "");
		   
		    hp.setHelicsPublicationId(pubId);
	   }
	   
	   
	   //register helics subscriptions
	   IpssLogger.getLogger().info("start to register helics subscriptions");
	   for(HelicsSubscription hs :helicsSubscriptions.values()) {
		   // subId is a pointer
//		   SWIGTYPE_p_void  subId = helics.helicsFederateRegisterSubscription(vFed1, hs.getTopicName(), hs.getParameterType(), "");
		   
		   SWIGTYPE_p_void  subId = helics.helicsFederateRegisterOptionalSubscription(vFed1, hs.getTopicName(), hs.getParameterType(), "");
		   
		   hs.setHelicsSubscriptionId(subId);
	   }
	  
	   
	   
	   //Helics enterIterization stage - start the power flow iteration
	   
	   IpssLogger.getLogger().info("calling helicsEnterInitializationMode");
	   helics.helicsFederateEnterInitializationMode(vFed1);
	   IpssLogger.getLogger().info("completed helicsEnterInitializationMode");
	 
	   
	   //---------------------------------------------------------------------
	   // step-2 run power flow 
	   //---------------------------------------------------------------------
	   

	   IpssDStab dstabDSL = new IpssDStab(net);
	   
	   //------------------------------------------
	   //TODO uncomment this part only when iteration is supported
       //------------------------------------------
	   
	// 1) get the boundary bus voltage results 
	   subscribeVariables(this.boundaryBusPosSeqVolt);
	   
	   
	   if(this.boundaryBusPosSeqVolt.size()==1) {
    	   for(Entry<String, Complex> e:this.boundaryBusPosSeqVolt.entrySet()) {
	    	   String busId = e.getKey();
	    	   Complex voltPU = e.getValue();
	    	   
	    	   if(voltPU.abs()>0.90) {
		    	   Bus3Phase sourceBus3Ph = (Bus3Phase) this.net.getBus(busId);
		    	   sourceBus3Ph.setVoltage(voltPU);
		    	   
		    	    Complex3x1 vabc = new Complex3x1();
					vabc.b_1 = voltPU;
					
					vabc = vabc.toABC();
					sourceBus3Ph.set3PhaseVoltages(vabc);
	    	   }
	    	   else {
	    		   IpssLogger.getLogger().info("Initial voltage is too low. VoltMag = "+voltPU.abs());
	    	   }
				
    	   }
	   }
	   else {
    	   throw new Error("There is not a single boundary Bus. Actual number is "+this.boundaryBusPosSeqVolt.size());
       }

	  
	   
	   // 3) run power flow
	   
	  
	   
	   
       // TODO note that the following part is only for non-iterated power flow
	   boolean converged = true;
       //step-1 run power flow to for network initialization in the following steps
       if(!net.isLfConverged()){
	        try {
				converged = runPowerFLow();
				
				if(!converged) {
					throw new Error("Load flow is not coverged! Cannot proceed to the initialization step of TD dynamic co-simulation");
				}
				else {
					System.out.println(DistPowerFlowOutFunc.powerflowResultSummary(net));
				}
				
				
			} catch (InterpssException e) {
				
				e.printStackTrace();
			}
       }
       
       
	   // 2) publish the distribution side total loads
	   
       publishVariables();
       
       
       IpssLogger.getLogger().setLevel(Level.INFO);
	   
	   //TODO check all federates complete the initialization mode??
       

       
       if(true) {
    	   
    	   IpssLogger.getLogger().info("calling helicsFederateEnterInitializationModeComplete");
    	   helics.helicsFederateEnterInitializationModeComplete(vFed1);
    	   
    	   
    	   IpssLogger.getLogger().info("calling helicsEnterExecutionMode");
		   helics.helicsFederateEnterExecutionMode(vFed1);
       }
	   
	   //---------------------------------------------------------------------------
	   // step-3 dstab algorithm initialization
	   //--------------------------------------------------------------------------
       
	   // define the dynamic simulation algorithm, use configuration data defined in CoSimConfigBean
	   
	   // 1) common dstab simulation setting
		
			dstabDSL.setTotalSimuTimeSec(coSimConfigBean.totalSimuTimeSec)
			        .setSimuTimeStep(coSimConfigBean.simuTimeStepSec)
			        .setIntegrationMethod(coSimConfigBean.dynMethod);
			//setRefMachine
			
			
			StateMonitor sm = new StateMonitor();
			sm.addBusStdMonitor(coSimConfigBean.monitoringBusAry);
			sm.addGeneratorStdMonitor(coSimConfigBean.monitoringGenAry);
			
	  //2)  set the output handler
			dstabDSL.setDynSimuOutputHandler(sm)
			        .setSimuOutputPerNSteps(coSimConfigBean.outputPerNSteps);
			
			dstabDSL.getDstabAlgo().setDynamicEventHandler(new DynamicEventProcessor3Phase());
			
	  //3) initialization
		boolean initStatus = dstabDSL.initialize();
		
		if(initStatus) {
			//System.out.println(ThreePhaseAclfOutFunc.busLfSummary((DStabNetwork3Phase) net));
	  		//System.out.println(net.getMachineInitCondition());
			 IpssLogger.getLogger().info("DStab initialized, enters dstab time step iteration");
			 
		}
		else {
			throw new Error("Something wrong in tranmission system dynamic simualtion intialization! Cannot proceed to the execustion step of TD dynamic co-simulation");
		}
		
		
	   //-----------------------------------------------------------------------
	   // step-4 enterExecution stage for Dstab step iteration
	   //------------------------------------------------------------------------
		double requestTime = dstabDSL.getDstabAlgo().getSimuStepSec();
		double[] helicsTime_ptr = {0.0};
		double helicsTime = 0.0;
		double dt = 0.0;
		double mvaBase = this.net.getBaseMva();
		double vaBase = mvaBase*1.0E6;
		//double lastApprovedHelicsTime = 0.0;
		System.out.println("start Dstab time step iteration");
		IpssLogger.getLogger().info("start Dstab time step iteration");
	   while(dstabDSL.getDstabAlgo().getSimuTime()<dstabDSL.getDstabAlgo().getTotalSimuTimeSec()) {
		   
		   
		    // get the approved time, this is a blocking call, only return when helics is ready
		   System.out.println("calling helics request time for time = "+requestTime);
		   IpssLogger.getLogger().info("calling helics request time for time = "+requestTime);
		    
		    helics.helicsFederateRequestTime(vFed1, requestTime,helicsTime_ptr); // all in second
		    
		    
			if(helicsTime_ptr.length>0)
		       helicsTime= helicsTime_ptr[0];
			else
				throw new Error("HelicsFederateRequestTime returns no request time");
				   
		   if(helicsTime>dstabDSL.getDstabAlgo().getSimuTime()) {
			   
			   System.out.println("Helics approved time = " + helicsTime);
			   // new time step
		       dt = helicsTime - dstabDSL.getDstabAlgo().getSimuTime();
		       
		       dstabDSL.getDstabAlgo().setSimuStepSec(dt);
		       
		       
		       // TODO the sequence of pub/sub process ??
		       
		       // subscribe the voltage from the transmission side
		       subscribeVariables(this.boundaryBusPosSeqVolt);
		       
		       if(this.boundaryBusPosSeqVolt.size()==1) {
		    	   for(Entry<String, Complex> e:this.boundaryBusPosSeqVolt.entrySet()) {
			    	   String busId = e.getKey();
			    	   Complex voltPU = e.getValue();
//			    	   Bus3Phase sourceBus3Ph = (Bus3Phase) this.net.getBus(busId);
//			    	   sourceBus3Ph.setVoltage(voltPU);
//			    	   
//			    	    Complex3x1 vabc = new Complex3x1();
//						vabc.b_1 = voltPU;
//						
//						vabc = vabc.toABC();
//					
//						
//						sourceBus3Ph.set3PhaseVoltages(vabc);
			    	   //double angle = Complex.
			    	   
			    	   EConstMachine mach = (EConstMachine) this.net.getBus(busId).getMachine("1");
//			    	   mach.setE(voltPU.abs());
//			    	   mach.setAngle(ComplexFunc.arg(voltPU));
		    	   }
			    	   
		       }
		       else {
		    	   throw new Error("There is not a single boundary Bus. Actual number is "+this.boundaryBusPosSeqVolt.size());
		       }
		       
		       //convert bus total loads to bus current injection
		       
//		       
//		       for(Entry<String, Complex> e:boundaryBusTotalLoads.entrySet()) {
//		    	   String busId = e.getKey();
//		    	   Complex loadPQ = e.getValue().divide(vaBase); // convert the total load in VA unit to PU on system MVA base.
//		    	   
//		    	   // injection into the bus as positive
//		    	   Complex curInj = loadPQ.divide(this.net.getBus(busId).getVoltage()).conjugate().multiply(-1.0);
//		    	   
//		    	   boundaryBusCurrInjection.put(busId, curInj);
//		       }
//		       
//		       //TODO need to make sure Current injection positive direction definition is consistent between T and D.
//		       this.net.setCustomBusCurrInjHashtable(boundaryBusCurrInjection);
//		       
		       // run one time step
		       //TODO need to set the updateTime to false if iteration is used
		       dstabDSL.runOneStepDStab(true); 
		       
		       // publish feeder total loads
			   publishVariables();
			   
			   //request time is to move one time step ahead
			   requestTime = dstabDSL.getDstabAlgo().getSimuTime() + dstabDSL.getDstabAlgo().getSimuStepSec();
		   }
		   else {
			   throw new Error("helics requested time should be larger than dstabDSL.getDstabAlgo().getSimuTime()");
		   }
		   
		   //TODO how to detect errors in the HELICS pub/sub process, in order to exit the iteration and terminate co-simulation
	   }
	   
	   //close the HELICS connection
	  
	   helics.helicsFederateFinalize(vFed1);
	   
	   helics.helicsCloseLibrary();
	   
	   return dstabDSL.getOutputHandler();
	   
	}
	
	
	
	@Override
	public boolean runPowerFLow() throws InterpssException {
		boolean converged;
//		converged = new AclfDslRunner()
//		                        .setNetwork(net)
//				                .run(coSimConfigBean.acscConfigBean.runAclfConfig);
		
		DistributionPowerFlowAlgorithm distPFAlgo = ThreePhaseObjectFactory.createDistPowerFlowAlgorithm(net);
		//distPFAlgo.orderDistributionBuses(true);
		
		converged = distPFAlgo.powerflow();
		
		return converged;
	}
	
	@Override
	protected Hashtable<String, Complex> subscribeVariables(Hashtable<String, Complex> boundaryVariableTable){
		//String gldString = "";
		//int maxLen = 1024;
		for(HelicsSubscription hs :helicsSubscriptions.values()) {
			    //gldString = "";
			    double[] realAry = {0.0};
			    double[] imaginaryAry = {0.0};
			    helics.helicsSubscriptionGetComplex(hs.getHelicsSubscriptionId(),  realAry, imaginaryAry);//(hs.getHelicsSubscriptionId(),gldString,maxLen);  
			    
			   // System.out.println("subscribed string = "+gldString);
	    	   
	    	   //TODO convert the String to a Complex
			    // process the unit, remove it before extracting the values
//			    if (gldString!=null) {
//			    	gldString = gldString.trim();
//			    	if(gldString.length()==0) {
//			    		throw new Error("NO return from HelicsSubscription # "+hs.getTopicName()); 
//			    	}
//			    	if(gldString.lastIndexOf("j")==(gldString.length()-1)) {
//			    		// no unit defined
//			    	}
//			    	else {
//			    		int endOfValue = gldString.lastIndexOf("j");
//			    		gldString = gldString.substring(0, endOfValue+1);
//			    	}
//			    }
			    
			    if(realAry!=null && imaginaryAry!=null) {
			    	
			    	 
			    	 Complex value = new Complex(realAry[0], imaginaryAry[0]);
			    	   
			    	 System.out.println("Dist got subscribed variable : "+hs.getTopicName() +", value = "+value.toString());
			    	   // update the currentInjection table
			    	 boundaryVariableTable.put(hs.getBusId(), value);
			    	
			    }
			    else
			    	throw new Error("NO return from HelicsSubscription # "+hs.getTopicName()); 
			    // extract the complex values
	    	   
	    	  
	       }
	    return boundaryVariableTable;
	}
	
	@Override
	protected boolean publishVariables(){
		boolean isPulishedDone = true;
		
		 
		int idx = 0;
		 for(HelicsPublication hp :helicsPublications.values()) {
	    	   Complex feederLoadMW = getFeederLoadVA(hp.getBusId());
	    	   
	    	  
	    	   idx++;
	    	   
	    	   //TODO convert the String to a format accepted by GLD
	    	   //String str = convertComplexToGLDString(busVolt);
	    	   
	    	   //IpssLogger.getLogger().info("calling helicsPublishString");
	    	   //helics.helicsPublicationPublishString(hp.getHelicsPublicationId(), str);
	    	   
	    	   IpssLogger.getLogger().info("calling helicsPublishComplex");
	    	   // id, real, imag
	    	   helics.helicsPublicationPublishComplex(hp.getHelicsPublicationId(),feederLoadMW.getReal(), feederLoadMW.getImaginary());
	    	   
	    	   System.out.println("\nDist published variable : "+hp.getTopicName()+", value = "+feederLoadMW.toString()+"\n");
	       }
		 return isPulishedDone;
	}
	
	private Complex getFeederLoadVA(String sourceBusId) {
		
		Bus3Phase sourceBus = (Bus3Phase) this.net.getBus(sourceBusId);
		
		Complex3x1 vabc_1 = sourceBus.get3PhaseVotlages();
		
		Complex3x1 currInj3Phase = new Complex3x1();
		
		
		
		for(Branch bra: sourceBus.getConnectedPhysicalBranchList()){
			if(bra.isActive()){
				Branch3Phase acLine = (Branch3Phase) bra;
				
				Complex3x1 Isource = null;
				
				if(bra.getFromBus().getId().equals(sourceBus.getId())){
					Bus3Phase toBus = (Bus3Phase) bra.getToBus();
					Complex3x1 vabc_2 = toBus.get3PhaseVotlages();
					
					Complex3x3 Yft = acLine.getYftabc();
					Complex3x3 Yff = acLine.getYffabc();
					Isource = Yff.multiply(vabc_1).add(Yft.multiply(vabc_2));
					currInj3Phase = currInj3Phase.subtract(Isource );
				}
				else{
					Bus3Phase fromBus = (Bus3Phase) bra.getFromBus();
					Complex3x1 vabc_2 = fromBus.get3PhaseVotlages();
					
					Complex3x3 Ytf = acLine.getYtfabc();
					Complex3x3 Ytt = acLine.getYttabc();
					
					Isource = Ytt.multiply(vabc_1).add(Ytf.multiply(vabc_2));
					
					currInj3Phase = currInj3Phase.subtract(Isource);
				}
			}
		}
		
		//TODO this needs to be updated if actual values are used in the distribution system
		double distVABase = this.net.getBaseMva()*1.0E6;
		

		Bus3Phase sourceBus3Ph = (Bus3Phase) sourceBus; 
		
		// from distribution to transmission
		Complex totalPower = sourceBus3Ph.get3PhaseVotlages().dotProduct(currInj3Phase.conjugate()).divide(3.0).multiply(distVABase);
		
		return totalPower.multiply(-1.0);
	}

}


