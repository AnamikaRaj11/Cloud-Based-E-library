from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_config import get_db_connection
import hashlib
from pymysql.cursors import DictCursor  # Import DictCursor explicitly

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # Required for session management

# Home Route (Index Page)
@app.route('/')
def home():
    return render_template('index.html')  # Shows index.html as the home page

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return redirect(url_for('register'))

        with conn.cursor(DictCursor) as cursor:  # ✅ Fixed the cursor issue
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash(f"User already registered with email: {email}", "warning")
                return redirect(url_for('login'))  # Redirect to login

            # Hash the password before storing it
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Insert new user
            cursor.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                           (full_name, email, password_hash))
            conn.commit()

        conn.close()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return redirect(url_for('login'))

        with conn.cursor(DictCursor) as cursor:  # ✅ Fixed the cursor issue
            cursor.execute("SELECT id, full_name, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

        conn.close()

        if not user:
            flash("No account found. Please register.", "danger")
            return redirect(url_for('register'))  # Redirect to register page

        # Verify hashed password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user['password'] != password_hash:
            flash("Invalid password. Try again.", "danger")
            return redirect(url_for('login'))

        # Successful login - Store in session
        session['user_id'] = user['id']  # Store user ID in session
        session['user_name'] = user['full_name']  # Store user name
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))  # Redirect to dashboard

    return render_template('login.html')

# Dashboard Route (Only for Logged-in Users)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))  # Redirect if not logged in

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('login'))

    with conn.cursor(DictCursor) as cursor:  # ✅ Fixed the cursor issue
        cursor.execute("SELECT id, full_name, email FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()

    conn.close()

    return render_template('dashboard.html', user=user)

# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))  # Redirect to login page

if __name__ == '__main__':
    app.run(debug=True)
