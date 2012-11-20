L1000 Analysis Tools v1.0
-------------------------

Copyright 2011,2012 Broad Institute of MIT and Harvard.

A collection of software tools to read and analyze data produced from
the L1000 project (www.broadinstitute.org/LINCS/).

Analysis Tools
--------------
A brief description of the tools included in this software package is
given below. The Matlab implementation of the tools is currently the
most mature. Some basic utilities in R and java are also included. We
will update the tools as they become available.

Matlab Tools: matlab/
------------
Requirements:
1. Matlab R2009a and above
2. Statistics Toolbox

Tools:
dpeak_demo.m		Demonstrates basic usage of the scripts. 
l1kt_dpeak.m		Performs peak deconvolution for all analytes in a single LXB
			file, and outputs a report of the detected peaks.
l1kt_plot_peaks.m	Plots intensity distributions for one or more analytes in 
			an LXB file.
l1kt_parse_lxb.m	Reads an LXB file and returns the RID and RP1 values.
l1kt_liss.m: 		Performs Luminex Invariant Set Smoothing on a raw (GEX) input 
			.gct file
l1kt_qnorm.m		Performs quantile normalization on an input .gct file
l1kt_infer.m		Infers expression of target genes from expression of landmark 
			genes in an input .gct file

See the documentation included with each script for a details on usage
and input parameters.

Demo:
To run the demo, start Matlab, change to the folder containing dpeak_demo and
type dpeak_demo in the Command Window. This will read a sample LXB
file (A10.lxb), generate a number of intensity distribution plots and create a
text report of the statistics of the detected peaks (A10_pkstats.txt).

R Tools: R/
-------
Requirements:
R versions 2.9 and above
prada package: http://www.bioconductor.org/packages/devel/bioc/html/prada.html

lxb2txt.R	Saves values from an LXB file as a tab-delimited text file.
lxb2txt.sh	Bash wrapper to lxb2txt.R 

Java Tools: java/
----------
lxb-util.jar	Java routine for parsing LXB files (source included).

Data format
-----------
Bead-level measurements from each detected well in L1000 assay are
stored as binary .LXB files. The LXB files conform to the FCS 3.0 data
file standard, commonly used to store flow cytometry data.  For
details see: http://isac-net.org/home.aspx

The two main measurement parameters are: 

RID: 	<32 bit unsigned integer> Reporter identifier. Values ranging
	[1-500] specifies the bead color/region. RID=0 refer to events
	that flowcytometer software was unable to classify.

RP1: 	<32 bit unsigned integer> Reporter fluorescent intensity,
	quantifies transcript abundance of the gene interrogated by
	the bead.

Python Tools: python/
-------
Requirements:
1. Python 2.6 and above (untested under Python 3)
2. numpy (http://numpy.scipy.org)
3. pytables (http://www.pytables.org/moin)
4. blessings (http://pypi.python.org/pypi/blessings)

See the GCT class documentation in python/cmap/io/gct for example usage and methods

Software License
----------------
This program is distributed under the terms of the BSD 2-Clause
license. You should have received a copy of the license along with
this program. If not see:
http://www.opensource.org/licenses/BSD-2-Clause

