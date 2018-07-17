import java.io.IOException;
import java.util.logging.Level;

import org.interpss.IpssCorePlugin;
import org.interpss.pssl.plugin.cmd.json.BaseJSONBean;
import org.junit.jupiter.api.Test;
import org.pnnl.gov.pssl.CoSimConfigBean;

import com.interpss.common.exp.InterpssException;
import com.interpss.common.util.IpssLogger;
public class TestCoSim {
	
	@Test
	public void testCoSim() throws InterpssException, IOException {
		IpssCorePlugin.init();
		
		IpssLogger.getLogger().setLevel(Level.INFO);
	
	    CoSimDslRunner coSimDSL = new CoSimDslRunner();
	    coSimDSL.run(coSimDSL.loadConfigBean("testData/IEEE39Bus/ieee39_cosim_config.json"));
	}
	
	//@Test
	public void testCosimConfig() throws IOException {
		CoSimConfigBean bean = BaseJSONBean.toBean("testData/IEEE39Bus/ieee39_cosim_config.json", CoSimConfigBean.class);
		System.out.println(bean.toString());
	}
	
	

}
