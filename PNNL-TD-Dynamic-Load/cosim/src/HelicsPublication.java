import com.java.helics.SWIGTYPE_p_void;

public class HelicsPublication {
	
	private String objectName = "";
	private String parameterType = "";
	private String busId = "";
	private String topicName = "";
	private SWIGTYPE_p_void helicsPublicationId = null;
	
	public HelicsPublication() {
		
	}

	public String getObjectName() {
		return objectName;
	}

	public void setObjectName(String objectName) {
		this.objectName = objectName;
	}

	public String getBusId() {
		return busId;
	}

	public void setBusId(String busId) {
		this.busId = busId;
	}

	public String getTopicName() {
		return topicName;
	}

	public void setTopicName(String topicName) {
		this.topicName = topicName;
	}

	public SWIGTYPE_p_void  getHelicsPublicationId() {
		return helicsPublicationId;
	}

	public void setHelicsPublicationId(SWIGTYPE_p_void  helicsPublicationId) {
		this.helicsPublicationId = helicsPublicationId;
	}

	public String getParameterType() {
		return parameterType;
	}

	public void setParameterType(String parameterType) {
		this.parameterType = parameterType;
	}

}
