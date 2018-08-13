Installing Gridlabd
====================

svn co http://svn.code.sf.net/p/gridlab-d/code/branch/3.1 gridlabd

copy files in `mods/` directory to `gridlabd/core/`

cd to gridlabd

`autoreconf -isf`
`./configure`
`make`
`sudo make install`

PFLOW
======

PFLOW uses PETSc. The provided code works with the latest version of PETSc 3.8.4. See installation instructions for PETSc <a href=InstallPETSc.md>here</a>.

The source code for PFLOW library is not provided. The source code for the application/driver is provided to give an idea of algorithmic flow along with shared library of pflow library (libpflow.so). This shared object has pflow library archived while PETSc and other other relevant dependencies are linked as shared objects. 

After installing PETSc add `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:path/to/helicsvvo/lib` to your `~/.bashrc` file and then do `make pflowDriver` from helicsvvo directory.

ZeroMQ
=======

1. Download

```
git clone git://github.com/zeromq/libzmq.git
```

2. Install

Assume <ZEROMQ_DIR> is the location of the libzmq directory.

```
cd <ZEROMQ_DIR>
./autogen.sh
mkdir build
cd build
cmake .. -DENABLE_CURVE=OFF -DWITH_PERF_TOOL=OFF -DZMQ_BUILD_TESTS=OFF -DENABLE_CPACK=OFF -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="<ZEROMQ_DIR>/build"
make
make install
```

3. pyzmq

You also need to install pyzmq using pip

Running Simulation
===================

*P.S. The code works only on Linux.*

Open six terminals, cd to helicsvvo directory

1) On the first terminal run
`path/to/helics_broker 4`

2) cd to helicsVVO/ and run pflow on the second window
`./pflowDriver`

3) cd to helicsVVO/src and run
`python3 adaptive_volt_var.py nDis=288 adaptive=1 ID=5,7,9`

4) cd to helicsVVO/src and run
`python3 pygld.py ID=5 client_portNum=10500 server_portNum=12000`

5) cd to helicsVVO/src and run
`python3 pygld.py ID=7 client_portNum=10510 server_portNum=12010`

6) cd to helicsVVO/src and run
`python3 pygld.py ID=9 client_portNum=10520 server_portNum=12020`

This will run a 288 dispatch tight coupling simulation. You can provide number of dispatches as command line argument. For instance, to run a 1 hour (00:00-01:00 hrs) quasi static time series spaced at 5 min intervals  with adaptive volt/var settings, use,

`python3 adaptive_volt_var.py nDis=12 adaptive=1 ID=5,7,9`
