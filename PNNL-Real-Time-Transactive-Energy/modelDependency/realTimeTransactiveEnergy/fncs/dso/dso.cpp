#include "dso.hpp"

/* ==================================================================================================================
====================== MAIN PART ====================================================================================
===================================================================================================================*/

int main(int argc, const char *argv[]) {
  // variable to keep track of the total time used
  time_t tStart = time(0);

  // Setting up the logger based on user input
  char *log_level_export = NULL;
  log_level_export = getenv("DSO_LOG_LEVEL");
  
  if (!log_level_export) {
    loglevel = logWARNING; 
  } else if (strcmp(log_level_export,"ERROR") == 0) {
    loglevel = logERROR;
  } else if (strcmp(log_level_export,"WARNING") == 0) {
    loglevel = logWARNING;
  } else if (strcmp(log_level_export,"INFO") == 0) {
    loglevel = logINFO;
  } else if (strcmp(log_level_export,"DEBUG") == 0) {
    loglevel = logDEBUG;
  } else if (strcmp(log_level_export,"DEBUG1") == 0) {
    loglevel = logDEBUG1;
  } else if (strcmp(log_level_export,"DEBUG2") == 0) {
    loglevel = logDEBUG2;
  } else if (strcmp(log_level_export,"DEBUG3") == 0) {
    loglevel = logDEBUG3;
  } else if (strcmp(log_level_export,"DEBUG4") == 0) {
    loglevel = logDEBUG4;
  }

  // increase the possible stack size for the application
  const rlim_t kStackSize = 1024L * 1024L * 1024L;   // min stack size = 1024 Mb
  struct rlimit rl;
  int result;

  result = getrlimit(RLIMIT_STACK, &rl);
  if (result == 0)
  {
    if (rl.rlim_cur < kStackSize)
    {
      rl.rlim_cur = kStackSize;
      result = setrlimit(RLIMIT_STACK, &rl);
      if (result != 0)
      {
        LERROR << "setrlimit returned result = " << result ;
      }
    }
  }    
  
  LINFO << "Running process -> " << argv[0] ;
  LINFO << "with a simulation stop time of " << argv[1] << " seconds";    
    
  try {                
    // time keeping variables
    double simStopTime; // simulation stop time
    sscanf(argv[1], "%lf%*s", &simStopTime);
    double wholesaleMarketPeriod;
    sscanf(argv[2], "%lf%*s", &wholesaleMarketPeriod);
    LINFO << "Wholesale market period [seconds]: " << wholesaleMarketPeriod;
    double wholesaleTimeShift;
    sscanf(argv[3], "%lf%*s", &wholesaleTimeShift);
    LINFO << "Wholesale market time shift relative to actual market clearing (due to delays in sequence) [seconds] " << wholesaleTimeShift;
    double dsoISORelativeTimeShift;
    sscanf(argv[4], "%lf%*s", &dsoISORelativeTimeShift);
    LINFO << "DSO time shift relative to when the wholesale market simulator (ISO) gets to run [seconds]: " << dsoISORelativeTimeShift;
    int quantityPriority;
    sscanf(argv[5], "%d%*s", &quantityPriority);
    LINFO << "Going with (if flag is 1) optimization at DSO and LSE levels to get local LMPs, that is 'quantity priority' case, or without (if flag is 0), that is 'price priority' case when DSO and LSE just take the ISO LMPs and propagate them downwards to the DER's." << quantityPriority;
    double currentTime = 0; //current time in seconds
    double nextTimeBM = 0, nextTimeAM = 0; // next time in seconds
    double nextFNCSTime = 0; // next time returned by FNCS for the simulator to run
    int iteration = 1;
    
    // a string stream we use to transfer from double to string
    stringstream doubleToString;
    
    // portion to initialize FNCS
    LINFO << "Initializing FNCS";                  
    fncs::initialize();

    // Initialization of times
    nextFNCSTime = wholesaleMarketPeriod - wholesaleTimeShift - dsoISORelativeTimeShift;
    nextTimeBM = nextFNCSTime;
    nextTimeAM = nextTimeBM + 2 * dsoISORelativeTimeShift;

    LDEBUG << "Some FNCS initial times: ";
    LDEBUG << "\t\t DSO time delta =  " << fncs::get_time_delta();
    LDEBUG << "\t\t DSO delta time between actual DSO calls = " << nextTimeAM - nextTimeBM;
    
    // determine simulator name
    string simName = fncs::get_name();
    LINFO << "Name of simulator is -> " << simName;        
    
    // get a vector list of the values we subscribe to and create a vector for bid price and quantity
    vector<string> subscription_keys = fncs::get_keys();
    vector<string> subscription_mdCurveCoeff_keys;    
    vector<string> subscription_MinMaxCumQuant_keys;
    vector<string> subscription_currUnrespLoad_keys;
    vector<string> connectedLSEnames;
    string subscription_iso_allocConsumption_key, subscription_iso_LMP_key;
            
    // loop through subscriptions and seperate them out into different vectors bid price and quantity
    for(vector<string>::size_type i = 0; i != subscription_keys.size(); i++) {
      if (subscription_keys[i].find("mdCurveCoeff") != string::npos) {
        subscription_mdCurveCoeff_keys.push_back(subscription_keys[i]); // each LSE under the DSO would publish the 2 coefficients of the linear fit for the marginal demand curve
        connectedLSEnames.push_back(subscription_keys[i].substr(0, subscription_keys[i].find("mdCurveCoeff") - 1));
      } else if (subscription_keys[i].find("MinMaxCumQuant") != string::npos) {
        subscription_MinMaxCumQuant_keys.push_back(subscription_keys[i]); // each LSE under the DSO would publish the minimum and maximum cumulative bids, in MW
      } else if (subscription_keys[i].find("currUnresponsiveLoad") != string::npos) {
        subscription_currUnrespLoad_keys.push_back(subscription_keys[i]); // each LSE under the DSO would publish its unresponsive/non-dispatchable current load, in MW
      } else if (subscription_keys[i].find("allocatedConsumption") != string::npos) {
        subscription_iso_allocConsumption_key = subscription_keys[i]; // the DSO receives the allocated power consumption from wholesale after OPF, in MW from MATPOWER
      } else if (subscription_keys[i].find("receivedLMP") != string::npos) {
        subscription_iso_LMP_key = subscription_keys[i]; // the DSO receives the bus LMP from wholesale after OPF, in $/MW from MATPOWER
      }
    }
    // vectors of equal size for the actual values
    vector<string> subscription_mdCurveCoeff_values(subscription_mdCurveCoeff_keys.size());
    vector<string> subscription_MinMaxCumQuant_values(subscription_MinMaxCumQuant_keys.size());
    vector<double> subscription_currUnrespLoad_values(subscription_currUnrespLoad_keys.size());
            
    // show the user what is being subscribed to
    LDEBUG << "Subscriptions:";
    for (vector<string>::const_iterator i = subscription_keys.begin(); i != subscription_keys.end(); ++i) {
        LDEBUG << "    " << *i ;
    }
        
    vector<double> lseMPcoeff(2 * subscription_mdCurveCoeff_keys.size());
    vector<double> lseMinMaxCumQuants(2 * subscription_MinMaxCumQuant_keys.size());
    int qLinSpaceLength = 100, costFitOrder = 2;
    vector<double> lseQuants; //(qLinSpaceLength * subscription_MinMaxCumQuant_keys.size());
    vector<double> lseCumQuants; //(qLinSpaceLength * subscription_MinMaxCumQuant_keys.size());
    vector<double> lseMargPrices;//(qLinSpaceLength * subscription_MinMaxCumQuant_keys.size());
    vector<double> dsoCosts;//(qLinSpaceLength * subscription_MinMaxCumQuant_keys.size());
    vector<double> dsoCumCosts;//(qLinSpaceLength * subscription_MinMaxCumQuant_keys.size());
    vector<double> demandCurveCoeff(costFitOrder + 1, 0);
    vector<double> lseAllocConsumption(subscription_mdCurveCoeff_keys.size());
    vector<double> tempQ(qLinSpaceLength), tempP(qLinSpaceLength);
    double dsoAllocatedLoad, isoLMP, dsoLMP;
    // output CSV file to save the data in
    ofstream dsoToISOOutputData(simName + "-dso2isoOutputData.csv", ios::out);
    dsoToISOOutputData << "iteration, current time [s], available dispatchable load [MW], c2, c1, c0, unresponsive load [MW]" << endl;
    ofstream dsoToLSEOutputData(simName + "-dso2lseOutputData.csv", ios::out);
    dsoToLSEOutputData << "iteration, current time [s], DSO allocated load [MW], DSO LMP [$/MW]";
    for (int i = 0; i < subscription_mdCurveCoeff_keys.size(); i++) {
      dsoToLSEOutputData << ", LSE " << i + 1 << " allocated load [MW]";
    }
    dsoToLSEOutputData << endl;

    do {
      // update time
      LDEBUG << "Current time = " << currentTime;

      if (currentTime == nextTimeBM) {
        // info for what iteration we are calculating for
        LDEBUG << "===== DSO performing tasks BEFORE wholesale market clears, at iteration -> " << iteration << " =====";
        dsoCosts.clear();
        dsoCumCosts.clear();
        lseQuants.clear();
        lseCumQuants.clear();
        lseMargPrices.clear();

        // obtain the currently unresponsive load at the level of each LSE
        for (vector<string>::size_type i = 0; i != subscription_currUnrespLoad_keys.size(); i++) {
          subscription_currUnrespLoad_values[i] = atof((fncs::get_value(subscription_currUnrespLoad_keys[i])).c_str());
          LDEBUG1 << subscription_currUnrespLoad_keys[i] << " -> " << subscription_currUnrespLoad_values[i];
        }
          
        // obtain marginal price curve coefficients from LSE as a string,
        // split it in 2 at the comma, create the 2 substrings,
        // eliminate spaces if any in the substrings, then stream them into a 2D array
        for(vector<string>::size_type i = 0; i != subscription_mdCurveCoeff_keys.size(); i++) {
          subscription_mdCurveCoeff_values[i] = fncs::get_value(subscription_mdCurveCoeff_keys[i]);
          LDEBUG1 << subscription_mdCurveCoeff_keys[i] << " -> " << subscription_mdCurveCoeff_values[i];
          size_t splitInd = subscription_mdCurveCoeff_values[i].find(",");
          stringstream(delSpace(subscription_mdCurveCoeff_values[i].substr(0, splitInd))) >> lseMPcoeff[2 * i];
          stringstream(delSpace(subscription_mdCurveCoeff_values[i].substr(splitInd + 1))) >> lseMPcoeff[2 * i + 1];
        }    

        // obtain minimum and maximum cumulative quantities from each LSE as a string
        for(vector<string>::size_type i = 0; i != subscription_MinMaxCumQuant_keys.size(); i++) {
          subscription_MinMaxCumQuant_values[i] = fncs::get_value(subscription_MinMaxCumQuant_keys[i]);
          size_t splitInd = subscription_MinMaxCumQuant_values[i].find(",");
          stringstream(delSpace(subscription_MinMaxCumQuant_values[i].substr(0, splitInd))) >> lseMinMaxCumQuants[2 * i];
          stringstream(delSpace(subscription_MinMaxCumQuant_values[i].substr(splitInd + 1))) >> lseMinMaxCumQuants[2 * i + 1];
          if (lseMinMaxCumQuants[2 * i] >= 0 && lseMinMaxCumQuants[2 * i + 1] > 0) {
            tempQ = linspace(lseMinMaxCumQuants[2 * i], lseMinMaxCumQuants[2 * i + 1], qLinSpaceLength);
            for (int j = 0; j < qLinSpaceLength; j++) {
              tempP[j] = lseMPcoeff[2 * i] * tempQ[j] + lseMPcoeff[2 * i + 1];
            }
            lseCumQuants.insert(lseCumQuants.begin(), tempQ.begin(), tempQ.end());
            lseMargPrices.insert(lseMargPrices.begin(), tempP.begin(), tempP.end());
            vector<double>::iterator inFirst = tempQ.begin();
            vector<double>::iterator inLast = tempQ.begin() + qLinSpaceLength;
            vector<double>::iterator outFirst = tempQ.begin();
            adjacent_difference(inFirst, inLast, outFirst);
            lseQuants.insert(lseQuants.begin(), tempQ.begin(), tempQ.end());
          }
          /*
          temp = linspace(lseMinMaxCumQuants[2 * i], lseMinMaxCumQuants[2 * i + 1], qLinSpaceLength);
          for (int j = 0; j < qLinSpaceLength; j++) {
           	lseCumQuants[qLinSpaceLength * i + j] = temp[j];
           	lseMargPrices[qLinSpaceLength * i + j] = lseMPcoeff[2 * i] * lseCumQuants[qLinSpaceLength * i + j] + lseMPcoeff[2 * i + 1];
          }
          vector<double>::iterator inFirst = lseCumQuants.begin() + i * qLinSpaceLength;
          vector<double>::iterator inLast = lseCumQuants.begin() + (i + 1) * qLinSpaceLength;
          vector<double>::iterator outFirst = lseQuants.begin() + i * qLinSpaceLength;
          adjacent_difference(inFirst, inLast, outFirst);
          */
        }
        if (!lseQuants.empty()) {
          vector<pair<double, double>> zipped;
          zip(lseQuants, lseMargPrices, zipped);
          sort(zipped.rbegin(), zipped.rend(), CompareSecond());
          unzip(zipped, lseQuants, lseMargPrices);
          partial_sum(lseQuants.begin(), lseQuants.end(), lseCumQuants.begin());
          for (int i = 0; i < lseMargPrices.size(); i++) {
            dsoCosts.push_back(lseMargPrices[i] * lseQuants[i]);
            //LDEBUG << "\t marg price: " << lseMargPrices[i] << ", quant: " << lseQuants[i] << ", cum quant: " << lseCumQuants[i] << ", dsoCost: " << dsoCosts[i] << "\n";
          }
          dsoCumCosts.resize(dsoCosts.size());
          partial_sum(dsoCosts.begin(), dsoCosts.end(), dsoCumCosts.begin());
          demandCurveCoeff = polyfit(lseCumQuants, dsoCumCosts, costFitOrder);
          for (vector<double>::iterator i = demandCurveCoeff.begin(); i != demandCurveCoeff.end(); i++)
            if (isnan(*i) != 0)
              *i = 0;
          LDEBUG << "\n\t demand curve coeff in incremental powers as returned by polyfit:\n\t";
          for (vector<double>::iterator i = demandCurveCoeff.begin(); i != demandCurveCoeff.end(); i++)
            LDEBUG << "\t" << *i;
          LDEBUG << "\n";
        
          // publish the maximum available dispatchable load
          doubleToString << lseCumQuants.back();
          fncs::publish("maxDispLoad", doubleToString.str());
          LDEBUG << "maximum dispatchable load [MW] -> " << doubleToString.str();
          doubleToString.str(string());

          // publish the demand curve coefficients in decremental powers as needed by MATPOWER
          for (vector<double>::iterator i = demandCurveCoeff.end() - 1; i != demandCurveCoeff.begin() - 1; i--) {
            if (i != demandCurveCoeff.end() - 1)
              doubleToString << ",";
            doubleToString << *i;
          }
          fncs::publish("dispLoadDemandCurve", doubleToString.str());
          dsoToISOOutputData << iteration << "," << currentTime << "," << lseCumQuants.back() << "," << doubleToString.str() << ","; // << dsoCurrUnrespLoad << endl;
          LDEBUG << "demand curve coefficients in decremental powers -> " << doubleToString.str();
          doubleToString.str(string());
        } else {
          // publish the maximum available dispatchable load
          fncs::publish("maxDispLoad", "0");
          LDEBUG << "maximum dispatchable load [MW] -> 0.";
          // publish the demand curve coefficients in decremental powers as needed by MATPOWER
          fncs::publish("dispLoadDemandCurve", "0,0,0");
          dsoToISOOutputData << iteration << "," << currentTime << ", 0, 0, 0, 0, "; // << dsoCurrUnrespLoad << endl;
          LDEBUG << "demand curve coefficients in decremental powers -> 0, 0, 0";
        }
        
        // the currently unresponsive load
        double dsoCurrUnrespLoad = accumulate(subscription_currUnrespLoad_values.begin(), subscription_currUnrespLoad_values.end(), 0.0);
        doubleToString << dsoCurrUnrespLoad;
        fncs::publish("unresponsiveLoad", doubleToString.str());
        LDEBUG << "currently unresponsive load [MW] -> " << doubleToString.str();
        dsoToISOOutputData << doubleToString.str() << endl;
        doubleToString.str(string());
        // request new time from FNCS
        nextTimeAM = min(currentTime + 2 * dsoISORelativeTimeShift, simStopTime);
				nextFNCSTime = fncs::time_request(nextTimeAM);
				LDEBUG << "Right before market: current time = " << currentTime << ", current before-market time = " << nextTimeBM << ", next after-market time = " << nextTimeAM << ", next FNCS time request = " << nextFNCSTime << ", iteration = " << iteration;
      } else if (currentTime == nextTimeAM) {
        LDEBUG << "===== DSO performing tasks AFTER wholesale market (ISO simulator) ran, at iteration -> " << iteration << " =====";
        dsoAllocatedLoad = atof((fncs::get_value(subscription_iso_allocConsumption_key)).c_str());
        isoLMP = atof((fncs::get_value(subscription_iso_LMP_key)).c_str());
        if (!lseQuants.empty() && quantityPriority == 1)
          dsoLMP = determinePrice(dsoAllocatedLoad, isoLMP, lseQuants, lseMargPrices);
        else
          dsoLMP = isoLMP;
        doubleToString << dsoLMP;
        fncs::publish("LMP", doubleToString.str());
        LDEBUG << "DSO locally calculated LMP: " << dsoLMP << " $/MW.";
        dsoToLSEOutputData << iteration << ", " << currentTime << ", " << dsoAllocatedLoad << ",  " << dsoLMP;
        doubleToString.str(string());
        LDEBUG << "There are " << dsoAllocatedLoad << " MW allocated for this DSO, at a local DSO LMP of " << dsoLMP << " $/MW";
        for (vector<string>::size_type i = 0; i < subscription_mdCurveCoeff_keys.size(); i++) {
          if (lseMPcoeff[2 * i] != 0) {
            lseAllocConsumption[i] = (dsoLMP - lseMPcoeff[2 * i + 1]) / lseMPcoeff[2 * i];
            lseAllocConsumption[i] = lseAllocConsumption[i] < lseMinMaxCumQuants[2 * i] ? lseMinMaxCumQuants[2 * i] : lseAllocConsumption[i];
            lseAllocConsumption[i] = lseAllocConsumption[i] > lseMinMaxCumQuants[2 * i + 1] ? lseMinMaxCumQuants[2 * i + 1] : lseAllocConsumption[i];
          } else
            lseAllocConsumption[i] = 0;
          LDEBUG << "Calculated load for LSE " << i + 1 << " -> " << lseAllocConsumption[i] << " MW.";
          doubleToString << lseAllocConsumption[i];
          fncs::publish(connectedLSEnames[i] + "_allocatedConsumption", doubleToString.str());
          LDEBUG << "Allocated load for LSE " << i + 1 << " -> " << doubleToString.str() << " MW, for a flexibility range between " << lseMinMaxCumQuants[2 * i] << " and " << lseMinMaxCumQuants[2 * i + 1] << " MW.";
          doubleToString.str(string());
          dsoToLSEOutputData << ", " << lseAllocConsumption[i];
        }
        dsoToLSEOutputData << endl;
        nextTimeBM = min(currentTime + wholesaleMarketPeriod - 2 * dsoISORelativeTimeShift, simStopTime);
				nextFNCSTime = fncs::time_request(nextTimeBM);
				LDEBUG << "Right after market: current time = " << currentTime << ", current after-market time = " << nextTimeAM << ", next before-market time = " << nextTimeBM << ", next FNCS time request = " << nextFNCSTime << ", iteration = " << iteration;
        iteration += 1;
      } else {
        nextFNCSTime = currentTime < nextTimeBM ? fncs::time_request(nextTimeBM) : fncs::time_request(nextTimeAM);
				LDEBUG << "Non-action time for DSO: current time = " << currentTime << ", next FNCS time request = " << nextFNCSTime;   
      }
      currentTime = nextFNCSTime;
    }
    while(currentTime < simStopTime);
  }    
  catch (const exception& e) {
    LERROR << "Caught a standard exception, see below for details";
    cerr << e.what() << endl;
    cerr << "Terminating program..." << endl;
    fncs::die();
    return -2;
  }
  catch (...) {
    LERROR << "Unknown and unexpected error thrown";
    cerr << "Terminating program..." << endl;
    fncs::die();
    return -3;
  }    
    
  time_t tStop = time(0);
  LINFO << "Simulation took " << (float) (tStop-tStart) << " seconds";
  LINFO << "Terminating FNCS";
  fncs::finalize();
  return 0;
}
