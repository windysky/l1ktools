#! /usr/bin/env python
'''
Created on Jan 12, 2012
provides .gct file io modules
@author: cflynn
'''
import csv
import os
import sqlite3

import numpy
import tables 

import cmap.util.progress as update

class GCT(object):
    '''
    top level gct class to handle data io as well as manipulation.  The read
    method of this class will handle reading of either .gct or .gctx files.  
    Once the read method is called,  The gct matrix data can be found in the
    matrix attribute of the object.  Meta data can be found in the _meta 
    attribute (an in memory sqlite database) and accessed through utility 
    class methods or directly through sqlite3 methods. Note that this class 
    requires numpy for matrix operations and pytables for .gctx processing.

    example usage:
    import cmap.io.gct as gct
    GCTObject = gct.GCT('path_to_gct_file')
    GCTObject.read(row_inds=range(100),col_inds=range(10))
    print(GCTObject.matrix)

    '''
    def __init__(self,src=None):
        self.src = src
        self.version = ''
        self.matrix = ''
        self._meta = sqlite3.connect(':memory:')
        self._gctx_file = ''
        
        self.matrix_node = ''
        self.column_id_node = ''
        self.row_id_node = ''
        self.column_data = ''
        self.row_data = ''
    
    def __repr__(self):
        return 'GCT(src=%r)' % (self.src,)
    
    def __str__(self):
        return '\n'.join(['src: ' + self.src,
                          'version: ' + self.version,
                          'matrix: numpy.ndarray of size ' + str(self.matrix.shape),
                          '_meta: ' + str(type(self._meta))])
    
    def _add_table_to_meta_db(self,table_name,col_names):
        '''
        constructs an in memory sqlite database for storage of row or column metadata
        '''
        
        #translate table_name and table_list into a valid SQL command
        command_string = 'create table ' + table_name + '('
        for i in range(len(col_names)):
            command_string += '%s text'
            if not i == len(col_names)-1:
                command_string += ', '
        command_string += ')'
        command_string = command_string % tuple(col_names)
        
        #connect to the db and create the table
        c = self._meta.cursor()
        c.execute(command_string)
        self._meta.commit()
        c.close()
        
    def _add_row_to_meta_table(self,table_name,data_array):
        '''
        adds the specified array of data to the desired metadata table
        '''
        
        
        #translate table_name and table_list into a valid SQL command
        command_string = "insert into %s values (" % (table_name,)
        for i in range(len(data_array)):
            command_string += "%s"
            if not i == len(data_array)-1:
                command_string += ", "
        command_string += ")"
        for i,item in enumerate(data_array):
            if isinstance(item,str):
                data_array[i] = '"' + str(item) + '"'
            
        command_string = command_string % tuple(data_array)
              
        #connect to the db and add data_array to the table
        c = self._meta.cursor()
        c.execute(command_string)
        self._meta.commit()
        c.close()
    
    def _read_gct(self,src,verbose=True):
        '''
        reads tab delimited gct file 
        '''
        #open a update indicator
        if verbose:
            progress_bar = update.DeterminateProgressBar('GCT_READER')
        
        #open the file
        f = open(src,'rb')
        reader = csv.reader(f, delimiter='\t')
        self.src = src
        
        #read the gct file header information and build the empty self.matrix 
        #array for later use
        self.version = reader.next()[0]
        dims = reader.next()
        self.matrix = numpy.ndarray([int(dims[0]), int(dims[1])]) 
        
        #parse the first line to get sample names and row meta_data headers
        titles = reader.next()
        cid = titles[int(dims[2])+1:]
        row_meta_headers = titles[:int(dims[2])+1]
        row_meta_headers.insert(0,'ind')
        self._add_table_to_meta_db('row', row_meta_headers)
        
        #parse the _meta data for the columns
        col_meta_array = []
        for ii,c in enumerate(cid):
            col_meta_array.append([ii,c])
        current_row = 0
        col_meta_headers = ['ind','id']
        while current_row < int(dims[3]):
            tmp_row = reader.next()
            col_meta_headers.append(tmp_row[0])
            for ii,item in enumerate(tmp_row[int(dims[2])+1:]):
                col_meta_array[ii].append(item)
            current_row += 1
        self._add_table_to_meta_db('col', col_meta_headers)
        for item in col_meta_array:
            self._add_row_to_meta_table('col', item)
        
        #parse the meta_data for the rows and store the data matrix
        for ii,row in enumerate(reader):
            row_meta_tmp = row[:int(dims[2])+1]
            row_meta_tmp.insert(0,ii)
            self._add_row_to_meta_table('row', row_meta_tmp)
            self.matrix[ii] = row[int(dims[2])+1:]
            if verbose:
                progress_bar.update('reading gct file: ', ii, int(dims[0]))
        
        if verbose:
            progress_bar.clear()
        
    def _open_gctx(self,src):
        '''
        opens the target gctx file
        '''
        #set self.src and self.version
        self.src = src
        self._gctx_file = tables.openFile(src)
        self.version = self._gctx_file.getNodeAttr("/","version")
        
        #create shortcut reference to matrix and metadata tables
        self.matrix_node = self._gctx_file.getNode("/0/DATA/0", "matrix")
        self.column_id_node = self._gctx_file.getNode("/0/META/COL", "id")
        self.row_id_node = self._gctx_file.getNode("/0/META/ROW", "id")
        self.column_data = self._gctx_file.listNodes("/0/META/COL")
        self.row_data = self._gctx_file.listNodes("/0/META/ROW")
    
    def _close_gctx(self):
        '''
        close the open gctx file
        '''
        self._gctx_file.close()
        
    
    def _read_gctx(self,src,verbose=True,cid=None,rid=None, 
                    col_inds=None, row_inds=None):
        '''
        reads hdf5 gctx file 
        '''
        
        #get the appropriate column indices
        if not col_inds:
            col_inds = self.get_gctx_cid_inds(src, match_list=cid)
        
        #read the column meta data
        self.read_gctx_col_meta(src, col_inds, verbose=verbose)
        
        #get the appropriate row indices
        if not row_inds:
            row_inds = self.get_gctx_rid_inds(src, match_list=rid)
        
        #read the row meta data
        self.read_gctx_row_meta(src, row_inds, verbose=verbose)
        
        #read the matrix data
        self.read_gctx_matrix(src=src,cid=cid,rid=rid,
                              col_inds=col_inds,
                              row_inds=row_inds)
        
    def _is_number(self,s):
        '''
        determine if the string s can be represented as a number
        '''
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def get_gctx_cid_inds(self,src,match_list=None):
        '''
        finds all indices of cid entries that match any of the strings given in match_list
        '''
        #if match_list is a string, wrap it in a list
        if type(match_list) == str:
            match_list = [match_list]
        
        #open the gctx file
        self._open_gctx(src)
        
        if match_list == None:
            matches = range(len(self.column_id_node))
        else:
            #find all of the matching cids
            matches = []
            for match in match_list:
                matches.extend([i for i in range(len(self.column_id_node)) if match in self.column_id_node[i]])
            
        self._close_gctx()
        return matches
    
    def get_gctx_cid(self,src,match_list=None):
        '''
        finds all cid entries that match any of the strings given in match_list
        '''
        #if match_list is a string, wrap it in a list
        if type(match_list) == str:
            match_list = [match_list]
        
        #open the gctx file
        self._open_gctx(src)
        
        if match_list == None:
            matches = [x for x in self.column_id_node]
        else:
            #find all of the matching cids
            matches = []
            for match in match_list:
                matches.extend([self.column_id_node[i] for i in range(len(self.column_id_node)) if match in self.column_id_node[i]])
            
        self._close_gctx()
        matches = [x.rstrip() for x in matches]
        return matches
    
    def get_gctx_rid_inds(self,src,match_list=None,exact=False):
        '''
        finds all the indices of rid entries that match any of the strings given in match_list
        '''
        #if match_list is a string, wrap it in a list
        if type(match_list) == str:
            match_list = [match_list]
        
        #open the gctx file
        self._open_gctx(src)
        
        if match_list == None:
            matches = range(len(self.row_id_node))
        else:
            #find all of the matching rids
            matches = []
            if exact:
                for match in match_list:
                    matches.extend([i for i in range(len(self.row_id_node)) if match == self.row_id_node[i].rstrip()])
                
            else:
                for match in match_list:
                    matches.extend([i for i in range(len(self.row_id_node)) if match in self.row_id_node[i]])
            
        self._close_gctx()
        return matches
    
    def get_gctx_rid(self,src,match_list=None):
        '''
        finds all rid entries that match any of the strings given in match_list
        '''
        #if match_list is a string, wrap it in a list
        if type(match_list) == str:
            match_list = [match_list]
        
        #open the gctx file
        self._open_gctx(src)
        
        if match_list == None:
            matches = [x for x in self.row_id_node]
        else:
            #find all of the matching cids
            matches = []
            for match in match_list:
                matches.extend([self.row_id_node[i] for i in range(len(self.row_id_node)) if match in self.row_id_node[i]])
            
        self._close_gctx()
        matches = [x.rstrip() for x in matches]
        return matches
    
    def read_gctx_matrix(self,src=None,cid=None,rid=None,col_inds=None,
                                            row_inds=None):
        '''
        read just the matrix data from a gctx file
        '''
        if not src:
            src = self.src
        
        #get the appropriate column indices
        if not col_inds:
            col_inds = self.get_gctx_cid_inds(src, match_list=cid)
        
        #get the appropriate row indices
        if not row_inds:
            row_inds = self.get_gctx_rid_inds(src, match_list=rid)
        #open the gctx file
        self._open_gctx(src)
        
        #set up the indices 
        if not col_inds:
            col_inds = range(len(self.column_id_node))
        if not row_inds:
            row_inds = range(len(self.row_id_node))

        #read the data
        if len(col_inds) < len(row_inds):
            self.matrix = self.matrix_node[col_inds,:]
            self.matrix = self.matrix[:,row_inds]
        else:
            chunk_size = 1000
            self.matrix = numpy.zeros((len(self.column_id_node),len(row_inds)))
            for i in range(0,len(self.column_id_node),chunk_size):
                try:
                    chunk_start = i
                    chunk_end = i+chunk_size
                    self.matrix[chunk_start:chunk_end,:] = self.matrix_node[chunk_start:chunk_end,row_inds]
                except IndexError:
                    chunk_start = i
                    chunk_end = len(self.column_id_node)
                    self.matrix[chunk_start:chunk_end,:] = self.matrix_node[chunk_start:chunk_end,row_inds]
                except ValueError:
                    chunk_start = i
                    chunk_end = len(self.column_id_node)
                    self.matrix[chunk_start:chunk_end,:] = self.matrix_node[chunk_start:chunk_end,row_inds]

            self.matrix = self.matrix[col_inds,:]
        # make sure the data is in the right order given the col_inds and row_inds
        self.matrix = self.matrix[col_inds.sort(),:]
        self.matrix = self.matrix[:,row_inds.sort()]
        self.matrix =  numpy.reshape(self.matrix,(len(col_inds),len(row_inds)))
        self.matrix = self.matrix.transpose()
        
        #close the gctx file
        self._close_gctx()
    
    def read_gctx_col_meta(self,src,col_inds=None, verbose=True):
        '''
        read the column meta data from the file given in src.  If col_inds is given, only
        those columns specified are read.  
        '''
        #open an update indicator
        if verbose:
            progress_bar = update.DeterminateProgressBar('GCTX_READER')
        
        #open the gctx file
        self._open_gctx(src)
        
        #set up the indices 
        if not col_inds:
            col_inds = range(len(self.column_id_node))
        
        #read in the column meta data
        column_headers = [x.name for x in self.column_data]
        column_headers.insert(0,'ind')
        self._add_table_to_meta_db("col", column_headers)
        num_rows = self.column_data[0].shape[0]
        for i in col_inds:
            if verbose:
                progress_bar.update('reading column meta data', i, num_rows)
            data_list = [i]
            for column in self.column_data:
                data_list.append(str(column[i]).rstrip())
            self._add_row_to_meta_table("col", data_list)
        
        #clear the update indicator
        if verbose:
            progress_bar.clear()
        
        #close the gctx file
        self._close_gctx()
    
    def read_gctx_row_meta(self,src,row_inds=None, verbose=True):
        '''
        read the row meta data from the file given in src.  If row_inds is given, only
        those rows specified are read.  
        '''
        #open an update indicator
        if verbose:
            progress_bar = update.DeterminateProgressBar('GCTX_READER')
        
        #open the gctx file
        self._open_gctx(src)
        
        #set up the indices 
        if not row_inds:
            row_inds = range(len(self.row_id_node))
        
        #read in the row meta data
        row_headers = [x.name for x in self.row_data]
        row_headers.insert(0,'ind')
        self._add_table_to_meta_db("row", row_headers)
        num_rows = self.row_data[0].shape[0]
        for i in row_inds:
            if verbose:
                progress_bar.update('reading row meta data', i, num_rows)
            data_list = [i]
            for column in self.row_data:
                data_list.append(str(column[i]).rstrip())
            self._add_row_to_meta_table("row", data_list)
        
        #clear the update indicator
        if verbose:
            progress_bar.clear()
            
        #close the gctx file
        self._close_gctx()
    
    def read(self,src=None,verbose=True,cid=None,rid=None, 
            col_inds=None, row_inds=None, matrix_only=False):
        '''
        reads data from src into metadata tables and data matrix 
        '''
        #determine file type
        if not src:
            src = self.src
        extension = os.path.splitext(src)[1]
        try:
            if extension == '.gct':
                self._read_gct(src,verbose)
            elif extension == '.gctx':
                if matrix_only:
                    self.read_gctx_matrix(cid=cid,rid=rid,col_inds=col_inds,
                                            row_inds=row_inds)
                else:            
                    self._read_gctx(src,verbose=verbose,cid=cid,rid=rid,col_inds=col_inds,
                                row_inds=row_inds)
            else:
                raise GCTException("source file must be .gct or .gctx")
        except GCTException, (instance):
            print instance.message
        
    def get_sample_meta(self,sample_name):
        '''
        return a dictionary of the _meta data for the sample specified by sample_name
        '''
        #get the headers of the col database
        chd = self.get_chd()
        
        #build a dictionary of _meta data for the sample
        sample_meta = {}
        c = self._meta.cursor()
        for header in chd:
            query = "SELECT %s FROM col WHERE id=?" % (header,)
            c.execute(query, (sample_name,))
            sample_meta.update({header : str(c.fetchone()[0])})
        self._meta.commit()
        c.close()
        
        #return the dictionary
        return sample_meta
    
    def get_column_meta(self,column_name):
        '''
        return a list of all meta data entries in the column specified by column_name
        '''
        c = self._meta.cursor()
        query = "SELECT %s FROM col" % (column_name,)
        c.execute(query)
        meta_list = []
        for row in c:
            meta_list.append(str(row[0]))
        c.close()
        return meta_list
    
    def get_row_meta(self,row_name):
        '''
        return a list of all meta data entries in the column specified by row_name
        '''
        c = self._meta.cursor()
        query = "SELECT %s FROM row" % (row_name,)
        c.execute(query)
        meta_list = []
        for row in c:
            meta_list.append(str(row[0]))
        c.close()
        return meta_list
    
    def get_probe_meta(self,sample_name):
        '''
        return a dictionary of the _meta data for the probe specified by probe_name
        '''
        #get the headers of the row database
        chd = self.get_rhd()
        
        #build a dictionary of _meta data for the sample
        probe_meta = {}
        c = self._meta.cursor()
        for header in chd:
            query = "SELECT %s FROM row WHERE id=?" % (header,)
            c.execute(query, (sample_name,))
            probe_meta.update({header : str(c.fetchone()[0])})
        self._meta.commit()
        c.close()
        
        #return the dictionary
        return probe_meta
    
    def get_inds_by_cdesc(self,column,desc,op='='):
        '''
        look for all of the entries in the column _meta data matching cdesc in column and
        return their indices in an list
        '''
        #construct the query
        if self._is_number(desc):
            query = "SELECT ind FROM col WHERE CAST(%s AS REAL) %s '%s'" % (column,op,desc)
        else:
            query = "SELECT ind FROM col WHERE %s %s '%s'" % (column,op,desc)
        
        #query the col database and store the returned indices
        inds = []
        c = self._meta.cursor()
        c.execute(query)
        for row in c:
            inds.append(int(row[0]))
        c.close()
        
        return inds
    
    def get_inds_by_rdesc(self,column,desc,op='='):
        '''
        look for all of the entries in the row _meta data matching cdesc in column and
        return their indices in an list
        '''
        #construct the query
        if self._is_number(desc):
            query = "SELECT ind FROM row WHERE CAST(%s AS REAL) %s '%s'" % (column,op,desc)
        else:
            query = "SELECT ind FROM row WHERE %s %s '%s'" % (column,op,desc)
        
        #query the col database and store the returned indices
        inds = []
        c = self._meta.cursor()
        c.execute(query)
        for row in c:
            inds.append(int(row[0]))
        c.close()
        
        return inds
        
    def get_cids(self):
        '''
        returns a list of all column ids found in the dataset
        '''
        #query the col database for all ids 
        inds = []
        ids = [] 
        c = self._meta.cursor()
        c.execute("SELECT ind, id FROM col")
        for row in c:
            inds.append(int(row[0]))
            ids.append(str(row[1]))
        c.close()
        
        #ensure that the ids are in the proper order according to ind
        inds_ids = zip(inds,ids)
        inds_ids.sort()
        ordered_ids = [item[1] for item in inds_ids]
        
        #return the result
        return ordered_ids
    
    def get_rids(self):
        '''
        returns a list of all row ids found in the dataset
        '''
        #query the col database for all ids 
        inds = []
        ids = [] 
        c = self._meta.cursor()
        c.execute("SELECT ind, id FROM row")
        for row in c:
            inds.append(int(row[0]))
            ids.append(str(row[1]))
        c.close()
        
        #ensure that the ids are in the proper order according to ind
        inds_ids = zip(inds,ids)
        inds_ids.sort()
        ordered_ids = [item[1] for item in inds_ids]
        
        #return the result
        return ordered_ids
    
    def get_rhd(self):
        '''
        returns the names of the row _meta data headers in a list
        '''
        #query the row data base for its headers using a pragma statement
        c = self._meta.cursor()
        c.execute("PRAGMA table_info(row)")
        
        #pull out all of the headers from the returned tuple
        rhd = []
        for header_tuple in c:
            rhd.append(str(header_tuple[1]))
        
        #return the header list
        return rhd

    
    def get_chd(self):
        '''
        returns the names of the column _meta data headers in a list
        '''
        #query the col data base for its headers using a pragma statement
        c = self._meta.cursor()
        c.execute("PRAGMA table_info(col)")
        
        #pull out all of the headers from the returned tuple
        chd = []
        for header_tuple in c:
            chd.append(str(header_tuple[1]))
        
        #return the header list
        return chd

