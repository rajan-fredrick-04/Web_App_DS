from flask import render_template, flash, redirect, url_for,request,session,jsonify
from psycopg2 import OperationalError
from utils.db_utils import create_connection
import psycopg2
import base64
import io

# UPLOAD_FOLDER = 'path/to/uploaded/images'
# ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fetch_data():
    user_name = user_email = user_age = user_gender = user_pref =user_image= None
    try:
        # Retrieve the user_id from session
        user_id = session.get('user_id')
        
        if not user_id:
            flash('Please log in to view your profile.', 'warning')
            return redirect(url_for('login'))  # Redirect to login if no user_id in session

        conn, cursor = create_connection()
        
        if conn and cursor:
            # Query to fetch user details using user_id from session
            cursor.execute(''' SELECT username, email, age, gender, preferences,profile_image
                               FROM public."User_log" WHERE user_id = %s''', (user_id,))
            result = cursor.fetchone()

            if result:
                user_name, user_email, user_age, user_gender, user_pref ,user_image= result
                
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

    user_image_base64 = None
    if user_image:
        import base64
        from io import BytesIO
        user_image_base64 = base64.b64encode(user_image).decode('utf-8')

    return render_template("profile_view.html",
                           name=user_name,
                           email=user_email,
                           age=user_age,
                           gender=user_gender,
                           preferences=user_pref,
                           image_base64=user_image_base64)


def update_profile():
    if 'user_id' not in session:
        flash('Not logged in!', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    new_name = request.form.get('username', '')
    new_age = request.form.get('age', '')
    new_gender = request.form.get('gender', '')
    new_pref = request.form.getlist('preferences') 
    new_image = request.files.get('user_image')

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
                # Join preferences into a single string
                new_pref_str = ', '.join(new_pref)
                update_fields.append("preferences = %s")
                params.append(new_pref_str)
            
            if new_image :
                # Read the image file as bytes
                image_bytes = new_image.read()
                # Append image bytea data to params
                update_fields.append("profile_image = %s")
                params.append(image_bytes)

            if update_fields:
                params.append(user_id)
                query = f'''UPDATE public."User_log" SET {", ".join(update_fields)} WHERE user_id=%s'''
                cursor.execute(query, tuple(params))
                conn.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('profile_view')) 
            else:
                flash('No changes made to the profile.', 'info')
        else:
            flash('No changes made to the profile.', 'info')

    except Exception as e:
        flash(f'Technical error occurred: {str(e)}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("profile_edit.html")





