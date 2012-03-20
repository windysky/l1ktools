function mktbl(outfile, tbl, varargin)
% MKSIN Create a sample information file
% MKSIN(SIN,outfile) Creates a sin file given a structure (SIN) with 
% fieldnames set to header labels in row one of outfile.

% $Author: Rajiv Narayan [narayan@broadinstitute.org]
% $Date: Jul.01.2010 12:01:46 EDT

pnames = {'precision', 'emptyval'};
dflts = {4, ''};
arg = parse_args(pnames, dflts, varargin{:});

nr = length(tbl);
fn = fieldnames(tbl);
nf = length(fn);
numfmt = sprintf('%%.%df', arg.precision);

if isequal (nr,1)
    %legacy mode, single structure where each fieldname is a cell array of
    % size nrec
    nrec = length(tbl.(fn{1}));
    x=struct2cell(tbl);
    % convert to columns
    x = cellfun(@(x)(x(:)), x, 'uniformoutput',false);
    isnum = cellfun(@(x) isnumeric(x)||islogical(x), x);
    if any(isnum)
        idx = find(isnum);
        n = nnz(isnum);
        for ii=1:n
           x{idx(ii)} =  num2cellstr(x{idx(ii)}, 'fmt', numfmt);
        end
    end    
    data = [x{:}];
else
    % preferred form, structure array of size nrec
    nrec = nr;
    data = struct2cell(tbl(:))';
end

fprintf ('Saving file to %s [%dr x %dc]\n', outfile, nrec, nf);
fid = fopen(outfile,'wt');
%print header
print_dlm_line(fn, 'fid', fid);

for ii=1:nrec
    print_dlm_line(data(ii,1:nf), 'fid', fid, ...
        'precision', arg.precision, 'emptyval', arg.emptyval);
end

fclose(fid);

