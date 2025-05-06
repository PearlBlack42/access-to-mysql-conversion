from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'simkopkar_db'
    # Removed unix_socket to use default TCP connection
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM tbluser WHERE UserId = %s AND Pass = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user:
                session['user_id'] = user['UserId']
                session['username'] = user['Nama']
                session['user_level'] = user.get('Level', 'user')  # Assuming Level column exists
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        else:
            flash('Database connection error', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

from flask import jsonify

@app.route('/employees')
def employees():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employees.html', employees=employees)

@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nik = request.form['nik']
        nama = request.form['nama']
        bagian = request.form['bagian']
        jabatan = request.form['jabatan']
        jk = request.form['jk']
        tmk = request.form['tmk']
        iuran_wajib = request.form['iuran_wajib']
        tgl_keluar = request.form['tgl_keluar']
        status = request.form.get('status') == 'on'
        khusus = request.form.get('khusus') == 'on'
        max_plafon = request.form['max_plafon']
        max_plafon_sembako = request.form['max_plafon_sembako']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employees (NIK, Nama, Bagian, Jabatan, JK, TMK, IuranWajib, TglKeluar, Status, Khusus, MaxPlafon, MaxPlafonSembako)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nik, nama, bagian, jabatan, jk, tmk, iuran_wajib, tgl_keluar, status, khusus, max_plafon, max_plafon_sembako))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('employees'))
    return render_template('add_employee.html')

if __name__ == '__main__':
    app.run(debug=True)
