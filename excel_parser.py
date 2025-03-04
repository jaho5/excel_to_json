import pandas as pd
import os
import logging
from typing import Dict, List, Union, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('excel_parser')

class ExcelParser:
    """
    Class for parsing Excel files into structured data
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Excel parser with optional configuration
        
        Args:
            config: Configuration dictionary that may include:
                   - required_columns: List of required columns
                   - sheet_name: Default sheet name to read
                   - header_row: Row number to use as header (0-indexed)
        """
        self.config = config or {}
        self.required_columns = self.config.get('required_columns', [])
        self.default_sheet = self.config.get('sheet_name', 0)
        self.header_row = self.config.get('header_row', 0)
    
    def read_excel_file(self, file_path: str, sheet_name: Optional[Union[str, int]] = None) -> Dict[str, pd.DataFrame]:
        """
        Read an Excel file and return dataframes for each sheet or specified sheet
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Name or index of the sheet to read, None reads all sheets
            
        Returns:
            Dictionary of sheet names and their corresponding dataframes
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid Excel file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        sheet_to_read = sheet_name if sheet_name is not None else None
        
        try:
            logger.info(f"Reading Excel file: {file_path}, sheet: {sheet_to_read}")
            
            # If sheet_to_read is None, read all sheets
            if sheet_to_read is None:
                excel_data = pd.read_excel(
                    file_path, 
                    sheet_name=None,  # Read all sheets
                    header=self.header_row
                )
            else:
                # Read specific sheet and return in the same dict format for consistency
                df = pd.read_excel(
                    file_path, 
                    sheet_name=sheet_to_read,
                    header=self.header_row
                )
                excel_data = {sheet_to_read: df}
            
            # Sheet name validation
            logger.info(f"Sheets found in Excel file: {list(excel_data.keys())}")
            return excel_data
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            raise ValueError(f"Failed to read Excel file: {e}")
    
    def validate_data(self, dataframes: Dict[str, pd.DataFrame]) -> bool:
        """
        Validate dataframes against required columns
        
        Args:
            dataframes: Dictionary of dataframes to validate
            
        Returns:
            True if valid, False otherwise
        """
        for sheet_name, df in dataframes.items():
            if not self._validate_dataframe(df, sheet_name):
                return False
        return True
    
    def _validate_dataframe(self, df: pd.DataFrame, sheet_name: str) -> bool:
        """
        Validate a single dataframe
        
        Args:
            df: DataFrame to validate
            sheet_name: Name of the sheet for logging purposes
            
        Returns:
            True if valid, False otherwise
        """
        # Check for empty dataframe
        if df.empty:
            logger.warning(f"Sheet '{sheet_name}' is empty")
            return False
            
        # Check for required columns if specified
        if self.required_columns:
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            if missing_columns:
                logger.warning(f"Missing required columns in sheet '{sheet_name}': {missing_columns}")
                return False
        
        return True
    
    def clean_dataframes(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Clean and normalize dataframes
        
        Args:
            dataframes: Dictionary of dataframes to clean
            
        Returns:
            Dictionary of cleaned dataframes
        """
        cleaned_dfs = {}
        
        for sheet_name, df in dataframes.items():
            cleaned_df = self._clean_dataframe(df)
            cleaned_dfs[sheet_name] = cleaned_df
            
        return cleaned_dfs
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean a single dataframe by:
        - Removing empty rows
        - Stripping whitespace from string columns
        - Converting column names to more usable format
        - Handling NaN values
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        # Make a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Drop rows that are all NaN
        cleaned_df = cleaned_df.dropna(how='all')
        
        # Clean column names: strip whitespace and convert to lowercase
        cleaned_df.columns = [str(col).strip() for col in cleaned_df.columns]
        
        # Strip whitespace from string columns
        for col in cleaned_df.select_dtypes(include=['object']).columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        
        # Replace empty strings with NaN
        cleaned_df = cleaned_df.replace('', pd.NA)
        
        # Fill NaN with None for better JSON serialization later
        cleaned_df = cleaned_df.where(pd.notna(cleaned_df), None)
        
        return cleaned_df
    
    def parse_excel(self, file_path: str, sheet_name: Optional[Union[str, int]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Main method to parse Excel file(s) into a dictionary structure
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Name or index of the sheet to read, None reads all sheets
            
        Returns:
            Dictionary with sheet names as keys and lists of row dictionaries as values
        """
        # Read Excel file
        dataframes = self.read_excel_file(file_path, sheet_name)
        
        # Validate data
        if not self.validate_data(dataframes):
            logger.warning("Data validation failed, but continuing with processing")
        
        # Clean data
        cleaned_dfs = self.clean_dataframes(dataframes)
        
        # Convert dataframes to lists of dictionaries
        result = {}
        for sheet_name, df in cleaned_dfs.items():
            # Convert to records (list of dicts)
            records = df.to_dict(orient='records')
            result[sheet_name] = records
            
        return result


if __name__ == "__main__":
    # Example usage
    parser = ExcelParser(config={
        'required_columns': ['name', 'value'],
        'sheet_name': 0,
        'header_row': 0
    })
    
    # Replace with your actual file path
    file_path = "example.xlsx"
    
    try:
        parsed_data = parser.parse_excel(file_path)
        print(f"Successfully parsed {len(parsed_data)} sheets")
        
        for sheet_name, rows in parsed_data.items():
            print(f"Sheet: {sheet_name}, Rows: {len(rows)}")
            
    except Exception as e:
        print(f"Error: {e}")
