import os
import argparse
import logging
import json
from typing import Dict, Any

from excel_parser import ExcelParser
from json_converter import JSONConverter

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
) -> None:
    """
    Convert Excel file to JSON
    
    Args:
        excel_path: Path to the Excel file
        output_path: Path to save the JSON output
        sheet_name: Name of the sheet to process (default: all sheets)
        config_path: Path to configuration file
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
        return json_data
        
    except Exception as e:
        logger.error(f"Excel to JSON conversion failed: {e}")
        raise

def main():
    """
    Main entry point for the script
    """
    parser = argparse.ArgumentParser(description='Convert Excel files to JSON')
    
    parser.add_argument('--excel', '-e', required=True, help='Path to the Excel file')
    parser.add_argument('--output', '-o', required=True, help='Path to save the JSON output')
    parser.add_argument('--sheet', '-s', help='Name of the sheet to process (default: all sheets)')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    
    args = parser.parse_args()
    
    try:
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
