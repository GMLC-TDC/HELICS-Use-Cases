function makemetadatafile(tcase,dinjectionP,outfilename)
%MAKEMETADATAFILE Create metadatafile for the T-D power flow
%   makemetadatafile(tcase,dinjectionP,outfilename)
%
% Creates a file containing the metadata needed for running the T-D power
% flow.
%
% Inputs
%     TCASE: The transmission network data file. Note that this code only
%       works with transmission network files in MATPOWER data format.
%    DINJECTIONP: The real power injection of the feeder to be connected at
%       each load bus.
%    OUTFILENAME: The name of the metadatafile to which the metadata info
%       for the T-D power flow co-simulation is saved. The format of the
%       metadatafile is as follows:
%       Line 1                  => <number of boundary buses>,number of feeders
%       Lines 2 - nbdry_buses+1 => boundary buses (one on each line)
%       Lines nbdry_buses+2:end => <boundary bus, feeder topic name> (one
%          on each line
%       Each feeder topic name has the format dcase_tbdry_i_feeder_j, where
%       i is the boundary bus number and j is the feeder number. For instance,
%       dcase_tbdry_6_feeder_4 indicates the 4th feeder on boundary bus 6.
%
% NOTES: 
%     This code uses routines from the MATPOWER package so it should be
%     installed and the MATLAB paths set up accordingly.
%
%     Load buses that have non-zero active power loads are considered as
%     boundary buses for T and D. Any buses that have reactive power load
%     only are not considered as boundary buses.


%% define named indices into data matrices
[PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, ...
    VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN] = idx_bus;
[F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, ...
    TAP, SHIFT, BR_STATUS, PF, QF, PT, QT, MU_SF, MU_ST, ...
    ANGMIN, ANGMAX, MU_ANGMIN, MU_ANGMAX] = idx_brch;
[GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN, ...
    MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN, PC1, PC2, QC1MIN, QC1MAX, ...
    QC2MIN, QC2MAX, RAMP_AGC, RAMP_10, RAMP_30, RAMP_Q, APF] = idx_gen;


mpct = runpf(tcase);
d_inj = dinjectionP;

bdry_buses = find(mpct.bus(:,PD)~=0 & mpct.bus(:,PD) > d_inj);
nbdry_buses = length(bdry_buses);
nfeeders_bus = ceil(mpct.bus(bdry_buses,PD)./d_inj);
nfeeders = sum(nfeeders_bus);

%% Create metadata file for tranmsmission federate.
fp = fopen(outfilename,'w');

fprintf(fp,'%d,%d\n',nbdry_buses,nfeeders);
for i = 1:nbdry_buses
    fprintf(fp,'%d\n',bdry_buses(i));
end
for i = 1:nbdry_buses
    for k = 1:nfeeders_bus
        dtopic = ['dcase_tbdry_',num2str(bdry_buses(i)),'_feeder_',num2str(k)];
        fprintf(fp,'%d,%s\n',bdry_buses(i),dtopic);
    end
end
fclose(fp);
