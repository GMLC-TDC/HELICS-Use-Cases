INSTALL_PATH := /home/laurentiu/work/CoSimulation/CCSI-2.8-LSEinstall
MCR_PATH := /usr/local/MATLAB/MATLAB_Runtime/v92
FNCS_PATH := /home/laurentiu/work/CoSimulation/FNCSinstall
zeroMQ_PATH := /home/laurentiu/work/CoSimulation/FNCSinstall
CZMQ_PATH := /home/laurentiu/work/CoSimulation/FNCSinstall
CXX = g++

CXXFLAGS =
CXXFLAGS += -g
CXXFLAGS += -ansi
CXXFLAGS += -pthread
CXXFLAGS += -O0
CXXFLAGS += -std=c++11

CPPFLAGS =
CPPFLAGS += -I$(MCR_PATH)/extern/include/cpp
CPPFLAGS += -I$(MCR_PATH)/extern/include
CPPFLAGS += -I$(FNCS_PATH)/include
CPPFLAGS += -I$(zeroMQ_PATH)/include
CPPFLAGS += -I$(CZMQ_PATH)/include
CPPFLAGS += -D_GNU_SOURCE
CPPFLAGS += -DUNIX
CPPFLAGS += -DX11
CPPFLAGS += -DGLNXA64
CPPFLAGS += -DGCC
CPPFLAGS += -DNDEBUG

LDFLAGS =
LDFLAGS += -Wl,-rpath=.
LDFLAGS += -Wl,-rpath-link,$(MCR_PATH)/bin/glnxa64
LDFLAGS += -L$(MCR_PATH)/runtime/glnxa64
LDFLAGS += -L$(FNCS_PATH)/lib
LDFLAGS += -Wl,-rpath=$(FNCS_PATH)/lib
LDFLAGS += -L$(zeroMQ_PATH)/lib
LDFLAGS += -Wl,-rpath=$(zeroMQ_PATH)/lib
LDFLAGS += -L$(CZMQ_PATH)/lib
LDFLAGS += -Wl,-rpath=$(CZMQ_PATH)/lib
LDFLAGS += -L.

LIBS =
LIBS += -lmwmclmcrrt
LIBS += -lm
LIBS += -lfncs
LIBS += -lczmq
LIBS += -ljsoncpp
LIBS += -lzmq

all: dso

dso.o: dso.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) $(CPPFLAGS)

dso: dso.o
	$(CXX) -o $@ $^ $(CXXFLAGS) $(LDFLAGS) $(LIBS)

clean:
	rm -f *~ *.o *.mod *.chk *.out dso

install:
	mv dso $(INSTALL_PATH)
	rm -f *~ *.o *.mod *.chk *.out
