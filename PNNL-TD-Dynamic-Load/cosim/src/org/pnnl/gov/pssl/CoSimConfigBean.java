package org.pnnl.gov.pssl;

import org.interpss.pssl.plugin.cmd.json.DstabRunConfigBean;

public class CoSimConfigBean extends DstabRunConfigBean{
	
	public CoSimConfigBean(){
		   // set the default AclfDslRunner class name
		   this.dslRunnerClassName = "org.pnnl.gov.pssl.CoSimDslRunner";
	}
	public String federateName = "InterPSS";
	public String[] boundaryBusAry = {};
	public double[] distBusNorminalkV = {};
	
	public String subscribedParamters  ="Three_Sequence_Current";// three_phase, three-sequence, or single-phase
	
	public String subscribedParamterType  ="String"; 
	
	public String[] subscribedTopicNames  = {}; //String topicName = "Transmission/"+busId+"/"+publishedParameter;
	
    public String publishedParamters  ="Three_Sequence_Voltage";
	
	public String publishedParamterType  ="String"; // three_phase, three-sequence, or single-phase
	
	public String[] publishedTopicNames  = {}; 
	
	public  int numberOfCores = 1;
	

}
