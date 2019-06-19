# HELICS download and installation
## GCC and CMake compilers
HELICS requires relatively newer versions of GCC and CMake compilers. The ones tested for this use-case example were gcc-6.2.0 and cmake-3.11.1.

## Installing HELICS dependencies

Before installing HELICS, let us install the dependendencies, Boost and ZeroMQ, for HELICS 

### Boost
1. Download

``` bash
wget http://dl.bintray.com/boostorg/release/1.65.0/source/boost_1_65_0.tar.gz
tar -xvf boost_1_65_0.tar.gz
```

2. Install
Assume BOOST_DIR is the location of the downloaded and extracted Boost library and <local_dir> is the location of the directory under which Boost was downloaded.
```  
mkdir build_boost_1_65_0
cd $BOOST_DIR
./bootstrap.sh --with-toolset=gcc --prefix=<localdir>/build_boost_1_65_0 --with-libraries=system,test,program_options,filesystem,date_time
/b2 install -j4 --prefix=<local_dir>/build_boost_1_65_0 --build-dir=<localdir>/buildboost toolset=gcc variant=release link=static link=shared cxxflags="-std=c++14 -fPIC" threading=multi address-model=64
```

Boost is a big library so it may take some time to install. Once the installation is complete, the installation files will be in <local_dir>/build_boost_1_65_0
3. Set up environment variables

To access the boost include and libs, we need to set up a few environmental variables so that these files get picked up correctly.

```
emacs ~/.bashrc
export PATH=<local_dir>/build_boost_1_65_0/include:$PATH
export LD_LIBRARY_PATH=<local_dir/build_boost_1_65_0/lib:$LD_LIBRARY_PATH
```
### ZeroMQ

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

3. Set up environment variables
```
emacs ~/.bashrc
export LD_LIBRARY_PATH=<ZEROMQ_DIR>/build/lib:$LD_LIBRARY_PATH
export PATH=<ZEROMQ_DIR>/build/lib:$PATH
export PATH=<ZEROMQ_DIR>/include:$PATH
```

With these two dependencies installed, we are ready to install the co-simulation tool HELICS.

### HELICS
1. Download

```
git clone https://github.com/GMLC-TDC/HELICS.git
```

2. Install

Assume <HELICS> is the location of the HELICS directory.
```
cd <HELICS>
emacs ThirdParty/helics_includes/optional.hpp
```
Before the line ```#define STX_NO_LIBRARY_OPTIONAL 1``` add line ```#define STX_NO_STD_OPTIONAL 1```. Save, close the file and return to HELICS
```
mkdir build
cd build
cmake .. -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DCMAKE_INSTALL_PREFIX=<HELICS>/build
make
make install
```
This finishes the installation of the HELICS library. Once completed, it should show the compilation was 100% successful.

3. Set environmental variables
We'll now set up some environmental that will be necessary for running the T-D dynamics co-simulation code
```
emacs ~/.bashrc
export HELICS_DIR=<HELICS>
export HELICS_BUILD=<HELICS>/build
export LD_LIBRARY_PATH=$HELICS_BUILD/lib:$LD_LIBRARY_PATH
export PATH=$HELICS_BUILD/bin:$PATH
export LD_LIBRARY_PATH=$HELICS_BUILD/src/helics/shared_api_library:$LD_LIBRARY_PATH
```

This completes installation of the HELICS library.


