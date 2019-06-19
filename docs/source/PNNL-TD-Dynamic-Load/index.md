PNNL TD Dynamic Load Use Case Scripts
=====================================

### Introduction

This use case is to provide data and insights of detailed individual load responses (including the protection actions) to faults in the transmission system for deriving the aggregate protection models and evaluating the performance of WECC composite load model, i.e., CMPLDW.  

Thus, it requires  the T&D  dynamic co-simulation capability. For initialization of the dynamic co-simulation, T&D power flow co-simulation is also required.

In this use case, the transmission part simulation is performed by [InterPSS](www.interpss.og), whereas [GridLAB-D](https://www.gridlabd.org/) is used for distribution power flow and dynamic simulation. GridLAB-D [subsecond (deltaMode)](http://gridlab-d.sourceforge.net/wiki/index.php/Subsecond)  simulation capability will be leveraged for dynamic simulation.  HELICS is utilized to handle time synchronization and data message exchange between InterPSS and GridLAB-D. As InterPSS is a Java-based simulation tool, so HELICS **with Java binding** is needed for InterPSS, while GridLAB-D will use the default HELICS C++ APIs.

In the current release, the test cases comprise IEEE 39-bus system (for the transmission system part), a test feeder and a generic commercial [PNNL taxonomy feeder](http://gridlab-d.sourceforge.net/wiki/index.php/Feeder_Taxonomy) (for the distribution system part).

While HECLIS supports iteration at both initialization and execution stages,  in this use case, iteration between T&D at both power flow and each time step of dynamic simulation has not been implemented yet, due to the fact that current GridLAB-D HELICS implementation do not support iteration. This will be one of the focuses of next phase development.

### Install GridLAB-D with HELICS interface

*The use case is currently developed in Linux environment, so the following instructions are only tested on Linux. Information for other development environment will be provided in the future.*

1. Follow the [instructions provided by HELICS developers](https://github.com/GMLC-TDC/HELICS) and install HELICS **with Java binding**, which will be enabled by default installation configuration setting. You can use `ccmake .`  during the build process to check or change the configuration. 

2. Install GridLAB-D. HELICS support currently (7/14/2018) is provided in the [`feature/1024` branch](https://github.com/gridlab-d/gridlab-d/tree/feature/1024), So you need to check it out first: `git checkout -b feature/1024 origin/feature/1024`

   Then you have to build GridLAB-D yourself as described [here](https://github.com/GMLC-TDC/HELICS-Tutorial/tree/master/setup). 

   **NOTE:**  The motor protection models in GridLAB-D are currently (7/14/2018) developed in [`feature/1105`](https://github.com/gridlab-d/gridlab-d/tree/feature/1105) branch, so it requires some extra work to check out and merge this part into the GridLAB-D to run on the one of the study cases with motor protection.

### Checkout required InterPSS libraries 

The modeling and simulation capabilities that will be used in this use case are accessed through InterPSS Java libraries (*jar), which in turn depend on some third-party libraries. All these libraries are access in the [InterPSS-Project/**ipss-common**  on github.](https://github.com/InterPSS-Project/ipss-common)

To checkout all the required libraries, simply run `git clone https://github.com/InterPSS-Project/ipss-common.git`



###Setup InterPSS running environment in Eclipse

Given that compiling the simulation java file for this use case using InterPSS and HELICS Jar files is very complex, Eclipse IDE is recommended to use to build and run the InterPSS-based simulation code.

1. Install Java-8, if it is not available or other Java version is used.
2. Install Eclipse. Follow Instructions provided [here](https://www.eclipse.org/downloads/)
3. Open Eclipse:
   1. `cd <path to Eclipse>`
   2. `./eclipse`
4. Import the InterPSS [ipss-common](https://github.com/InterPSS-Project/ipss-common) project into Eclipse
5. Check out this [TDC-Use-Case project](https://github.com/GMLC-TDC/HELICS-Use-Cases)
6. Import **ipss.plugin.external.cosim** project under the PNNL-TD-Dynamic-Load into Eclipse
7. Configure  **ipss.plugin.external.cosim** project
   * Select Project->Right Click->Build Path->Link Source..., 
   * Select the `<Path to HELICS Build folder>/swig/java` folder as the Linked folder location.
   * Configure Build Path:
       * For the libraries, select and add all those under the `ipss.lib` folder of the [ipss-common](https://github.com/InterPSS-Project/ipss-common) , select and add the following jar files under the `ipss.lib.3rdPty` folder:
       * apache: commons-logging, commons-math3
       * cache: hazelcast-3.8.jar
       * eclipse: all emf  jar files


### Case files

1. Transmissions: 
   * A dataset for IEEE 39-Bus system, including power flow, dynamic and sequence data
   * A json configuration file for co-simulation
2. Distribution feeders:
   * A simple  feeder with diesel generators-- IEEE-13_Dynamic_2gen_swingsub_helics.glm, and associated player files and a json configuration file for co-simulation
   * A general commercial taxonomy feeder, i.e., [GC-12.47-1.glm](https://github.com/gridlab-d/Taxonomy_Feeders/blob/master/GC-12.47-1.glm), with  `motor` and `helics_msg` modules added to it, and associated player files and a json configuration file for co-simulation



### Run the use case

1. Open *terminal 1*, start helics_brokers with cmd lines, for one transmission and one distribution feeder co-simulation, we will need 2 brokers, and the cmd line should be, `helics_broker 2`
2. Open *terminal 2*, start Eclipse, run `TestTransCoSim.java`
3. Open *terminal 3*, first get the case folder: `cd /home/huan289/eclipse-workspace/ipss.plugin.external.cosim/testData/GLD/`, then run `gridlab-d IEEE-13_Dynamic_2gen_swingsub_helics.glm`
  