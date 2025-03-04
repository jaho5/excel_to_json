# Excel to JSON Converter

This tool converts Excel files to JSON format as part of a larger project to map Excel data to web form fields.

## Features

- Parse Excel files with multiple sheets
- Convert Excel data to structured JSON
- Configurable parsing and conversion
- Clean and validate data during processing

## Setup

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main.py --excel input.xlsx --output output.json
```

### Advanced Usage

```bash
python main.py --excel input.xlsx --output output.json --sheet "Sheet1" --config config.json
```

#### Command-line Arguments

- `--excel` or `-e`: Path to the Excel file (required)
- `--output` or `-o`: Path to save the JSON output (required)
- `--sheet` or `-s`: Name of the sheet to process (optional, default: all sheets)
- `--config` or `-c`: Path to configuration file (optional)

### Configuration

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
  }
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

### Use custom configuration

```bash
python main.py --excel data/sales.xlsx --output data/sales.json --config custom_config.json
```

## Next Steps

This tool is part of a larger project that will eventually:
1. Map JSON data to form fields in a web application
2. Use APIs or scripts to populate web forms

## Project Structure

```
excel_to_json/
├── excel_parser.py        # Handles Excel file parsing
├── json_converter.py      # Converts parsed data to JSON
├── main.py                # Main execution script
├── config.json            # Configuration settings (optional)
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```
