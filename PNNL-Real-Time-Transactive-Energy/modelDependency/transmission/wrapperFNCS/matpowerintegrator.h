/*
==========================================================================================
Copyright (C) 2015, Battelle Memorial Institute
Written by Laurentiu Dan Marinovici, Pacific Northwest National Laboratory
==========================================================================================
*/
#include "fncs.hpp"

#ifdef _WIN32
  #include <Windows.h>
#else
  #include <sys/time.h> // for Unix time/POSIX time/epoch time
  #include <ctime>
#endif

/* Remove if already defined */
typedef long long int64;
typedef unsigned long long uint64;

typedef unsigned long long TIME;

TIME getCurrentTime();

bool synchronize(bool ack);

//void getpower(string lookupKey, int *has, double *real, double *imag, string &actUnit, string &reactUnit);
void getpower(string lookupKey, int *has, double *real, double *imag);
void getDispLoad(string lookupKey, double *maxDispLoad);
void getDLDemandCurve(string lookupKey, double *c2, double *c1, double *c0);
void getUnrespLoad(string lookupKey, double *unrespLoad);

string delSpace(string complexValue);
string makeComplexStr(double *real, double *imag);

uint64 GetTimeMs64();
