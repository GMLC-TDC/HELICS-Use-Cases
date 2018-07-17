import java.io.IOException;
import java.util.logging.Level;

import org.interpss.IpssCorePlugin;
import org.junit.Test;

import com.interpss.common.exp.InterpssException;
import com.interpss.common.util.IpssLogger;

public class TestDistCoSim {
	
	    @Test
		public void testDistCoSim() throws InterpssException, IOException {
			IpssCorePlugin.init();
			
			IpssLogger.getLogger().setLevel(Level.INFO);
		
		    CoSimDslRunner coSimDSL = new DistCoSimDslRunner();
		    coSimDSL.run(coSimDSL.loadConfigBean("testData/gldFeeders/GC_feeder_cosim_config.json"));
		}

}
