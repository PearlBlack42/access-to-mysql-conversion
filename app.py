from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='simkopkar_db',
            user='root',
            password=''
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Platform: {e}")
        return None

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tbluser WHERE UserId = %s AND Pass = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['UserId']
            session['username'] = user['Nama']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    username = session.get('username', 'User')
    return render_template('dashboard.html', username=username)

# API endpoint for jenis simpanan live search
@app.route('/api/jenis_simpanan')
def api_jenis_simpanan():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        like_search = f"%{search}%"
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstjenissimpanan WHERE JenisId LIKE %s OR Keterangan LIKE %s", (like_search, like_search))
    else:
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstjenissimpanan")
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page

    if search:
        cursor.execute("""
            SELECT * FROM tblmstjenissimpanan
            WHERE JenisId LIKE %s OR Keterangan LIKE %s
            LIMIT %s OFFSET %s
        """, (like_search, like_search, per_page, offset))
    else:
        cursor.execute("SELECT * FROM tblmstjenissimpanan LIMIT %s OFFSET %s", (per_page, offset))
    jenis_simpanans = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        'jenis_simpanan': jenis_simpanans,
        'page': page,
        'total_pages': total_pages
    })

# API endpoint for periode live search
@app.route('/api/periode')
def api_periode():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        like_search = f"%{search}%"
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstperiode WHERE PeriodeID LIKE %s OR Periode LIKE %s", (like_search, like_search))
    else:
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstperiode")
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page

    if search:
        cursor.execute("""
            SELECT * FROM tblmstperiode
            WHERE PeriodeID LIKE %s OR Periode LIKE %s
            LIMIT %s OFFSET %s
        """, (like_search, like_search, per_page, offset))
    else:
        cursor.execute("SELECT * FROM tblmstperiode LIMIT %s OFFSET %s", (per_page, offset))
    periodes = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        'periode': periodes,
        'page': page,
        'total_pages': total_pages
    })

@app.route('/employees')
def employees():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        like_search = f"%{search}%"
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstkaryawan WHERE NIK LIKE %s OR Nama LIKE %s", (like_search, like_search))
    else:
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstkaryawan")
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page

    if search:
        cursor.execute("""
            SELECT * FROM tblmstkaryawan
            WHERE NIK LIKE %s OR Nama LIKE %s
            LIMIT %s OFFSET %s
        """, (like_search, like_search, per_page, offset))
    else:
        cursor.execute("SELECT * FROM tblmstkaryawan LIMIT %s OFFSET %s", (per_page, offset))
    employees = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('employees.html', employees=employees, page=page, total_pages=total_pages, search=search)

@app.route('/delete_employees', methods=['POST'])
def delete_employees():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    selected_ids = request.form.getlist('selected_ids')
    if selected_ids:
        conn = get_db_connection()
        cursor = conn.cursor()
        format_strings = ','.join(['%s'] * len(selected_ids))
        cursor.execute(f"DELETE FROM tblmstkaryawan WHERE NIK IN ({format_strings})", tuple(selected_ids))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Deleted {len(selected_ids)} employees.", 'success')
    else:
        flash("No employees selected for deletion.", 'warning')

    return redirect(url_for('employees'))

@app.route('/list_barang')
def list_barang():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        like_search = f"%{search}%"
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstbrg WHERE KodeBarang LIKE %s OR NamaBarang LIKE %s", (like_search, like_search))
    else:
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstbrg")
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page

    if search:
        cursor.execute("""
            SELECT * FROM tblmstbrg
            WHERE KodeBarang LIKE %s OR NamaBarang LIKE %s
            LIMIT %s OFFSET %s
        """, (like_search, like_search, per_page, offset))
    else:
        cursor.execute("SELECT * FROM tblmstbrg LIMIT %s OFFSET %s", (per_page, offset))
    barangs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('list_barang.html', barangs=barangs, page=page, total_pages=total_pages, search=search)

@app.route('/list_jenis_simpanan')
def list_jenis_simpanan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        like_search = f"%{search}%"
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstjenissimpanan WHERE JenisId LIKE %s OR Keterangan LIKE %s", (like_search, like_search))
    else:
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstjenissimpanan")
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page

    if search:
        cursor.execute("""
            SELECT * FROM tblmstjenissimpanan
            WHERE JenisId LIKE %s OR Keterangan LIKE %s
            LIMIT %s OFFSET %s
        """, (like_search, like_search, per_page, offset))
    else:
        cursor.execute("SELECT * FROM tblmstjenissimpanan LIMIT %s OFFSET %s", (per_page, offset))
    jenis_simpanans = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('list_jenis_simpanan.html', jenis_simpanans=jenis_simpanans, page=page, total_pages=total_pages, search=search)

