% Two Area Test Case
% with dc link added

% bus data format
% bus: 
% col1 number
% col2 voltage magnitude(pu)
% col3 voltage angle(degree)
% col4 p_gen(pu)
% col5 q_gen(pu),
% col6 p_load(pu)
% col7 q_load(pu)
% col8 G shunt(pu)
% col9 B shunt(pu)
% col10 bus_type
%       bus_type - 1, swing bus
%               - 2, generator bus (PV bus)
%               - 3, load bus (PQ bus)
% col11 q_gen_max(pu)
% col12 q_gen_min(pu)
% col13 v_rated (kV)
% col14 v_max  pu
% col15 v_min  pu

bus_ori=[
  % bus    V        Angle     P_gen     Q_gen     P_load    Q_load          G       B      type QgenMax   QgenMin      V_rate vmax vmin 

   1   1.048  -9.43   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
   2   1.0505 -6.89   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
   3   1.0341 -9.73   0.0000   0.0000   8.2200   0.0240 0.00000 0.00000 3 99  -99 1.0   0     0;
   4   1.0116 -10.53  0.0000   0.0000   11.0000   1.8400 0.00000 1.00000 3 99  -99 1.0   0     0;
   5   1.0165 -9.38   0.0000   0.0000   0.0000   0.0000 0.00000 2.00000 3 99  -99 1.0   0     0;
   6   1.0172 -8.68   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99 -99  1.0  1.17  0.98;
   7   1.0067 -10.84  0.0000   0.0000   2.3380   8.4000 0.00000 0.00000 3 99  -99 1.0   0     0;
   8   1.0057 -11.34  0.0000   0.0000   5.2200   1.7600 0.00000 0.00000 3 99  -99 1.0   0     0;
   9   1.0322 -11.15  0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
  10   1.0235 -6.31   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
  11   1.0201 -7.12   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
  12   1.0072 -7.14   0.0000   0.0000   0.0850   0.8800 0.00000 0.00000 3 99  -99 1.0   0     0;
  13   1.0207 -7.02   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
  14   1.0181 -8.66   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
  15   1.0194 -9.06   0.0000   0.0000   3.2000   1.5300 0.00000 0.00000 3 99  -99 1.0   0     0;
  16   1.0346 -7.66   0.0000   0.0000   3.2940   3.2300 0.00000 0.00000 3 99  -99 1.0   0     0;
  17   1.0365 -8.65   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
  18   1.0343 -9.49   0.0000   0.0000   1.5800   0.3000 0.00000 0.00000 3 99  -99 1.0   0     0;
  19   1.0509 -3.04   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
  20   0.9914 -4.45   0.0000   0.0000   6.8000   1.0300 0.00000 0.00000 3 99  -99 1.0   0     0;
  21   1.0337 -5.26   0.0000   0.0000   2.7400   1.1500 0.00000 0.00000 3 99  -99 1.0   0     0;
  22   1.0509 -0.82   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;
  23   1.0459 -1.02   0.0000   0.0000   2.4750   0.8460 0.00000 0.00000 3 99  -99 1.0   0     0;
  24   1.0399 -7.54   0.0000   0.0000   3.0860   -0.922 0.00000 0.00000 3 99  -99 1.0   0     0;
  25   1.0587 -5.51   0.0000   0.0000   2.2400   0.4720 0.00000 0.00000 3 99  -99 1.0   0     0;
  26   1.0536 -6.77   0.0000   0.0000   1.3900   0.1700 0.00000 0.00000 3 99  -99 1.0   0     0;
  27   1.0399 -8.78   0.0000   0.0000   2.8100   0.7550 0.00000 0.00000 3 99  -99 1.0   0     0;
  28   1.0509 -3.27   0.0000   0.0000   2.0600   0.2760 0.00000 0.00000 3 99  -99 1.0   0     0;
  29   1.0505 -0.51   0.0000   1.0000   2.8350   1.2690 0.00000 0.00000 3 99  -99 1.0   0     0;
  30   1.0475 -4.47   2.5000   1.3621   0.0000   0.0000 0.00000 0.00000 2  18   -15 1.0   0     0;
  31   1.0400  0.00   5.7293   1.7036   0.0920   0.0460 0.00000 0.00000 2  18   -15 1.0   0     0;
  32   0.9831  1.63   6.5000   1.7590   0.0000   0.0000 0.00000 0.00000 2  18   -15 1.0   0     0;
  33   0.9972  2.18   11.3200  3.0335   0.0000   0.0000 0.00000 0.00000 2  18   -15 1.0   0     0;
  34   1.0123  0.74   12.0800  4.6400   0.0000   0.0000 0.00000 0.00000 2  14   -13 1.0   0     0;
  35   1.0493  4.14   6.5000   2.0884   0.0000   0.0000 0.00000 0.00000 2  18   -15 1.0   0     0;
  36   1.0635  6.83   7.6000   0.9688   0.0000   0.0000 0.00000 0.00000 2  18   -15 1.0   0     0;
  37   1.0278  1.26   5.4000  -0.0444   0.0000   0.0000 0.00000 0.00000 2  18   -15 1.0   0     0;
  38   1.0265  6.55   8.3000   0.1939   0.0000   0.0000 0.00000 0.00000 2  18   -15 1.0   0     0;
  39   1.0300 -10.96  10.000   0.6846   11.040   2.5000 0.00000 0.00000 1  15 -10 1.0   0     0];

