function s = l1kt_parse_lxb(fname, varargin)
% L1KT_PARSE_LXB Parse an LXB (L1000 raw binary) file.
%   RAW = PARSE_LXB(LXBFILE) Returns a sructure with bead-level intensity
%   data from LXBFILE. RAW is a structure with the following fields.
%   'RID': vector, analyte ids. Ids ranging from [1-500] are to 500 valid
%   bead regions. Ids labeled 0 are unclassified beads and can be ignored.
%   'RP1': vector, reporter fluorescent intensities of each detected bead.
%
if isfileexist(fname)
    tmp = which(mfilename);
    p = fileparts(tmp);
    lxbutil_cp = fullfile(p, 'private/lxb-util.jar');
    dp = javaclasspath;
    if isempty(strcmp(lxbutil_cp, dp))
        fprintf('Adding lxb-util.jar to classpath\n');
        javaaddpath(lxbutil_cp)
    end
    
    data = org.broadinstitute.cancer.io.luminex.LXBUtil.loadLXB(fname, 'RP1');
    s.RID = double(data.analytes);
    s.RP1 = double(data.values);
else
    error('%s: file not found', fname);
end