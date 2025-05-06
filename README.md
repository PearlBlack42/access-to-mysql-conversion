
Built by https://www.blackbox.ai

---

# Access to MySQL Conversion

## Project Overview
This project provides scripts to convert Microsoft Access databases (.mdb files) to MySQL databases, along with a Flask web application for managing employee data. The conversion involves reading data from Access databases, creating corresponding tables in MySQL, and transferring the data while handling basic datatype mappings. The web application allows users to log in, view, and manage employee records.

## Installation
### Prerequisites
- Python 3.x
- Microsoft Access ODBC Driver (installed on your system)
- MySQL Server (with a database created for usage)

### Step-by-Step Guide
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install required Python packages**:
   ```bash
   pip install pyodbc mysql-connector-python Flask
   ```

3. **Update connection parameters**:
   Modify the `MYSQL_CONFIG` and `ACCESS_DB_PATH` parameters in the scripts (`access_to_mysql_conversion.py` and `extract_access_schema.py`) to connect to your specific Access and MySQL databases.

4. **Run the conversion script**:
   Execute the following command to run the script and initiate data conversion:
   ```bash
   python access_to_mysql_conversion.py
   ```

5. **Start the Flask application**:
   Run the Flask application with:
   ```bash
   python app.py
   ```

## Usage
- Access the Flask web application by navigating to `http://127.0.0.1:5000` in your web browser.
- Log in using your credentials (make sure the `tbluser` table exists in your MySQL database).
- Manage employee records through the provided dashboard.

## Features
- Conversion of Microsoft Access database tables to MySQL.
- A Flask web application to manage employee data, including:
  - User authentication.
  - Viewing employee records.
  - Adding new employees to the database.

## Dependencies
- `pyodbc`: For connecting to Microsoft Access databases.
- `mysql-connector-python`: For connecting to MySQL databases.
- `Flask`: For the web application framework.

You can install all dependencies via `pip` as specified in the Installation section.

## Project Structure
```
.
├── access_to_mysql_conversion.py  # Script for converting Access DB to MySQL
├── extract_access_schema.py        # Script for extracting Access DB schema
└── app.py                          # Flask web application for managing employees
```

## Notes
- Ensure that the Microsoft Access ODBC driver is installed on your machine for the conversion scripts to work properly.
- If you encounter issues or need advanced configurations, please consult the respective package documentation.
- Manual adjustments may be needed after data conversion if the Access database contains complex types or relationships not handled by the script.

## License
This project is open source. You are free to modify and use it as per your requirements.