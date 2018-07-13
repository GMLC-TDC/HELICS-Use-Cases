function f = mdc_sig(t,k)
% Syntax: f = mdc_sig(t,k)
% 4:40 PM 21/08/97
% defines modulation signal for dc converter control
global dc_sig  r_idx i_idx n_conv mac_spd

global bus_v bus_ang bus_int bus_freq bus_freqf  freq_pst  freq_received
global hvdc_dc_con fdout_hvdc_dc thdiff 

f=0; %dummy variable
if n_conv~=0

global varpru_HVDC

Gam_t = 0.15;

if ~isempty(varpru_HVDC)

    switch varpru_HVDC
        case 0
        if t<=5.0
            dc_sig(:,k) = zeros(n_conv,1);
        else
            dc_sig(:,k) = -Gam_t; dc_sig(:,k+1) = -Gam_t;
        end
        case 1
            if t<=5.0
                dc_sig(r_idx,k) = zeros(n_conv/2,1);
            else
                dc_sig(r_idx,k) = -Gam_t; dc_sig(r_idx,k+1) = -Gam_t;
            end
        case 2
            tsig = Gam_t*sin(2*pi*t);
            if t<=5.0
                dc_sig(:,k) = zeros(n_conv,1);
            else
                dc_sig(:,k) = ones(n_conv,1)*tsig; 
                dc_sig(:,k+1) = ones(n_conv,1)*tsig; 
            end
        case 3
            tsig = Gam_t*sin(2*pi*t);
            if t<=5.0
                dc_sig(r_idx,k) = zeros(n_conv/2,1);
            else
                dc_sig(r_idx,k) = ones(n_conv/2,1)*tsig; 
                dc_sig(r_idx,k+1) = ones(n_conv/2,1)*tsig; 
            end
            
        case 4
            tsig = 2*Gam_t*sin(2*pi*t);
            if t<=5.0
                dc_sig(:,k) = zeros(n_conv,1);
            else
                dc_sig(:,k) = ones(n_conv,1)*tsig; 
                dc_sig(:,k+1) = ones(n_conv,1)*tsig; 
            end
        case 5
            tsig = 2*Gam_t*sin(2*pi*t);
            if t<=5.0
                dc_sig(r_idx,k) = zeros(n_conv/2,1);
            else
                dc_sig(r_idx,k) = ones(n_conv/2,1)*tsig; 
                dc_sig(r_idx,k+1) = ones(n_conv/2,1)*tsig; 
            end
        otherwise
    end

end

    % Control implementation
    
    kp_dc1=250 ; %1000 / 60;

    hvdc_dc_con = [19  16   kp_dc1];
    
    if ~isempty(hvdc_dc_con)

        ix_HVDC_DC = hvdc_dc_con(:,1:2);
        Kp_HVDC_DC = hvdc_dc_con(:,3);

        ix_lc = bus_int(ix_HVDC_DC(:,1));
        ix_rm = bus_int(ix_HVDC_DC(:,2));
    
        % control enables after 80 steps
          if k<81 & bus_freq(ix_lc,k)~=0
            freq_pst = 60;
          end
        
        
        if k>80 & bus_freq(ix_lc,k)~=0
         
         freq_rectify = (bus_freq(ix_lc,k)-1)+60;    

       
            dc_sig(r_idx,k) =  -Kp_HVDC_DC.*( freq_rectify - freq_received);
       
            freq_pst = (bus_freq(ix_rm,k)-1)+60;
                   
        else
            dc_sig(r_idx,k) =0;
        end
        
        lim = pi;
        dc_sig(dc_sig(:,k) > lim,k) = lim; 
        dc_sig(dc_sig(:,k) < -lim,k) = -lim;
      
        
        % *********** Derivative filter in Z domain ********** %
        % CHECK sampling is constant
        
         dt =  diff(t);
        
        
%         tst_60 = any((dt - 1/60)<1e-6);
%         if any(tst_60)
%             error('H(z) filter needs a sampling rate of 60hz')
%         end
        
        b_lpf = [0.29192028  0  -0.29192028];
        a_lpf = [1 -1.5555722597  0.61839942];
        
        ixLV = abs(bus_v(ix_lc,k))>0.5 & abs(bus_v(ix_rm,k))>0.5;
        thdiff(:,k) = angle(bus_v(ix_lc,k)./bus_v(ix_rm,k));
        
        if k>2 % from 3 on
            fdout_hvdc_dc(:,k) = b_lpf(1).*thdiff(:,k) + b_lpf(2).*thdiff(:,k-1) + b_lpf(3).*thdiff(:,k-2) - ...
                a_lpf(2).*fdout_hvdc_dc(:,k-1) - a_lpf(3).*fdout_hvdc_dc(:,k-2);
            
            thdiff(~ixLV,k) = thdiff(~ixLV,k-1);
            fdout_hvdc_dc(~ixLV,k) = fdout_hvdc_dc(~ixLV,k-1);
        elseif k==2
            fdout_hvdc_dc(:,k) = b_lpf(1).*thdiff(:,k) + b_lpf(2).*thdiff(:,k-1) - ...
                a_lpf(2).*fdout_hvdc_dc(:,k-1);
            
            thdiff(~ixLV,k) = thdiff(~ixLV,k-1);
            fdout_hvdc_dc(~ixLV,k) = fdout_hvdc_dc(~ixLV,k-1);
        elseif k==1
            fdout_hvdc_dc(:,k) = b_lpf(1).*thdiff(:,k);
        end
        
        
        
    end
    
end
return