bus=zeros(41,15);
bus(1:39,:)=bus_ori;

% 16   1.0346 -7.66   0.0000   0.0000   3.2940   3.2300 0.00000 0.00000 3 99  -99 1.0   0     0;%49    1.0273  -61.7461         0         0    -PDC(1)   0.0000         0   0.5206250    3    0.0        0.0         500    1.5  0.5; %HV bus for Gen 21 and load bus 50, sWest
% 19   1.0509 -3.04   0.0000   0.0000   0.0000   0.0000 0.00000 0.00000 3 99  -99 1.0   0     0;


bus(1:29,13) =500; 
bus(30:39,13) =22;
bus(1:39,14) =1.2; 
bus(1:39,15) =0.5; 
bus(40,:)=[219  1.0     -5.8989    0.00   0.00  3.09    0.6   0.00  0.00 3  99.0   -99.0 220.0   1.2     0.5];
bus(41,:)=[216  1.0     -6.7461     0.00   0.00  -3.0   0.59  0.00   0.00 3  99.0  -99.0  220.0   1.2     0.5];

% line data format
% line: from bus, to bus, resistance(pu), reactance(pu),
%       line charging(pu), tap ratio, tap phase, tapmax, tapmin, tapsize

line_ori = [
   1   2 0.00350  0.04110 0.69870 0.0000 0   0    0    0;
   1  39 0.00100  0.02500 0.75000 0.0000 0   0    0    0;
   2   3 0.00130  0.01510 0.25720 0.0000 0   0    0    0;
   2  25 0.00700  0.00860 0.14600 0.0000 0   0    0    0;
   2  30 0.00000  0.01810 0.00000 1.0250 0   0    0    0;
   3   4 0.00130  0.02130 0.22140 0.0000 0   0    0    0;
   3  18 0.00110  0.01330 0.21380 0.0000 0   0    0    0;
   4   5 0.00080  0.01280 0.13420 0.0000 0   0    0    0;
   4  14 0.00080  0.01290 0.13820 0.0000 0   0    0    0;
   5   8 0.00080  0.01120 0.14760 0.0000 0   0    0    0;
   6   5 0.00020  0.00260 0.04340 0.0000 0   0    0    0;
   6   7 0.00060  0.00920 0.11300 0.0000 0   0    0    0;
   6  11 0.00070  0.00820 0.13890 0.0000 0   0    0    0;
   7   8 0.00040  0.00460 0.07800 0.0000 0   0    0    0;
   8   9 0.00230  0.03630 0.38040 0.0000 0   0    0    0;
   9  39 0.00100  0.02500 1.20000 0.0000 0   0    0    0;
  10  11 0.00040  0.00430 0.07290 0.0000 0   0    0    0;
  10  13 0.00040  0.00430 0.07290 0.0000 0   0    0    0;
  10  32 0.00000  0.02000 0.00000 1.0700 0   0    0    0;
  12  11 0.00160  0.04350 0.00000 1.0060 0   0    0    0;
  12  13 0.00160  0.04350 0.00000 1.0060 0   0    0    0;
  13  14 0.00090  0.01010 0.17230 0.0000 0   0    0    0;
  14  15 0.00180  0.02170 0.36600 0.0000 0   0    0    0;
  15  16 0.00090  0.00940 0.17100 0.0000 0   0    0    0;
  16  17 0.00070  0.00890 0.13420 0.0000 0   0    0    0;
  16  19 0.00160  0.01950 0.30400 0.0000 0   0    0    0;
  16  21 0.00080  0.01350 0.25480 0.0000 0   0    0    0;
  16  24 0.00030  0.00590 0.06800 0.0000 0   0    0    0;
  17  18 0.00070  0.00820 0.13190 0.0000 0   0    0    0;
  17  27 0.00130  0.01730 0.32160 0.0000 0   0    0    0;
  19  33 0.00070  0.01420 0.00000 1.0700 0   0    0    0;
  19  20 0.00070  0.01380 0.00000 1.0600 0   0    0    0;
  20  34 0.00090  0.01800 0.00000 1.0090 0   0    0    0;
  21  22 0.00080  0.01400 0.25650 0.0000 0   0    0    0;
  22  23 0.00060  0.00960 0.18460 0.0000 0   0    0    0;
  22  35 0.00000  0.01430 0.00000 1.0250 0   0    0    0;
  23  24 0.00220  0.03500 0.36100 0.0000 0   0    0    0;
  23  36 0.00050  0.02720 0.00000 1.0000 0   0    0    0;
  25  26 0.00320  0.03230 0.51300 0.0000 0   0    0    0;
  25  37 0.00060  0.02320 0.00000 1.0250 0   0    0    0;
  26  27 0.00140  0.01470 0.23960 0.0000 0   0    0    0;
  26  28 0.00430  0.04740 0.78020 0.0000 0   0    0    0;
  26  29 0.00570  0.06250 1.02900 0.0000 0   0    0    0;
  28  29 0.00140  0.01510 0.24900 0.0000 0   0    0    0;
  29  38 0.00080  0.01560 0.00000 1.0250 0   0    0    0;
  31   6 0.00000  0.02500 0.00000 1.0000 0  0  0.8  0.05;];

