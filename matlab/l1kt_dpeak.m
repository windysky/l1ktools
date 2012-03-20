function [pkstats, raw] = l1kt_dpeak(lxbfile, varargin)
% L1KT_DPEAK Perform peak detection on bead-level L1000 data files.
%   PKSTATS = DPEAK(LXBFILE) Process data from LXBFILE and returns
%   peak-detection statistics. PKSTATS is a structure array of length equal
%   to the number of analytes. See DETECT_LXB_PEAKS_MULTI for a
%   description of the fields in PKSTATS.
%
%   [PKSTATS, RAW] = DPEAK(LXBFILE) returns the bead-level intensity data.
%       RAW is a structure with the following fields.
%   'RID': vector, analyte ids. Ids ranging from [1-500] are to 500 valid
%   bead regions. Ids labeled 0 are unclassified beads and are ignored by
%   dpeak.
%   'RP1': vector, reporter fluorescent intensities of each detected bead.
%
%   [...] = DPEAK(LXBFILE, param1, val1,...) specify optional
%   parameter/value pairs:
%   'out' : string, Output folder. If not empty, will save a tab-delimited
%       textfile of detected peaks and optionally plots of the intensity
%       distributions if 'showfig' is true.
%   'outfile' : string, Output filename. Default is pkstats.txt
%   'showfig' : boolean, Show intensity distributions. Default is false.
%
%   See also: L1KT_PLOT_PEAKS, SAVE_PKSTATS, DETECT_LXB_PEAKS_MULTI

pnames = {'out', 'showfig', 'outfile'};
dflts = {'', false, 'pkstats.txt'};
args = parse_args(pnames, dflts, varargin{:});

% read raw data
raw = l1kt_parse_lxb(lxbfile);

% detect peaks
pkstats = detect_lxb_peaks_multi(raw.RP1, raw.RID, ...
    'showfig', args.showfig, 'newfig', false, varargin{:});

% save pkstats
if ~isempty(args.out)
    save_pkstats(fullfile(args.out, args.outfile), pkstats)
end

end