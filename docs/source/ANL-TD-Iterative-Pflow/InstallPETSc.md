# PETSc download and installation

This document shows steps to download and install PETSc

## PETSc

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