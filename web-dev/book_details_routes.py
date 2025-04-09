from flask import Blueprint, render_template, session
from db import mysql  # no import from run.py to avoid circular import

book_details_bp = Blueprint("book_details_bp", __name__)

@book_details_bp.route('/book/<int:book_id>')
def book_detail(book_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM book WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()

    if book:
        return render_template("book_details.html", book=book)
    else:
        return "Book not found", 404

# ✅ Add a separate route to handle reading
@book_details_bp.route('/book/<int:book_id>/read')
def read_book(book_id):
    # Check if user is logged in
    if not session.get('user_id'):
        # Not logged in — redirect to login
        return render_template("login_required.html")  # Create this template or redirect to login
    
    # User is logged in, but no PDF available yet
    return render_template("blank_reader.html", book_id=book_id)  # Show a placeholder/blank page
