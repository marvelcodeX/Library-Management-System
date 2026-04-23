import os
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    mysql = None
    Error = Exception


app = Flask(
    __name__,
    template_folder="TEMPLATES",
    static_folder="STATIC",
    static_url_path="/static",
)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "pass")
LOAN_DAYS = int(os.getenv("LOAN_DAYS", "14"))

DB_CONFIG = {
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "pwd"),
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "db_name"),
}


@contextmanager
def db_cursor(dictionary=False):
    if mysql is None:
        raise RuntimeError(
            "mysql-connector-python is not installed. Run: pip install -r requirements.txt"
        )

    cnx = mysql.connector.connect(**DB_CONFIG)
    cursor = cnx.cursor(dictionary=dictionary)
    try:
        yield cursor
        cnx.commit()
    except Exception:
        cnx.rollback()
        raise
    finally:
        cursor.close()
        cnx.close()


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please log in as admin to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapper


def get_dashboard_data():
    stats = {
        "total_books": 0,
        "available_books": 0,
        "issued_books": 0,
        "due_tomorrow": 0,
    }

    with db_cursor(dictionary=True) as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_books,
                COALESCE(SUM(CASE
                    WHEN LOWER(COALESCE(Issue_status, 'Available')) = 'available' THEN 1
                    ELSE 0
                END), 0) AS available_books,
                COALESCE(SUM(CASE
                    WHEN LOWER(COALESCE(Issue_status, 'Available')) = 'unavailable' THEN 1
                    ELSE 0
                END), 0) AS issued_books
            FROM book
            """
        )
        stats.update(cursor.fetchone() or {})

        books_due = get_books_due_tomorrow(cursor)
        stats["due_tomorrow"] = len(books_due)

    return stats, books_due


def get_books_due_tomorrow(cursor=None):
    query = """
        SELECT
            COALESCE(i.Title, b.Title) AS Title,
            i.Student_Name,
            b.return_date
        FROM issue i
        LEFT JOIN book b ON i.AC_No = b.`A/c No`
        WHERE DATE(b.return_date) = CURDATE() + INTERVAL 1 DAY
        ORDER BY b.return_date ASC, Title ASC
    """

    if cursor:
        cursor.execute(query)
        return cursor.fetchall()

    with db_cursor(dictionary=True) as owned_cursor:
        owned_cursor.execute(query)
        return owned_cursor.fetchall()


def add_book_record(form):
    with db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO book
                (`SL.NO`, `A/c No`, `Title`, `Author`, `Edition/Year`,
                 `Publication`, `Issue_status`)
            VALUES (%s, %s, %s, %s, %s, %s, 'Available')
            """,
            (
                form["sl_no"].strip(),
                form["ac_no"].strip(),
                form["title"].strip(),
                form["author"].strip(),
                form["edition"].strip(),
                form["publication"].strip(),
            ),
        )


def delete_book_record(ac_no):
    with db_cursor(dictionary=True) as cursor:
        cursor.execute(
            "SELECT `Issue_status` FROM book WHERE `A/c No` = %s",
            (ac_no,),
        )
        book = cursor.fetchone()

        if not book:
            raise ValueError("No book was found for that accession number.")

        if (book.get("Issue_status") or "Available").lower() == "unavailable":
            raise ValueError("This book is currently issued and cannot be deleted.")

        cursor.execute("DELETE FROM book WHERE `A/c No` = %s", (ac_no,))


def issue_book_record(form):
    ac_no = form["ac_no"].strip()
    issue_date = datetime.now().date()
    return_date = issue_date + timedelta(days=LOAN_DAYS)

    with db_cursor(dictionary=True) as cursor:
        cursor.execute(
            """
            SELECT `A/c No`, `Title`, `Author`, `Issue_status`
            FROM book
            WHERE `A/c No` = %s
            """,
            (ac_no,),
        )
        book = cursor.fetchone()

        if not book:
            raise ValueError("No book was found for that accession number.")

        if (book.get("Issue_status") or "Available").lower() == "unavailable":
            raise ValueError("This book is already issued.")

        cursor.execute(
            """
            UPDATE book
            SET Issue_status = 'Unavailable', return_date = %s
            WHERE `A/c No` = %s
            """,
            (return_date, ac_no),
        )
        cursor.execute(
            """
            INSERT INTO issue
                (`Student_Name`, `Reg_no`, `AC_No`, `Title`, `Author`, `Issue_Date`)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                form["sname"].strip(),
                form["reg_no"].strip(),
                ac_no,
                book["Title"],
                book["Author"],
                issue_date,
            ),
        )

    return return_date


def return_book_record(ac_no):
    today = datetime.now().date()

    with db_cursor(dictionary=True) as cursor:
        cursor.execute(
            """
            SELECT `Student_Name`, `Reg_no`, `AC_No`, `Title`, `Author`
            FROM issue
            WHERE `AC_No` = %s
            """,
            (ac_no,),
        )
        issue_record = cursor.fetchone()

        if not issue_record:
            raise ValueError("This book has not been issued.")

        cursor.execute(
            """
            UPDATE book
            SET Issue_status = 'Available', return_date = NULL
            WHERE `A/c No` = %s
            """,
            (ac_no,),
        )
        cursor.execute(
            """
            INSERT INTO returnb
                (`Student_Name`, `Reg_no`, `AC_No`, `Title`, `Author`, `Return_Date`)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                issue_record["Student_Name"],
                issue_record["Reg_no"],
                issue_record["AC_No"],
                issue_record["Title"],
                issue_record["Author"],
                today,
            ),
        )
        cursor.execute("DELETE FROM issue WHERE `AC_No` = %s", (ac_no,))


