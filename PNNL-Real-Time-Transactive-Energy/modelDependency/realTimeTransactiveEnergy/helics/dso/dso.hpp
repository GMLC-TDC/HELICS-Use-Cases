#include <iostream>
#include <fstream>
#include <cstdlib>
#include <sstream>
#include <thread>
#include <string.h>
#include <ctime>
#include <complex>
#include <vector>
#include <algorithm>
#include <cmath>
#include <sys/resource.h>
#include <numeric>
#include <iterator>

#include "helics/helics.hpp"
#include "helics/application_api/queryFunctions.hpp"
#include "polyfit.hpp"
#include "logging.hpp"

using namespace std;

#define BID_PRICE_CAP 1000
#define BID_PRICE_MIN 0
#define BID_QUANT_MIN 0

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

string delSpace(string str) {
  int ind = 0;
  do {
    if (isspace(str[ind])) {
      str.erase(ind, 1);
      str = delSpace(str);
    }
    ind += 1;
  } while (ind < str.length());
  return str;
};

vector<double> linspace(double minVal, double maxVal, int num) {
  vector<double> linSpace(num);
  for (int i = 0; i < num; i++) {
    linSpace[i] = minVal + i * (maxVal - minVal) / (num - 1);
  }
  return linSpace;
};

double determinePrice(double givenQuant, double lmp, vector<double> quantVector, vector<double> priceVector) {
  // create the cumulative sum of the quantity vector
	vector<double> cumQuantVector(quantVector.size());
	partial_sum(quantVector.begin(), quantVector.end(), cumQuantVector.begin());
  if (round(givenQuant * 1000) / 1000 <= cumQuantVector.front() || givenQuant > cumQuantVector.back()) {
    // use highest price, that is the first element of the ordered price sequence
    // return priceVector.front();
    // return BID_PRICE_CAP;
    return lmp;
  }
  // if (givenQuant > cumQuantVector.back()) {
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
