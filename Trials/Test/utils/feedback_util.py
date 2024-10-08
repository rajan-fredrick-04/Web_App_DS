from flask import render_template, flash, redirect, url_for,request,session
from psycopg2 import OperationalError
from utils.db_utils import create_connection

def update_feedback():
    conn = None
    cursor = None
    try:
        user_id=session.get('user_id')
        
        if not user_id:
            flash('Please log in to view your profile.', 'warning')
            return redirect(url_for('login'))  
        
        if request.method=="POST":
            conn,cursor=create_connection()
            feedback_input1=request.form["feedback1"]
            feedback_input2=request.form["feedback2"]
            feedback_input3=request.form["feedback3"]
            feedback_input=feedback_input1+feedback_input2+feedback_input3

            query=''' INSERT INTO public."Feedback"  (user_id,feedback) VALUES (%s,%s)'''
            cursor.execute(query, (user_id, feedback_input))
            conn.commit()
            flash('Feedback submitted successfully!', 'success')
            return redirect(url_for('profile_view'))
    except OperationalError as e:
        flash('Technical error occurred. Please try again later.', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('feedback'))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()   
    return render_template("feedback.html")