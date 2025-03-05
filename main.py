import os
import argparse
import logging
import json
import getpass
import sys
from typing import Dict, Any, Optional

from excel_parser import ExcelParser
from json_converter import JSONConverter
from field_mapper import FieldMapper
from api_transformer import APITransformer
from curl_generator import CURLGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('excel_to_json')

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config file: {e}")
        return {}

def excel_to_json(
    excel_path: str, 
    output_path: str, 
    sheet_name: str = None,
    config_path: str = None
) -> Dict[str, Any]:
    """
    Convert Excel file to JSON
    
    Args:
        excel_path: Path to the Excel file
        output_path: Path to save the JSON output
        sheet_name: Name of the sheet to process (default: all sheets)
        config_path: Path to configuration file
        
    Returns:
        Parsed and converted data
    """
    # Load configuration if provided
    config = load_config(config_path) if config_path else {}
    
    # Get parser and converter configs
    parser_config = config.get('parser', {})
    converter_config = config.get('converter', {})
    
    # Initialize components
    parser = ExcelParser(config=parser_config)
    converter = JSONConverter(config=converter_config)
    
    try:
        # Parse Excel file
        logger.info(f"Parsing Excel file: {excel_path}")
        parsed_data = parser.parse_excel(excel_path, sheet_name)
        
        # Convert to JSON and save
        logger.info(f"Converting data to JSON and saving to: {output_path}")
        json_data = converter.process_data(parsed_data, output_path)
        
        logger.info("Excel to JSON conversion completed successfully")
        return parsed_data
        
    except Exception as e:
        logger.error(f"Excel to JSON conversion failed: {e}")
        raise

def generate_api_calls(
    excel_path: str,
    api_endpoint: str,
    mapping_file: Optional[str] = None,
    sheet_name: str = 'fields',
    username: Optional[str] = None,
    password: Optional[str] = None,
    output_curl: Optional[str] = None,
    config_path: Optional[str] = None
) -> str:
    """
    Generate API calls from Excel data
    
    Args:
        excel_path: Path to the Excel file
        api_endpoint: API endpoint URL
        mapping_file: Path to field mapping file (optional)
        sheet_name: Name of the sheet containing fields (default: 'fields')
        username: Basic auth username (optional)
        password: Basic auth password (optional)
        output_curl: Path to save generated curl commands (optional)
        config_path: Path to configuration file (optional)
        
    Returns:
        Generated curl commands as a string
    """
    # Load configuration if provided
    config = load_config(config_path) if config_path else {}
    
    # Get component configs
    parser_config = config.get('parser', {})
    api_config = config.get('api', {})
    
    # Initialize components
    parser = ExcelParser(config=parser_config)
    mapper = FieldMapper(mapping_file) if mapping_file else FieldMapper()
    transformer = APITransformer(config=api_config)
    curl_generator = CURLGenerator(api_endpoint, username, password)
    
    try:
        # Parse Excel file
        logger.info(f"Parsing Excel file: {excel_path}")
        parsed_data = parser.parse_excel(excel_path, sheet_name)
        
        # Apply field mapping if mapping file provided
        if mapping_file:
            logger.info(f"Applying field mapping from: {mapping_file}")
            parsed_data = mapper.apply_mapping(parsed_data, sheet_name)
        
        # Transform data for API
        logger.info("Transforming data for API call")
        transformed_data = transformer.transform_data(parsed_data, sheet_name)
        
        # Validate transformed data
        if not transformer.validate_transformed_data(transformed_data):
            raise ValueError("Generated API data failed validation")
        
        # Generate curl commands
        logger.info("Generating curl commands")
        curl_commands = curl_generator.generate_curl_commands(transformed_data)
        
        if not curl_commands:
            logger.warning("No curl commands generated")
            return ""
        
        # Save curl commands if output path provided
        if output_curl:
            logger.info(f"Saving curl commands to: {output_curl}")
            curl_generator.save_curl_commands(curl_commands, output_curl)
        
        logger.info("API call generation completed successfully")
        return curl_commands[0] if curl_commands else ""
        
    except Exception as e:
        logger.error(f"API call generation failed: {e}")
        raise

