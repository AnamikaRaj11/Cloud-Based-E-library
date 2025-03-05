from flask import Flask, render_template, request, redirect, url_for, session
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "User already registered. Please <a href='/login'>Login</a>."

        # Insert new user
        cursor.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                       (full_name, email, password))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user'] = user[1]  # Store the user's name in session
            return redirect(url_for('dashboard'))
        else:
            return "Invalid email or password. Try again."

    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