line = zeros(48,10);
line(1:46,1:5)=line_ori(:,1:5);
line(1:46,5)=0.0;
line(1:46,6)=1.0;
line(47,:)=[19    219  0.0     0.01    0.00    1.0   0. 5.0 0.5 0.005];
line(48,:)=[16    216  0.0     0.01    0.00    1.0   0. 5.0 0.5 0.005];




% col 1  hvdc converter number
% col 2  LT bus number in load flow data
% col 3  converter type
%        1 - rectifier
%        2 - inverter
% col 4  dc rated voltage (kV)
% col 5  commutating reactance ohms/bridge
% col 6  number of bridges in series
% col 7  rectifier - alfa min
%        inverter  - gamma min
% col 8  rectifier - alpha max
%        inverter  - gamma max
      
dcsp_con = [...
1  219  1  500  5    2   5   30;
2  216  2  500  5    2  12   25];

% col 1   rectifier number
% col 2   inverter number
% col 3   dc line resistance ohms
% col 4   dc line inductance ( milli H)
% col 5   dc line capacitance (micro F)
% col 6   rectifier smoothing inductance (milli H)
% col 7   inverter smoothing inductance (milli H)
% col 8   dc line rating (MW)
% col 9   current margin for inverter current control %


dcl_con = [...
1  2  10  5.0  0  1000.0  1000.0  1000  10];

