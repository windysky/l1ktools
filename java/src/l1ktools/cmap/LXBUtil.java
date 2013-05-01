package l1ktools.cmap;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import org.flowcyt.cfcs.CFCSData;
import org.flowcyt.cfcs.CFCSDataSet;
import org.flowcyt.cfcs.CFCSError;
import org.flowcyt.cfcs.CFCSErrorCodes;
import org.flowcyt.cfcs.CFCSKeyword;
import org.flowcyt.cfcs.CFCSKeywords;
import org.flowcyt.cfcs.CFCSListModeData;
import org.flowcyt.cfcs.CFCSParameter;
import org.flowcyt.cfcs.CFCSParameters;
import org.flowcyt.cfcs.CFCSSystem;
import org.flowcyt.facejava.fcsdata.exception.DuplicateParameterReferenceException;
import org.flowcyt.facejava.fcsdata.exception.InvalidCFCSDataSetTypeException;
import org.flowcyt.facejava.fcsdata.exception.InvalidParameterNumberException;
import org.flowcyt.facejava.fcsdata.impl.FcsParameter;

/**
 * Utility class for LXB files.
 * 
 */
public class LXBUtil {

    /**
     * Prevent instantiation
     */
    private LXBUtil() {
    }

    /**
     * Load an LXB file from an input stream.
     * 
     * @param is
     *            The input stream to an LXB file.
     * @param dataColumnName
     *            The data column in the LXB file or <tt>null</tt> in which case
     *            RP1 is used.
     * @return The LXB data.
     * @throws Exception
     *             If an error occurs.
     */
    public static LXBData loadLXB(InputStream is, String dataColumnName) throws Exception {
	CFCSSystem readSystem = new CFCSSystem();
	try {
	    readSystem.open(is);
	} catch (CFCSError e) {
	    if (e.errorNumber == CFCSErrorCodes.CFCSIOError)
		throw new IOException(e.toString());
	    throw e;
	}
	if (readSystem.getCount() > 1) {
	    throw new IOException();
	}

	CFCSDataSet cfcsDs = readSystem.getDataSet(0);
	int dataColumnIndex = getColumnIndex(cfcsDs, dataColumnName);
	return extractDataSet(cfcsDs, 1, dataColumnIndex);

    }

    /**
     * Load an LXB file.
     * 
     * @param file
     *            The LXB file to load.
     * @param dataColumnName
     *            The data column in the LXB file or <tt>null</tt> in which case
     *            RP1 is used.
     * @return The LXB data.
     * @throws Exception
     *             If an error occurs.
     */
    public static LXBData loadLXB(String file, String dataColumnName) throws Exception {
	return loadLXB(new BufferedInputStream(new FileInputStream(file)), dataColumnName);
    }

    /**
     * Extracts the FCS Data in the CFCSDataSet and creates the corresponding
     * FCSData impls.
     * 
     * @param cfcsDs
     *            The CFCSDataSet to extract data from.
     * @param datasetNumber
     *            The dataset number of the given CFCSDataSet.
     * @return Returns the DataSet representation of the FCS Data in the given
     *         CFCSDataSet.
     * @throws InvalidCFCSDataSetTypeException
     *             Thrown if the CFCSDataSet does not contain List Mode Data.
     * @throws InvalidParameterNumberException
     *             Thrown if one of the FCS parameters has an invalid parameter
     *             number.
     * @throws DuplicateParameterReferenceException
     *             Thrown if there is a duplicate FCS parameter name ($PnN) in
     *             the given CFCSDataSet.
     */
    private static LXBData extractDataSet(CFCSDataSet cfcsDs, int datasetNumber, int dataColumnIndex) throws Exception {
	CFCSData readData = cfcsDs.getData();
	if (readData.getType() != CFCSData.LISTMODE) {
	    throw new InvalidCFCSDataSetTypeException();
	}
	CFCSKeywords keywords = cfcsDs.getKeywords();
	String well = null;
	String scanner = null;
	for (int i = 0; i < keywords.getCount(); i++) {
	    CFCSKeyword kw = keywords.getKeyword(i);
	    String name = kw.getKeywordName();
	    if ("$CYTSN".equals(name)) { // scanner
		scanner = kw.getKeywordValue();

	    } else if ("$SMNO".equals(name)) { // well
		well = kw.getKeywordValue();
	    }
	}

	CFCSParameters cfcsDsParams = cfcsDs.getParameters();
	int parameterCount = cfcsDsParams.getCount();
	List<FcsParameter> parameters = new ArrayList<FcsParameter>(parameterCount);

	for (int i = 0; i < parameterCount; ++i) {
	    CFCSParameter cfcsParam = cfcsDsParams.getParameter(i);
	    FcsParameter param;
	    try {
		param = new FcsParameter(cfcsParam.getShortName(), i + 1);
	    } catch (CFCSError e) {
		param = new FcsParameter(i + 1);
	    }
	    parameters.add(param);
	}

	CFCSListModeData readLMData = (CFCSListModeData) readData;
	int eventCount = readLMData.getCount();
	float[] values = new float[eventCount];
	int[] analytes = new int[eventCount];
	float[] tmp = new float[parameterCount];

	for (int i = 0; i < eventCount; ++i) {
	    readLMData.getEvent(i, tmp);
	    int analyte = (int) tmp[0];
	    values[i] = tmp[dataColumnIndex];
	    analytes[i] = analyte;
	}
	return new LXBData(values, analytes, scanner, well, keywords);
    }

    /**
     * Gets the column index for the specified column name.
     * 
     * @param fcsDataset
     *            The dataset.
     * @param dataColumnName
     *            The dataset column name (e.g. RP1).
     * @return The column index in the dataset containing the specified column
     *         or <tt>-1</tt> if the column name is not found. name.
     */
    private static int getColumnIndex(CFCSDataSet fcsDataset, String dataColumnName) {
	CFCSParameters parameterList = fcsDataset.getParameters();

	int dataColumnIndex = -1;
	if (dataColumnName == null) {
	    dataColumnName = "RP1";
	}

	for (int i = 0; i < parameterList.getCount(); i++) { // data types
							     // stored in
							     // file
	    CFCSParameter p = parameterList.getParameter(i);
	    if (dataColumnName.equalsIgnoreCase(p.getShortName())) {
		dataColumnIndex = i;
		break;
	    }

	}
	return dataColumnIndex;

    }

    /**
     * 
     * Stores information from an LXB file.
     * 
     */
    public static class LXBData {
	/**
	 * Array of all values. Analytes array gives the analyte at a given
	 * index.
	 */
	public float[] values;
	/**
	 * The scanner name
	 */
	public String scanner;
	/** The well */
	public String well;
	/** Array of analyte numbers */
	public int[] analytes;
	/** List of keywords */
	public CFCSKeywords keywords;

	public LXBData(float[] values, int[] analytes, String scanner, String well, CFCSKeywords keywords) {
	    this.values = values;
	    this.analytes = analytes;
	    this.scanner = scanner;
	    this.well = well;
	    this.keywords = keywords;
	}

	@Override
	public String toString() {
	    return "LXBData [scanner=" + scanner + ", well=" + well + "]";
	}

    }

}
