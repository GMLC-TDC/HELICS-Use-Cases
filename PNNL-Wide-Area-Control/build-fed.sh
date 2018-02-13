if test "x$HELICS_ROOT" = x
then
    echo "You must set HELICS_ROOT to the ns-3 installation."
    exit 1
fi
if test ! -d "$HELICS_ROOT"
then
    echo "HELICS_ROOT='$HELICS_ROOT' but directory does not exist."
    exit 1
fi

if test "x$CXX" = x
then
    CXX=g++
fi

if test "x$BOOST_ROOT" = x
then
    echo "You must set BOOST_ROOT to the ns-3 installation."
    exit 1
fi
if test ! -d "$BOOST_ROOT"
then
    echo "BOOST_ROOT='$BOOST_ROOT' but directory does not exist."
    exit 1
fi

CXX=g++
CXXFLAGS=""
CXXFLAGS="$CXXFLAGS -std=c++14"
CXXFLAGS="$CXXFLAGS -pthread"
CPPFLAGS=""
CPPFLAGS="$CPPFLAGS -I$HELICS_ROOT/include"
CPPFLAGS="$CPPFLAGS -I$BOOST_ROOT/include"
LDFLAGS=""
LDFLAGS="$LDFLAGS -L$HELICS_ROOT/lib"
LDFLAGS="$LDFLAGS -L$BOOST_ROOT/lib"
LIBS=""
LIBS="$LIBS -lhelics_apps-static"
LIBS="$LIBS -lhelics-static"
LIBS="$LIBS -lboost_program_options"
LIBS="$LIBS -lboost_filesystem"
LIBS="$LIBS -lboost_system"
LIBS="$LIBS -lzmq"
LIBS="$LIBS -lrt"

cmd="$CXX $CXXFLAGS -o fed fed.cc $CPPFLAGS $LDFLAGS $LIBS"
echo "$cmd"
eval "$cmd"
