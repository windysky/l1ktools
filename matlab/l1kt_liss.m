function normds = l1kt_liss(raw, out, varargin)
% L1KT_LISS Perform L1000 Invariant Set Scaling on unnormalized .gct data
% set
%   NORMDS = L1KT_LISS(RAW,OUT) takes as input either a raw (unnormalized)
%   .gct data structure, or the path to a .gct file. It returns a
%   normalized data structure NORMDS to the MATLAB workspace, and saves the
%   data set in the directory specified by OUT. It also outputs a
%   "calibration plot" to the directory OUT.
%   
%   NORMDS = L1KT_LISS(RAW,OUT,'PARAM1',VAL1,'PARAM2',VAL2,...) specifies
%   additional parameters and their values. Valid parameters are the
%   following:
%       Parameter   Value
%        'ref'       File path to reference expression values. Default is
%                    '../data/log_ybio_epsilon.gct'
%        'gmx_cal'   File path to a .gmx file listing the calibration
%                    levels. Default is '../data/epsilon_cal.gmx'

% Get optional arguments
pnames = {'ref', 'gmx_cal'};
dflts = {'../data/log_ybio_epsilon.gct', '../data/epsilon_cal.gmx'};
args = parse_args(pnames,dflts,varargin{:});

% normalize the data sets
raw = parse_gct(raw, 'class', 'double');
raw.mat = safe_log2(raw.mat);
calibds = gen_calib_matrix(args.gmx_cal, raw);
ref = parse_gct(args.ref, 'class', 'double');
normds = liss(raw, calibds, ref.mat);

% drop the control beads from the data set
calnames = cellfun(@(x) ['CAL' sprintf('%0.2d', x)], num2cell(1:10)', ...
    'UniformOutput', false);
if ~isequal(normds.rid(1:10), calnames)
    error('The first 10 analytes in the data set should be the calibration beads')
end
normds = gctextract_tool(normds, 'rid', normds.rid(11:end));
mkgct(fullfile(out, 'NORM'), normds)

% generate calibration plots of the unnormalized data
if calibds.cdict.isKey('pert_type')
    plot_calib(calibds.mat, 'showfig', true, ...
        'group', calibds.cdesc(:,calibds.cdict('pert_type')),...
        'sl', calibds.cid, ...
        'showsamples',true, ...
        'islog2', true);
else
    plot_calib(calibds.mat, 'showfig', true, 'sl', ...
        calibds.cid, 'showsamples', true, ...
        'islog2', true);
end
print('-dpng', fullfile(out, 'calib_plot'))