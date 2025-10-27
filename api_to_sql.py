import requests
import json
import sys
import os
from datetime import datetime
from urllib.parse import urlparse

def fetch_json_from_api(api_url, headers=None):
    """Fetch JSON data from an API endpoint."""
    try:
        # Check if the URL looks valid
        if not api_url.startswith(('http://', 'https://')):
            print(f"❌ Error: Invalid URL format. Expected a full URL starting with http:// or https://")
            print(f"\nYou provided: {api_url}")
            print(f"\nExample of correct usage:")
            print(f"  python api_to_sql.py https://api.example.com/data?api_key=YOUR_KEY")
            print(f"\nIf using API key in headers, use the -H flag:")
            print(f"  python api_to_sql.py -H 'X-API-Key: YOUR_KEY' https://api.example.com/data")
            sys.exit(1)
        
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from API: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        sys.exit(1)

def get_table_name(api_url):
    """Extract a suitable table name from the API URL."""
    parsed_url = urlparse(api_url)
    path = parsed_url.path.strip('/')
    
    if path:
        # Take the last part of the path as table name
        table_name = path.split('/')[-1]
        # Remove common suffixes like .json, .api, etc.
        table_name = table_name.split('.')[0]
    else:
        # Use a default table name
        table_name = 'api_data'
    
    return table_name.replace('-', '_').replace('.', '_')

def json_to_sql(json_data, table_name='api_data'):
    """Convert JSON data to SQL INSERT statements."""
    sql_statements = []
    
    # SQL header comment
    sql_statements.append(f"-- SQL generated from JSON API\n-- Table: {table_name}\n-- Generated: {datetime.now().isoformat()}\n")
    
    if isinstance(json_data, dict):
        # If it's a single object, convert to list
        json_data = [json_data]
    
    if isinstance(json_data, list):
        # Process array of objects
        if not json_data:
            return "-- No data to insert\n"
        
        # Get column names from first object
        first_object = json_data[0]
        columns = list(first_object.keys())
        
        # Create CREATE TABLE statement
        create_table = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        create_table += "    id INTEGER PRIMARY KEY AUTOINCREMENT"
        
        for col in columns:
            # Determine SQL type based on data
            sql_type = "TEXT"
            sample_value = first_object.get(col)
            if isinstance(sample_value, (int, float)):
                if isinstance(sample_value, int):
                    sql_type = "INTEGER"
                else:
                    sql_type = "REAL"
            elif isinstance(sample_value, bool):
                sql_type = "INTEGER"
            elif isinstance(sample_value, dict) or isinstance(sample_value, list):
                sql_type = "TEXT"  # Store as JSON string
            
            create_table += f",\n    {col} {sql_type}"
        
        create_table += "\n);\n"
        sql_statements.append(create_table)
        sql_statements.append("\n")
        
        # Generate INSERT statements
        for obj in json_data:
            values = []
            for col in columns:
                value = obj.get(col, None)
                
                if value is None:
                    values.append("NULL")
                elif isinstance(value, (dict, list)):
                    # Convert nested objects to JSON string
                    values.append(f"'{json.dumps(value).replace("'", "''")}'")
                elif isinstance(value, bool):
                    values.append(str(1 if value else 0))
                elif isinstance(value, str):
                    # Escape single quotes
                    escaped_value = value.replace("'", "''")
                    values.append(f"'{escaped_value}'")
                elif isinstance(value, (int, float)):
                    values.append(str(value))
                else:
                    values.append(f"'{str(value)}'")
            
            insert_stmt = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
            sql_statements.append(insert_stmt)
    
    else:
        # Handle primitive types
        return f"-- Simple value detected\nINSERT INTO {table_name} (value) VALUES ('{str(json_data)}');\n"
    
    return ''.join(sql_statements)

def save_sql_to_file(sql_content, api_url, table_name):
    """Save SQL content to a file."""
    # Generate filename from table name
    filename = f"{table_name}.sql"
    
    # If file exists, create a numbered version
    counter = 1
    original_filename = filename
    while os.path.exists(filename):
        filename = f"{table_name}_{counter}.sql"
        counter += 1
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        print(f"\nSQL file saved as: {filename}")
        print(f"Location: {os.path.abspath(filename)}")
        return filename
    except IOError as e:
        print(f"Error saving file: {e}")
        sys.exit(1)

def parse_headers(args):
    """Parse custom headers from command line arguments."""
    headers = {}
    if '-H' in args:
        idx = args.index('-H')
        if idx + 1 < len(args):
            header_str = args[idx + 1]
            if ':' in header_str:
                key, value = header_str.split(':', 1)
                headers[key.strip()] = value.strip()
                return args[:idx] + args[idx+2:], headers
    return args, headers

def main():
    """Main function to run the script."""
    # Parse headers if provided
    args = sys.argv[1:]
    
    # Check for custom headers
    if '-H' in args:
        remaining_args, headers = parse_headers(args)
        api_url = remaining_args[0] if remaining_args else None
    else:
        headers = {}
        api_url = args[0] if args else None
    
    # Get API URL if not provided
    if not api_url:
        api_url = input("Enter API URL: ").strip()
    
    if not api_url:
        print("Error: API URL is required")
        sys.exit(1)
    
    print(f"\nFetching data from: {api_url}")
    if headers:
        print(f"Using custom headers: {headers}")
    
    # Fetch JSON data
    json_data = fetch_json_from_api(api_url, headers=headers if headers else None)
    print("✓ JSON data fetched successfully")
    
    # Get table name
    table_name = get_table_name(api_url)
    print(f"✓ Using table name: {table_name}")
    
    # Convert to SQL
    print("Converting JSON to SQL...")
    sql_content = json_to_sql(json_data, table_name)
    print("✓ Conversion complete")
    
    # Save to file
    save_sql_to_file(sql_content, api_url, table_name)
    print("\nDone!")

if __name__ == "__main__":
    main()
