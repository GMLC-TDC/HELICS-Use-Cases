GridLAB-D
=========

These are the steps neccesary to install the proper version of GridLAB-D that works with this script base. Currently that is feature branch #1153 (This will be updated when this feature is merged in).

Install Xerces

``` bash	
# navigate to the repositories folder
cd $HOME/repositories
	
# get the correct version of Xerces by cloning the  GridLAB-D repository
git clone https://github.com/gridlab-d/gridlab-d.git
cd gridlab-d/third_party
tar -zxf xerces-c-3.2.0.tar.gz
cd xerces-c-3.2.0
 	
# build Xerces
./configure --prefix=$HOME/software/xerces/3.2.0
make
make install
```

Install GridLAB-D

``` bash	
# navigate to the repositories folder
cd $HOME/repositories
	
# GridLAB-D is already cloned so move to that folder
cd gridlab-d
	
# build GridLAB-D 
autoreconf -ifs
./configure --prefix=$HOME/software/gridlabd/develop --with-xerces=$HOME/software/xerces/3.2.0 --with-helics="$HOME/software/zeromq/4.2.5 $HOME/software/boost/1.6.1 $HOME/software/helics/2.0.0-beta.1" --enable-silent-rules 'CFLAGS=-w -O3 -fno-inline-functions' 'CXXFLAGS=-w -O3 -fno-inline-functions -std=c++14' 'LDFLAGS=-w -O3'
make
make install
	
# add helics to the path environment (you can replace this with your favorite way to do this)
echo "export PATH=PATH:$HOME/software/gridlabd/develop/bin" >> /etc/profile.d/userAddedPaths.sh
echo "export GLPATH=$HOME/software/gridlabd/develop/lib/gridlabd:$HOME/software/gridlabd/develop/share/gridlabd" >> /etc/profile.d/userAddedPaths.sh
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/software/zeromq/4.2.5/lib:$HOME/software/boost/1.6.1/lib" >> /etc/profile.d/userAddedPaths.sh
```