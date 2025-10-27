# API to SQL Converter

A Python script that fetches JSON data from an API and converts it to SQL INSERT statements.

## Features

- Fetches JSON data from any API endpoint
- Automatically generates CREATE TABLE statements
- Converts JSON objects to SQL INSERT statements
- Handles nested objects and arrays
- Saves SQL file in the same directory
- Automatically extracts table name from API endpoint

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line
```bash
python api_to_sql.py <API_URL>
```

Example:
```bash
python api_to_sql.py https://jsonplaceholder.typicode.com/users
```

### Interactive Mode
If you run the script without arguments, it will prompt you for the API URL:
```bash
python api_to_sql.py
```

## Output

The script generates a `.sql` file with:
- CREATE TABLE statement (auto-generated based on the JSON structure)
- INSERT statements for all data items
- Comments with metadata (timestamp, source API)

## Examples

Example API endpoints you can try:

```bash
# Get users data
python api_to_sql.py https://jsonplaceholder.typicode.com/users

# Get posts data
python api_to_sql.py https://jsonplaceholder.typicode.com/posts

# Get todos
python api_to_sql.py https://jsonplaceholder.typicode.com/todos
```

## Notes

- The table name is automatically extracted from the API URL path
- If multiple files would have the same name, numbered suffixes are added (e.g., `users_1.sql`)
- Nested JSON objects and arrays are stored as TEXT (JSON strings)
- The script handles various data types: strings, numbers, booleans, null values
