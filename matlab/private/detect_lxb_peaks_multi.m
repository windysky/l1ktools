function pkstats = detect_lxb_peaks_multi(rp1, rid, varargin)
% DETECT_LXB_PEAKS_MULTI Detect peaks for multiple analytes in lxb data.
%   PKSTATS = DETECT_LXB_PEAKS_MULTI(RP1, RID) detect peaks for all
%   analytes specified by nonzero entries in the grouping variable RID. RP1
%   is a vector of fluorescent intensities. RID has the same dimension
%   as RP1. PKSTATS is a structure array with the detected peaks and
%   support information. The size of the array equals the number of
%   analytes specified by unique non-zero entries in RID. PKSTATS contains
%   the following fields:
%
%   'analyte_id': string, Analyte identifier corresponding to the RID.
%   'npeak': number of peaks detected
%   'pkexp': vector, Expression of each detected peak in linear scale.
%       Length equals npeak
%   'pksupport': vector, Number of beads supporting each peak.
%   'pksupport_pct': vector, Percentage bead support of each peak.
%   'pkheight': vector, Height of smoothed kernel density evaluated at
%       each peak.
%   'totbead': scalar, Total number of beads
%   'ngoodbead': scalar, Number of uncensored beads with intensities within
%       the specified thresholds. See lowthresh and highthresh parameters
%       in DETECT_LXB_PEAKS_SINGLE.
%   'medexp': scalar, Median expression of all uncensored beads. 
%   'method': string, The peak detection method.
%
%   PKSTATS = DETECT_LXB_PEAKS_MULTI(RP1, RID, 'Param1, 'Value1',...)
%   Specify optional parameter/value pairs:
%   'analyte': vector, List of analytes to process. If empty processes all
%       available analytes. Default all analytes.
%   'allanalytes' : vector indicating valid analyte indices. Default is
%       1:500 
%   'notduo' : string indicating analyte indices to ignore. Default
%       is '[1:10,11,499]'
%
%   Also see DETECT_LXB_PEAKS_SINGLE for description of peak calling
%   parameters.
%
% See: DETECT_LXB_PEAKS_SINGLE

pnames = {'analyte', 'allanalytes', 'notduo', ...
    'showfig', 'rpt', 'out',...
    'overwrite', 'newfig'};
dflts = { [], 1:500, '[1:10,11,499]',...
    false, 'analyte', '', ...
    'true', true};
arg = parse_args(pnames, dflts, varargin{:});
% nonduo analytes
arg.notduo = eval(arg.notduo);
if isempty(arg.analyte)
    analyte = unique(rid(rid>0));
else
    analyte = unique(arg.analyte);
end

nanalyte = length(analyte);
totanalyte = length(arg.allanalytes);
pkstats(1:totanalyte, 1) = struct('pkexp', 1,...
    'pksupport', 0, 'pksupport_pct', 0, 'pkheight', 0,...
    'totbead', 0, 'ngoodbead', 0,...
    'medexp', 1, ...
    'method','none');

% tag missing analytes
miss = setdiff(arg.allanalytes, analyte);
[pkstats(miss).method] = deal('missing');

for ii=1:nanalyte    
    % just report median for not duo analytes
    if ismember(analyte(ii), arg.notduo)
        pkstats(analyte(ii)) = detect_lxb_peaks_single(rp1(rid==analyte(ii)), varargin{:}, 'pkmethod', 'median');
    else
        pkstats(analyte(ii)) = detect_lxb_peaks_single(rp1(rid==analyte(ii)), varargin{:});
    end
    if arg.showfig
        namefig(sprintf('%s_%d', arg.rpt, analyte(ii)));
        if ~arg.newfig
            if ii == 1 && ~exist(fullfile(arg.out, 'figures'), 'dir')
                mkdir(fullfile(arg.out, 'figures'))
            end
            savefigures('out', fullfile(arg.out, 'figures'), 'mkdir', false, 'overwrite', arg.overwrite);
            hold off
        end
    end
end

newfields = struct('analyte_id', num2cellstr(arg.allanalytes(:)),...
    'npeak', num2cell(cellfun(@length, {pkstats.pkexp})'));
pkstats = mergestruct(newfields, pkstats);
