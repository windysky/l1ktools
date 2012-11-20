# read the full data file
import cmap.io.gct as gct
GCTObject = gct.GCT('path_to_gctx_file')
GCTObject.read()
print(GCTObject.matrix)

# read the first 100 rows and 10 columns of the data
import cmap.io.gct as gct
GCTObject = gct.GCT('path_to_gctx_file')
GCTObject.read(row_inds=range(100),col_inds=range(10))
print(GCTObject.matrix)

# get the available meta data headers for data columns and row
column_headers = GCTObject.get_chd()
row_headers = GCTObject.get_rhd()

# get the perturbagen description meta data field from the column data
descs = GCTObject.get_column_meta('pert_desc')

# get the gene symbol meta data field from the row data
symbols = GCTObject.get_row_meta('pr_gene_symbol')