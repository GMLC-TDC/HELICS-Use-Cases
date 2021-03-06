ANL Adaptive Volt Var
=====================

Installing Gridlabd
-------------------

svn co http://svn.code.sf.net/p/gridlab-d/code/branch/3.1 gridlabd

copy files in `mods/` directory to `gridlabd/core/`

cd to gridlabd

`autoreconf -isf`
`./configure`
`make`
`sudo make install`

PFLOW
-----

PFLOW uses PETSc. The provided code works with the latest version of PETSc 3.8.4. See installation instructions for PETSc <a href=InstallPETSc.md>here</a>.

The source code for PFLOW library is not provided. The source code for the application/driver is provided to give an idea of algorithmic flow along with shared library of pflow library (libpflow.so). This shared object has pflow library archived while PETSc and other other relevant dependencies are linked as shared objects. 

After installing PETSc add `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:path/to/helicsvvo/lib` to your `~/.bashrc` file and then do `make pflowDriver` from helicsvvo directory.

ZeroMQ
------

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
------------------

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

PETSc download and installation
-------------------------------

PETSc is an open-source numerical library providing high-performance time-stepping, nonlinear, and linearsolvers. The following are steps to install PETSc

<b>Step 1.</b> Clone PETSc from its git repository
```
git clone https://bitbucket.org/petsc/petsc.git
```

<b>Step 2.</b> Set PETSC_DIR and PETSC_ARCH environment variables

Before beginning the installation, let us set two environmental variables needed by PETSc. The first one is the location of the library, called PETSC_DIR, and the second one is PETSC_ARCH. When PETSc is installed, the configuration settings are saved in a directory with the PETSC_ARCH name set. Thus, this provides flexibility in maintaing several configuration settings with different PETSC_ARCH. The environmental variables can set by the ```export``` command in bash shell. Its best to store environmental variables in .bashrc file in the root folder. Thus, every time the bash shell is active, all environmental variables in the .bashrc file are loaded. Here's how to set the environmental variables in .bashrc file

``` 
cd ~
emacs .bashrc
export PETSC_DIR=<location_of_PETSc directory>
export PETSC_ARCH=<any-arbritraty-name-you-want>  for e.g. debug-mode
```
Save .bashrc file and then source it so that the environmental variables are loaded
```
source ~/.bashrc
```
Now, check whether the environment variables are loaded
```
echo $PETSC_DIR
```
This should display the PETSC_DIR variable you set previously. If you don't see anything, then the environmental variable is not loaded.

<b>Step 3.</b> Configure and compile PETSc
```
cd $PETSC_DIR
./config/configure.py
make
make test
```
The above commands will configure the PETSc library and compile it. If everything goes correctly then you should see display messages by PETSc that all tests have passed. 
This completes basic installation of the PETSc library that we need. For additional detailed installation instructions refer to <a href="https://www.mcs.anl.gov/petsc/documentation/installation.html">PETSc Installation</a>.
