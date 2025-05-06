"""
Python script to convert Microsoft Access database (.mdb) to MySQL database.

Requirements:
- Python 3.x
- pyodbc (for Access connection)
- mysql-connector-python (for MySQL connection)
- Access ODBC driver installed on your system

Instructions:
1. Install required packages:
   pip install pyodbc mysql-connector-python

2. Ensure you have the Microsoft Access ODBC driver installed.
   On Windows, it is usually installed with MS Office or Access Runtime.
   On Linux/Mac, you may need to use alternatives or run on Windows.

3. Update the connection parameters below:
   - ACCESS_DB_PATH: Path to your .mdb file
   - MYSQL_CONFIG: Your MySQL connection details

4. Run the script:
   python access_to_mysql_conversion.py

Note: This script reads tables and data from Access and creates corresponding tables in MySQL.
      It does not handle complex data types or relationships perfectly, so manual adjustments may be needed.

"""

import pyodbc
import mysql.connector
from mysql.connector import errorcode

# Update these parameters
ACCESS_DB_PATH_1 = r"D:\\simkopkar\\simkopkar.mDB"  # Path to first Access .mdb file
ACCESS_DB_PATH_2 = r"D:\\simkopkar\\simkopkardata.mDB"  # Path to linked Access .mdb file
MYSQL_CONFIG = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'simkopkar_db',
    'raise_on_warnings': True
}

def get_access_connection(db_path):
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={db_path};'
        r'SystemDB=D:\\simkopkar\\miw.mdw;'
        r'UID=sa;'
        r'PWD=0711321277;'
    )
    return pyodbc.connect(conn_str)

def get_mysql_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

def get_access_tables(cursor):
    tables = []
    for row in cursor.tables(tableType='TABLE'):
        tables.append(row.table_name)
    return tables

def get_access_columns(cursor, table):
    columns = []
    for row in cursor.columns(table=table):
        columns.append((row.column_name, row.type_name))
    return columns

def map_access_type_to_mysql(access_type):
    # Basic mapping, extend as needed
    access_type = access_type.lower()
    if 'int' in access_type:
        return 'INT'
    elif 'char' in access_type or 'text' in access_type:
        return 'VARCHAR(255)'
    elif 'date' in access_type or 'time' in access_type:
        return 'DATETIME'
    elif 'double' in access_type or 'float' in access_type or 'decimal' in access_type:
        return 'DOUBLE'
    elif 'bit' in access_type:
        return 'BOOLEAN'
    else:
        return 'VARCHAR(255)'

def create_mysql_table(cursor, table, columns):
    col_defs = []
    for col_name, col_type in columns:
        mysql_type = map_access_type_to_mysql(col_type)
        col_defs.append(f"`{col_name}` {mysql_type}")
    col_defs_str = ", ".join(col_defs)
    create_stmt = f"CREATE TABLE IF NOT EXISTS `{table}` ({col_defs_str})"
    cursor.execute(create_stmt)

def transfer_data(access_cursor, mysql_cursor, table, columns):
    access_cursor.execute(f"SELECT * FROM [{table}]")
    rows = access_cursor.fetchall()
    if not rows:
        return
    placeholders = ", ".join(["%s"] * len(columns))
    insert_stmt = f"INSERT INTO `{table}` VALUES ({placeholders})"
    for row in rows:
        # Convert row to tuple if not already
        if not isinstance(row, tuple):
            row = tuple(row)
        mysql_cursor.execute(insert_stmt, row)

def main():
    print("Connecting to Access databases...")
    access_conn_1 = get_access_connection(ACCESS_DB_PATH_1)
    access_cursor_1 = access_conn_1.cursor()
    access_conn_2 = get_access_connection(ACCESS_DB_PATH_2)
    access_cursor_2 = access_conn_2.cursor()

    print("Connecting to MySQL database...")
    mysql_conn = get_mysql_connection()
    mysql_cursor = mysql_conn.cursor()

    print("Fetching tables from first Access database...")
    tables_1 = get_access_tables(access_cursor_1)
    print(f"Found tables in simkopkar.mDB: {tables_1}")

    print("Fetching tables from linked Access database...")
    tables_2 = get_access_tables(access_cursor_2)
    print(f"Found tables in simkopkardata.mDB: {tables_2}")

    # Combine tables, avoid duplicates
    all_tables = list(dict.fromkeys(tables_1 + tables_2))

    for table in all_tables:
        if table in tables_1:
            cursor = access_cursor_1
        else:
            cursor = access_cursor_2

        print(f"Processing table: {table}")
        try:
            columns = get_access_columns(cursor, table)
            print(f"Columns: {columns}")

            print(f"Creating table {table} in MySQL...")
            create_mysql_table(mysql_cursor, table, columns)
            mysql_conn.commit()

            print(f"Transferring data for table {table}...")
            transfer_data(cursor, mysql_cursor, table, columns)
            mysql_conn.commit()
        except Exception as e:
            print(f"Warning: Skipping table {table} due to error: {e}")

    access_cursor_1.close()
    access_conn_1.close()
    access_cursor_2.close()
    access_conn_2.close()
    mysql_cursor.close()
    mysql_conn.close()
    print("Conversion completed successfully.")

if __name__ == "__main__":
    main()