def search_books(form):
    conditions = []
    values = []

    search_fields = {
        "ac_no": ("`A/c No` = %s", lambda value: value),
        "sl_no": ("`SL.NO` = %s", lambda value: value),
        "title": ("`Title` LIKE %s", lambda value: f"%{value}%"),
        "author": ("`Author` LIKE %s", lambda value: f"%{value}%"),
    }

    for field_name, (condition, formatter) in search_fields.items():
        value = form.get(field_name, "").strip()
        if value:
            conditions.append(condition)
            values.append(formatter(value))

    show_all = form.get("all_books") == "1"
    if not conditions and not show_all:
        return [], "Enter at least one search value or choose View all books."

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT
            `SL.NO` AS sl_no,
            `A/c No` AS ac_no,
            `Title` AS title,
            `Author` AS author,
            `Edition/Year` AS edition,
            `Publication` AS publication,
            `Issue_status` AS issue_status,
            `return_date` AS return_date
        FROM book
        {where_clause}
        ORDER BY `Title` ASC
        LIMIT 100
    """

    with db_cursor(dictionary=True) as cursor:
        cursor.execute(query, values)
        return cursor.fetchall(), None


@app.route("/")
def login():
    if session.get("is_admin"):
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/admin", methods=["POST"])
def admin_login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["is_admin"] = True
        flash("Welcome back. Dashboard is ready.", "success")
        return redirect(url_for("home"))

    return render_template("login.html", message="Invalid username or password.")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/user")
def user_page():
    return redirect(url_for("search"))


@app.route("/home")
@admin_required
def home():
    try:
        stats, books_due = get_dashboard_data()
    except Error as err:
        stats, books_due = {}, []
        flash(f"Database error: {err}", "error")

    return render_template("home.html", stats=stats, books_due=books_due)


@app.route("/add")
@admin_required
def add():
    return render_template("add.html")


@app.route("/add_book", methods=["POST"])
@admin_required
def add_book():
    try:
        add_book_record(request.form)
        flash("Book added successfully.", "success")
    except (Error, ValueError, KeyError) as err:
        flash(f"Could not add book: {err}", "error")

    return redirect(url_for("add"))


@app.route("/delete")
@admin_required
def delete():
    return render_template("delete.html")


@app.route("/delete_book", methods=["POST"])
@admin_required
def delete_book():
    ac_no = request.form.get("ac_no", "").strip()

    if not ac_no:
        flash("Accession number is required.", "warning")
        return redirect(url_for("delete"))

    try:
        delete_book_record(ac_no)
        flash("Book deleted successfully.", "success")
    except (Error, ValueError) as err:
        flash(f"Could not delete book: {err}", "error")

    return redirect(url_for("delete"))


@app.route("/issue")
@admin_required
def issue():
    return render_template("issue.html", loan_days=LOAN_DAYS)


@app.route("/issue_book", methods=["POST"])
@admin_required
def issue_book():
    try:
        return_date = issue_book_record(request.form)
        flash(f"Book issued successfully. Due date: {return_date}.", "success")
    except (Error, ValueError, KeyError) as err:
        flash(f"Could not issue book: {err}", "error")

    return redirect(url_for("issue"))


@app.route("/returnb")
@admin_required
def returnb():
    return render_template("returnb.html")


@app.route("/return_book", methods=["POST"])
@admin_required
def return_book():
    ac_no = request.form.get("ac_no", "").strip()

    if not ac_no:
        flash("Accession number is required.", "warning")
        return redirect(url_for("returnb"))

    try:
        return_book_record(ac_no)
        flash("Book returned successfully.", "success")
    except (Error, ValueError) as err:
        flash(f"Could not return book: {err}", "error")

    return redirect(url_for("returnb"))


@app.route("/search")
def search():
    return render_template("search.html", rows=[], searched=False)


@app.route("/search_book", methods=["POST"])
def search_book():
    try:
        rows, message = search_books(request.form)
        if message:
            flash(message, "warning")
        elif not rows:
            flash("No matching books found.", "info")
    except Error as err:
        rows = []
        flash(f"Database error: {err}", "error")

    return render_template("search.html", rows=rows, searched=True)


@app.route("/check_books_due")
@admin_required
def check_books_due():
    try:
        books_due = get_books_due_tomorrow()
    except Error:
        books_due = []

    return jsonify(books_due=books_due)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
