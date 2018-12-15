#include "lse.hpp"

/* ==================================================================================================================
====================== MAIN PART ====================================================================================
===================================================================================================================*/

int main(int argc, const char *argv[]) {
	// variable to keep track of the total time used
	time_t tStart = time(0);
	
	// Setting up the logger based on user input
	char *log_level_export = NULL;
	log_level_export = getenv("LSE_LOG_LEVEL");
	
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
		LINFO << "Simulation stop time [seconds]: " << simStopTime;
		double amp_fact;
		sscanf(argv[2], "%lf%*s", &amp_fact);
		LINFO << "Amplification factor: " << amp_fact;
		double wholesaleMarketPeriod;
		sscanf(argv[3], "%lf%*s", &wholesaleMarketPeriod);
		LINFO << "Wholesale market period [seconds]: " << wholesaleMarketPeriod;
		double wholesaleTimeShift;
		sscanf(argv[4], "%lf%*s", &wholesaleTimeShift);
		LINFO << "Wholesale market time shift relative to actual market clearing (due to delays in sequence) [seconds] " << wholesaleTimeShift;
		double lseISORelativeTimeShift;
		sscanf(argv[5], "%lf%*s", &lseISORelativeTimeShift);
		LINFO << "LSE time shift relative to when the wholesale market simulator (ISO) gets to run [seconds]: " << lseISORelativeTimeShift;
		int quantityPriority;
    sscanf(argv[6], "%d%*s", &quantityPriority);
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
		nextFNCSTime = wholesaleMarketPeriod - wholesaleTimeShift - lseISORelativeTimeShift;
		nextTimeBM = nextFNCSTime;
		nextTimeAM = nextTimeBM + 2 * lseISORelativeTimeShift;

		LDEBUG << "Some FNCS initial times: ";
		LDEBUG << "\t\t LSE time delta =  " << fncs::get_time_delta();
		LDEBUG << "\t\t LSE delta time between actual LSE calls = " << nextTimeAM - nextTimeBM;
		
		// determine simulator name
		string simName = fncs::get_name();
		LINFO << "Name of simulator is -> " << simName;		
		
		// get a vector list of the values we subscribe to and create a vector for bid price and quantity
		vector<string> subscription_keys = fncs::get_keys();
		vector<string> subscription_bid_price_keys;	
		vector<string> subscription_bid_quantity_keys;
		vector<string> subscription_actual_load_keys;
		string subscription_feeder_load_key, subscription_dso_allocConsumption_key, subscription_dso_LMP_key;
			
		// loop through subscriptions and seperate them out into different vectors bid price and quantity
		for(vector<string>::size_type i = 0; i != subscription_keys.size(); i++) {
			if (subscription_keys[i].find("bid_price") != string::npos) {
				subscription_bid_price_keys.push_back(subscription_keys[i]); // GridLAB-D, through its DER components, will provide this, and it will be in $/W
			} else if (subscription_keys[i].find("bid_quantity") != string::npos) {
				subscription_bid_quantity_keys.push_back(subscription_keys[i]); // GridLAB-D, through its DER components, will provide this, and it will be in W
			} else if (subscription_keys[i].find("actual_load") != string::npos) {
				subscription_actual_load_keys.push_back(subscription_keys[i]); // GridLAB-D, through its DER components, will provide this, and it will be in KW
			} else if (subscription_keys[i].find("headLoad") != string::npos) {
				subscription_feeder_load_key = subscription_keys[i]; // GridLAB-D will provide this, and could be in different formats, with different units
			} else if (subscription_keys[i].find("allocatedConsumption") != string::npos) {
				subscription_dso_allocConsumption_key = subscription_keys[i]; // DSO simulator will provide the allocated power consumption, and will be given in MW
			} else if (subscription_keys[i].find("receivedLMP") != string::npos) {
				subscription_dso_LMP_key = subscription_keys[i]; // DSO simulator will provide its locally calculated LMP, and will be given in $/MW
			}
		}
		
		// vectors of equal size for the actual values
		vector<double> subscription_values (subscription_keys.size());
		vector<double> subscription_bid_price_values (subscription_bid_price_keys.size());
		vector<double> subscription_bid_quantity_values (subscription_bid_quantity_keys.size());
		vector<double> subscription_actual_load_values (subscription_actual_load_keys.size());
		
		// adding in a file that collects data for bid price
		ofstream controller_price_data(simName + "-PriceData.csv", ios::out);
		// creating the beginning of the header for the file
		controller_price_data << "iteration, current time";
		for (vector<string>::const_iterator i = subscription_bid_price_keys.begin(); i != subscription_bid_price_keys.end(); ++i) {
			controller_price_data << "," << *i ;
		}
		controller_price_data << endl;

		// adding in a file that collects data for bid quantity
		ofstream controller_quantity_data(simName + "-QuantityData.csv", ios::out);
		// creating the beginning of the header for the file
		controller_quantity_data << "iteration, current time";
		for (vector<string>::const_iterator i = subscription_bid_quantity_keys.begin(); i != subscription_bid_quantity_keys.end(); ++i) {
			controller_quantity_data << "," << *i ;
		}
		controller_quantity_data << endl;

		// adding in a file that collects data for actual load
		ofstream controller_actual_load_data(simName + "-ActualLoadData.csv", ios::out);
		// creating the beginning of the header for the file
		controller_actual_load_data << "iteration, current time";
		for (vector<string>::const_iterator i = subscription_actual_load_keys.begin(); i != subscription_actual_load_keys.end(); ++i) {
			controller_actual_load_data << "," << *i ;
		}
		controller_actual_load_data << endl;		
		
		// adding in a file that collects data for aggregator demand curve and maximun controllable load
		ofstream lse2dso(simName + "-lse2dsoOutputData.csv", ios::out);
		// creating the beginning of the header for the file
		lse2dso << "iteration, current time, mc1, mc0, min Q bid, max Q bid, currently dispatched load, feeder head real power, feeder head unresponsive load" << endl;
		
		// adding a file to collect the LSE allocated load, and its local LMP
		ofstream lse2feederOutputData(simName + "-lse2feederOutputData.csv", ios::out);
		lse2feederOutputData << "iteration, current time [s], allocated load [MW], local LMP [$/MW]" << endl;

    // ====================== 2018/08/07 =========================
		// for the purpose of analyzing the demand curve approximation process, we log some of the intermediate data
		ofstream intDataBeforeZip(simName + "-intDataBeforeZip.csv", ios::out);
		intDataBeforeZip << "iteration, current time, xData, yData" << endl;
		ofstream intDataAfterZip(simName + "-intDataAfterZip.csv", ios::out);
		intDataAfterZip << "iteration, current time, xData, yData" << endl;
		ofstream intDataCumSum(simName + "-intDataCumSum.csv", ios::out);
		intDataCumSum << "iteration, current time, xDataSum" << endl;

		// show the user what is being subscribed to
		LDEBUG << "Subscriptions:";
		for (vector<string>::const_iterator i = subscription_keys.begin(); i != subscription_keys.end(); ++i) {
			LDEBUG << "    " << *i ;
		}

		// let's create new data sets with only the value that are not 0 or pricecap (1000)
		vector<double> xData, yData, xDataSum, loadData, marginalDemandCurve;
		vector<double> demandCurve;
		double feederHeadRealPower, lseAllocatedLoad, dsoLMP;
		double actualDispLoad, feederUnrespRealPower;
		
    do {
			// update time
			LDEBUG << "Current time = " << currentTime;
		
			if (currentTime == nextTimeBM) { // calculate next step		
				// info for what iteration we are calculating for
				LDEBUG << "===== LSE performing tasks BEFORE wholesale market clears, at iteration -> " << iteration << " =====";
				
				// update bid price subscriptions
				for(vector<double>::size_type i = 0; i != subscription_bid_price_keys.size(); i++) {
					subscription_bid_price_values[i] = atof((fncs::get_value(subscription_bid_price_keys[i])).c_str());
					LDEBUG1 << subscription_bid_price_keys[i] << " -> " << subscription_bid_price_values[i];			
				}	

				// update bid quantity subscriptions
				for(vector<double>::size_type i = 0; i != subscription_bid_quantity_keys.size(); i++) {
					subscription_bid_quantity_values[i] = atof((fncs::get_value(subscription_bid_quantity_keys[i])).c_str());
					LDEBUG1 << subscription_bid_quantity_keys[i] << " -> " << subscription_bid_quantity_values[i];			
				}	

				// update actual load subscriptions
				for(vector<double>::size_type i = 0; i != subscription_actual_load_keys.size(); i++) {
					subscription_actual_load_values[i] = atof((fncs::get_value(subscription_actual_load_keys[i])).c_str());
					LDEBUG1 << subscription_actual_load_keys[i] << " -> " << subscription_actual_load_values[i];			
				}
				
				// update the real power at the head of the feeder, in MW
        		feederHeadRealPower = amp_fact * getFeederHeadRealPower(fncs::get_value(subscription_feeder_load_key));
				LDEBUG1 << subscription_feeder_load_key << " -> " << feederHeadRealPower;

				// let's create new data sets with only the value that are not 0 or pricecap (1000)
				xData.clear();
				xDataSum.clear();
				yData.clear();
				loadData.clear();
				demandCurve.clear();
							
				// then let's get that curve going
				for(vector<double>::size_type i = 0; i != subscription_bid_price_keys.size(); i++) {
					// check that bid price is greater than 0 but less than 40. Also check that bid_quantity is greater than zero
					if (subscription_bid_price_values[i] > BID_PRICE_MIN && subscription_bid_price_values[i] < BID_PRICE_CAP && subscription_bid_quantity_values[i] > BID_QUANT_MIN) {
						// for now we are using units in MW
						xData.push_back(subscription_bid_quantity_values[i] / 1e6 * amp_fact);
						loadData.push_back(subscription_actual_load_values[i] / 1e3 * amp_fact);
						yData.push_back(subscription_bid_price_values[i]);
					}		
				}
				
				// some debug messages for what is in the curve
				for(vector<double>::size_type i = 0; i != xData.size(); i++) {
					LDEBUG1 << "    xData -> " << xData[i] << "    yData -> " << yData[i];
				}
				
				// check if we have enough points to continue
				// for the marginal demand curve, we only need a minimum of 2 points, as the curve is approximate as linear
				if (static_cast<int>(xData.size()) >= (int) 2) {
				  // ====================== 2018/08/07 =========================
					for(vector<double>::size_type i = 0; i != xData.size(); i++) {
						intDataBeforeZip << iteration << "," << currentTime << "," << xData[i] << "," << yData[i] << endl;
					}
					// ===========================================================

					// Zip the demand curve vectors together
					vector<pair<double, double>> zipped;
					zip(xData, yData, zipped);
					
					// Sort the vector of pairs descending according to price, that is the 2nd column in the marginal demand curve zip
					sort(zipped.rbegin(), zipped.rend(), CompareSecond());
		
					// Write the sorted pairs back to the original vectors
					unzip(zipped, xData, yData);
					
					// ====================== 2018/08/07 =========================
					for(vector<double>::size_type i = 0; i != xData.size(); i++) {
						intDataAfterZip << iteration << "," << currentTime << "," << xData[i] << "," << yData[i] << endl;
					}
					// ===========================================================

					// some debug messages for what is in the curve
					LDEBUG1 << "";
					for(vector<double>::size_type i = 0; i != xData.size(); i++) {
						LDEBUG1 << "    xData -> " << xData[i] << "    yData -> " << yData[i];
					}
					
					// create the cumulative sum of the quantity vector
					xDataSum.resize(xData.size());
					partial_sum(xData.begin(), xData.end(), xDataSum.begin());
					xDataSum.front() = 0;

					// ====================== 2018/08/07 =========================
					for(vector<double>::size_type i = 0; i != xDataSum.size(); i++) {
						intDataCumSum << iteration << "," << currentTime << "," << xDataSum[i] << endl;
					}
					// ===========================================================

					// some debug messages for what is in cumulative sum vector
					LDEBUG1 << "";
					for(vector<double>::size_type i = 0; i != xDataSum.size(); i++) {
						LDEBUG1 << "    xDataSum -> " << xDataSum[i] ;
					}
					
					// approximating the marginal demand curve with a linear curve
					marginalDemandCurve = polyfit(xDataSum, yData, 1);
					// some debug messages for what is in the marginalDemandCurve vector
					LDEBUG1 << "";				
					for (vector<double>::const_iterator i = marginalDemandCurve.begin(); i != marginalDemandCurve.end(); ++i) {
						LDEBUG1 << "    marginalDemandCurve -> " << *i;
					}
          // publish marginal demand curve coefficients
          for (vector<double>::const_iterator i = marginalDemandCurve.end() - 1; i != marginalDemandCurve.begin() - 1; --i) {
            if (i != marginalDemandCurve.end() - 1) {
              doubleToString << ",";
            }
            doubleToString << *i;
          }
          fncs::publish("dispLoadMarginalDemandCurve", doubleToString.str());
          LDEBUG << "marginal demand curve coefficients -> " << doubleToString.str();
          doubleToString.str(string());
          // publish the minimum and maximum quantity bids (dispatachable loads), that is first and last element in xDataSum
          doubleToString << xDataSum.front() << "," << xDataSum.back();
          fncs::publish("min-maxQbids", doubleToString.str());
          LDEBUG << "min and max Q bids -> " << doubleToString.str();
          doubleToString.str(string());
				  // publish currently unresponsive load
					actualDispLoad = accumulate(loadData.begin(), loadData.end(), 0.0);
					feederUnrespRealPower = feederHeadRealPower - actualDispLoad;
					doubleToString << feederUnrespRealPower;
					fncs::publish("unresponsiveLoad", doubleToString.str());
					LDEBUG << "current unresponsive load -> " << doubleToString.str();
					doubleToString.str(string());	 
					// update the outcome data file
					lse2dso << iteration << "," << currentTime;
					for (vector<double>::const_iterator i = marginalDemandCurve.end() - 1; i != marginalDemandCurve.begin() - 1; --i) {
					  lse2dso << "," << *i;
					}
					lse2dso << "," << xDataSum.front() << "," << xDataSum.back();
					lse2dso << "," << actualDispLoad << "," << feederHeadRealPower << "," << feederUnrespRealPower << endl;	
				} else {
					LWARNING << "not enough controllers are bidding";
					// publish marginal demand curve coefficients
					fncs::publish("dispLoadMarginalDemandCurve", "0,0");
					LDEBUG << "marginal demand curve coefficients -> " << "0,0";
					// publish minimum and maximum qunatity bids
					fncs::publish("min-maxQbids", "0,0");
					LDEBUG << "min and max Q bids -> " << "0,0";
					// publish currently dispatched load
					actualDispLoad = accumulate(loadData.begin(), loadData.end(), 0.0);
          feederUnrespRealPower = feederHeadRealPower - actualDispLoad;
					doubleToString << feederUnrespRealPower;
					fncs::publish("unresponsiveLoad", doubleToString.str());
					LDEBUG << "current unresponsive load -> " << doubleToString.str();
					doubleToString.str(string());	

					// update the outcome data file
					lse2dso << iteration << "," << currentTime << ",0,0,0,0," << actualDispLoad << "," << feederHeadRealPower << "," << feederUnrespRealPower << endl;
				}
				
				// update the price data file
				controller_price_data << iteration << "," << currentTime;
				for (vector<double>::const_iterator i = subscription_bid_price_values.begin(); i != subscription_bid_price_values.end(); ++i) {
					controller_price_data << "," << *i;
				}
				controller_price_data << endl;

				// update the quantity data file
				controller_quantity_data << iteration << "," << currentTime;
				for (vector<double>::const_iterator i = subscription_bid_quantity_values.begin(); i != subscription_bid_quantity_values.end(); ++i) {
					controller_quantity_data << "," << *i;
				}
				controller_quantity_data << endl;				
				
				// update the actual load data file
				controller_actual_load_data << iteration << "," << currentTime;
				for (vector<double>::const_iterator i = subscription_actual_load_values.begin(); i != subscription_actual_load_values.end(); ++i) {
					controller_actual_load_data << "," << *i;
				}
				controller_actual_load_data << endl;
				
				// request new time from FNCS
				nextTimeAM = min(currentTime + 2 * lseISORelativeTimeShift, simStopTime);
				nextFNCSTime = fncs::time_request(nextTimeAM);
				LDEBUG << "Right before market: current time = " << currentTime << ", current before-market time = " << nextTimeBM << ", next after-market time = " << nextTimeAM << ", next FNCS time request = " << nextFNCSTime << ", iteration = " << iteration;
			} else if (currentTime == nextTimeAM) {
				LDEBUG << "===== LSE performing tasks AFTER wholesale market (ISO simulator) ran, at iteration -> " << iteration << " =====";
				lseAllocatedLoad = atof((fncs::get_value(subscription_dso_allocConsumption_key)).c_str());
				dsoLMP = atof((fncs::get_value(subscription_dso_LMP_key)).c_str());
				LDEBUG << "There are " << lseAllocatedLoad << " MW allocated to this LSE.";
				double lseLMP;
				if (static_cast<int>(xData.size()) >= (int) 2 && quantityPriority == 1) {
				  lseLMP = determinePrice(lseAllocatedLoad, dsoLMP, xData, yData);
				} else {
					lseLMP = dsoLMP;
				}
				doubleToString << lseLMP;
				fncs::publish("LMP", doubleToString.str());
				LDEBUG << "LSE LMP -> " << doubleToString.str();
				doubleToString.str(string());
				// collecting data to output file
				lse2feederOutputData << iteration << "," << currentTime << "," << lseAllocatedLoad << "," << lseLMP << endl;
				// request new time from FNCS
        nextTimeBM = min(currentTime + wholesaleMarketPeriod - 2 * lseISORelativeTimeShift, simStopTime);
				nextFNCSTime = fncs::time_request(nextTimeBM);
				LDEBUG << "Right after market: current time = " << currentTime << ", current after-market time = " << nextTimeAM << ", next before-market time = " << nextTimeBM << ", next FNCS time request = " << nextFNCSTime << ", iteration = " << iteration;
				iteration += 1;
			} else {
				nextFNCSTime = currentTime < nextTimeBM ? fncs::time_request(nextTimeBM) : fncs::time_request(nextTimeAM);
				LDEBUG << "Non-action time for LSE: current time = " << currentTime << ", next FNCS time request = " << nextFNCSTime;
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