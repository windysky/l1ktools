% DPEAK_DEMO Demo of peak detection.

lxbfile = '../data/A10.lxb';
outfolder = '../data/';
% sample_analytes = [15, 25, 100, 200, 300];
% 
% % plot peak intensity distributions for a few analytes
% fprintf ('Plotting distributions...\n');
% plot_peaks(lxbfile, sample_analytes);
% close all

% detect peaks and save stats to a file
fprintf('Detecting peaks...\n');
[pkstats, raw] = l1kt_dpeak(lxbfile, 'out', outfolder, 'showfig', true);
fprintf('Done\n')
