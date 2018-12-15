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
  
  	LINFO << "Running process -> " << argv[0] ;
     
  	// portion to initialize HELICS
  	LINFO << "Initializing HELICS federate";
  	// configuration file for federate
  	std::string configString = argv[1];
  	auto fed = std::make_unique<helics::ValueFederate> (configString); 
	
  	try {                
		// time keeping variables
		double simStopTime; // simulation stop time
		sscanf(argv[2], "%lf%*s", &simStopTime);
		LINFO << "Simulation stop time [seconds]: " << simStopTime;
		
		double wholesaleMarketPeriod;
		sscanf(argv[3], "%lf%*s", &wholesaleMarketPeriod);
		LINFO << "Wholesale market period [seconds]: " << wholesaleMarketPeriod;
		
		double wholesaleTimeShift;
		sscanf(argv[4], "%lf%*s", &wholesaleTimeShift);
		LINFO << "Wholesale market time shift relative to actual market clearing (due to delays in sequence) [seconds] " << wholesaleTimeShift;
		
		double dsoISORelativeTimeShift;
		sscanf(argv[5], "%lf%*s", &dsoISORelativeTimeShift);
		LINFO << "DSO time shift relative to when the wholesale market simulator (ISO) gets to run [seconds]: " << dsoISORelativeTimeShift;
		
		int quantityPriority;
		sscanf(argv[6], "%d%*s", &quantityPriority);
		LINFO << "Going with (if flag is 1) optimization at DSO and LSE levels to get local LMPs, that is 'quantity priority' case, or without (if flag is 0), that is 'price priority' case when DSO and LSE just take the ISO LMPs and propagate them downwards to the DER's." << quantityPriority;
		
		double currentTime = 0; //current time in seconds
		double nextTimeBM = 0, nextTimeAM = 0; // next time in seconds
		double nextHELICSTime = 0; // next time returned by HELICS for the simulator to run
		int iteration = 1;
	
		// a string stream we use to transfer from double to string
		stringstream doubleToString;
		
		// Initialization of times
		nextHELICSTime = wholesaleMarketPeriod - wholesaleTimeShift - dsoISORelativeTimeShift;
		nextTimeBM = nextHELICSTime;
		nextTimeAM = nextTimeBM + 2 * dsoISORelativeTimeShift;

		LDEBUG << "Some HELICS initial times: ";
		//LDEBUG << "\t\t LSE time delta =  " << fed->getTimeProperty();
		LDEBUG << "\t\t DSO delta time between actual DSO calls = " << nextTimeAM - nextTimeBM;
		
		// determine simulator name
		string simName = fed->getName();
		LINFO << "Name of simulator is -> " << simName;       
		
		// Let's get a list of the subscriptions we have 
		vector<string> subscription_keys;
		subscription_keys = vectorizeAndSortQueryResult(fed->query(fed->getName(), "subscriptions"));

		// list for properties we care about
		vector<string> subscription_mdCurveCoeff_keys;
		vector<helics::Input> subscription_mdCurveCoeff_ids;    
		vector<string> subscription_MinMaxCumQuant_keys;
		vector<helics::Input> subscription_MinMaxCumQuant_ids;
		vector<string> subscription_currUnrespLoad_keys;
		vector<helics::Input> subscription_currUnrespLoad_ids;
		string subscription_iso_allocConsumption_key, subscription_iso_LMP_key;
		helics::Input subscription_iso_allocConsumption_id, subscription_iso_LMP_id;
				
		// loop through subscriptions and seperate them out into different vectors bid price and quantity
		for(vector<string>::size_type i = 0; i != subscription_keys.size(); i++) {
			if (subscription_keys[i].find("demandCurve") != string::npos) {
				subscription_mdCurveCoeff_keys.push_back(subscription_keys[i]); // each LSE under the DSO would publish the 2 coefficients of the linear fit for the marginal demand curve
				auto idTemp = fed->getSubscription(subscription_keys[i]);
				idTemp.setDefault<string>("0,0");
				subscription_mdCurveCoeff_ids.push_back(idTemp);
			} else if (subscription_keys[i].find("minMaxQ") != string::npos) {
				subscription_MinMaxCumQuant_keys.push_back(subscription_keys[i]); // each LSE under the DSO would publish the minimum and maximum cumulative bids, in MW
				auto idTemp = fed->getSubscription(subscription_keys[i]);
				idTemp.setDefault<string>("0,0");
				subscription_MinMaxCumQuant_ids.push_back(idTemp);
			} else if (subscription_keys[i].find("unRespLoad") != string::npos) {
				subscription_currUnrespLoad_keys.push_back(subscription_keys[i]); // each LSE under the DSO would publish its unresponsive/non-dispatchable current load, in MW
				auto idTemp = fed->getSubscription(subscription_keys[i]);
				idTemp.setDefault<double>(0.0);
				subscription_currUnrespLoad_ids.push_back(idTemp);
			} else if (subscription_keys[i].find("dispLoad") != string::npos) {
				subscription_iso_allocConsumption_key = subscription_keys[i]; // the DSO receives the allocated power consumption from wholesale after OPF, in MW from MATPOWER
				subscription_iso_allocConsumption_id = fed->getSubscription(subscription_keys[i]);
				subscription_iso_allocConsumption_id.setDefault<double>(0.0);
			} else if (subscription_keys[i].find("lmp") != string::npos) {
				subscription_iso_LMP_key = subscription_keys[i]; // the DSO receives the bus LMP from wholesale after OPF, in $/MW from MATPOWER
				subscription_iso_LMP_id = fed->getSubscription(subscription_keys[i]);
				subscription_iso_LMP_id.setDefault<double>(0.0);
			}
		}
		
		if (loglevel >= logDEBUG) {
			LDEBUG << "Subscriptions:";
			for(auto it = subscription_keys.begin(); it != subscription_keys.end(); ++it) {
				LDEBUG << "    " << *it ;
			}

			LDEBUG << "demand curve:";
			for(auto it = subscription_mdCurveCoeff_keys.begin(); it != subscription_mdCurveCoeff_keys.end(); ++it) {
				LDEBUG << "    " << *it ;
			}
			// show the user what is being subscribed to
			LDEBUG << "min max Q:";
			for(auto it = subscription_MinMaxCumQuant_keys.begin(); it != subscription_MinMaxCumQuant_keys.end(); ++it) {
				LDEBUG << "    " << *it ;
			}
			LDEBUG << "unresponsive load:";
			for(auto it = subscription_currUnrespLoad_keys.begin(); it != subscription_currUnrespLoad_keys.end(); ++it) {
				LDEBUG << "    " << *it ;
			}

			LDEBUG << "LMP: " << subscription_iso_LMP_key;
			LDEBUG << "dispatchable load: " << subscription_iso_allocConsumption_key;
		}
			
		// also get the publication we need to do. We expect 4 of them!
		vector<string> connected_lse_keys;
		vector<helics::Publication> connected_lse_ids;
		helics::Publication demandCurve_id, maxQbids_id, unresponsiveLoad_id, LMP_id;
		bool fLSE, fDC, fMM, fUR, fLMP = false;
		vector<string> publication_keys;
		publication_keys = vectorizeAndSortQueryResult(fed->query(fed->getName(), "publications"));
		
		LDEBUG << "Publications:";
	    for(vector<string>::size_type i = 0; i != publication_keys.size(); i++) {
	        if (publication_keys[i].find("dispLoad") != string::npos) {
				connected_lse_keys.push_back(publication_keys[i]); 
				connected_lse_ids.push_back(fed->getPublication(publication_keys[i]));
	        	fLSE = true;
	        } else if (publication_keys[i].find("demandCurve") != string::npos) {
	        	demandCurve_id = fed->getPublication(publication_keys[i]);
	        	fDC = true;
	        } else if (publication_keys[i].find("maxQ") != string::npos) {
	        	maxQbids_id = fed->getPublication(publication_keys[i]);
	        	fMM = true;
	        } else if (publication_keys[i].find("unRespLoad") != string::npos) {
	        	unresponsiveLoad_id = fed->getPublication(publication_keys[i]);
	        	fUR = true;
	        } else if (publication_keys[i].find("lmp") != string::npos) {
	        	LMP_id = fed->getPublication(publication_keys[i]);
	        	fLMP = true;
	        } else {
	        	LERROR << "unknown type of publication detected";
				fed->error(-4, "unknown type of publication detected");
        		return -4;
	        } 
	        LDEBUG  << "\t " << publication_keys[i];
   		}

   		if (fLSE+fDC+fMM+fUR+fLMP != 5) {
   			LERROR << "you entered " << fLSE+fDC+fMM+fUR+fLMP << "publications, we expect 4";
			fed->error(-5, "wrong number of publication detected");
        	return -5;
   		}	
		
		// vectors of equal size for the actual values
		vector<string> subscription_mdCurveCoeff_values(subscription_mdCurveCoeff_keys.size());
		vector<string> subscription_MinMaxCumQuant_values(subscription_MinMaxCumQuant_keys.size());
		vector<double> subscription_currUnrespLoad_values(subscription_currUnrespLoad_keys.size());
				
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

		// we are done with the setup, start the initialization
	    LINFO << "federate entering init mode";
	    fed->enterInitializingMode ();

	    // now enter execution state
	    fed->enterExecutingMode ();
	    LINFO << "federate entering exec mode";

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
					subscription_currUnrespLoad_values[i] = subscription_currUnrespLoad_ids[i].getValue<double>();
				  	LDEBUG1 << subscription_currUnrespLoad_keys[i] << " -> " << subscription_currUnrespLoad_values[i];
				}
				  
				// obtain marginal price curve coefficients from LSE as a string,
				// split it in 2 at the comma, create the 2 substrings,
				// eliminate spaces if any in the substrings, then stream them into a 2D array
				for(vector<string>::size_type i = 0; i != subscription_mdCurveCoeff_keys.size(); i++) {
					subscription_mdCurveCoeff_values[i] = subscription_mdCurveCoeff_ids[i].getValue<string>();
				  	LDEBUG1 << subscription_mdCurveCoeff_keys[i] << " -> " << subscription_mdCurveCoeff_values[i];
				  	size_t splitInd = subscription_mdCurveCoeff_values[i].find(",");
				  	stringstream(delSpace(subscription_mdCurveCoeff_values[i].substr(0, splitInd))) >> lseMPcoeff[2 * i];
				  	stringstream(delSpace(subscription_mdCurveCoeff_values[i].substr(splitInd + 1))) >> lseMPcoeff[2 * i + 1];
				}    

				// obtain minimum and maximum cumulative quantities from each LSE as a string
				for(vector<string>::size_type i = 0; i != subscription_MinMaxCumQuant_keys.size(); i++) {
					subscription_MinMaxCumQuant_values[i] = subscription_MinMaxCumQuant_ids[i].getValue<string>();
				  	LDEBUG1 << subscription_MinMaxCumQuant_keys[i] << " -> " << subscription_MinMaxCumQuant_values[i];
				  	size_t splitInd = subscription_MinMaxCumQuant_values[i].find(",");
				  	stringstream(delSpace(subscription_MinMaxCumQuant_values[i].substr(0, splitInd))) >> lseMinMaxCumQuants[2 * i];
				  	stringstream(delSpace(subscription_MinMaxCumQuant_values[i].substr(splitInd + 1))) >> lseMinMaxCumQuants[2 * i + 1];
				  	
				  	// if (lseMinMaxCumQuants[2 * i] >= 0.  && lseMinMaxCumQuants[2 * 1 + 1] > 0.) { // JH pretty sure this is a bug!
				  	if (lseMinMaxCumQuants[2 * i] >= 0.  && lseMinMaxCumQuants[2 * i + 1] > 0.) { 
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
				  
				  	for (vector<double>::iterator i = demandCurveCoeff.begin(); i != demandCurveCoeff.end(); i++) {
						if (isnan(*i) != 0) {
					  		*i = 0;
						}
				  	}
				  		
				  	LDEBUG << "\n\t demand curve coeff in incremental powers as returned by polyfit:\n\t";
				  	for (vector<double>::iterator i = demandCurveCoeff.begin(); i != demandCurveCoeff.end(); i++) {
						LDEBUG << "\t" << *i;
				  	}
				  	LDEBUG << "\n";
				
				  	// publish the maximum available dispatchable load
				  	maxQbids_id.publish(lseCumQuants.back());
				  	LDEBUG << "maximum dispatchable load [MW] -> " << lseCumQuants.back();


				  	// publish the demand curve coefficients in decremental powers as needed by MATPOWER
				  	for (vector<double>::iterator i = demandCurveCoeff.end() - 1; i != demandCurveCoeff.begin() - 1; i--) {
						if (i != demandCurveCoeff.end() - 1) {
					  		doubleToString << ",";
						}
						doubleToString << *i;
				  	}
				  
				  	demandCurve_id.publish(doubleToString.str());
				  	dsoToISOOutputData << iteration << "," << currentTime << "," << lseCumQuants.back() << "," << doubleToString.str() << ","; // << dsoCurrUnrespLoad << endl;
				  	LDEBUG << "demand curve coefficients in decremental powers -> " << doubleToString.str();
				 	doubleToString.str(string());
				} else {
				  	// publish the maximum available dispatchable load
					maxQbids_id.publish(0.0);
				  	LDEBUG << "maximum dispatchable load [MW] -> 0.";
				  	// publish the demand curve coefficients in decremental powers as needed by MATPOWER
					demandCurve_id.publish("0,0,0");
				  	dsoToISOOutputData << iteration << "," << currentTime << ", 0, 0, 0, 0, "; // << dsoCurrUnrespLoad << endl;
				  	LDEBUG << "demand curve coefficients in decremental powers -> 0, 0, 0";
				}
				
				// the currently unresponsive load
				double dsoCurrUnrespLoad = accumulate(subscription_currUnrespLoad_values.begin(), subscription_currUnrespLoad_values.end(), 0.0);
				unresponsiveLoad_id.publish(dsoCurrUnrespLoad);
				LDEBUG << "currently unresponsive load [MW] -> " << dsoCurrUnrespLoad;
				dsoToISOOutputData << dsoCurrUnrespLoad << endl;

				// request new time from HELICS
				nextTimeAM = min(currentTime + 2 * dsoISORelativeTimeShift, simStopTime);
				nextHELICSTime = fed->requestTime ((helics::Time) nextTimeAM);
				LDEBUG << "Right before market: current time = " << currentTime << ", current before-market time = " << nextTimeBM << ", next after-market time = " << nextTimeAM << ", next HELICS time request = " << nextHELICSTime << ", iteration = " << iteration;
			  
			} else if (currentTime == nextTimeAM) {
				LDEBUG << "===== DSO performing tasks AFTER wholesale market (ISO simulator) ran, at iteration -> " << iteration << " =====";

				dsoAllocatedLoad = subscription_iso_allocConsumption_id.getValue<double>();
				isoLMP = subscription_iso_LMP_id.getValue<double>();
				
				LDEBUG << "ISO received LMP: " << isoLMP << " $/MW.";

				if (!lseQuants.empty() && quantityPriority == 1) {
					dsoLMP = determinePrice(dsoAllocatedLoad, isoLMP, lseQuants, lseMargPrices);
				} else {
				  	dsoLMP = isoLMP;
				}
				
				LMP_id.publish(dsoLMP);
				LDEBUG << "DSO locally calculated LMP: " << dsoLMP << " $/MW.";
				dsoToLSEOutputData << iteration << ", " << currentTime << ", " << dsoAllocatedLoad << ",  " << dsoLMP;
				LDEBUG << "There are " << dsoAllocatedLoad << " MW allocated for this DSO, at a local DSO LMP of " << dsoLMP << " $/MW";
				
				for (vector<string>::size_type i = 0; i < subscription_mdCurveCoeff_keys.size(); i++) {
					if (lseMPcoeff[2 * i] != 0) {
						lseAllocConsumption[i] = (dsoLMP - lseMPcoeff[2 * i + 1]) / lseMPcoeff[2 * i];
						lseAllocConsumption[i] = lseAllocConsumption[i] < lseMinMaxCumQuants[2 * i] ? lseMinMaxCumQuants[2 * i] : lseAllocConsumption[i];
						lseAllocConsumption[i] = lseAllocConsumption[i] > lseMinMaxCumQuants[2 * i + 1] ? lseMinMaxCumQuants[2 * i + 1] : lseAllocConsumption[i];
				  	} else {
						lseAllocConsumption[i] = 0;
				  	}
				  
				  	LDEBUG << "Calculated load for LSE " << i + 1 << " -> " << lseAllocConsumption[i] << " MW.";
				 	connected_lse_ids[i].publish(lseAllocConsumption[i]);
				 	LDEBUG << "Allocated load for LSE " << i + 1 << " -> " << lseAllocConsumption[i] << " MW, for a flexibility range between " << lseMinMaxCumQuants[2 * i] << " and " << lseMinMaxCumQuants[2 * i + 1] << " MW.";
				  	dsoToLSEOutputData << ", " << lseAllocConsumption[i];
				}

				dsoToLSEOutputData << endl;
				nextTimeBM = min(currentTime + wholesaleMarketPeriod - 2 * dsoISORelativeTimeShift, simStopTime);
				nextHELICSTime = fed->requestTime ((helics::Time) nextTimeBM);
				LDEBUG << "Right after market: current time = " << currentTime << ", current after-market time = " << nextTimeAM << ", next before-market time = " << nextTimeBM << ", next HELICS time request = " << nextHELICSTime << ", iteration = " << iteration;
				iteration += 1;
		
			} else {
				nextHELICSTime = currentTime < nextTimeBM ? fed->requestTime((helics::Time) nextTimeBM) : fed->requestTime((helics::Time) nextTimeAM);
				LDEBUG << "Non-action time for DSO: current time = " << currentTime << ", next HELICS time request = " << nextHELICSTime;   
			}
			
			currentTime = nextHELICSTime;
		}
		while(currentTime < simStopTime);

	}    
  	catch (const exception& e) {
		LERROR << "Caught a standard exception, see below for details";
		cerr << e.what() << endl;
		cerr << "Terminating program..." << endl;
        fed->error(-2, e.what());
        fed->finalize();
		helics::cleanupHelicsLibrary();
        return -2;
  	}
    catch (...) {
        LERROR << "Unknown and unexpected error thrown";
		cerr << "Terminating program..." << endl;
        fed->error(-3, "Unknown and unexpected error thrown");
        fed->finalize();
		helics::cleanupHelicsLibrary();
        return -3;
	}	
	
	time_t tStop = time(0);
	LINFO << "Simulation took " << (float) (tStop-tStart) << " seconds";
	LINFO << "Terminating HELICS federate";
	fed->finalize();
	helics::cleanupHelicsLibrary();
	return 0;
}