class GCTException(Exception):
    '''
    custom exception class for GCT object exceptions
    '''
    def __init__(self, message):
        self.message = 'GCTException: ' + message
    def __str__(self):
        return repr(self.message)

def parse_gct_dict(file_path):
    '''
    parses the .gct file at the given file path into a dictionary structure
    '''
    f = open(file_path,'rb')
    reader = csv.reader(f, delimiter='\t')
    #read the gct file header information
    version = reader.next()[0]
    dims = reader.next()
    
    #set up the column names
    titles = reader.next()
    cid = titles[int(dims[2])+1:]
    
    #set up a dictionary read and skip the header info
    reader = csv.DictReader(f, fieldnames=titles, delimiter='\t')
    
    #read in data
    current_row = 0
    samples = {}
    probes = {}
    for c in cid:
        samples[c] = {'PROBE_NAMES':[],'PROBE_VALS':[]}
    for row in reader:
        if current_row < int(dims[3]):
            for c in cid:
                samples[c][row['id']] = row[c]
        else:
            probes[row['id']] = row
            for c in cid:
                samples[c][row['id']] = float(row[c])
                samples[c]['PROBE_NAMES'].append(row['id'])
                samples[c]['PROBE_VALS'].append(float(row[c]))
                probes[row['id']][c] = float(probes[row['id']][c])
        current_row+=1
    
    #package the data into a single dictionary and return it
    gct_data = {'SAMPLES':samples,'PROBES':probes,'VERSION':version, "SOURCE":file_path}
    return gct_data

if __name__ == '__main__':
    os.chdir('../../unittest_resources')
    gct_data = parse_gct_dict('gct_v13.gct')
    print sum(gct_data['SAMPLES']['LITMUS001_PC3_96H_X2:J16']['PROBE_VALS'])
    