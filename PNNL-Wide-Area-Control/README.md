# PNNL Wide Area Control

Use case description - TODO.

The C++ application measures and sends a value through a simulated
communication network and the network delivers the value to a controller
that is also represented in the C++ application.

## Building ns-3

The GMLC-TDC team maintains a branch of ns-3 that contains the HELICS
integration.

https://github.com/GMLC-TDC/ns-3-dev-git.git

The current branch to use is `helics-1.0-alpha`.

We build ns-3 using its waf tool.  See
https://www.nsnam.org/wiki/Installation#Configuration_with_Waf for some
examples of how to configure and build ns-3.

To build ns-3 with the HELICS integration, you might need to specify the
location of the boost, zeromq, and HELICS installations if they aren't
located automatically. For example, from the top-level ns-3 source

```bash
./waf configure --prefix=/home/username/ns-3-install --enable-examples --with-helics=/home/username/HELICS-install --boost-includes=/home/username/boost_1_62_0-c++11-install/include --boost-libs=/home/username/boost_1_62_0-c++11-install/lib
```

In the above example, boost was installed manually into a non-default
location. If you install HELICS using the install instructions
(https://gmlc-tdc.github.io/HELICS-src/installation/linux.html) the
boost and zeromq dependencies might be located for you automatically in
system locations.

Once waf configures successfully, you should see output similar to the
following:

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

Note that "NS-3 HELICS Integration" is "enabled". Do not forget to run "./waf install".


## Building the ns-3 Model
ns-3 models are usually compiled C++ applications. The provided shell
script `build-ns3.sh` will compile the ns3-sndrcv.cc code using the
appropriate flags so long as you specify BOOST_ROOT, HELICS_ROOT, and
NS3_ROOT.

## Building the Message Federate
The provided shell script `build-fed.sh` will compile the fed.cc code
using the appropriate flags so long as you specify BOOST_ROOT and
HELICS_ROOT.
