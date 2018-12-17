Main Scripts
============

These are the steps neccesary to get the proper version of the Main scripts and install neccesary python packages to run it.


Install Python

.. code-block:: bash
	
	# navigate to the repositories folder
	cd $HOME/repositories

	# get the anaconda python package	
	wget https://repo.anaconda.com/archive/Anaconda3-5.3.1-Linux-x86_64.sh
	 	
	# install anaconda
	chmod +x Anaconda3-5.3.1-Linux-x86_64.sh
	./Anaconda3-5.3.1-Linux-x86_64.sh
	# specify to install in $HOME/software/python/anaconda3.7
	
	# add helics to the path environment (you can replace this with your favorite way to do this)
	echo "export PATH=PATH:$HOME/software/python/anaconda3.7/bin" >> /etc/profile.d/userAddedPaths.sh
	source /etc/profile.d/userAddedPaths.sh
	
	# install python packages needed
	pip install tqdm
	pip install numpy
	pip install scipy

Get Main Scripts

.. code-block:: bash
	
	# navigate to the repositories folder
	cd $HOME/repositories

	# get the main scripts
	git clone https://github.com/GMLC-TDC/HELICS-Use-Cases.git -b PNNL-Real-Time-Transactive-Energy
	cd HELICS-Use-Cases/PNNL-Real-Time-Transactive-Energy
