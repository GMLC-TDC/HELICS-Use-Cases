CFLAGS += -Iinclude -I${HELICS_DIR}/src/helics/shared_api_library -I${HELICS_BUILD}/src/helics/shared_api_library

include $(PETSC_DIR)/lib/petsc/conf/variables
include $(PETSC_DIR)/lib/petsc/conf/rules

helicsbroker: helics-broker.o chkopts
	-${CLINKER} -o helicsbroker helics-broker.o  -L${HELICS_BUILD}/lib -lhelicsSharedLib ${PETSC_LIB}
	${RM} helics-broker.o

PFLOWHELICST_APP_OBJECTS =  pflow-helics-trans.o
PFLOWHELICST: $(PFLOWHELICST_APP_OBJECTS) chkopts
	 -$(CLINKER) -o PFLOWHELICST $(PFLOWHELICST_APP_OBJECTS) -L${HELICS_BUILD}/lib -lhelicsSharedLib -Llib -lpflow ${PETSC_LIB}
	$(RM) $(PFLOWHELICST_APP_OBJECTS)

PFLOWHELICSD_APP_OBJECTS =  pflow-helics-dist.o
PFLOWHELICSD: $(PFLOWHELICSD_APP_OBJECTS) chkopts
	 -$(CLINKER) -o PFLOWHELICSD $(PFLOWHELICSD_APP_OBJECTS) -L${HELICS_BUILD}/lib -lhelicsSharedLib -Llib -lklusolve -lopendssdirect -lopendssc ${PETSC_LIB}
	$(RM) $(PFLOWHELICSD_APP_OBJECTS)

PFLOWHELICST1_APP_OBJECTS =  pflow-helics-trans1.o
PFLOWHELICST1: $(PFLOWHELICST1_APP_OBJECTS) chkopts
	 -$(CLINKER) -o PFLOWHELICST1 $(PFLOWHELICST1_APP_OBJECTS) -L${HELICS_BUILD}/lib -lhelicsSharedLib -Llib -lpflow ${PETSC_LIB}
	$(RM) $(PFLOWHELICST1_APP_OBJECTS)

PFLOWHELICSD1_APP_OBJECTS =  pflow-helics-dist1.o
PFLOWHELICSD1: $(PFLOWHELICSD1_APP_OBJECTS) chkopts
	 -$(CLINKER) -o PFLOWHELICSD1 $(PFLOWHELICSD1_APP_OBJECTS) -L${HELICS_BUILD}/lib -lhelicsSharedLib -Llib -lklusolve -lopendssdirect -lopendssc ${PETSC_LIB}
	$(RM) $(PFLOWHELICSD1_APP_OBJECTS)
