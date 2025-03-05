# Excel to JSON and API Call Generator

This tool converts Excel files to JSON format and generates API calls based on Excel data.

## Features

- Parse Excel files with multiple sheets
- Convert Excel data to structured JSON
- Generate curl commands for API calls
- Map Excel field names to API field names
- Support for basic authentication
- Interactive mode for easy usage
- Configurable parsing, conversion, and API formatting

## Setup

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic JSON Conversion

```bash
python main.py --excel input.xlsx --output output.json
```

### Generate API Calls

```bash
python main.py --excel input.xlsx --generate-api-calls --api-endpoint "https://api.example.com/endpoint"
```

### Advanced API Call Generation

```bash
python main.py --excel input.xlsx --generate-api-calls --api-endpoint "https://api.example.com/endpoint" --mapping mapping.json --username admin --output-curl api_calls.sh
```

### Interactive Mode

For users unfamiliar with command-line options:

```bash
python main.py --interactive
```

## Command-line Arguments

### Basic Arguments

- `--excel` or `-e`: Path to the Excel file
- `--output` or `-o`: Path to save the JSON output
- `--sheet` or `-s`: Name of the sheet to process (default depends on operation)
- `--config` or `-c`: Path to configuration file

### API Call Generation Arguments

- `--generate-api-calls` or `-g`: Enable API call generation
- `--mapping` or `-m`: Path to field mapping JSON file
- `--api-endpoint` or `-a`: API endpoint URL
- `--username` or `-u`: Basic auth username
- `--password` or `-p`: Basic auth password
- `--output-curl` or `-curl`: Path to save curl commands

### Other Arguments

- `--interactive` or `-i`: Run in interactive mode

## Field Mapping

Create a mapping file (`mapping.json`) to map Excel column names to API field names:

```json
{
  "excel_column1": "ENGINE_FIELD_NAME",
  "excel_column2": "ENGINE_DISPLAY_NAME",
  "excel_column3": "ENGINE_FIELD_TYPE"
}
```

A template mapping file (`mapping_template.json`) is provided for reference.

## Configuration

Create a `config.json` file to customize the behavior:

```json
{
  "parser": {
    "required_columns": ["column1", "column2"],
    "sheet_name": 0,
    "header_row": 0
  },
  "converter": {
    "indent": 2,
    "date_format": "%Y-%m-%d",
    "flatten": false
  },
  "api": {
    "application_name": "ENGINE",
    "form_name": "ENGINE_FIELD_SETTINGS",
    "locale": "en"
  }
}
```

## Example API Data Format

The API call generator produces data in the following structure:

```json
{
  "Document": [
    {
      "applicationName": "ENGINE",
      "formName": "ENGINE_FIELD_SETTINGS",
      "phase": "",
      "locale": "en",
      "Fields": [
        {
          "fieldName": "ENGINE_FIELD_NAME",
          "Values": ["FIELD_VALUE"]
        },
        {
          "fieldName": "ENGINE_DISPLAY_NAME",
          "Values": ["Display Name"]
        }
      ]
    }
  ]
}
```

## Examples

### Convert all sheets in an Excel file to JSON

```bash
python main.py --excel data/customers.xlsx --output data/customers.json
```

### Convert a specific sheet

```bash
python main.py --excel data/products.xlsx --output data/products.json --sheet "Inventory"
```

### Generate API calls with field mapping

```bash
python main.py --excel data/fields.xlsx --generate-api-calls --api-endpoint "https://api.example.com/endpoint" --mapping mapping.json --output-curl api_calls.sh
```

### Generate API calls with authentication

```bash
python main.py --excel data/fields.xlsx --generate-api-calls --api-endpoint "https://api.example.com/endpoint" --username admin --password secret
```

## Project Structure

```
excel_to_json/
├── excel_parser.py        # Handles Excel file parsing
├── json_converter.py      # Converts parsed data to JSON
├── field_mapper.py        # Maps field names using a mapping file
├── api_transformer.py     # Transforms data into API-ready format
├── curl_generator.py      # Generates curl commands for API calls
├── main.py                # Main execution script
├── config_template.json   # Template for configuration settings
├── mapping_template.json  # Template for field mapping
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```
