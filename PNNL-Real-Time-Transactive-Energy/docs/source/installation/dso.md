DSO
===

These are the steps neccesary to install the proper version of the DSO that works with this script base.


Install DSO 

.. code-block:: bash
	
	# navigate to the repositories folder
	cd $HOME/repositories
	
	# If you have not already downloadded the main repository do the following
	git clone https://github.com/GMLC-TDC/HELICS-Use-Cases.git -b PNNL-Real-Time-Transactive-Energy
	cd HELICS-Use-Cases/PNNL-Real-Time-Transactive-Energy
	# otherwise just navigate to the right folder
	cd HELICS-Use-Cases/PNNL-Real-Time-Transactive-Energy
 	
	# build DSO
	cd modelDependency/realTimeTransactiveEnergy/helics/dso
	mkdir build
	cd build
	cmake ../ -DCMAKE_INSTALL_PREFIX=$HOME/software/dso/helics/1.0 -DZeroMQ_ROOT_DIR=$HOME/software/zeromq/4.1.6 -DBOOST_ROOT=$HOME/software/boost/1.6.1
	make
	make install
	
	# add helics to the path environment (you can replace this with your favorite way to do this)
	echo "export PATH=PATH:$HOME/software/dso/helics/1.0/bin" >> /etc/profile.d/userAddedPaths.sh

