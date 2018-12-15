INSTALL_PATH := /home/nodes/software/matpower/1.5
MCR_PATH := /home/nodes/software/matlab_runtime/v92
FNCS_PATH := /home/nodes/software/fncs/launcher2
zeroMQ_PATH := /home/nodes/software/zeromq/3.2.5
CZMQ_PATH := /home/nodes/software/czmq/3.0.2
CXX = g++

CXXFLAGS =
CXXFLAGS += -O2
CXXFLAGS += -DNUM_THREADS=1
CXXFLAGS += -fopenmp

CPPFLAGS =
CPPFLAGS += -I$(MCR_PATH)/extern/include/cpp
CPPFLAGS += -I$(MCR_PATH)/extern/include
CPPFLAGS += -I$(FNCS_PATH)/include
CPPFLAGS += -I$(zeroMQ_PATH)/include
CPPFLAGS += -I$(CZMQ_PATH)/include
CPPFLAGS += -O2

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
LDFLAGS += -L$(INSTALL_PATH)
LDFLAGS += -Wl,-rpath=$(INSTALL_PATH)
LDFLAGS += -O2

LIBS =
LIBS += -lmwmclmcrrt
LIBS += -lm
LIBS += -lMATPOWER
LIBS += -lfncs
LIBS += -lczmq
LIBS += -ljsoncpp
LIBS += -lzmq

all: start_MATPOWER

start_MATPOWER.o: start_MATPOWER.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) $(CPPFLAGS)

matpowerintegrator.o: matpowerintegrator.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) $(CPPFLAGS)

read_load_profile.o: read_load_profile.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) $(CPPFLAGS)

read_model_dim.o: read_model_dim.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) $(CPPFLAGS)

read_model_data.o: read_model_data.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) $(CPPFLAGS)

matpowerLoadMetrics.o: matpowerLoadMetrics.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) $(CPPFLAGS)

matpowerGeneratorMetrics.o: matpowerGeneratorMetrics.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) $(CPPFLAGS)

jsoncpp.o: jsoncpp.cpp
	$(CXX) -c $< -o $@ $(CXXFLAGS) $(CPPFLAGS)

start_MATPOWER: start_MATPOWER.o matpowerintegrator.o read_load_profile.o read_model_dim.o read_model_data.o matpowerLoadMetrics.o matpowerGeneratorMetrics.o jsoncpp.o
	$(CXX) -o $@ $^ $(CXXFLAGS) $(LDFLAGS) $(LIBS)

clean:
	rm -f *~
	rm -f *.o
	rm -f *.mod
	rm -f start_MATPOWER
	rm -f *.chk
	rm -f *.out

install:
	mkdir -p $(INSTALL_PATH)
	cp lib*.so $(INSTALL_PATH)
	cp lib*.h $(INSTALL_PATH)
	cp start_MATPOWER $(INSTALL_PATH)
	rm -f *~ *.o *.mod *.chk *.out
