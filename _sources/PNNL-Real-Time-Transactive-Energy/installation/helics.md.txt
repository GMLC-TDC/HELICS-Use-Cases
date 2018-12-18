HELICS
======

These are the steps neccesary to install the proper version of HELICS that works with this script base. Currently that is the 2.0 beta 1 release (This will be updated to 2.0 when released).

Install ZMQ

.. code-block:: bash

	# create the folders needed 
	mkdir -p $HOME/software
	mkdir -p $HOME/repositories
	
	# navigate to the repositories folder
	cd $HOME/repositories
	
	# get the latest ZMQ version
	wget https://github.com/zeromq/libzmq/releases/download/v4.2.5/zeromq-4.2.5.tar.gz
	tar -zxf zeromq-4.2.5.tar.gz
	rm zeromq-4.2.5.tar.gz
	cd zeromq-4.2.5 
	
	# build ZMQ
	./configure --prefix=$HOME/software/zeromq/4.2.5
	make
	make install

Install Boost

.. code-block:: bash

	# navigate to the repositories folder
	cd $HOME/repositories
	
	# get Boost version 1.6.1 
	# download from here: https://sourceforge.net/projects/boost/files/boost/1.61.0/
	tar -zxf boost_1_61.tar.gz
	rm boost_1_61.tar.gz
	cd boost_1_61
	
	# build boost 
	./bootstrap.sh --prefix=$HOME/software/boost/1.6.1
	./bjam cxxflags='-fPIC' cflags='-fPIC' -a link=dynamic,static install


Install HELICS

.. code-block:: bash

	# navigate to the repositories folder
	cd $HOME/repositories
	
	# clone the HELICS repository
	git clone https://github.com/GMLC-TDC/HELICS-src.git -b HELICS_2_0
	git checkout tags/v2.0.0-beta.1
	
	# build helics
	mkdir build
	cd build
	cmake ../ -DCMAKE_INSTALL_PREFIX=$HOME/software/helics/2.0.0-beta.1 -DZeroMQ_ROOT_DIR=$HOME/software/zeromq/4.2.5 -DBOOST_ROOT=$HOME/software/boost/1.6.1
	make 
	make install
	
	# add helics to the path environment (you can replace this with your favorite way to do this)
	echo "export PATH=PATH:$HOME/software/helics/2.0.0-beta.1/bin" >> /etc/profile.d/userAddedPaths.sh
	source /etc/profile.d/userAddedPaths.sh


