import sqlite3
import pandas as pd
import os
import json
from datetime import datetime, timedelta

def calculate_recent_outliers_bounds(db_path, config_path):
    # Load the initial configuration from the JSON file
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Calculate the date 30 days ago from today
    thirty_days_ago = datetime.now() - timedelta(days=30)
    thirty_days_ago_str = thirty_days_ago.strftime('%Y-%m-%d')

    # Get a list of all tables in the database that have a 'price' and 'condition' column
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        cursor.execute(f"PRAGMA table_info(\"{table_name}\")")
        columns_info = cursor.fetchall()
        column_names = [info[1] for info in columns_info]

        if 'price' in column_names and 'condition' in column_names:
            # Select rows where the date_sold is within the last 30 days and group them by 'condition'
            query = f'''
            SELECT * FROM "{table_name}"
            WHERE date_sold >= "{thirty_days_ago_str}"
            '''
            df = pd.read_sql_query(query, conn)

            # Split the DataFrame into two groups based on the 'condition'
            brand_new_group = df[df['condition'] == 'Brand New']
            other_conditions_group = df[df['condition'] != 'Brand New']

            # Initialize bounds
            lowest_lower_bound = float('inf')
            highest_upper_bound = float('-inf')

            # Function to calculate bounds for a given group
            def calculate_bounds(group):
                nonlocal lowest_lower_bound, highest_upper_bound
                if not group.empty:
                    Q1 = group['price'].quantile(0.25)
                    Q3 = group['price'].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1 * IQR
                    upper_bound = Q3 + 3 * IQR
                    # Update the lowest lower bound and highest upper bound if necessary
                    lowest_lower_bound = min(lowest_lower_bound, lower_bound)
                    highest_upper_bound = max(highest_upper_bound, upper_bound)

            # Calculate bounds for each group
            calculate_bounds(brand_new_group)
            calculate_bounds(other_conditions_group)

            # Update the configuration with the new bounds
            if table_name in config:
                if lowest_lower_bound != float('inf'):
                    if lowest_lower_bound<0:
                        config[table_name]['MinPrice']=0
                    else:
                        config[table_name]['MinPrice'] = round(lowest_lower_bound)
                if highest_upper_bound != float('-inf'):
                    config[table_name]['MaxPrice'] = round(highest_upper_bound)

    # Save the updated configuration back to the JSON file
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

    # Close the connection
    conn.close()

def main():
    database_path =  os.environ.get('SHARED_PATH')+"/items_database.db"
    config_path = os.environ.get('SHARED_PATH') + "/config.json"
    calculate_recent_outliers_bounds(database_path, config_path)
