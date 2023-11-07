import sqlite3
import pandas as pd
import os

def find_outliers(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key constraint support

    # Get a list of all tables in the database
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        # Check if the 'price' column exists in the table
        cursor.execute(f"PRAGMA table_info(\"{table_name}\")")
        columns_info = cursor.fetchall()
        column_names = [info[1] for info in columns_info]

        if 'price' in column_names:
            # Load the data into a pandas DataFrame
            df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)

            # Define two groups based on the condition
            group_brand_new = df[df['condition'] == 'Brand New']
            group_other_conditions = df[df['condition'] != 'Brand New']

            # Function to calculate and delete outliers for a given group
            def delete_outliers(group, group_name):
                Q1 = group['price'].quantile(0.25)
                Q3 = group['price'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 3 * IQR
                outliers = group[(group['price'] < lower_bound) | (group['price'] > upper_bound)]

                # Check if the 'itemID' column exists
                if 'itemID' in group.columns:
                    outlier_ids = outliers['itemID'].tolist()
                    # Delete the outlier rows
                    cursor.executemany(f'DELETE FROM "{table_name}" WHERE itemID = ?', [(id,) for id in outlier_ids])
                    conn.commit()
                    print(f"Deleted outliers for group '{group_name}' in table '{table_name}' based on IQR method.")
                else:
                    print(f"No 'itemID' column found in table '{table_name}'.")

            # Delete outliers for each group
            delete_outliers(group_brand_new, "Brand New")
            delete_outliers(group_other_conditions, "Other Conditions")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    database_path = os.environ.get('SHARED_PATH')+"/items_database.db"
    find_outliers(database_path)
