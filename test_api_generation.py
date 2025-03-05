import os
import pandas as pd
import json
from excel_parser import ExcelParser
from field_mapper import FieldMapper
from api_transformer import APITransformer
from curl_generator import CURLGenerator

def create_test_excel(file_path):
    """
    Create a test Excel file with field data for API testing
    
    Args:
        file_path: Path where to create the test Excel file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Create sample data for 'fields' sheet
    fields_data = {
        'field_id': ['FIELD1', 'FIELD2'],
        'display_name': ['First Field', 'Second Field'],
        'field_type': ['Text', 'Number'],
        'required': ['Yes', 'No'],
        'display_type': ['Editable', 'Read-Only'],
        'parent_apps': ['App1', 'App2'],
        'parent_forms': ['Form1', 'Form2'],
        'refresh_on_change': ['Yes', 'No'],
        'is_multivalue': ['No', 'Yes']
    }
    df = pd.DataFrame(fields_data)
    
    # Create Excel writer
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='fields', index=False)
    
    print(f"Test Excel file created at: {file_path}")

def create_test_mapping(file_path):
    """
    Create a test mapping file
    
    Args:
        file_path: Path where to create the test mapping file
    """
    mapping = {
        "field_id": "ENGINE_FIELD_NAME",
        "display_name": "ENGINE_DISPLAY_NAME",
        "field_type": "ENGINE_FIELD_TYPE",
        "required": "ENGINE_REQUIRED_WHEN_VISIBLE_AND_EDITABLE",
        "display_type": "ENGINE_DISPLAY_TYPE",
        "parent_apps": "ENGINE_FIELD_PARENT_APPLICATIONS",
        "parent_forms": "ENGINE_FIELD_PARENT_FORMS",
        "refresh_on_change": "ENGINE_REFRESH_ON_CHANGE",
        "is_multivalue": "ENGINE_IS_MULTIVALUE"
    }
    
    with open(file_path, 'w') as f:
        json.dump(mapping, f, indent=2)
        
    print(f"Test mapping file created at: {file_path}")

def test_api_generation():
    """
    Test the API call generation
    """
    # Create test directory
    test_dir = os.path.join(os.getcwd(), 'test_output')
    os.makedirs(test_dir, exist_ok=True)
    
    # Define file paths
    excel_path = os.path.join(test_dir, 'test_fields.xlsx')
    mapping_path = os.path.join(test_dir, 'test_mapping.json')
    curl_path = os.path.join(test_dir, 'test_api_calls.sh')
    
    # Create test files
    create_test_excel(excel_path)
    create_test_mapping(mapping_path)
    
    # Initialize components
    parser = ExcelParser()
    mapper = FieldMapper(mapping_path)
    transformer = APITransformer()
    curl_generator = CURLGenerator(
        api_endpoint="https://api.example.com/endpoint",
        username="test_user",
        password="test_password"
    )
    
    # Test each step of the pipeline
    
    # 1. Parse Excel
    print("\nParsing Excel file...")
    parsed_data = parser.parse_excel(excel_path, 'fields')
    print(f"Parsed {len(parsed_data.get('fields', []))} rows from the fields sheet")
    
    # 2. Apply mapping
    print("\nApplying field mapping...")
    mapped_data = mapper.apply_mapping(parsed_data, 'fields')
    first_row = mapped_data.get('fields', [])[0] if mapped_data.get('fields') else {}
    print(f"First row after mapping: {list(first_row.keys())}")
    
    # 3. Transform data for API
    print("\nTransforming data for API...")
    transformed_data = transformer.transform_data(mapped_data, 'fields')
    print(f"Transformed data contains {len(transformed_data.get('Document', []))} documents")
    
    # 4. Validate transformed data
    print("\nValidating transformed data...")
    is_valid = transformer.validate_transformed_data(transformed_data)
    print(f"Data validation: {'Passed' if is_valid else 'Failed'}")
    
    # 5. Generate curl commands
    print("\nGenerating curl commands...")
    curl_commands = curl_generator.generate_curl_commands(transformed_data)
    print(f"Generated {len(curl_commands)} curl commands")
    
    # 6. Save curl commands
    print("\nSaving curl commands...")
    curl_generator.save_curl_commands(curl_commands, curl_path)
    print(f"Curl commands saved to: {curl_path}")
    
    # 7. Print sample of the curl command
    if curl_commands:
        print("\nSample curl command (truncated):")
        command_lines = curl_commands[0].split('\n')
        preview_lines = command_lines[:5] + ['  ...'] + command_lines[-3:] if len(command_lines) > 8 else command_lines
        print('\n'.join(preview_lines))
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_api_generation()
