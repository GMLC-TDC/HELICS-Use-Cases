MATPOWER Wrapper
================

These are the steps neccesary to install the proper version of MATPOWER that works with this script base.

Install MCR

``` bash	
# navigate to the repositories folder
cd $HOME/repositories

# get the correct version of MCR
wget http://ssd.mathworks.com/supportfiles/downloads/R2018a/deployment_files/R2018a/installers/glnxa64/MCR_R2018a_glnxa64_installer.zip
unzip MCR_R2018a_glnxa64_installer.zip -d MCR_R2018a
cd MCR_R2018a
	
# Install MCR
./install -mode silent -agreeToLicense yes -destinationFolder $HOME/software/matlab_runtime/
```

Install MATPOWER Wrapper

``` bash	
# navigate to the repositories folder
cd $HOME/repositories
	
# get the correct version of MATPOWER Wrapper
git clone https://github.com/GMLC-TDC/MATPOWER-wrapper.git
cd MATPOWER-wrapper
 	
# build MATPOWER wrapper
mkdir build
cd build
cmake ../ -DCMAKE_INSTALL_PREFIX=$HOME/software/matpower/helics/1.0 -DMatlab_ROOT_DIR=$HOME/software/matlab_runtime/v94 -DZeroMQ_ROOT_DIR=$HOME/software/zeromq/4.1.6 -DBOOST_ROOT=$HOME/software/boost/1.6.1
make
make install
	
# add helics to the path environment (you can replace this with your favorite way to do this)
echo "export PATH=PATH:$HOME/software/matpower/helics/1.0/bin" >> /etc/profile.d/userAddedPaths.sh
```
