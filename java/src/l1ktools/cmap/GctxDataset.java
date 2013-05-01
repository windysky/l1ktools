package l1ktools.cmap;

import java.util.List;
import java.util.Map;

/**
 * 
 * Class for storing gctx data.
 * 
 */
public class GctxDataset {
    private float[] array;
    private int columnCount;
    private Map<String, List<?>> columnMetadata;
    private int rowCount;
    private Map<String, List<?>> rowMetadata;

    /**
     * Creates a new GctxDataset.
     * 
     * @param array
     *            The column major order data array.
     * @param rowMetadata
     *            Maps metadata name to list of values.
     * @param columnMetadata
     *            Maps metadata name to list of values.
     * @param rowCount
     *            The number of rows in the dataset.
     * @param columnCount
     *            The number of columns in the dataset.
     */
    public GctxDataset(float[] array, Map<String, List<?>> rowMetadata, Map<String, List<?>> columnMetadata,
	    int rowCount, int columnCount) {
	this.array = array;
	this.rowMetadata = rowMetadata;
	this.columnMetadata = columnMetadata;
	this.rowCount = rowCount;
	this.columnCount = columnCount;
    }

    /**
     * Gets the column major order array.
     * 
     * @return The array.
     */
    public float[] getArray() {
	return array;
    }

    /**
     * Gets the number of columns in this dataset.
     * 
     * @return The number of columns.
     */
    public int getColumnCount() {
	return columnCount;
    }

    /**
     * Gets a map that maps metadata name to a list of values.
     * 
     * @return The column metadata.
     */
    public Map<String, List<?>> getColumnMetadata() {
	return columnMetadata;
    }

    /**
     * Gets the number of rows in this dataset.
     * 
     * @return The number of rows.
     */
    public int getRowCount() {
	return rowCount;
    }

    /**
     * Gets a map that maps metadata name to a list of values.
     * 
     * @return The row metadata.
     */
    public Map<String, List<?>> getRowMetadata() {
	return rowMetadata;
    }

    /**
     * Gets the value at the given row and column indices.
     * 
     * @param row
     *            The row index.
     * @param column
     *            The column index.
     * @return The value.
     */
    public float getValue(int row, int column) {
	return array[row + column * rowCount];
    }

}
