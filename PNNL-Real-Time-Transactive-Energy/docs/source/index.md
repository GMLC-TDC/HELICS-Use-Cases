Co-Simulation Use Case Scripts
==============================

This is the documentation for a collection of scripts that can be used to create simulations of power systems. Specifically they can be used to run the following type of simulations:

* population of Technologies on distribution feeders
* Transmission + Distribution Co-Simulation using HELICS
* Transmission + Distribution + Transactive Energy using HELICS


The simulation uses the HELICS Co-Simulation framework and the scripts automatically sets up all the required simulators and configuration files needded for an experiment.

The sctript base supports the following types of federate:

* `GridLAB-D <https://github.com/gridlab-d/gridlab-d>`_ for the distribution system modeling
* `MATPOWER <http://www.pserc.cornell.edu/matpower/>`_ for the transmission system modeling
* Purpose built LSE and DSO constructs included in the repository for Transactive Energy use case

To get started please take a look at the example experiments linked below and to run the experiments please follow the install guides below as well.

.. toctree::
 :maxdepth: 1
 
 experiments/index
 installation/index
 api_calls/index
