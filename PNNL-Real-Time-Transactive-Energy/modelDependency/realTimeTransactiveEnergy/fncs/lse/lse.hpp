#include <iostream>
#include <fstream>
#include <cstdlib>
#include <sstream>
#include <string.h>
#include <ctime>
#include <vector>
#include <algorithm> // for the transform function
#include <cmath> // for the absolute value
#include <sys/resource.h>
#include <numeric>
#include <iterator>

#include "fncs.hpp"
#include "polyfit.hpp"
#include "logging.hpp"

#define PI 3.14159265
#define BID_PRICE_CAP 1000
#define BID_PRICE_MIN 0
#define BID_QUANT_MIN 0

using namespace std;

// set the definition for the logger
loglevel_e loglevel;

// Fill the zipped vector with pairs consisting of the
// corresponding elements of a and b. (This assumes 
// that the vectors have equal length)
template <typename A, typename B>
void zip(
    const std::vector<A> &a, 
    const std::vector<B> &b, 
    std::vector<std::pair<A,B>> &zipped)
{
    for(size_t i=0; i<a.size(); ++i)
    {
        zipped.push_back(std::make_pair(a[i], b[i]));
    }
}

// Write the first and second element of the pairs in 
// the given zipped vector into a and b. (This assumes 
// that the vectors have equal length)
template <typename A, typename B>
void unzip(
    const std::vector<std::pair<A, B>> &zipped, 
    std::vector<A> &a, 
    std::vector<B> &b)
{
    for(size_t i=0; i<a.size(); i++)
    {
        a[i] = zipped[i].first;
        b[i] = zipped[i].second;
    }
}

// Function for comparing second entry in s struct
// Used to sort the zipped vectors
struct CompareSecond {
    template <class Fst, class Snd>
    bool operator()(const pair<Fst,Snd>& l, const pair<Fst,Snd>& r) const {
        return l.second < r.second;
    }
};

// Function for eliminating the spaces in a string. It is needed to eliminate the spaces
// inside the string representing the complex power at the head of the feeder, in order to
// be able to process it further, and extract the correct unit and real power.
string delSpace (string str)
{
  int i = 0;
  do
  {
    if (isspace(str[i]))
    {
      str.erase(i, 1);
      str = delSpace(str);
    }
    i += 1;
  }
  while (i < str.length());
  return str;
}