def run_interactive_mode():
    """
    Run the tool in interactive mode
    """
    print("\n=== Excel to JSON / API Call Generator ===\n")
    
    # Get Excel file path
    while True:
        excel_path = input("Enter path to Excel file: ").strip()
        if os.path.exists(excel_path):
            break
        print(f"File not found: {excel_path}")
    
    # Select operation
    while True:
        try:
            operation = int(input("Select operation (1=Convert to JSON, 2=Generate API calls): ").strip())
            if operation in [1, 2]:
                break
            print("Please enter 1 or 2")
        except ValueError:
            print("Please enter a number")
    
    if operation == 1:
        # Excel to JSON operation
        output_path = input("Enter path to save JSON output: ").strip()
        sheet_name = input("Enter sheet name to process (leave blank for all sheets): ").strip() or None
        config_path = input("Enter path to configuration file (leave blank for none): ").strip() or None
        
        try:
            excel_to_json(
                excel_path=excel_path,
                output_path=output_path,
                sheet_name=sheet_name,
                config_path=config_path
            )
            print(f"\nSuccess! JSON data saved to: {output_path}")
        except Exception as e:
            print(f"\nError: {e}")
            
    else:
        # Generate API calls operation
        api_endpoint = input("Enter API endpoint URL: ").strip()
        mapping_file = input("Enter path to mapping file (leave blank for none): ").strip() or None
        sheet_name = input("Enter name of the sheet containing fields (leave blank for 'fields'): ").strip() or 'fields'
        use_auth = input("Use basic authentication? (y/n): ").strip().lower() == 'y'
        
        username = None
        password = None
        if use_auth:
            username = input("Enter basic auth username: ").strip()
            password = getpass.getpass("Enter basic auth password: ")
            
        output_curl = input("Enter path to save CURL commands (leave blank to display only): ").strip() or None
        config_path = input("Enter path to configuration file (leave blank for none): ").strip() or None
        
        try:
            curl_command = generate_api_calls(
                excel_path=excel_path,
                api_endpoint=api_endpoint,
                mapping_file=mapping_file,
                sheet_name=sheet_name,
                username=username,
                password=password,
                output_curl=output_curl,
                config_path=config_path
            )
            
            if output_curl:
                print(f"\nSuccess! Curl commands saved to: {output_curl}")
            
            if curl_command:
                print("\nGenerated curl command:\n")
                print(curl_command)
                
        except Exception as e:
            print(f"\nError: {e}")

def main():
    """
    Main entry point for the script
    """
    parser = argparse.ArgumentParser(description='Convert Excel files to JSON and generate API calls')
    
    # Basic Excel to JSON arguments
    parser.add_argument('--excel', '-e', help='Path to the Excel file')
    parser.add_argument('--output', '-o', help='Path to save the JSON output')
    parser.add_argument('--sheet', '-s', help='Name of the sheet to process (default: all sheets)')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    
    # API call generation arguments
    parser.add_argument('--generate-api-calls', '-g', action='store_true', help='Enable API call generation')
    parser.add_argument('--mapping', '-m', help='Path to field mapping JSON file')
    parser.add_argument('--api-endpoint', '-a', help='API endpoint URL')
    parser.add_argument('--username', '-u', help='Basic auth username')
    parser.add_argument('--password', '-p', help='Basic auth password')
    parser.add_argument('--output-curl', '-curl', help='Path to save curl commands')
    
    # Interactive mode
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Run in interactive mode if specified
    if args.interactive:
        run_interactive_mode()
        return
    
    try:
        # Check if generating API calls
        if args.generate_api_calls:
            # Validate required arguments
            if not args.excel:
                parser.error("--excel is required")
            if not args.api_endpoint:
                parser.error("--api-endpoint is required when using --generate-api-calls")
            
            # If password is specified but not username, prompt for username
            username = args.username
            password = args.password
            if password and not username:
                username = input("Enter basic auth username: ").strip()
            
            # If username is specified but not password, prompt for password
            if username and not password:
                password = getpass.getpass("Enter basic auth password: ")
            
            # Generate API calls
            curl_command = generate_api_calls(
                excel_path=args.excel,
                api_endpoint=args.api_endpoint,
                mapping_file=args.mapping,
                sheet_name=args.sheet or 'fields',
                username=username,
                password=password,
                output_curl=args.output_curl,
                config_path=args.config
            )
            
            # Print curl command if no output file specified
            if not args.output_curl and curl_command:
                print(curl_command)
                
        else:
            # Regular Excel to JSON conversion
            if not args.excel:
                parser.error("--excel is required")
            if not args.output:
                parser.error("--output is required for Excel to JSON conversion")
                
            excel_to_json(
                excel_path=args.excel,
                output_path=args.output,
                sheet_name=args.sheet,
                config_path=args.config
            )
            
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