@app.route('/list_periode')
def list_periode():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    page = request.args.get('page', default=1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        like_search = f"%{search}%"
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstperiode WHERE PeriodeID LIKE %s OR Periode LIKE %s", (like_search, like_search))
    else:
        cursor.execute("SELECT COUNT(*) AS total FROM tblmstperiode")
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page

    if search:
        cursor.execute("""
            SELECT * FROM tblmstperiode
            WHERE PeriodeID LIKE %s OR Periode LIKE %s
            LIMIT %s OFFSET %s
        """, (like_search, like_search, per_page, offset))
    else:
        cursor.execute("SELECT * FROM tblmstperiode LIMIT %s OFFSET %s", (per_page, offset))
    periodes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('list_periode.html', periodes=periodes, page=page, total_pages=total_pages, search=search)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Implement form submission logic here
        # For now, just redirect to employees list
        return redirect(url_for('employees'))
    return render_template('add_employee.html')

@app.route('/add_barang', methods=['GET', 'POST'])
def add_barang():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Implement form submission logic here
        return redirect(url_for('list_barang'))
    return render_template('add_barang.html')

@app.route('/add_jenis_simpanan', methods=['GET', 'POST'])
def add_jenis_simpanan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        jenis_id = request.form.get('kode')
        keterangan = request.form.get('nama')
        bunga = request.form.get('bunga', 0)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tblmstjenissimpanan (JenisId, Keterangan, Bunga) VALUES (%s, %s, %s)", (jenis_id, keterangan, bunga))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Jenis Simpanan added successfully.', 'success')
        return redirect(url_for('list_jenis_simpanan'))
    return render_template('add_jenis_simpanan.html')

@app.route('/periode/add', methods=['GET', 'POST'])
def add_periode():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        periode_id = request.form.get('kode')
        periode = request.form.get('nama')
        awal = request.form.get('tanggal_mulai')
        akhir = request.form.get('tanggal_selesai')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tblmstperiode (PeriodeID, Periode, Awal, Akhir) VALUES (%s, %s, %s, %s)", (periode_id, periode, awal, akhir))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Periode added successfully.', 'success')
        return redirect(url_for('list_periode'))
    return render_template('add_periode.html')

@app.route('/edit_employee/<nik>', methods=['GET', 'POST'])
def edit_employee(nik):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        # Implement update logic here
        # For now, just redirect to employees list
        cursor.close()
        conn.close()
        return redirect(url_for('employees'))
    else:
        cursor.execute("SELECT * FROM tblmstkaryawan WHERE NIK = %s", (nik,))
        employee = cursor.fetchone()
        cursor.close()
        conn.close()
        if employee:
            return render_template('edit_employee.html', employee=employee)
        else:
            flash('Employee not found.', 'danger')
            return redirect(url_for('employees'))

@app.route('/delete_employee/<nik>', methods=['GET', 'POST'])
def delete_employee(nik):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblmstkaryawan WHERE NIK = %s", (nik,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Employee deleted successfully.', 'success')
    return redirect(url_for('employees'))

@app.route('/periodes')
def periodes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblMstPeriode")
    periodes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('periodes.html', periodes=periodes)

@app.route('/periode/add', methods=['GET', 'POST'])
def add_periode():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        periodeid = request.form['periodeid']
        periode = request.form['periode']
        awal = request.form['awal']
        akhir = request.form['akhir']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tblMstPeriode (PeriodeID, Periode, Awal, Akhir)
            VALUES (%s, %s, %s, %s)
        """, (periodeid, periode, awal, akhir))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('periodes'))
    return render_template('add_periode.html')

@app.route('/edit_periode/<periodeid>', methods=['GET', 'POST'])
def edit_periode(periodeid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        periode = request.form['periode']
        awal = request.form['awal']
        akhir = request.form['akhir']
        cursor.execute("""
            UPDATE tblMstPeriode
            SET Periode = %s, Awal = %s, Akhir = %s
            WHERE PeriodeID = %s
        """, (periode, awal, akhir, periodeid))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Periode updated successfully.', 'success')
        return redirect(url_for('periodes'))
    else:
        cursor.execute("SELECT * FROM tblMstPeriode WHERE PeriodeID = %s", (periodeid,))
        periode_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if periode_data:
            return render_template('edit_periode.html', periode=periode_data)
        else:
            flash('Periode not found.', 'danger')
            return redirect(url_for('periodes'))

@app.route('/delete_periode/<periodeid>', methods=['POST'])
def delete_periode(periodeid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblMstPeriode WHERE PeriodeID = %s", (periodeid,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Periode deleted successfully.', 'success')
    return redirect(url_for('periodes'))

@app.route('/edit_jenis_simpanan/<jenisid>', methods=['GET', 'POST'])
def edit_jenis_simpanan(jenisid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        keterangan = request.form['keterangan']
        bunga = request.form['bunga']
        cursor.execute("""
            UPDATE tblMstJenisSimpanan
            SET Keterangan = %s, Bunga = %s
            WHERE JenisId = %s
        """, (keterangan, bunga, jenisid))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Jenis Simpanan updated successfully.', 'success')
        return redirect(url_for('list_jenis_simpanan'))
    else:
        cursor.execute("SELECT * FROM tblMstJenisSimpanan WHERE JenisId = %s", (jenisid,))
        jenis_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if jenis_data:
            return render_template('edit_jenis_simpanan.html', jenis=jenis_data)
        else:
            flash('Jenis Simpanan not found.', 'danger')
            return redirect(url_for('list_jenis_simpanan'))

@app.route('/delete_jenis_simpanan/<jenisid>', methods=['POST'])
def delete_jenis_simpanan(jenisid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblMstJenisSimpanan WHERE JenisId = %s", (jenisid,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Jenis Simpanan deleted successfully.', 'success')
    return redirect(url_for('list_jenis_simpanan'))

if __name__ == '__main__':
    app.run(debug=True)