// The LSE is an entity working at the level of each feeder/GridLAB-D model, and hence it receives
// the power at the head of the feeder as a comlpex number and differet units. But all it needs is the real
// power in MW.
// stringPower is the power value as a string, as read from the FNCS subscription space
double getFeederHeadRealPower(string stringPower)
{
  double real, imag, magnitude, phase;
  string unit, actUnit, reactUnit; // just the unit strings
  if (!stringPower.empty())
  {
    // The complex power value from GridLAB-D can come in several formats; see file preamble for details
    size_t foundD = stringPower.find("d"); // find the ``d''; polar format with angle in degrees
    size_t foundR = stringPower.find("r"); // find the ``r''; polar format with angle in radians
    size_t foundI = stringPower.find("i"); // find the ``i'' (complex) position
    size_t foundJ = stringPower.find("j"); // find the ``j'' (complex) position
    try
    {
      if (foundD != string::npos)
      {
        string complexValue = stringPower.substr(0, foundD + 1); // separate the complex power value as string
        complexValue = delSpace(complexValue); // eliminate the white spaces in the complex value string
        sscanf(&complexValue[0], "%lf%lf%*[^d]", &magnitude, &phase); // parse the polar complex value string to get magnitude and phase in degrees
        unit = stringPower.substr(foundD + 1, string::npos); // separate the unit string
        real = magnitude * cos(phase * PI / 180); // real part in rectangular coordinates (active power)
        imag = magnitude * sin(phase * PI / 180); // imaginary part in rectangular coordinates (reactive power)
      }
      else if (foundJ != string::npos)
      {
        string complexValue = stringPower.substr(0, foundJ + 1); // separate the complex power value as string
        complexValue = delSpace(complexValue); // eliminate the white spaces in the complex value string
        sscanf(&complexValue[0], "%lf%lf%*[^j]", &real, &imag); // parse the rectangular complex value string to get active and reactive powers
        unit = stringPower.substr(foundJ + 1, string::npos); // separate the unit string
      }
      else if (foundI != string::npos)
      {
        string complexValue = stringPower.substr(0, foundI + 1); // separate the complex power value as string
        complexValue = delSpace(complexValue); // eliminate the white spaces in the complex value string
        sscanf(&complexValue[0], "%lf%lf%*[^i]", &real, &imag); // parse the rectangular complex value string to get active and reactive powers
        unit = stringPower.substr(foundI + 1, string::npos); // separate the unit string
      }
      else if (foundR != string::npos)
      {
        string complexValue = stringPower.substr(0, foundR + 1); // separate the complex power value as string
        complexValue = delSpace(complexValue); // eliminate the white spaces in the complex value string
        sscanf(&complexValue[0], "%lf%lf%*[^r]", &magnitude, &phase); // parse the polar complex value string to get magnitude and phase in radians
        unit = stringPower.substr(foundR + 1, string::npos); // separate the unit string
        real = magnitude * cos(phase); // real part in rectangular coordinates (active power)
        imag = magnitude * sin(phase); // imaginary part in rectangular coordinates (reactive power)
      }
      else
      {
        throw 225;
      }
      unit = delSpace(unit); // eliminate spaces in the unit string
      std::transform(unit.begin(), unit.end(), unit.begin(), ::toupper); // transform unit string to upper string for comparison purposes
    }
    catch (int e)
    {
      cout << "The power format might be wrong!!!" << endl;
      fncs::die();
      exit(EXIT_FAILURE);
    }
    try
    {
      if (unit.compare("VA") == 0)
      {
        real /= 1000000; // W to MW conversion
        imag /= 1000000; // VAR to Mvar conversion
        actUnit = string("MW");
        reactUnit = string("Mvar");    }
      else if (unit.compare("MVA") == 0)
      {
        actUnit = string("MW");
        reactUnit = string("Mvar");
      }
      else if (unit.compare("KVA") == 0)
      {
        real /= 1000; // KW to MW conversion
        imag /= 1000; // KVAR to Mvar conversion
        actUnit = string("MW");
        reactUnit = string("Mvar");
      }
      else
      {
        throw 225; // just an exception code
      }
    }
    catch (int e)
    {
      LERROR << "Unit is not correct. Check YAML file or the GLD side!";
      fncs::die();
      exit(EXIT_FAILURE);
    }
    return real;
  }
  else
  {
    LINFO << "No published power from the head of the feeder.";
    throw 225; // just an exception code
  }
}

double determinePrice(double givenQuant, double lmp, vector<double> quantVector, vector<double> priceVector) {
  // create the cumulative sum of the quantity vector
	vector<double> cumQuantVector(quantVector.size());
	partial_sum(quantVector.begin(), quantVector.end(), cumQuantVector.begin());
  if (givenQuant < cumQuantVector.front() || givenQuant > cumQuantVector.back()) {
    // use highest price, that is the first element of the ordered price sequence
    // return priceVector.front();
    // return BID_PRICE_CAP;
    return lmp;
  }
  //if (givenQuant > cumQuantVector.back()) {
    // use the lowest price, that is the last element of the ordered price sequence
  //  return priceVector.back();
  //}
  // if givenQuant is between values of quantVector, we use a piece-wise linear characteristic
  // of the marginal demand curve to find the choresponding price
  int ind = 0;
  while (cumQuantVector[ind] < givenQuant) {
    ind += 1;
  }
  return priceVector[ind - 1] + ((priceVector[ind] - priceVector[ind - 1]) / (cumQuantVector[ind] - cumQuantVector[ind - 1])) * (givenQuant - cumQuantVector[ind - 1]);
}