% col 1 converter number
% col 2 proportional gain
% col 3 integral gain
% col 4 output gain
% col 5 max integral limit
% col 6 min integral limit
% col 7 max output limit
% col 8 min output limit
% col 9  control type 
%       - 1 rectifier current control
%       - 2 rectifier power control
%       - 0 for inverter controls
% note: the order of the converters must be the same as that in dcsp_con
dcc_con = [...
1  1.0  1.0  0.1  15 0  90  5   1;
2  1.0  1.0  0.1  15  0 90  10  0];


% Machine data format
% Machine data format
%       1. machine number,
%       2. bus number,
%       3. base mva,
%       4. leakage reactance x_l(pu),
%       5. resistance r_a(pu),
%       6. d-axis sychronous reactance x_d(pu),
%       7. d-axis transient reactance x'_d(pu),
%       8. d-axis subtransient reactance x"_d(pu),
%       9. d-axis open-circuit time constant T'_do(sec),
%      10. d-axis open-circuit subtransient time constant
%                T"_do(sec),
%      11. q-axis sychronous reactance x_q(pu),
%      12. q-axis transient reactance x'_q(pu),
%      13. q-axis subtransient reactance x"_q(pu),
%      14. q-axis open-circuit time constant T'_qo(sec),
%      15. q-axis open circuit subtransient time constant
%                T"_qo(sec),
%      16. inertia constant H(sec),
%      17. damping coefficient d_o(pu),
%      18. dampling coefficient d_1(pu),
%      19. bus number
%
% note: all the following machines use sub-transient model
a_temp = 2.0;
a_Iner = 3.0;
mac_con = [
  1  30  1000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1;
  2  31  1000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1;
  3  32  1000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1;
  4  33  2000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1;
  5  34  2000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1;
  6  35  1000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1;
  7  36  1000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1;
  8  37  1000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1;
  9  38  1000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1;
  10 39  1000 0.200  0.00    1.8  0.30  0.25 a_temp  0.03 1.7  0.55  0.24 0.4   0.05 a_Iner  0  0  1];

exc_con =[
% 0 1 0.01 200.0  0     0     0    5.0  -5.0    0    0      0     0     0    0    0      0      0    0   0;  
% 0 2 0.01 200.0  0     0     0    5.0  -5.0    0    0      0     0     0    0    0      0      0    0   0;  
% 0 3 0.01 200.0  0     0     0    5.0  -5.0    0    0      0     0     0    0    0      0      0    0   0;  
% 0 4 0.01 200.0  0     0     0    5.0  -5.0    0    0      0     0     0    0    0      0      0    0   0;  
% % 0 5 0.01 200.0  0     0     0    5.0  -5.0    0    0      0     0     0    0    0      0      0    0   0;  
% % 0 6 0.01 200.0  0     0     0    5.0  -5.0    0    0      0     0     0    0    0      0      0    0   0;  
% 0 7 0.01 200.0  0     0     0    5.0  -5.0    0    0      0     0     0    0    0      0      0    0   0;  
% 0 8 0.01 200.0  0     0     0    5.0  -5.0    0    0      0     0     0    0    0      0      0    0   0;  
0 10 0.01 200.0  0     0     0    5.0  -5.0    0    0      0     0     0    0    0      0      0    0   0];



pss_con = [...
 1 10 100.0  20.0  0.06  0.04  0.08  0.04  0.1  -0.1];
% 1 4 100.0  20.0  0.06  0.04  0.08  0.04  0.1  -0.1];
% 1 5 100.0  20.0  0.06  0.04  0.08  0.04  0.1  -0.1];
% pss_con matrix format
%column        data         unit
%  1      Type input (1=spd, 2=power)
%  2      machine number
%  3      gain K
%  4      Washout time const Tw (sec)
%  5      1st lead time const T1 (sec)
%  6      1st lag time const T2 (sec)
%  7      2nd lead time const T3 (sec)
%  8      2nd lag time const T4 (sec)
%  9      max output limit (pu)
%  10     min output limit (pu)
%  1 4 300.0  20.0  0.06  0.04  0.08  0.04  0.2  -0.05];


