
# Automated Excel & CSV Data Cleaning System

A Python-based data cleaning and automation tool that processes CSV and Excel files, removes duplicate records, handles missing values, validates email addresses, and generates professional reports.

## Features

- CSV and Excel file processing
- Automatic column name cleaning
- Duplicate record removal
- Missing value handling
- Email validation
- Date format standardization
- Before and after data quality comparison
- Excel report generation with multiple sheets
- SQLite database storage
- JSON summary report
- Error handling

## Technologies Used

- Python
- Pandas
- OpenPyXL
- SQLite
- Regular Expressions
- JSON

## Project Output

The application generates:

1. Cleaned Excel Report
2. SQLite Database
3. JSON Data Quality Report

## Installation

```bash
pip install pandas openpyxl
```

## Run the Project

```bash
python app.py
```

Enter your CSV or XLSX file path when prompted.

Example:

```text
sample.csv
```

## Sample Test Results

- Original Rows: 6
- Cleaned Rows: 5
- Duplicate Rows Removed: 1
- Invalid Emails Detected: 1
- Excel Sheets Generated: 5

## Author

Python Developer | Data Cleaning | Automation | ETL

## License

MIT License
