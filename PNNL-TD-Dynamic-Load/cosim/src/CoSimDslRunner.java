import java.io.IOException;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.List;
import java.util.Map.Entry;
import java.util.logging.Level;

import org.apache.commons.math3.complex.Complex;
import org.interpss.pssl.plugin.cmd.AclfDslRunner;
import org.interpss.pssl.plugin.cmd.BaseDStabDslRunner;
import org.interpss.pssl.plugin.cmd.json.BaseJSONBean;
import org.interpss.pssl.plugin.cmd.json.DstabRunConfigBean;
import org.interpss.pssl.simu.IpssDStab;
import org.pnnl.gov.pssl.CoSimConfigBean;

import com.interpss.CoreObjectFactory;
import com.interpss.common.exp.InterpssException;
import com.interpss.common.util.IpssLogger;
import com.interpss.core.aclf.AclfLoad;
import com.interpss.dstab.DStabBus;
import com.interpss.dstab.cache.StateMonitor;
import com.interpss.dstab.common.IDStabSimuOutputHandler;
import com.java.helics.SWIGTYPE_p_void;
import com.java.helics.helics;

/**
 * The run() method is the function to be called to run the simulation.
 * runDstab() method is called within run().
 * Check the BaseDStabDslRunner class for more details.
 * 
 * @author huan289
 *
 */

public class CoSimDslRunner extends BaseDStabDslRunner{
	

	protected CoSimConfigBean coSimConfigBean = null;
	
	protected Hashtable<String, HelicsPublication> helicsPublications= null;
	protected Hashtable<String, HelicsSubscription> helicsSubscriptions= null;
	
	protected List<String> boundaryBusIds = null;
	protected Hashtable<String, Complex> boundaryBusPosSeqVolt = null;
	protected Hashtable<String, Complex> boundaryBusCurrInjection = null;
	protected Hashtable<String, Complex> boundaryBusTotalLoads = null;
	
	protected String DEFAULT_CORE_TYPE = "zmq";
	protected String DEFAULT_FEDERATE_NAME ="InterPSS";

	
	public CoSimDslRunner() {
		helicsPublications = new Hashtable<>();
		helicsSubscriptions = new Hashtable<>();
		boundaryBusIds = new ArrayList<>();
		
		boundaryBusTotalLoads = new Hashtable<>();
		boundaryBusPosSeqVolt = new Hashtable<>();
		boundaryBusCurrInjection = new Hashtable<>();
		
		
	}
	@Override
	public BaseJSONBean loadConfigBean(String beanFileName)  throws IOException { 
		return BaseJSONBean.toBean(beanFileName, CoSimConfigBean.class);
	}
	
	
	@Override
	protected IDStabSimuOutputHandler runDstab(DstabRunConfigBean configBean) throws Exception {
	    
		double mvaBase = this.net.getBaseMva();
		double vaBase = mvaBase*1.0E6;
		
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
	   
	   /*
	   //set the boundary bus loads to be zeros
	   for (String id: this.boundaryBusIds) {
		   DStabBus bus = this.net.getBus(id);
		   if(bus.isActive()) {
			   bus.setLoadP(0.0);
			   bus.setLoadQ(0.0);
			   bus.getContributeLoadList().clear();
		   }
	   }
	   */
	   
	   
       // 1) send the boundary bus voltage results to the distribution side
       publishVariables();
	   
	   // 2) receive the total loads from the distribution side and update the total loads of the boundary buses
	   
	   subscribeVariables(boundaryBusTotalLoads);
	   
	 //set the boundary bus loads to be zeros
	   
	   for(Entry<String, Complex> e:boundaryBusTotalLoads.entrySet()) {
    	   String busId = e.getKey();
    	   Complex loadPQ = e.getValue().divide(vaBase); // convert the total load in VA unit to PU on system MVA base.
    	   
    	   // injection into the bus as positive
    	   AclfLoad ld = CoreObjectFactory.createAclfLoad();
    	   ld.setLoadCP(loadPQ);
    	   this.net.getBus(busId).getContributeLoadList().add(ld);
    	   
    	   
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
				
				
			} catch (InterpssException e) {
				
				e.printStackTrace();
			}
       }
	  
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
			
	  //3) initialization
		boolean initStatus = dstabDSL.initialize();
		
