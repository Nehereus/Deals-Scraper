import sqlite3
import os

def delete_parts_only_items(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get a list of all tables in the database except for 'gpuSpecs'
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'gpuSpecs';")
    tables = cursor.fetchall()

    # Loop through all tables and delete items with condition "Parts Only"
    for table_name in tables:
        table = table_name[0]
        try:
            # Perform the delete operation
            cursor.execute(f"DELETE FROM \"{table}\" WHERE condition='Parts Only';")
            print(f"Deleted 'Parts Only' items from table '{table}'.")
        except sqlite3.Error as e:
            print(f"An error occurred in table '{table}': {e}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("All 'Parts Only' items have been deleted from the database, except from 'gpuSpecs' table.")

if __name__ == "__main__":
    # Retrieve the database path from the 'SHARED_PATH' environment variable
    shared_path = os.environ.get('SHARED_PATH')
    if shared_path:
        database_path = os.path.join(shared_path, "items_database.db")
        delete_parts_only_items(database_path)
    else:
        print("The 'SHARED_PATH' environment variable is not set.")
