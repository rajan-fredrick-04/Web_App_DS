from flask import render_template, flash, redirect, url_for,request,session,jsonify
from psycopg2 import OperationalError
from utils.db_utils import create_connection

def fetch_data():
    try:
        # Retrieve the user_id from session
        user_id = session.get('user_id')
        
        if not user_id:
            flash('Please log in to view your profile.', 'warning')
            return redirect(url_for('login'))  # Redirect to login if no user_id in session

        conn, cursor = create_connection()
        
        if conn and cursor:
            # Query to fetch user details using user_id from session
            cursor.execute(''' SELECT username, email, age, gender, preferences 
                               FROM public."User_log" WHERE user_id = %s''', (user_id,))
            result = cursor.fetchone()

            if result:
                user_name, user_email, user_age, user_gender, user_pref = result
            else:
                flash('No user data found.', 'warning')
                return redirect(url_for("recommends"))
        else:
            flash('Failed to connect to the database.', 'danger')
            return redirect(url_for("recommends"))

    except OperationalError as e:
        flash('Technical error occurred. Please try again later.', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for("recommends"))

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return render_template("profile_view.html",
                           name=user_name,
                           email=user_email,
                           age=user_age,
                           gender=user_gender,
                           preferences=user_pref)

def update_profile():
    email = "jane@gmail.com"  # Assume we are updating based on email for now
    new_name = request.form.get('name')
    new_age = request.form.get('age')
    new_gender = request.form.get('gender')
    new_pref = request.form.get('preferences')

    try:
        if request.method=="POST":
            conn,cursor=create_connection()
            if conn and cursor:
                update_fields = []
                params = []
                if new_name:
                    update_fields.append("username = %s")
                    params.append(new_name)
                if new_age:
                    update_fields.append("age = %s")
                    params.append(new_age)
                if new_gender:
                    update_fields.append("gender = %s")
                    params.append(new_gender)
                if new_pref:
                    update_fields.append("preferences = %s")
                    params.append(new_pref)

                params.append(email)
                query=(f'''UPDATE public."User_log" SET{",".join(update_fields)} WHERE email=%s''')
                cursor.execute(query,tuple(params))
                conn.commit()
                flash('Profile updated successfully!', 'success')
            else:
                flash('No changes made to the profile.', 'info')

    except OperationalError as e:
        flash('Technical error occurred. Please try again later.', 'danger')
        print(f"Database error: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return redirect(url_for("profile_view"))
def update_profile():
    if 'user_id' not in session:
        flash('Not Logged in!!', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']  # Get the user_id from the session
    data = request.get_json()  # Get the JSON data sent from the frontend
    new_name = data.get('username')
    new_age = data.get('age')
    new_gender = data.get('gender')
    new_pref = data.get('preferences')
    new_bio = data.get('bio')  # Assuming you're adding bio to the database
    
    try:
        conn, cursor = create_connection()
        if conn and cursor:
            update_fields = []
            params = []
            if new_name:
                update_fields.append("username = %s")
                params.append(new_name)
            if new_age:
                update_fields.append("age = %s")
                params.append(new_age)
            if new_gender:
                update_fields.append("gender = %s")
                params.append(new_gender)
            if new_pref:
                update_fields.append("preferences = %s")
                params.append(new_pref)
            if new_bio:
                update_fields.append("bio = %s")
                params.append(new_bio)

            params.append(user_id)
            query = f'''UPDATE public."User_log" SET {", ".join(update_fields)} WHERE user_id=%s'''
            cursor.execute(query, tuple(params))
            conn.commit()
            flash('Profile updated successfully!', 'success')
        else:
            flash('No changes made to the profile.', 'info')

    except Exception as e:
        flash(f'Technical error occurred: {str(e)}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('profile_view'))