% governor model
% tg_con matrix format
%column         data       unit
%  1  turbine model number (=1)  
%  2  machine number 
%  3  speed set point   wf    pu
%  4  steady state gain 1/R      pu
%  5  maximum power order  Tmax  pu on generator base
%  6  servo time constant   Ts   sec
%  7  governor time constant  Tc sec
%  8  transient gain time constant T3  sec
%  9  HP section time constant   T4 sec
% 10  reheater time constant    T5  sec

tg_con = [...
1  1  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0;
1  2  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0;
1  3  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0;
1  4  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0;
1  5  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0;
1  6  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0;
1  7  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0;
1  8  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0;
1  9  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0;
1  10  1  25.0  1.0  0.1  0.15 0.0 1.25 5.0];
% 
% 
%Switching file defines the simulation control
% row 1 col1  simulation start time (s) (cols 2 to 6 zeros)
%       col7  initial time step (s)
% row 2 col1  fault application time (s)
%       col2  bus number at which fault is applied
%       col3  bus number defining far end of faulted line
%       col4  zero sequence impedance in pu on system base
%       col5  negative sequence impedance in pu on system base
%       col6  type of fault  - 0 three phase
%                            - 1 line to ground
%                            - 2 line-to-line to ground
%                            - 3 line-to-line
%                            - 4 loss of line with no fault
%                            - 5 loss of load at bus
%       col7  time step for fault period (s)
% row 3 col1  near end fault clearing time (s) (cols 2 to 6 zeros)
%       col7  time step for second part of fault (s)
% row 4 col1  far end fault clearing time (s) (cols 2 to 6 zeros)
%       col7  time step for fault cleared simulation (s)
% row 5 col1  time to change step length (s)
%       col7  time step (s)
%
%
%
% row n col1 finishing time (s)  (n indicates that intermediate rows may be inserted)
ts = 1;
tf = 10;
stamp=1/128;

sw_con = [...
0           0    0      0     0      0        stamp;%sets intitial time step
ts          36    23    0     0      7        stamp; %3 ph fault bus 3 line 3-101 
ts + 0.021   0    0      0     0      0        stamp; %clear fault at bus 3
ts + 0.04   0    0      0     0      0        stamp;%clear remote end
ts + 0.5    0    0      0     0      0        stamp;
tf          0    0      0     0      0        0]; % end simulation


% sw_con = [...
% 0     0    0      0     0      0        0.001;%sets intitial time step
% 0.01  3    101    .4     .4    4        0.0001; %3 ph fault bus 3 line 3-101 
% 0.02  0    0      0     0      0        0.0001; %clear fault at bus 3
% 0.03  0    0      0     0      0        0.0005;%clear remote end
% 2.0   0    0      0     0      0        0.001;
% 5.0   0    0      0     0      0        0]; % end simulation

% non-conforming load declaration of dc LT buses
% col 1           bus number
% col 2           fraction const active power load
% col 3           fraction const reactive power load
% col 4           fraction const active current load
% col 5           fraction const reactive current load
load_con = [...
            % 4  0  0  .5 0;
             219  0  0  0  0;
             216  0  0  0  0];
         
% sw_con = [...
% 0     0    0      0     0      0        0.005;%sets intitial time step
% 0.30  36    23    0     0     0        0.0005; %3 ph fault bus 3 line 3-101 
% 0.31  0    0      0     0      0        0.0005; %clear fault at bus 3
% 0.32  0    0      0     0      0        0.0005;%clear remote end
% 0.5   0    0      0     0      0        0.005;
% 15.0   0    0      0     0      0        0]; % end simulation
