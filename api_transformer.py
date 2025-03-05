import logging
from typing import Dict, List, Any, Optional
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api_transformer')

class APITransformer:
    """
    Class for transforming data into API-ready format
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the API transformer with optional configuration
        
        Args:
            config: Configuration dictionary that may include:
                   - application_name: Default application name
                   - form_name: Default form name
                   - locale: Default locale
        """
        self.config = config or {}
        self.application_name = self.config.get('application_name', 'ENGINE')
        self.form_name = self.config.get('form_name', 'ENGINE_FIELD_SETTINGS')
        self.locale = self.config.get('locale', 'en')
    
    def transform_data(self, parsed_data: Dict[str, List[Dict[str, Any]]], 
                       sheet_name: str = 'fields') -> Dict[str, List[Dict[str, Any]]]:
        """
        Transform parsed data into API-ready format
        
        Args:
            parsed_data: Parsed data from Excel file
            sheet_name: Name of the sheet containing fields to transform
            
        Returns:
            Transformed data in API-ready format
        """
        if sheet_name not in parsed_data:
            logger.warning(f"Sheet '{sheet_name}' not found in data")
            return {"Document": []}
            
        api_data = {"Document": []}
        field_rows = parsed_data[sheet_name]
        
        # Group rows by a common identifier (e.g. fieldName) if needed
        # For now, we'll create a separate document for each row
        for row in field_rows:
            document = self._create_document(row)
            api_data["Document"].append(document)
            
        logger.info(f"Transformed {len(field_rows)} rows into {len(api_data['Document'])} API documents")
        return api_data
    
    def _create_document(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a document structure for a single row
        
        Args:
            row_data: Data for a single row
            
        Returns:
            Document structure ready for API call
        """
        # Extract field name for identification
        field_name_key = next((k for k in row_data.keys() if k.lower().endswith('field_name')), '')
        field_name = row_data.get(field_name_key, 'UNKNOWN')
        
        # Create document structure
        document = {
            "applicationName": self.application_name,
            "formName": self.form_name,
            "phase": "",
            "locale": self.locale,
            "Fields": []
        }
        
        # Transform each field in the row to a Field entry
        for key, value in row_data.items():
            if value is None or pd.isna(value) or (isinstance(value, str) and not value.strip()):
                continue
            # Skip empty values
            if value is None or (isinstance(value, str) and not value.strip()):
                field_entry = {
                    "fieldName": key
                }
            else:
                # Convert to list for Values
                if not isinstance(value, list):
                    value = [str(value)]
                else:
                    value = [str(v) for v in value]
                    
                field_entry = {
                    "fieldName": key,
                    "Values": value
                }
                
            document["Fields"].append(field_entry)
            
        return document
    
    def validate_transformed_data(self, transformed_data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """
        Validate transformed data against API requirements
        
        Args:
            transformed_data: Transformed data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if Document key exists
        if "Document" not in transformed_data:
            logger.error("Missing 'Document' key in transformed data")
            return False
            
        # Check if Document is a list
        if not isinstance(transformed_data["Document"], list):
            logger.error("'Document' must be a list")
            return False
            
        # Check each document
        for i, doc in enumerate(transformed_data["Document"]):
            # Check required keys
            required_keys = ["applicationName", "formName", "Fields"]
            missing_keys = [key for key in required_keys if key not in doc]
            if missing_keys:
                logger.error(f"Document {i} is missing required keys: {missing_keys}")
                return False
                
            # Check if Fields is a list
            if not isinstance(doc["Fields"], list):
                logger.error(f"Document {i}: 'Fields' must be a list")
                return False
                
            # Check each field entry
            for j, field in enumerate(doc["Fields"]):
                if "fieldName" not in field:
                    logger.error(f"Document {i}, Field {j} is missing 'fieldName'")
                    return False
                
                # Check Values format if present
                if "Values" in field and not isinstance(field["Values"], list):
                    logger.error(f"Document {i}, Field {j}: 'Values' must be a list")
                    return False
                    
        return True


if __name__ == "__main__":
    # Example usage
    transformer = APITransformer({
        'application_name': 'ENGINE',
        'form_name': 'ENGINE_FIELD_SETTINGS',
        'locale': 'en'
    })
    
    # Example data
    example_data = {
        'fields': [
            {
                'ENGINE_FIELD_NAME': 'FIELD1',
                'ENGINE_DISPLAY_NAME': 'Field 1',
                'ENGINE_FIELD_TYPE': 'Text'
            },
            {
                'ENGINE_FIELD_NAME': 'FIELD2',
                'ENGINE_DISPLAY_NAME': 'Field 2',
                'ENGINE_FIELD_TYPE': 'Number'
            }
        ]
    }
    
    try:
        # Transform data
        transformed_data = transformer.transform_data(example_data)
        
        # Validate
        if transformer.validate_transformed_data(transformed_data):
            print("Data transformation successful and validated")
        else:
            print("Validation failed")
            
    except Exception as e:
        print(f"Error: {e}")
