import com.java.helics.SWIGTYPE_p_void;

public class HelicsSubscription {
	
	private String objectName = "";
	private String parameterType = "";
	private String busId = "";
	private String topicName = "";
	private SWIGTYPE_p_void  helicsSubscriptionId = null;
	
	public HelicsSubscription() {
		
	}

	public String getBusId() {
		return busId;
	}

	public void setBusId(String busId) {
		this.busId = busId;
	}

	public String getObjectName() {
		return objectName;
	}

	public void setObjectName(String objectName) {
		this.objectName = objectName;
	}

	public String getTopicName() {
		return topicName;
	}

	public void setTopicName(String topicName) {
		this.topicName = topicName;
	}

	public SWIGTYPE_p_void  getHelicsSubscriptionId() {
		return helicsSubscriptionId;
	}

	public void setHelicsSubscriptionId(SWIGTYPE_p_void  helicsSubscriptionId) {
		this.helicsSubscriptionId = helicsSubscriptionId;
	}

	public String getParameterType() {
		return parameterType;
	}

	public void setParameterType(String parameterType) {
		this.parameterType = parameterType;
	}

}
