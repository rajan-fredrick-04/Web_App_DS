# utils/auth_utils.py
from flask import render_template, flash, redirect, url_for,session,request
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import OperationalError
from utils.db_utils import create_connection
import smtplib
import random

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
                cursor.execute('''SELECT user_id,password FROM public."User_log" WHERE email = %s''', (email,))
                result = cursor.fetchone()
                if result is None:
                    flash('Invalid email or password', 'danger')
                    return redirect(url_for("login"))
                else:
                    user_id, stored_password = result[0], result[1]
                    if check_password_hash(stored_password, password):
                        session.permanent = True  
                        session['user_id'] = user_id  
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




otp_storage = {}  # Temporary storage for OTP

def send_email(to_email, subject, message):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  
        server.starttls()
        server.login("rajan.fredrick04@gmail.com", "vxmi titq csmy bpwy")
        server.sendmail("rajan.fredrick04@gmail.com", to_email, f"Subject:{subject}\n\n{message}")
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def forgot_pwd():
    if request.method == "POST":
        email = request.form['email']
        connection, cursor = create_connection()
        
        cursor.execute('''SELECT user_id FROM public."User_log" WHERE email=%s''', (email,))
        user = cursor.fetchone()
        
        if user:
            user_id = user[0]
            otp = random.randint(100000, 999999) 
            otp_storage[user_id] = otp  
            
            # Send OTP via email
            if send_email(email, "Your OTP Code", f"Your OTP is {otp}. Please use this to reset your password."):
                flash("OTP sent to your email. Please check your inbox.", "info")
                session['reset_user_id'] = user_id  # Store user_id in session for OTP verification
                return redirect(url_for('verify_otp'))
            else:
                flash("Failed to send OTP. Please try again later.", "danger")
        else:
            flash("Email not found in our system.", "warning")

    return render_template('forgot_password.html')

def verify():
    if request.method == "POST":
        user_id = session.get('reset_user_id')
        otp = request.form['otp']

        if user_id in otp_storage and otp_storage[user_id] == int(otp):
            session['otp_verified'] = True
            flash("OTP verified. You can now reset your password.", "success")
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template('verify_otp.html')

def reset_pwd():
    if not session.get('otp_verified'):
        flash("You must verify OTP before resetting your password.", "warning")
        return redirect(url_for('forgot_password'))

    if request.method == "POST":
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash("Passwords don't match. Try again.", "danger")
        else:
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
            user_id = session.get('reset_user_id')
            
            connection, cursor = create_connection()
            cursor.execute('''UPDATE public."User_log" SET password=%s WHERE user_id=%s''', (hashed_password, user_id))
            connection.commit()
            
            flash("Password successfully reset. Please log in.", "success")
            session.pop('reset_user_id', None)  # Clear session data
            session.pop('otp_verified', None)
            otp_storage.pop(user_id, None)  # Clear OTP
            
            return redirect(url_for('login'))
    
    return render_template('reset_password.html')


