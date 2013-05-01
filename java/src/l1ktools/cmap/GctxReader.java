package l1ktools.cmap;

import java.io.File;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import ncsa.hdf.object.Dataset;
import ncsa.hdf.object.FileFormat;
import ncsa.hdf.object.Group;
import ncsa.hdf.object.HObject;
import ncsa.hdf.object.h5.H5File;

/**
 * 
 * A class for reading gctx files.
 * 
 */
public class GctxReader {

    private H5File h5File;

    private String path;

    /**
     * Creates a new GctxReader, given the name of the file to read from.
     * 
     * @param fileName
     *            the name of the file to read from
     */
    public GctxReader(String fileName) {
	try {
	    if (!new File(fileName).exists()) {
		throw new RuntimeException("File " + fileName + " not found.");
	    }
	    this.path = fileName;
	    FileFormat fileFormat = FileFormat.getFileFormat(FileFormat.FILE_TYPE_HDF5);
	    if (fileFormat == null) {
		throw new RuntimeException("Cannot find HDF5 FileFormat.");
	    }

	    h5File = (H5File) fileFormat.createInstance(path, FileFormat.READ);
	    if (h5File == null) {
		throw new RuntimeException("Failed to open " + fileName + " for reading.");
	    }
	    h5File.open();
	} catch (Exception x) {
	    throw new RuntimeException(x);
	}

    }

    /**
     * Closes the reader and releases any system resources associated with it.
     */
    public void close() {
	try {
	    if (h5File.getFID() != -1 && h5File != null) {
		h5File.close();
	    }
	} catch (Exception e) {

	}
    }

    /**
     * Reads a dataset.
     * 
     * 
     * @return The dataset.
     * @throws Exception
     *             If an error occurs.
     */
    public GctxDataset read() throws Exception {
	Dataset matrixDataset = (Dataset) h5File.get("/0/DATA/0/matrix");
	matrixDataset.init();
	long[] dims = matrixDataset.getDims();
	float[] matrix = (float[]) matrixDataset.read();
	Map<String, List<?>> columnMetadata = readMeta("/0/META/COL");
	Map<String, List<?>> rowMetadata = readMeta("/0/META/ROW");
	return new GctxDataset(matrix, rowMetadata, columnMetadata, (int) dims[1], (int) dims[0]);

    }

    private Map<String, List<?>> readMeta(String path) throws Exception {
	Group colGroup = (Group) h5File.get(path);
	Map<String, List<?>> map = new HashMap<String, List<?>>();
	List<HObject> members = colGroup.getMemberList();
	for (HObject member : members) {
	    Dataset d = (Dataset) member;
	    d.init();
	    String name = d.getName();
	    Object obj = d.read();
	    List<?> list = null;
	    if (obj instanceof String[]) {
		String[] array = (String[]) obj;
		list = Arrays.asList(array);
	    } else if (obj instanceof float[]) {
		float[] array = (float[]) obj;
		list = Arrays.asList(array);
	    } else if (obj instanceof double[]) {
		double[] array = (double[]) obj;
		list = Arrays.asList(array);
	    } else if (obj instanceof int[]) {
		int[] array = (int[]) obj;
		list = Arrays.asList(array);
	    }
	    if (list != null) {
		map.put(name, list);
	    }
	}
	return map;
    }

}
