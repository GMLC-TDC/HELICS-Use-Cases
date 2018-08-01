/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/csma-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/ipv4-global-routing-helper.h"

#include "ns3/helics-helper.h"



using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("HelicsExample");

/*
 * The main() loop below represents the ns-3 model. The helics ns-3
 * integration will filter messages sent by MessageFederate instances by
 * creating HelicsApplication instances at Nodes. The name given to the
 * HelicsApplication should match a registered endpoint.
 */

int 
main (int argc, char *argv[])
{
	// from original FNCS
	double onMin = 0.001;
    	double onMax = 0.010;
    	double offMin = 1;
    	double offMax = 1;
    	double errorRate = 0.05;
        int ipacketSize = 512;
	std::string dataRate = "5Mbps";
	std::string delay_p2p = "150ms";
	std::string dataRate_p2p = "5Mbps";

  bool verbose = true;
  //uint32_t nCsma = 3;
  std::string endpoint1 = "endpoint1";
  std::string endpoint2 = "endpoint2";
  std::string finalDest = "PST/recv_freq";

  HelicsHelper helicsHelper;

  CommandLine cmd;
  	// from original FNCS
    	cmd.AddValue ("onMin", "Min value for RNG defining congesting traffic on-time.", onMin);
    	cmd.AddValue ("onMax", "Max value for RNG defining congesting traffic on-time.", onMax);
    	cmd.AddValue ("offMin", "Min value for RNG defining congesting traffic off-time.", offMin);
    	cmd.AddValue ("offMax", "Max value for RNG defining congesting traffic off-time.", offMax);
    	//cmd.AddValue ("errorRate", "Rate at which packets are corrupted.", errorRate);
    	//cmd.AddValue ("dataRate", "ns3::OnOffApplication::DataRate");
    	//cmd.AddValue ("packetSize", "ns3::OnOffApplication::PacketSize");
	//cmd.AddValue("delay_p2p", "ns3::PointToPointChannel::Delay");
	//cmd.AddValue("dataRate_p2p", "ns3::PointToPointChannel::DataRate");

  //cmd.AddValue ("nCsma", "Number of \"extra\" CSMA nodes/devices", nCsma);
  //cmd.AddValue ("verbose", "Tell echo applications to log if true", verbose);
  helicsHelper.SetupCommandLine(cmd);
  //cmd.AddValue ("endpoint1", "First helics endpoint", endpoint1);
  //cmd.AddValue ("endpoint2", "Second helics endpoint", endpoint2);
  //cmd.AddValue ("finalDest", "Last helics endpoint", finalDest);
  cmd.Parse (argc,argv);

  if (verbose)
    {
      LogComponentEnable ("HelicsExample", LOG_LEVEL_INFO);
      LogComponentEnable ("HelicsSimulatorImpl", LOG_LEVEL_LOGIC);
      LogComponentEnable ("HelicsStaticSinkApplication", LOG_LEVEL_LOGIC);
      LogComponentEnable ("HelicsStaticSourceApplication", LOG_LEVEL_LOGIC);
      LogComponentEnable ("HelicsApplication", LOG_LEVEL_LOGIC);
    }

  	// from original FNCS: 
	// Setting up the channel receive error rate
    	std::string errorModelType = "ns3::RateErrorModel";
    	Config::SetDefault ("ns3::RateErrorModel::ErrorRate", DoubleValue (errorRate));
    	Config::SetDefault ("ns3::RateErrorModel::ErrorUnit", StringValue ("ERROR_UNIT_PACKET"));

  NS_LOG_INFO ("Calling helicsHelper.SetupApplicationFederate");
  helicsHelper.SetupApplicationFederate();

  //nCsma = nCsma == 0 ? 1 : nCsma;

  NodeContainer p2pNodes;
  p2pNodes.Create (2);

  //NodeContainer csmaNodes;
  //csmaNodes.Add (p2pNodes.Get (1));
  //csmaNodes.Create (nCsma);

  PointToPointHelper pointToPoint;
    pointToPoint.SetDeviceAttribute ("DataRate", StringValue (dataRate_p2p)); // from original FNCS: 
    pointToPoint.SetChannelAttribute ("Delay", StringValue (delay_p2p));

  NetDeviceContainer p2pDevices;
  p2pDevices = pointToPoint.Install (p2pNodes);

  //CsmaHelper csma;
  //csma.SetChannelAttribute ("DataRate", StringValue ("100Mbps"));
  //csma.SetChannelAttribute ("Delay", TimeValue (NanoSeconds (6560)));

  //NetDeviceContainer csmaDevices;
  //csmaDevices = csma.Install (csmaNodes);

  InternetStackHelper stack;
  stack.Install (p2pNodes);
  //stack.Install (csmaNodes);

  Ipv4AddressHelper address;
  address.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer p2pInterfaces;
  p2pInterfaces = address.Assign (p2pDevices);

  //address.SetBase ("10.1.2.0", "255.255.255.0");
  //Ipv4InterfaceContainer csmaInterfaces;
  //csmaInterfaces = address.Assign (csmaDevices);

    // from original FNCS:
    NS_LOG_INFO("Installing congesting traffic applications...");
    uint16_t port = 9;
    Address sinkAddress (InetSocketAddress (p2pInterfaces.GetAddress(0), port));
    PacketSinkHelper packetSinkHelper ("ns3::UdpSocketFactory", sinkAddress);
    ApplicationContainer receiveApp = packetSinkHelper.Install (p2pNodes.Get(0));
    receiveApp.Start (Seconds (0.2));
    receiveApp.Stop (Seconds (10.5));

    std::ostringstream onTime, offTime;
    OnOffHelper onOffHelper ("ns3::UdpSocketFactory", sinkAddress);
    onTime << "ns3::UniformRandomVariable[Min=" << onMin << "|Max=" << onMax << "]";
    offTime << "ns3::UniformRandomVariable[Min=" << offMin << "|Max=" << offMax << "]";  
    onOffHelper.SetAttribute ("OnTime", StringValue (onTime.str()));
    onOffHelper.SetAttribute ("OffTime", StringValue (offTime.str()));
    onOffHelper.SetAttribute ("DataRate", StringValue (dataRate));
    onOffHelper.SetAttribute ("PacketSize", UintegerValue(ipacketSize));
    ApplicationContainer sendApp = onOffHelper.Install (p2pNodes.Get(1));
    sendApp.Start (Seconds (0.2));
  


  //ApplicationContainer apps1 = helicsHelper.InstallStaticSink (
  //        csmaNodes.Get (nCsma), endpoint1, endpoint2);
  //apps1.Start (Seconds (0.0));
  //apps1.Stop (Seconds (10.0));

  ApplicationContainer apps1 = helicsHelper.InstallStaticSink (
          p2pNodes.Get (0), endpoint1, endpoint2);
  apps1.Start (Seconds (0.0));
  apps1.Stop (Seconds (10.5));

  ApplicationContainer apps2 = helicsHelper.InstallStaticSource (
          p2pNodes.Get (1), endpoint2, finalDest);
  apps2.Start (Seconds (0.0));
  apps2.Stop (Seconds (10.5));

  // Ipv4GlobalRoutingHelper::PopulateRoutingTables ();

  pointToPoint.EnablePcapAll ("second");
  //csma.EnablePcap ("second", csmaDevices.Get (1), true);

  Simulator::Stop (Seconds (10.5));

  NS_LOG_INFO("Running Simulation...");
  Simulator::Run ();

  Simulator::Destroy ();
  NS_LOG_INFO("Simulation complete.");
  return 0;
}

