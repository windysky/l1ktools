function pkstats = detect_lxb_peaks_single(x, varargin)
% DETECT_LXB_PEAKS_SINGLE Detect peaks for a single analyte in lxb data.
%   PKSTATS = DETECT_LXB_PEAKS_SINGLE(X) detect peaks for intensities X. X
%   is a 1d vector of fluorescent intensities for the given analyte.
%   PKSTATS is a structure array with the detected peaks and support
%   information.
%
%   PKSTATS = DETECT_LXB_PEAKS_SINGLE(X, 'Param1, 'Value1',...)
%   Specify optional parameter/value pairs:
%
%   'logxform' : boolean, log2 transform the data before detecting peaks.
%       Default is true.
%   'lowthresh' : scalar, log2 lower threshold for expression. Values below
%       lowthresh are ignored. Default is 4.
%   'highthresh' : scalar, log2 upper threshold for expression. Values
%       above highthresh are ignored. Default is 15.
%   'showfig' : boolean, Display figure showing detected peaks. Default is
%       false.
%   'minbead : integer, Minimum good beads to make a call. Default is 10.
%   'pkmethod' : string, Peak calling method. Valid options are
%       {'kmeans_opt','kmeans','median'}. Default is kmeans_opt.
%       'kmeans_opt': Applies k-means with k=2,3,4. Picks the K based on
%           the clustering that yields the support gradient closest to
%           expect_support_pct.
%       'kmeans': Applies kmeans with k=2.
%       'median': Reports the median value of the distribution. This is the
%           default for 'notduo' analytes and for analytes which lack
%           sufficient support to make a call.
%   'debug' : Print debugging info. Logical [true] 
%   'expect_npeak' : integer, Expected number of peaks. Default is 2.
%   'expect_support_pct': vector, Expected bead support gradient. Default
%       is [65 35]s
%
%   See also: DETECT_LXB_PEAKS_MULTI

pnames = {'logxform', 'lowthresh', 'highthresh', ...  
    'showfig', ...
    'minbead', 'pkmethod', 'expect_npeak',...
    'debug', 'title', ...
    'rpt',...
    'expect_support_pct', 'newfig'};

dflts = { true, 4, 15,...    
    false, ...
    10, 'kmeans_opt', 2,...
    false, '', ...
    'hist',...
    [65 35], true};
arg = parse_args(pnames, dflts, varargin{:});

nbead = length(x);

%convert x to log scale
if (arg.logxform)
    x = log2(max(x, eps));
end

%censor beads with high / low expression
badbeads = (x < arg.lowthresh | x > arg.highthresh);
xcensored=x;
xcensored(badbeads)=[];
ngoodbead = length(xcensored);

%default value is median of good beads
medexp = median(xcensored);

% bad or missing data defaults to one (zero on log scale)
if isempty(medexp) || isnan(medexp) || isequal(nbead,0)
    medexp = 1;
end

%default stats
if (ngoodbead < arg.minbead)
    arg.pkmethod = 'median';    
end

switch (arg.pkmethod)
    case 'median'
       % dont detect peaks just return median
       [f, xi]=ksdensity(xcensored);
       pkheight = interp1(xi,f, medexp);
       pkstats =  struct('pkexp', medexp,...
           'pksupport', ngoodbead, 'pksupport_pct',100,'pkheight', pkheight,...
           'totbead', nbead, 'ngoodbead', ngoodbead,...
           'medexp', medexp, ...
           'method', 'median');
       
    case 'kmeans_opt'
        % turn off emptycluster warning
        warning('off', 'stats:kmeans:EmptyCluster')
        sd = zeros(4, 1);
        sup_ratio = zeros(4, 1);
        sup_pct = zeros(4, 1);
        sd(1) = sum((xcensored - mean(xcensored)).^2);
        sup_pct(1) = sum(abs([100 0]-arg.expect_support_pct));
        for k=2:4
            [idx, c, sumd, d] = kmeans(xcensored, k, 'emptyaction','drop','replicates', 3);
            if nnz(~isnan(c)) == 1
                continue
            end
            sup = accumarray(idx, ones(size(idx)))';
            srtsup = sort(sup, 'descend');
            sd(k) = sum(sumd);
            sup_ratio(k) = (srtsup(1)/ngoodbead) ./ (srtsup(2)/ngoodbead);
            sup_pct(k) = sum(abs(100*srtsup(1:2)/ngoodbead - arg.expect_support_pct));
        end
        [~, optk] = min(sup_pct);
        if isempty(optk)
            optk = 2;
        end
        printdbg(sprintf ('optk=%d, pctdiff=%2.2f ratio=%2.2f sd=%2.2f\n', ...
            optk, sup_pct(optk), sup_ratio(optk), sd(optk)), arg.debug);
        [idx, pkexp, sumd, d] = kmeans(xcensored, optk, ...
            'emptyaction', 'singleton', 'replicates', 5);
        
        % median of clusters instead of the mean
        pkexp = zeros(1, optk);
        for ii=1:optk
            pkexp(1,ii) = median(xcensored(idx==ii));
        end
        
        pksup = accumarray(idx,ones(size(idx)))';
        pksup_pct = 100*pksup/ngoodbead';
        
        % compute smoothed kernel, lookup pk heights
        [f, xi] = ksdensity(xcensored);
        pkheight = interp1(xi,f, pkexp);
        [srt_pksup_pct, srtidx] = sort(pksup_pct, 'descend');
        srt_pkexp = pkexp(srtidx);
        srt_pkheight = pkheight(srtidx);
        srt_pksup = pksup(srtidx);
        
        pkstats = struct(...
            'pkexp', srt_pkexp,...
            'pksupport', srt_pksup,...
            'pksupport_pct', srt_pksup_pct,...
            'pkheight', srt_pkheight,...
            'totbead', nbead,...
            'ngoodbead', ngoodbead,...
            'medexp', medexp,...
            'method', arg.pkmethod);
        
    case 'kmeans'
        [idx, pkexp, sumd, d] = kmeans(xcensored, arg.expect_npeak, 'emptyaction','drop','replicates',10);
        % median of clusters instead of the mean
        pkexp = zeros(1, arg.expect_npeak);
        for ii=1:arg.expect_npeak
            pkexp(1, ii) = median(xcensored(idx==ii));
        end
        
        pksup = accumarray(idx,ones(size(idx)))';
        pksup_pct = 100*pksup/ngoodbead';
        
        % compute smoothed kernel, lookup pk heights
        [f, xi]=ksdensity(xcensored);
        pkheight = interp1(xi,f, pkexp);
        [srt_pksup_pct, srtidx] = sort(pksup_pct, 'descend');
        srt_pkexp = pkexp(srtidx);
        srt_pkheight = pkheight(srtidx);
        srt_pksup = pksup(srtidx);
        
        pkstats = struct(...
            'pkexp', srt_pkexp,...
            'pksupport', srt_pksup,...
            'pksupport_pct', srt_pksup_pct,...
            'pkheight', srt_pkheight,...
            'totbead', nbead,...
            'ngoodbead', ngoodbead,...
            'medexp', medexp,...
            'method', arg.pkmethod);
    otherwise
        error('Unknown pkmethod:%s',arg.pkmethod)
        
end

if arg.showfig
    if arg.newfig
        hf = figure;
    end
    bins = linspace(4, 16, 50);
    [a0,b0] = hist(x, bins);
    bar(b0,a0/max(a0), 'facecolor',[0.75,0.75,0.75])
    hold on
    [a, b] = hist(xcensored, bins);
    bh = bar(b,a/max(a), 'hist');
    orange = [241, 163, 64]/255;
    set (bh, 'facecolor', orange)
        
    pklbl = regexp(num2str(1:length(pkstats.pkexp)),'\s+','split');
    th = text(pkstats.pkexp+0.05, pkstats.pkheight+0.05, pklbl);
    set(th,'color', 'k', 'fontsize', 16, 'fontweight', 'bold', ...
        'backgroundcolor', [.7 .9 .7])
    
    [f, xi] = ksdensity(xcensored);
    plot(xi, f, 'k', 'linewidth', 2)
    plot(pkstats.pkexp, pkstats.pkheight, 'ko','markerfacecolor', 'c', 'markersize', 7)
    keep = 1:min(4, length(pkstats.pkexp));
    expstr = print_dlm_line(pkstats.pkexp(keep), 'dlm', ', ', 'precision', 1);
    supstr = print_dlm_line(pkstats.pksupport(keep), 'dlm', ', ', 'precision', 0);
    suppctstr = print_dlm_line(pkstats.pksupport_pct(keep),'dlm',', ','precision',0);
    xlim ([4, 15])
    h = title(texify(sprintf('%s n=%d exp:(%s) sup:(%s) pct:(%s)', ...
        upper(pkstats.method), pkstats.ngoodbead, expstr, supstr, suppctstr)));
    set(h,'fontweight','bold','fontsize',11)
    namefig(arg.rpt);
    ylabel('Normalized Count')
    xlabel('Log2 Expression')
end

% convert expression to linear scale
if (arg.logxform)
    pkstats.pkexp = round(pow2(pkstats.pkexp));
end
end



