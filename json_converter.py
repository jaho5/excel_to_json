import json
import os
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('json_converter')

class JSONConverter:
    """
    Class for converting structured data to JSON format
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the JSON converter with optional configuration
        
        Args:
            config: Configuration dictionary that may include:
                   - indent: Indentation level for JSON formatting
                   - date_format: Format string for date serialization
                   - flatten: Whether to flatten nested structures
        """
        self.config = config or {}
        self.indent = self.config.get('indent', 2)
        self.date_format = self.config.get('date_format', '%Y-%m-%d')
        self.flatten = self.config.get('flatten', False)
    
    def convert_to_json(self, data: Any) -> str:
        """
        Convert data to JSON string
        
        Args:
            data: Data to convert to JSON
            
        Returns:
            JSON string representation of the data
        """
        try:
            return json.dumps(
                data,
                indent=self.indent,
                default=self._json_serializer,
                ensure_ascii=False
            )
        except Exception as e:
            logger.error(f"Error converting to JSON: {e}")
            raise ValueError(f"Failed to convert data to JSON: {e}")
    
    def _json_serializer(self, obj: Any) -> Any:
        """
        Custom JSON serializer to handle non-serializable types
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON serializable representation of the object
        """
        # Handle datetime objects
        if isinstance(obj, (datetime, date)):
            return obj.strftime(self.date_format)
            
        # Handle pandas NaT, NaN, etc.
        if pd.isna(obj):
            return None
            
        # Handle other types as needed
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def save_json(self, json_data: str, output_path: str) -> None:
        """
        Save JSON string to file
        
        Args:
            json_data: JSON string to save
            output_path: Path where to save the JSON file
            
        Raises:
            IOError: If unable to write to the file
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            logger.info(f"Saving JSON to: {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
                
        except Exception as e:
            logger.error(f"Error saving JSON to file: {e}")
            raise IOError(f"Failed to save JSON to file: {e}")
    
    def validate_json(self, json_data: str) -> bool:
        """
        Validate JSON string
        
        Args:
            json_data: JSON string to validate
            
        Returns:
            True if valid JSON, False otherwise
        """
        try:
            json.loads(json_data)
            return True
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return False
    
    def clean_json_data(self, data: Any) -> Any:
        """
        Clean and normalize data before JSON conversion
        
        Args:
            data: Data to clean
            
        Returns:
            Cleaned data ready for JSON conversion
        """
        if isinstance(data, dict):
            return {k: self.clean_json_data(v) for k, v in data.items() if k is not None}
            
        elif isinstance(data, list):
            return [self.clean_json_data(item) for item in data if item is not None]
            
        elif pd.isna(data):
            return None
            
        # Convert any other types as needed
        return data
    
    def flatten_json(self, data: Dict[str, Any], separator: str = '_') -> Dict[str, Any]:
        """
        Flatten nested JSON structures
        
        Args:
            data: Nested dictionary to flatten
            separator: Character to use when joining keys
            
        Returns:
            Flattened dictionary
        """
        result = {}
        
        def _flatten(current_data, parent_key=''):
            if isinstance(current_data, dict):
                for key, value in current_data.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    _flatten(value, new_key)
            elif isinstance(current_data, list):
                for i, item in enumerate(current_data):
                    new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                    _flatten(item, new_key)
            else:
                result[parent_key] = current_data
        
        _flatten(data)
        return result
    
    def process_data(self, data: Any, output_path: Optional[str] = None) -> str:
        """
        Process data to JSON and optionally save to file
        
        Args:
            data: Data to convert to JSON
            output_path: Optional path to save the JSON file
            
        Returns:
            JSON string representation of the data
        """
        # Clean the data
        cleaned_data = self.clean_json_data(data)
        
        # Flatten if configured
        if self.flatten:
            if isinstance(cleaned_data, dict):
                cleaned_data = self.flatten_json(cleaned_data)
            elif isinstance(cleaned_data, list) and all(isinstance(item, dict) for item in cleaned_data):
                cleaned_data = [self.flatten_json(item) for item in cleaned_data]
        
        # Convert to JSON
        json_data = self.convert_to_json(cleaned_data)
        
        # Validate
        if not self.validate_json(json_data):
            raise ValueError("Generated JSON is invalid")
        
        # Save if output path is provided
        if output_path:
            self.save_json(json_data, output_path)
        
        return json_data


if __name__ == "__main__":
    # Example usage
    converter = JSONConverter(config={
        'indent': 2,
        'date_format': '%Y-%m-%d',
        'flatten': False
    })
    
    # Example data
    example_data = {
        'sheet1': [
            {'name': 'John', 'age': 30, 'date': datetime.now()},
            {'name': 'Jane', 'age': 25, 'date': datetime.now()}
        ]
    }
    
    try:
        # Process and save
        json_result = converter.process_data(example_data, 'output.json')
        print("Successfully converted data to JSON")
        
    except Exception as e:
        print(f"Error: {e}")