		if(initStatus) {
			   //System.out.println("calling helicsEnterExecutionMode");
			   IpssLogger.getLogger().info("Transmisison side dstab algo is intialized, enters time step iteration.");
			 
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
		       
		       // subscribe the current injections from the distribution system
		       subscribeVariables(boundaryBusTotalLoads);
		       
		       //convert bus total loads to bus current injection
		       
		       
		       for(Entry<String, Complex> e:boundaryBusTotalLoads.entrySet()) {
		    	   String busId = e.getKey();
		    	   Complex loadPQ = e.getValue().divide(vaBase); // convert the total load in VA unit to PU on system MVA base.
		    	   
		    	   // injection into the bus as positive
		    	   Complex curInj = loadPQ.divide(this.net.getBus(busId).getVoltage()).conjugate().multiply(-1.0);
		    	   
		    	   boundaryBusCurrInjection.put(busId, curInj);
		       }
		       
		       //TODO need to make sure Current injection positive direction definition is consistent between T and D.
		       this.net.setCustomBusCurrInjHashtable(boundaryBusCurrInjection);
		       
		       // run one time step
		       //TODO need to set the updateTime to false if iteration is used
		       dstabDSL.runOneStepDStab(true); 
		       
		       // publish the boundary bus voltages
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
	public boolean runPowerFLow() throws InterpssException {
		boolean converged;
		converged = new AclfDslRunner()
		                        .setNetwork(net)
				                .run(coSimConfigBean.acscConfigBean.runAclfConfig);
		return converged;
	}

	
	protected Hashtable<String, Complex> subscribeVariables(Hashtable<String, Complex> boundaryVariableTable){
		String gldString = "";
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
			    	   
			    	 System.out.println("InterPSS got subscribed variable : "+hs.getTopicName() +", value = "+value.toString());
			    	   // update the currentInjection table
			    	 boundaryVariableTable.put(hs.getBusId(), value);
			    	
			    }
			    else
			    	throw new Error("NO return from HelicsSubscription # "+hs.getTopicName()); 
			    // extract the complex values
	    	   
	    	  
	       }
	    return boundaryVariableTable;
	}
	
	protected boolean publishVariables(){
		boolean isPulishedDone = true;
		double[] distBaseKV = coSimConfigBean.distBusNorminalkV;
		 
		int idx = 0;
		 for(HelicsPublication hp :helicsPublications.values()) {
	    	   Complex busVolt = this.net.getBus(hp.getBusId()).getVoltage();
	    	   
	    	   //TODO comment out for testing
	    	   //busVolt =busVolt.multiply(distBaseKV[idx]);
	    	   
	    	   idx++;
	    	   
	    	   //TODO convert the String to a format accepted by GLD
	    	   //String str = convertComplexToGLDString(busVolt);
	    	   
	    	   //IpssLogger.getLogger().info("calling helicsPublishString");
	    	   //helics.helicsPublicationPublishString(hp.getHelicsPublicationId(), str);
	    	   
	    	   IpssLogger.getLogger().info("calling helicsPublishComplex");
	    	   // id, real, imag
	    	   helics.helicsPublicationPublishComplex(hp.getHelicsPublicationId(),busVolt.getReal(), busVolt.getImaginary());
	    	   
	    	   System.out.println("\nInterPSS published variable : "+hp.getTopicName()+", value = "+busVolt.toString()+"\n");
	       }
		 return isPulishedDone;
	}
	
	private String convertComplexToGLDString(Complex value) {
		//example 0.000000+2771.281292j, -2400.000000 -1385.640646j;
		String gldString ="";
		if(value!=null && !value.isNaN()) {
			if(value.getImaginary()>=0.0)
			   gldString = value.getReal()+"+"+value.getImaginary()+"j";
			else
			   gldString = value.getReal()+" "+value.getImaginary()+"j";
		}
		return gldString;
		
	}

   private  Complex convertGLDStringToComplex(String GLDString) {
	   //example 0.000000+2771.281292j ; -2400.000000 -1385.640646j;
	   
	   
	   double real = 0.0;
	   double imag = 0.0;
	   
	   if(GLDString!=null) {
		   GLDString = GLDString.trim();
		   if(GLDString.length()>0) {
			   if (GLDString.contains("j")) { // has the imaginary part
				   if(GLDString.lastIndexOf("-")>0) { // negative imaginary part
					   int negativeIdx = GLDString.indexOf("-");
					   String realStr = GLDString.substring(0, negativeIdx);
					   real = Double.parseDouble(realStr);
					   
					    String imagStr = GLDString.substring(negativeIdx,GLDString.length()); // remove the "j" at the end;
					   imag = Double.parseDouble(imagStr);
					}
				   else {
					   int plusIdx = GLDString.lastIndexOf("+");
					  
					   real = Double.parseDouble(GLDString.substring(0, plusIdx));
					   
					   imag = Double.parseDouble(GLDString.substring(plusIdx,GLDString.length())); // remove the "j" at the end;
				   }
			   }
			   else {
				   real = Double.parseDouble(GLDString); // no imaginary part
		       }
          }
     }
	
    Complex a = new Complex(real,imag);
    return a;

   }
}
