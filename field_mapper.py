import json
import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('field_mapper')

class FieldMapper:
    """
    Class for mapping field names using a mapping file
    """
    
    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize the field mapper with optional mapping file
        
        Args:
            mapping_file: Path to the mapping file (JSON format)
        """
        self.mapping = {}
        if mapping_file:
            self.load_mapping(mapping_file)
    
    def load_mapping(self, mapping_file: str) -> Dict[str, str]:
        """
        Load mapping from JSON file
        
        Args:
            mapping_file: Path to the mapping file
            
        Returns:
            Mapping dictionary
            
        Raises:
            FileNotFoundError: If the mapping file doesn't exist
            ValueError: If the mapping file is not valid JSON
        """
        if not os.path.exists(mapping_file):
            raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
        
        try:
            logger.info(f"Loading mapping from: {mapping_file}")
            with open(mapping_file, 'r') as f:
                self.mapping = json.load(f)
            
            # Validate mapping format
            if not isinstance(self.mapping, dict):
                raise ValueError("Mapping file must contain a JSON object")
                
            logger.info(f"Loaded {len(self.mapping)} field mappings")
            return self.mapping
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in mapping file: {e}")
            raise ValueError(f"Invalid JSON in mapping file: {e}")
        except Exception as e:
            logger.error(f"Error loading mapping file: {e}")
            raise
    
    def apply_mapping(self, data: Dict[str, Any], sheet_name: str = 'fields') -> Dict[str, Any]:
        """
        Apply field name mappings to parsed data
        
        Args:
            data: Parsed data from Excel file (dictionary with sheet names as keys)
            sheet_name: Name of the sheet containing fields to map
            
        Returns:
            Data with field names mapped according to the mapping file
        """
        if not self.mapping:
            logger.warning("No mapping loaded, returning original data")
            return data
            
        if sheet_name not in data:
            logger.warning(f"Sheet '{sheet_name}' not found in data, returning original data")
            return data
            
        result = data.copy()
        mapped_rows = []
        
        # Map each row in the specified sheet
        for row in data[sheet_name]:
            mapped_row = {}
            for field_name, field_value in row.items():
                # Apply mapping if field exists in mapping dictionary
                mapped_field = self.mapping.get(field_name, field_name)
                mapped_row[mapped_field] = field_value
            mapped_rows.append(mapped_row)
            
        # Replace original rows with mapped rows
        result[sheet_name] = mapped_rows
        
        logger.info(f"Applied field mapping to {len(mapped_rows)} rows in sheet '{sheet_name}'")
        return result
    
    def get_mapping(self) -> Dict[str, str]:
        """
        Get the current mapping dictionary
        
        Returns:
            Mapping dictionary
        """
        return self.mapping


if __name__ == "__main__":
    # Example usage
    mapper = FieldMapper("example_mapping.json")
    
    # Example data
    example_data = {
        'fields': [
            {'excel_column1': 'value1', 'excel_column2': 'value2'},
            {'excel_column1': 'value3', 'excel_column2': 'value4'}
        ]
    }
    
    try:
        # Apply mapping
        mapped_data = mapper.apply_mapping(example_data)
        print("Successfully mapped field names")
        
    except Exception as e:
        print(f"Error: {e}")
