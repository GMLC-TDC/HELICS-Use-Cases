CFLAGS = -Iinclude -DDEBUGPS

include ${PETSC_DIR}/lib/petsc/conf/variables
include ${PETSC_DIR}/lib/petsc/conf/rules

pflowDriver:
	-${CLINKER} -o pflowDriver src/pflowDriver.c -Llib -lpflow -lcjson ${PETSC_SNES_LIB} -L/usr/local/lib/ -lzmq
