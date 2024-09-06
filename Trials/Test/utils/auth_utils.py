# utils/auth_utils.py

from flask import render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import OperationalError
from utils.db_utils import create_connection

def register_user(request):
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(
            request.form['password'],
            method='pbkdf2:sha256',
            salt_length=8
        )
        connection, cursor = create_connection()
        try:
            if connection and cursor:
                cursor.execute('''INSERT INTO public."User_log" (username,password,email)VALUES (%s,%s,%s)''',
                               (username, password, email))
                connection.commit()
                flash('Registered successfully! Please log in.', 'success')
                return render_template("redirect.html", redirect_url=url_for('login'))
        except OperationalError as e:
            flash('Technical error occurred. Please try again later.', 'danger')
            print(f"Database error: {e}")
            return render_template("redirect.html", redirect_url=url_for('register'))
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
    return render_template("signup.html")


def login_user(request):
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        connection, cursor = create_connection()
        try:
            if connection and cursor:
                cursor.execute('''SELECT password FROM public."User_log" WHERE email = %s''', (email,))
                result = cursor.fetchone()
                if result is None:
                    flash('Invalid email or password', 'danger')
                    return redirect(url_for("login"))
                else:
                    stored_password = result[0]
                    if check_password_hash(stored_password, password):
                        return redirect(url_for("emotion"))  # Redirect to emotion page
                    else:
                        flash('Invalid email or password', 'danger')
        except OperationalError as e:
            flash('Technical error occurred. Please try again later.', 'danger')
            print(f"Database error: {e}")
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    return render_template('login.html')
