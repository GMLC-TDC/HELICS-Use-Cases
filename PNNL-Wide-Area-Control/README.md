# PNNL Wide Area Control

## Introduction

This use case is a transmission and communication co-simulation that aims to investigate the impact of the communication network on wide-area controls. The transmission simulation is run in MATLAB using the Power System Toolbox (PST) and the communication simulation is run in ns-3. In this use case, specifically, we would study the impact of time delay on the HVDC oscillation damping controller. The HVDC damping controller requires two inputs, one is local frequency information, one is remote frequency information that comes from hundreds or thousands miles away which introduces delay. In this co-simulation, the Matlab PST send the remote frequency to ns3 through HELICS platform. The signal goes through the ns3 network where communication delay and loss of packages are simulated, and finally it is sent back to the Matlab PST as an input to the HVDC damping controller. The co-simulation is realized on a modified IEEE 39Bus test system for the transmission model and a simple two-node link for the communication system model.


## Building ns-3

The GMLC-TDC team maintains a branch of ns-3 that contains the HELICS
integration at [https://github.com/GMLC-TDC/ns-3-dev-git.git](https://github.com/GMLC-TDC/ns-3-dev-git.git).

ns-3 is built using the "waf" tool.  See
[https://www.nsnam.org/wiki/Installation#Configuration_with_Waf](https://www.nsnam.org/wiki/Installation#Configuration_with_Waf) for some
examples of how to configure and build ns-3.

To build ns-3 with the HELICS integration, specify the location of the Boost, zeromq, and HELICS installations if they aren't located automatically. For example, from the top-level ns-3 source

```bash
./waf configure --prefix=/home/username/ns-3-install --enable-examples --with-helics=/home/username/HELICS-install --boost-includes=/home/username/boost_1_62_0-c++11-install/include --boost-libs=/home/username/boost_1_62_0-c++11-install/lib
```

In the above example, boost was installed manually into a non-default
location. If you install HELICS using the install instructions at [https://gmlc-tdc.github.io/HELICS-src/installation/linux.html](https://gmlc-tdc.github.io/HELICS-src/installation/linux.html) the
boost and zeromq dependencies might be located for you automatically in system locations.

Once waf configures the build for ns-3, you should see output similar to the following:

```bash
---- Summary of optional NS-3 features:
Build profile                 : debug
Build directory               : 
BRITE Integration             : not enabled (BRITE not enabled (see option --with-brite))
DES Metrics event collection  : not enabled (defaults to disabled)
Emulation FdNetDevice         : enabled
Examples                      : enabled
File descriptor NetDevice     : enabled
GNU Scientific Library (GSL)  : not enabled (GSL not found)
Gcrypt library                : not enabled (libgcrypt not found: you can use libgcrypt-config to find its location.)
GtkConfigStore                : not enabled (library 'gtk+-2.0 >= 2.12' not found)
MPI Support                   : not enabled (option --enable-mpi not selected)
NS-3 Click Integration        : not enabled (nsclick not enabled (see option --with-nsclick))
NS-3 HELICS Integration       : enabled
NS-3 OpenFlow Integration     : not enabled (OpenFlow not enabled (see option --with-openflow))
Network Simulation Cradle     : not enabled (NSC not found (see option --with-nsc))
PlanetLab FdNetDevice         : not enabled (PlanetLab operating system not detected (see option --force-planetlab))
PyViz visualizer              : not enabled (Python Bindings are needed but not enabled)
Python Bindings               : not enabled (PyBindGen missing)
Real Time Simulator           : enabled
SQlite stats data output      : not enabled (library 'sqlite3' not found)
Tap Bridge                    : enabled
Tap FdNetDevice               : enabled
Tests                         : not enabled (defaults to disabled)
Threading Primitives          : enabled
Use sudo to set suid bit      : not enabled (option --enable-sudo not selected)
XmlIo                         : not enabled (library 'libxml-2.0 >= 2.7' not found)
ZMQ Integration               : enabled
'configure' finished successfully (3.501s)
```

Note that "NS-3 HELICS Integration" is "enabled". Do not forget to run `./waf install`.


## Building HELICS with the Matlab Extension
The tricky part for building HELICS with Matlab extension under Linux is that, even using the MATLAB 2017a or MATLAB 2017b, the Matlab MEX tool, which is used to build the Matlab extension for HELICS, only supports gcc 4.9. However, the HELICS build for ns3 requires gcc 5.4. To work around this, a version of HELICS to support the MATLAB extension needs to be built separately from the ns-3 installation of HELICS using gcc 4.9.

1. Install gcc 4.9
2. switch the system default gcc and g++ from 5.x to 4.9 by:
`sudo update-alternatives --config gcc` and selecting gcc 4.9.x. Check that the appropriate version was installed and has been properly linked by running
`gcc –version` and verifying it returns verison 4.9.x
The same thing needs to be done for g++ by:
`sudo update-alternatives --config g++`
3. Build boost with gcc 4.9, as cmake will throw errors if you build HELICS with gcc 4.9 while the Boost libraries is compiled with gcc 5.x. It is recommended building and installing this version of boost with gcc 4.9 into unique location outside the system path. In this way, two version of boost compiled with different versions of gcc can be used by the two installations of HELICS. 
4. start to build the HELICS with Matlab extension, assuming you already have Matlab installed in your Linux machine.
  * cd to HELICS-src
  * `mkdir build`
  * `cd build`
  * 

  ```bash 
 cmake -DBUILD_MATLAB_INTERFACE=ON  -DCMAKE_INSTALL_PREFIX=/path/to/your/helics/install/  ..
 ```
 
  * `ccmake ..`
  * make sure the following boost options in the ccamke point to the correct boost directory with gcc 4.9:  
 `Boost_CHRONO_LIBRARY_DEBUG`       
 `Boost_CHRONO_LIBRARY_RELEASE`    
 `Boost_DATE_TIME_LIBRARY_DEBUG`   
 `Boost_DATE_TIME_LIBRARY_RELEASE`  
 `Boost_FILESYSTEM_LIBRARY_DEBUG`  
 `Boost_FILESYSTEM_LIBRARY_RELEASE`              
 `Boost_LIBRARY_DIR_DEBUG`         
 `Boost_LIBRARY_DIR_RELEASE`       
 `Boost_PROGRAM_OPTIONS_LIBRARY_DEBUG`  
 `Boost_PROGRAM_OPTIONS_LIBRARY_RELEASE`  
 `Boost_SYSTEM_LIBRARY_DEBUG`      
 `Boost_SYSTEM_LIBRARY_RELEASE`    
 `Boost_TIMER_LIBRARY_DEBUG`     
 `Boost_TIMER_LIBRARY_RELEASE`     
 `Boost_UNIT_TEST_FRAMEWORK_LIBRARY_DEBUG`  
 `Boost_UNIT_TEST_FRAMEWORK_LIBRARY_RELEASE`
 
 then run `make -j8` followed by `make install`
5. Build the MATLAB extension
  * `cd ..\swig`
  * 
  
  ```bash
  mex -I/home/huan495/helics-test/helics-install/include/helics/shared_api_library/ ./matlab/helicsMEX.cpp -lhelicsSharedLib -L/home/huan495/helics-test/helics-install/lib
  ```
  * `mv helicsMEX.mexa64 matlab`
 
6. Start MATLAB and test HELICS MATLAB extension:
  * 
  
  ```bash
  `LD_PRELOAD=/path/to/your/zeromq-install-directory/lib/libzmq.so matlab
  ```
  * From within MATLAB test the HELICS installation by running `helics.helicsGetVersion()`

Further information on building HELICS with the MATLAB extension can be found at [https://gmlc-tdc.github.io/HELICS-src/installation/language.html](https://gmlc-tdc.github.io/HELICS-src/installation/language.html)


## Running the Use Case
By this point there should be two versions of HELICS installed, one for ns-3 and one for MATLAB.

To run ns-3 with HELICS two environmental variables need to be set:

```bash 
export LD_LIBRARY_PATH="$path/to/helics/install/withgcc5.x/lib:$LD_LIBRARY_PATH"
```

```bash
export LD_LIBRARY_PATH="$ path/to/Boost/install/withgcc5.x /lib:$LD_LIBRARY_PATH"
```

Similarly, to run MATLAB with HELICS the same environment variables need to be set (in a different terminal session so they don't overwrite the setting for ns-3):

```bash 
export LD_LIBRARY_PATH="$path/to/helics/install/withgcc4.9/lib:$LD_LIBRARY_PATH"
```

```bash 
export LD_LIBRARY_PATH="$ path/to/Boost/install/withgcc4.9/lib:$LD_LIBRARY_PATH"
```

To run the MATLAB model the Power System Toolbox (PST) needs to be installed from [http://www.eps.ee.kth.se/personal/vanfretti/pst/Power_System_Toolbox_Webpage/PST.html](http://www.eps.ee.kth.se/personal/vanfretti/pst/Power_System_Toolbox_Webpage/PST.html) After installing PST, move the files from the "examples-matlab" in this repository to the root folder of the PST installation.

For the ns-3 model, move "ns3-sndrcv.cc" from the "examples-ns3" folder in this repository to the "example" folder in the ns-3 source tree and build ns-3 and this model (from the session where the ns-3 environment variables have been set):
`./waf build`

To run the co-simulation, using the session where the MATLAB environment variables have been set, open MATLAB and run "s_simu_fedmessage_ns3_hvdc.m". When selecting the system model choose "d_revised_newengland39bus.m". The MATLAB code will begin running and then halt while it waits for ns-3 to begin.

To run the ns-3 model, from the session where the ns-3 variables have been defined, execute "ns3-sndrcv.cc" from the "build" folder. This will connect the ns-3 model to the co-simulation, allowing both the MATLAB model and ns-3 model to run to the completion of the co-simulation.

