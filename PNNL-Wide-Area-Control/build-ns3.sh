if test "x$NS3_ROOT" = x
then
    echo "You must set NS3_ROOT to the ns-3 installation."
    exit 1
fi
if test ! -d "$NS3_ROOT"
then
    echo "NS3_ROOT='$NS3_ROOT' but directory does not exist."
    exit 1
fi

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

# ns-3 default build is 'debug', so many folders and libraries get 'dev'
# in their names.
MAYBE_DEV=
MAYBE_DEBUG=
if test -d "$NS3_ROOT/include/ns3-dev"
then
    MAYBE_DEV="-dev"
    MAYBE_DEBUG="-debug"
fi

CXX=g++
CXXFLAGS="-std=c++14"
CPPFLAGS=""
CPPFLAGS="$CPPFLAGS -I$NS3_ROOT/include/ns3$MAYBE_DEV"
CPPFLAGS="$CPPFLAGS -I$HELICS_ROOT/include"
CPPFLAGS="$CPPFLAGS -I$BOOST_ROOT/include"
LDFLAGS=""
LDFLAGS="$LDFLAGS -L$NS3_ROOT/lib"
LDFLAGS="$LDFLAGS -L$HELICS_ROOT/lib"
LDFLAGS="$LDFLAGS -L$BOOST_ROOT/lib"
LIBS=""
LIBS="$LIBS -lns3-dev-helics$MAYBE_DEBUG"
LIBS="$LIBS -lns3-dev-core$MAYBE_DEBUG"
LIBS="$LIBS -lns3-dev-point-to-point$MAYBE_DEBUG"
LIBS="$LIBS -lns3-dev-csma$MAYBE_DEBUG"
LIBS="$LIBS -lns3-dev-internet$MAYBE_DEBUG"
LIBS="$LIBS -lns3-dev-applications$MAYBE_DEBUG"
LIBS="$LIBS -lns3-dev-network$MAYBE_DEBUG"
LIBS="$LIBS -lhelics-static"

cmd="$CXX $CXXFLAGS -o ns3-sndrcv ns3-sndrcv.cc $CPPFLAGS $LDFLAGS $LIBS"
echo "$cmd"
eval "$cmd"
