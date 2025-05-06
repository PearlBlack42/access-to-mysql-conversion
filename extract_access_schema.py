import pyodbc

ACCESS_DB_PATH = r"D:\\simkopkar\\simkopkar.mDB"

def get_access_connection(db_path):
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={db_path};'
        r'SystemDB=D:\\simkopkar\\miw.mdw;'
        r'UID=sa;'
        r'PWD=0711321277;'
    )
    return pyodbc.connect(conn_str)

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

def main():
    try:
        conn = get_access_connection(ACCESS_DB_PATH)
        cursor = conn.cursor()
        tables = get_access_tables(cursor)
        print("Tables in simkopkar.mDB:")
        for table in tables:
            print(f"Table: {table}")
            columns = get_access_columns(cursor, table)
            for col_name, col_type in columns:
                print(f"  - {col_name} ({col_type})")
            print()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
