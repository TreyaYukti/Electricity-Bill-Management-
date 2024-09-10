from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_db_connection():
    try:
        connection = sqlite3.connect('electricity.db')
        connection.row_factory = sqlite3.Row
        print("Successfully connected to the database")
        return connection
    except Error as e:
        print(f"Error connecting to SQLite: {e}")
        return None

def initialize_database():
    try:
        conn = get_db_connection()
        if conn is None:
            print("Failed to initialize database: Unable to connect")
            return

        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                units_consumed INTEGER NOT NULL,
                bill_amount REAL NOT NULL
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Error as e:
        print(f"Error initializing database: {e}")

def calculate_bill(units):
    if units <= 100:
        return units * 5
    elif units <= 200:
        return 100 * 5 + (units - 100) * 7
    else:
        return 100 * 5 + 100 * 7 + (units - 200) * 10

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        units = int(request.form['units'])
        bill_amount = calculate_bill(units)

        conn = get_db_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                sql = "INSERT INTO bills (customer_name, units_consumed, bill_amount) VALUES (?, ?, ?)"
                cursor.execute(sql, (customer_name, units, bill_amount))
                conn.commit()
                bill_id = cursor.lastrowid
                cursor.close()
                conn.close()
                flash('Bill calculated and saved successfully!', 'success')
                return redirect(url_for('bill_details', bill_id=bill_id))
            except Error as e:
                flash(f'An error occurred: {e}', 'error')
        else:
            flash('Unable to connect to the database', 'error')

    return render_template('index.html')

@app.route('/bill/<int:bill_id>')
def bill_details(bill_id):
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
            bill = cursor.fetchone()
            cursor.close()
            conn.close()
            if bill:
                return render_template('bill_details.html', bill=bill)
            else:
                flash('Bill not found', 'error')
                return redirect(url_for('index'))
        except Error as e:
            flash(f'An error occurred: {e}', 'error')
    else:
        flash('Unable to connect to the database', 'error')
    return redirect(url_for('index'))

@app.route('/bills')
def all_bills():
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bills ORDER BY id DESC")
            bills = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('all_bills.html', bills=bills)
        except Error as e:
            flash(f'An error occurred: {e}', 'error')
    else:
        flash('Unable to connect to the database', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5001)