from flask import Flask, render_template, request, redirect, url_for, flash,session
from werkzeug.security import generate_password_hash,check_password_hash
import mysql.connector
from mysql.connector import Error
import traceback
from flask_mail import Mail,Message   
import uuid
import random
import string
from datetime import datetime  # Import datetime module
import matplotlib.pyplot as plt
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from mysql.connector.errors import IntegrityError
import json
from dateutil.relativedelta import relativedelta



connection=mysql.connector.connect(host="Localhost",user="root",password="",database="online_quiz_system")

if connection.is_connected():
    print("connected succeesfully..")

else:
    print("Failed to connect...")

app = Flask(__name__)

# Configure Flask-Mail settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ananahd1000@gmail.com'  
app.config['MAIL_PASSWORD'] = 'sqxb fzvr lonm oojx'  
mail=Mail(app)
app.secret_key = 'AmaanAhmed'





@app.route('/log')
def log():
    return render_template('login.html')

@app.route('/generateQuiz')
def generateQuiz():
    return render_template('generateQuiz.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/admindashboard')
def adminLogin():
    return render_template('admindashboard.html')

@app.route('/studentdashboard')
def stuLogin():
    return render_template('studentdashboard.html')

@app.route('/defaultAdminDashContent')
def defaultAdminContent():
    return render_template('defaultAdminDashContent.html')

@app.route('/defaultStuDashContent')
def defaultStuDashContent():
    return render_template('defaultStudentDashContent.html')

@app.route('/adminCreateAccount')
def adminCreateAccount():
    return render_template('adminAccountCreate.html')

@app.route('/ProfileUpdate')
def ProfileUpdate():
    return render_template('profileUpdate.html')

@app.route('/loadGuidelines')
def loadGuidelines():
    return render_template('guidelines.html')

@app.route('/manageUsers')
def manageUsers():
    return render_template('manageUser.html')

@app.route('/logout')
def loggedOut():
    return render_template('logout.html')

@app.route('/forgotpwd')
def forgotpwd():
    return render_template('forgotpassword.html')

@app.route('/manageQuiz')
def manageQuiz():
    return render_template('manageQuiz.html')

@app.route('/manageLink')
def manageLink():
    return render_template('manageLink.html')

@app.route('/updateQuestions')
def updateQuestions():
    return render_template('updateQuestions.html')

@app.route('/firstYearFirstSem')
def firstYearFirstSem():
    return render_template('quizFirstYearFirstSem.html')

@app.route('/firstYearSecondSem')
def firstYearSecondSem():
    return render_template('quizFirstYearSecondSem.html')

@app.route('/SecondYearFirstSem')
def SecondYearFirstSem():
    return render_template('quizSecondYearFirstSem.html')

@app.route('/SecondYearSecondSem')
def SecondYearSecondSem():
    return render_template('quizSecondYearSecondSem.html')


@app.route('/attemptQuiz')
def attemptQuiz():
    return render_template('attemptQuiz.html')


@app.route('/loadReport')
def loadReport():
    return render_template('report.html')



@app.route('/')
def index():
    try:
        
        cursor = connection.cursor(dictionary=True)

        # Retrieve all feedback entries
        cursor.execute("SELECT uname, email, comments FROM feedback_details LIMIT 9")

        feedback_data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
       

        # Process feedback data into columns
        columns = [[], [], []]
        for i, feedback in enumerate(feedback_data):
            columns[i % 3].append(feedback)

        return render_template('index.html', columns=columns)

    except Error as e:
        print(f"Error: {e}")
        return "There was an error loading the feedback. Please try again later.", 500


@app.route('/quiz/<path:url>')
def load_quiz(url):
    # Extract semester, subject, and quiz_id from the URL
    parts = url.split('/')
    if len(parts) >= 4:
        semester = parts[1]
        subject = parts[2]
        quiz_id = parts[3]
        
        if 'user_type' in session and session['user_type'] == 'student' and subject == "sub1":
            # If logged in and subject is "sub1", redirect to stuLogin with iframe_url parameter
             return redirect(url_for('stuLogin', subject='sub1'))
        
        elif 'user_type' in session and session['user_type'] == 'student' and subject == "sub2":
            return redirect(url_for('stuLogin', subject='sub2'))
        
        elif 'user_type' in session and session['user_type'] == 'student' and subject == "sub3":
            return redirect(url_for('stuLogin', subject='sub3'))
        
        elif 'user_type' in session and session['user_type'] == 'student' and subject == "sub4":
            return redirect(url_for('stuLogin', subject='sub4'))     
        else:
            # If not logged in or subject is not "sub1", render the login.html page
            return render_template('login.html', semester=semester, subject=subject, quiz_id=quiz_id)
            
            
    else:
        # Handle invalid URLs
        return "Invalid URL"


# display year when student login
def get_user_data(email):
    cursor = connection.cursor()
    cursor.execute("SELECT year FROM student_details WHERE email = %s", (email,))
    user_data = cursor.fetchone()
    cursor.close()
    return  int(user_data[0]) 


#close icon
@app.route('/closeupdate')
def closeupdate():
            if 'student' in session:
                return redirect(url_for('stuLogin'))  # Redirect to the login page
            elif 'admin' in session:
                return redirect(url_for('adminLogin'))  # Redirect to the login page
            else:
                # If the user type is not specified in the session, return an error or handle it accordingly
                flash("User type not specified", "error")
                return redirect(url_for('log'))


# create admin account
@app.route('/createAdminAccount', methods=['POST'])
def createAdminAccount():
    try:
        s_email = request.form.get('email')
        s_name = request.form.get('name')
        s_password = request.form.get('password')
        s_confirmpassword = request.form.get('confirmpassword')  # corrected variable name
        
        # Perform validation
        if not s_email or not s_password or not s_name:
            flash("All fields are required", "error")
            return redirect(url_for('adminCreateAccount'))
        elif s_password != s_confirmpassword:
            flash("Passwords do not match", "error")
            return redirect(url_for('adminCreateAccount'))
        else:
            # Hash the password
            hashed_password =generate_password_hash(request.form.get('confirmpassword'), method='pbkdf2:sha256')  # Hash password

            cursor = connection.cursor()
            sql = "INSERT INTO admin_details(email, username, password, status) VALUES (%s, %s, %s, %s)"
            val = (s_email, s_name,hashed_password, "active")
            cursor.execute(sql, val)
            connection.commit()
            cursor.close()
            flash("Admin Account created successfully", "success")
            return redirect(url_for('adminCreateAccount'))

    except IntegrityError as e:
        flash("Account already available!", "error")
        return redirect(url_for('adminCreateAccount'))
    
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('adminCreateAccount'))
    


# Inserting data into details table
@app.route('/studentRegistration', methods=['POST'])
def insert_data():
    try:
        s_email = request.form.get('email')
        s_index = request.form.get('index')
        s_name = request.form.get('name')
       
        # registration_date = request.form.get('year')  # Get date string from form

        # # Parse the date string to get year and month
        # registration_date_obj = datetime.strptime(registration_date, '%Y-%m-%d')
        # year = registration_date_obj.year
        # month = registration_date_obj.month
        current_datetime = datetime.now()
        current_date = current_datetime.date()
               
        s_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')  # Hash password
        
        # Perform validation
        if not s_email or not s_index or not s_name  or not current_date or not s_password:
            flash("All fields are required", "error")
            return redirect(url_for('register'))

        cursor = connection.cursor()
        sql = "INSERT INTO student_details(email,index_no,username,password,semester,date,status) VALUES (%s, %s, %s, %s, %s, %s,%s)"
        val = (s_email, s_index, s_name, s_password, "First Year First semester", current_date, "active")
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()
        flash("Account Created Successfully !!!", "success")
        return redirect(url_for('log'))

    except IntegrityError as e:
        flash("Account  or Index already available!", "error")
        return redirect(url_for('register'))
    
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('register'))



# login 
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        s_email = request.form.get('email')
        s_password = request.form.get('password')
        
        cursor = connection.cursor()

        # Check admin_details table
        cursor.execute("SELECT email, password, status FROM admin_details WHERE email = %s", (s_email,))
        admin_data = cursor.fetchone()

        if admin_data:  # If user data exists
            if admin_data[0] == s_email and check_password_hash(admin_data[1], s_password) and admin_data[2] == "active":  # If password matches
                session['user_type'] = 'admin'  # Set session variable to identify user type
                session['admin'] = s_email  # Store the current user's email in the session
                sql = "UPDATE admin_details SET status = %s WHERE email = %s"
                cursor.execute(sql, ('loggedin', s_email))
                connection.commit()
                cursor.close()
                return render_template('admindashboard.html',stid=session['admin'])  # Redirect to admin dashboard

        # Check student_details table
        cursor.execute("SELECT email, password, status FROM student_details WHERE email = %s", (s_email,))
        student_data = cursor.fetchone()
       
        if student_data:  # If user data exists
            if student_data[0] == s_email and check_password_hash(student_data[1], s_password) and student_data[2] == "active":  # If password matches
                session['user_type'] = 'student'  # Set session variable to identify user type
                session['student'] = s_email  # Store the current user's email in the session
                sql = "UPDATE student_details SET status = %s WHERE email = %s"
                cursor.execute(sql, ('loggedin', s_email))
                connection.commit()
                cursor.close()
                
                update_semester(s_email)
                
                return render_template('studentdashboard.html',stid=session['student'])
               

        cursor.close()

        # If no match is found in either table, show error message and redirect to login page
        flash("Invalid email or password", "error")
        return redirect(url_for('log'))
    
    # If it's a GET request, render the login page
    return render_template('login.html')




def update_semester(email):
    cursor = connection.cursor()

    # Retrieve user's year and semester from the student_details table using session data
    cursor.execute("SELECT  semester,date FROM student_details WHERE email = %s", (email,))
    user_data = cursor.fetchone()

    # Check if user_data is fetched properly
    if user_data:
        registeredDate = user_data[1]  # Convert to int
        registered_date = datetime.strptime(registeredDate, "%Y-%m-%d").date()
        current_datetime = datetime.now()
        current_date = current_datetime.date()
       # Calculate the difference between the current date and registered date in terms of months
        delta = relativedelta(current_date, registered_date)

        # Calculate the total number of months passed
        total_months = delta.years * 12 + delta.months
        intervals_passed=total_months//6
      

        if intervals_passed>0:
            if intervals_passed == 1:
                    
                            # Update the semester and current year/month in the database
                            cursor.execute("UPDATE student_details SET semester = %s  WHERE email = %s",
                                        ("First Year Second semester", email))

                            connection.commit()
                           
            elif intervals_passed == 2 :
                    
                            # Update the semester and current year/month in the database
                            cursor.execute("UPDATE student_details SET semester = %s  WHERE email = %s",
                                        ("Second Year First semester", email))

                            connection.commit()
                            
            elif intervals_passed == 3 :
                    
                            # Update the semester and current year/month in the database
                            cursor.execute("UPDATE student_details SET semester = %s  WHERE email = %s",
                                        ("Second Year Second semester", email))

                            connection.commit()
                           

            else:
                            # Update the semester and current year/month in the database
                            cursor.execute("UPDATE student_details SET semester = %s  WHERE email = %s",
                                        ("over", email))

                            connection.commit()
                           
        else:
             return None



       

    else:
        flash("User's year and semester information not found.", "error")

    cursor.close()  # Close the cursor outside the loop





#signout
@app.route('/signOut', methods=['POST'])
def logOut():
    confirmed = request.form.get('confirmed')
    if confirmed == 'yes':
       
            cursor = connection.cursor()
            if 'student' in session:
                # If the session indicates that the current user is a student, update the student_details table
                sql = "UPDATE student_details SET status = %s WHERE email = %s"
                cursor.execute(sql, ('active', session.get('student')))
                connection.commit()
                cursor.close()
                session.pop('student')  # Remove the user's email from the session
                session.pop('user_type')  # Remove the user's type from the session
                flash("Logged out successfully student", "success")
                return redirect(url_for('log'))  # Redirect to the login page
            elif 'admin' in session:
                # If the session indicates that the current user is an admin, update the admin_details table
                sql = "UPDATE admin_details SET status = %s WHERE email = %s"
                cursor.execute(sql, ('active', session.get('admin')))
                connection.commit()
                cursor.close()
                session.pop('admin')  # Remove the user's email from the session
                session.pop('user_type')  # Remove the user's type from the session
                flash("Logged out successfully admin", "success")
                return redirect(url_for('log'))  # Redirect to the login page
            else:
                # If the user type is not specified in the session, return an error or handle it accordingly
                flash("User type not specified", "error")
                return redirect(url_for('log'))
     

    
    if 'student' in session:
        return redirect(url_for('stuLogin'))  # Redirect to the home page or another appropriate page
    elif 'admin' in session:
        return redirect(url_for('adminLogin'))  # Redirect to the home page or another appropriate page
    else:
        return redirect(url_for('loggedOut'))


#update Account
@app.route('/updateAccount', methods=['POST'])
def updateAccount():
    newemail = request.form.get('email')
    newname = request.form.get('name')
    newpassword = generate_password_hash(request.form.get('newpass'), method='pbkdf2:sha256')
    cursor = connection.cursor()
    
  
    if 'student' in session:
            # If the session indicates that the current user is a student, update the student_details table
            sql = "UPDATE student_details SET username = %s, password = %s, email = %s, status = %s WHERE email = %s"
            cursor.execute(sql, (newname, newpassword, newemail, 'active', session.get('student')))
            connection.commit()
            cursor.close()
            session.pop('student')  # Remove the user's email from the session
            session.pop('user_type')  # Remove the user's type from the session
            flash("Profile updated successfully student", "success")
           
    elif 'admin' in session:
            # If the session indicates that the current user is an admin, update the admin_details table
            sql = "UPDATE admin_details SET username = %s, password = %s, email = %s, status = %s WHERE email = %s"
            cursor.execute(sql, (newname, newpassword, newemail, 'active', session.get('admin')))
            connection.commit()
            cursor.close()
            session.pop('admin')  # Remove the user's email from the session
            session.pop('user_type')  # Remove the user's type from the session
            flash("Profile updated successfully admin", "success")
          
    else:
           
            return redirect(url_for('log'))
        
    return redirect(url_for('log'))  # Redirect to the logout route

  

#forgot password
@app.route('/forgotpassword', methods=['POST'])
def forgotpassword():        
    try:
        s_email = request.form.get('email')
        s_password = request.form.get('password')
        s_confirmpassword = request.form.get('confirmpassword')  # corrected variable name
       
        
        # Perform validation
        if not s_confirmpassword or not s_password or not s_email:
            flash("All fields are required", "error")
            return redirect(url_for('forgotpwd'))
        elif s_password != s_confirmpassword:
            flash("Passwords do not match", "error")
            return redirect(url_for('forgotpwd'))
        else:
            cursor = connection.cursor()
               # Check student_details table
            cursor.execute("SELECT email FROM student_details WHERE email = %s", (s_email,))
            student_data = cursor.fetchone()
       
            if student_data:  # If user data exists
                  
                    msg = Message('Subject: New Password for Your Account', sender='ananahd1000@gmail.com', recipients=[s_email])  # Replace sender and recipients
                    msg.body =  f"Your new password is: {s_confirmpassword}"
                    mail.send(msg)
                    hashed_password =generate_password_hash(request.form.get('confirmpassword'), method='pbkdf2:sha256')  # Hash password
                    # If the session indicates that the current user is an admin, update the admin_details table
                    sql = "UPDATE student_details SET  password = %s WHERE email = %s"
                    cursor.execute(sql, (hashed_password,s_email))
                    connection.commit()
                    cursor.close()
                    flash("password updated successfully student", "success")
                    return redirect(url_for('log'))
            
            cursor.execute("SELECT email FROM admin_details WHERE email = %s", (s_email,))
            admin_data = cursor.fetchone()
            if admin_data:  # If user data exists 
                    msg = Message('Subject: New Password for Your Account', sender='ananahd1000@gmail.com', recipients=[s_email])  # Replace sender and recipients
                    msg.body =  f"Your new password is: {s_confirmpassword}"
                    mail.send(msg)
                    hashed_password =generate_password_hash(request.form.get('confirmpassword'), method='pbkdf2:sha256')  # Hash password
                    # If the session indicates that the current user is an admin, update the admin_details table
                    sql = "UPDATE admin_details SET  password = %s WHERE email = %s"
                    cursor.execute(sql, (hashed_password,s_email))
                    connection.commit()
                    cursor.close()
                    flash("password updated successfully admin", "success")
                    return redirect(url_for('log'))  # Redirect to the login page
                
              
            flash("Account not found", "error")
            return redirect(url_for('forgotpwd'))  # Redirect to the login page


    except IntegrityError as e:
        flash("Account already available!", "error")
        return redirect(url_for('forgotpwd'))
    
    except Exception as e:
     
        flash(f"An error occurred: {traceback.format_exc()}", "error")
        return redirect(url_for('forgotpwd'))
    

#update user status
@app.route('/update_user_status/<string:email>/<string:action>', methods=['POST'])
def update_user_status(email, action):
    try:
        cursor = connection.cursor()
        if action == 'activate':
            status = 'active'
        elif action == 'deactivate':
            status = 'inactive'
        else:
            flash("Invalid action", "error")
            return redirect(url_for('manageUsers'))

        sql = "UPDATE student_details SET status = %s WHERE email = %s"
        cursor.execute(sql, (status, email))
        connection.commit()
        cursor.close()
        return redirect(url_for('displayUsers'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('manageUsers'))


#display users
@app.route('/displayUsers')
def displayUsers():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT email, index_no, username, password, semester, date, status FROM student_details")
        users_data = cursor.fetchall()
        cursor.close()
        return render_template('manageUser.html', users=users_data)
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('adminLogin'))



#view quiz
@app.route('/viewQuiz')
def viewQuiz():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT  qid,semester, subject, questions,answers,quiz_id FROM questions")
        quiz_data = cursor.fetchall()
        cursor.close()
        return render_template('manageQuiz.html', quizes=quiz_data)
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('manageQuiz'))
    


@app.route('/update_quiz_status/<string:qid>/<string:action>', methods=['POST'])
def update_quiz_status(qid, action):
    try:
        cursor = connection.cursor()
        if action == 'Delete':
            sql = "DELETE FROM questions WHERE qid= %s"
            cursor.execute(sql, (qid,))
            connection.commit()
            cursor.close()
            flash("Deleted Successfully!!!", "success")
            return redirect(url_for('viewQuiz'))  # Redirect after deletion
        
        elif action == 'Update':
            # Fetch the details of the question using the qid
            sql = "SELECT * FROM questions WHERE qid = %s"
            cursor.execute(sql, (qid,))
            question_details = cursor.fetchone()
            cursor.close()

            # Pass the question details to the updateQuestions.html template
            return render_template('updateQuestions.html', question_details=question_details)
        
        else:
            flash("Invalid action", "error")
            return redirect(url_for('viewQuiz'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('viewQuiz'))
    


@app.route('/updateQuestionsForm', methods=['POST'])
def updateQuestionsForm():
    try:
        cursor = connection.cursor()
        qid = request.form.get('qid')
        quiz_id = request.form.get('quizid')
        subject = request.form.get('name')
        semester = request.form.get('semester')
        question = request.form.get('q1')
        answer = request.form.get('q1a1')

        sql = "UPDATE questions SET semester = %s, subject = %s, questions = %s, answers = %s, quiz_id = %s WHERE qid = %s"
        cursor.execute(sql, (semester, subject, question, answer, quiz_id, qid))
        connection.commit()
        cursor.close()
        flash("Successfully Updated Question !!!")
        return redirect(url_for('viewQuiz'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('viewQuiz'))
    


#manage links 

@app.route('/manageLinks')
def manageLinks():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT  link_id,semester, subject, link,year,quiz_id,admin_email FROM link_details")
        link_data = cursor.fetchall()
        cursor.close()
        return render_template('manageLink.html', links=link_data)
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('manageLink'))
    


@app.route('/update_link_status/<string:link_id>/<string:action>', methods=['POST'])
def update_link_status(link_id, action):
    try:
        cursor = connection.cursor()
        if action == 'Delete':
            sql = "DELETE FROM link_details WHERE link_id= %s"
            cursor.execute(sql, (link_id,))
            connection.commit()
            cursor.close()
            flash("Deleted Successfully!!!", "success")
            return redirect(url_for('manageLinks'))  # Redirect after deletion
        
        elif action == 'Update':
            # Fetch the details of the question using the qid
            sql = "SELECT * FROM link_details WHERE link_id = %s"
            cursor.execute(sql, (link_id,))
            link_details = cursor.fetchone()
            cursor.close()

            # Pass the question details to the updateQuestions.html template
            return render_template('updatelink.html', link_details=link_details)
        
        else:
            flash("Invalid action", "error")
            return redirect(url_for('manageLinks'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('manageLinks'))
    


@app.route('/updateLinkForm', methods=['POST'])
def updateLinkForm():
    try:
        cursor = connection.cursor()
        link_id = request.form.get('link_id')
        old_link_id = request.form.get('old_link_id')
        link= request.form.get('link')
        subject = request.form.get('name')
        semester = request.form.get('sem')
        year=request.form.get('year')

        sql = "UPDATE link_details SET link_id=%s, semester = %s, subject = %s, link= %s, year= %s WHERE link_id= %s"
        cursor.execute(sql, (link_id,semester, subject,link,year,old_link_id))
        connection.commit()
        cursor.close()
        flash("Successfully Updated link details!!!")
        return redirect(url_for('manageLinks'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('manageLinks'))
    




@app.route('/quiz', methods=['GET'])
def quiz():
    try:
        cursor = connection.cursor()
        sql = "SELECT semester FROM student_details WHERE email = %s"
        cursor.execute(sql, (session.get('student'),))
        semester_row = cursor.fetchone()
        cursor.close()

        if semester_row:
            semester = semester_row[0]  # Extract the string value from the tuple
            if semester == "First Year First semester":
                return redirect(url_for('firstYearFirstSem'))
            elif semester == "First Year Second semester":
                return redirect(url_for('firstYearSecondSem'))
            elif semester == "Second Year First semester":
                return redirect(url_for('SecondYearFirstSem'))
            elif semester == "Second Year Second semester":
                return redirect(url_for('SecondYearSecondSem'))
            else:
                flash("Successfully Updated Question !!!")
                return redirect(url_for('viewQuiz'))
        else:
            flash("Semester information not found for the user.")
            return redirect(url_for('viewQuiz'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('viewQuiz'))
    






@app.route('/attemptQuizSubOne', methods=['GET'])
def attemptQuizSubOne():
   
    sub1 = request.args.get('subject')
   
    try:
        cursor = connection.cursor()
        sql = "SELECT semester FROM student_details WHERE email = %s"
        cursor.execute(sql, (session.get('student'),))
        semester_row = cursor.fetchone()

        if semester_row:
            semester = semester_row[0]  # Extract the string value from the tuple
            if semester == "First Year First semester":

                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("First Year First semester","sub1"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizFirstYearFirstSem.html', message=message)
                else:

                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub1' AND semester = 'First Year First semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub1' AND semester = 'First Year First semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub1)
            
            elif semester=="First Year Second semester":

                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("First Year Second semester","sub1"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizFirstYearSecondSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub1' AND semester = 'First Year Second semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub1' AND semester = 'First Year Second semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub1)
                
            elif semester=="Second Year First semester":
         
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("Second Year First semester","sub1"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizSecondYearFirstSem.html', message=message)
                else:

                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub1' AND semester = 'Second Year First semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub1' AND semester = 'Second Year First semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub1)
            
            elif semester=="Second Year Second semester":
                
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("Second Year Second semester","sub1"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizSecondYearSecondSem.html', message=message)
                else:
                     
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub1' AND semester = 'Second Year Second semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub1' AND semester = 'Second Year Second semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub1)
            
            


        else:
            flash("Semester information not found for the user.")
            return redirect(url_for('viewQuiz'))

    except Exception as e:
        print(e)
        flash("An error occurred while fetching questions.", "error")
        return redirect(url_for('viewQuiz'))
    finally:
        cursor.close()


@app.route('/loadDefaultStudentDashContent', methods=['GET'])
def loadDefaultStudentDashContent():
    
    cursor = connection.cursor(dictionary=True)

    # Assuming you have a way to identify the logged-in student,
    # let's say you have their ID stored in a session variable called student
    student_id = session.get('student')  # You need to implement this function

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query1 = "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query1, (student_id, "First Year First semester"))
    one = cursor.fetchall()

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query2 = "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query2, (student_id, "First Year Second semester"))
    two = cursor.fetchall()

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query3 = "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query3, (student_id, "Second Year First semester"))
    three = cursor.fetchall()

     # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query4= "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query4, (student_id, "Second Year Second semester"))
    four = cursor.fetchall()
    

    # Close MySQL connection
    cursor.close()
    

    # Pass the organized data to your HTML template for rendering
    return render_template('defaultStudentDashContent.html', one=one,two=two,three=three,four =four)


@app.route('/attemptQuizSubTwo', methods=['GET'])
def attemptQuizSubTwo():
    sub2 = request.args.get('subject')
    try:
        cursor = connection.cursor()
        sql = "SELECT semester FROM student_details WHERE email = %s"
        cursor.execute(sql, (session.get('student'),))
        semester_row = cursor.fetchone()

        if semester_row:
            semester = semester_row[0]  # Extract the string value from the tuple
            if semester == "First Year First semester":
                
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("First Year First semester","sub2"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizFirstYearFirstSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub2' AND semester = 'First Year First semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub2' AND semester = 'First Year First semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub2)
            
            elif semester=="First Year Second semester":
                
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("First Year Second semester","sub2"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizFirstYearSecondSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub2' AND semester = 'First Year Second semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub2' AND semester = 'First Year Second semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub2)
            
            elif semester=="Second Year First semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("Second Year First semester","sub2"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizSecondYearFirstSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub2' AND semester = 'Second Year First semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub2' AND semester = 'Second Year First semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub2)
            
            elif semester=="Second Year Second semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("Second Year Second semester","sub2"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizSecondYearSecondSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub2' AND semester = 'Second Year Second semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub2' AND semester = 'Second Year Second semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub2)
            
            


        else:
            flash("Semester information not found for the user.")
            return redirect(url_for('viewQuiz'))

    except Exception as e:
        print(e)
        flash("An error occurred while fetching questions.", "error")
        return redirect(url_for('viewQuiz'))
    finally:
        cursor.close()


    

@app.route('/attemptQuizSubThree', methods=['GET'])
def attemptQuizSubThree():
    sub3 = request.args.get('subject')
    try:
        cursor = connection.cursor()
        sql = "SELECT semester FROM student_details WHERE email = %s"
        cursor.execute(sql, (session.get('student'),))
        semester_row = cursor.fetchone()

        if semester_row:
            semester = semester_row[0]  # Extract the string value from the tuple
            if semester == "First Year First semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("First Year First semester","sub3"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizFirstYearFirstSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub3' AND semester = 'First Year First semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub3' AND semester = 'First Year First semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub3)
            
            elif semester=="First Year Second semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("First Year Second semester","sub3"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizFirstYearSecondSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub3' AND semester = 'First Year Second semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub3' AND semester = 'First Year Second semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub3)
            
            elif semester=="Second Year First semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("Second Year First semester","sub3"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizSecondYearFirstSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub3' AND semester = 'Second Year First semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub3' AND semester = 'Second Year First semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub3)
            
            elif semester=="Second Year Second semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("Second Year Second semester","sub3"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizSecondYearSecondSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub3' AND semester = 'Second Year Second semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub3' AND semester = 'Second Year Second semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub3)
            
            


        else:
            flash("Semester information not found for the user.")
            return redirect(url_for('viewQuiz'))

    except Exception as e:
        print(e)
        flash("An error occurred while fetching questions.", "error")
        return redirect(url_for('viewQuiz'))
    finally:
        cursor.close()
    



@app.route('/attemptQuizSubFour', methods=['GET'])
def attemptQuizSubFour():
    sub4 = request.args.get('subject')
    try:
        cursor = connection.cursor()
        sql = "SELECT semester FROM student_details WHERE email = %s"
        cursor.execute(sql, (session.get('student'),))
        semester_row = cursor.fetchone()

        if semester_row:
            semester = semester_row[0]  # Extract the string value from the tuple
            if semester == "First Year First semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("First Year First semester","sub4"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizFirstYearFirstSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub4' AND semester = 'First Year First semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub4' AND semester = 'First Year First semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub4)
            
            elif semester=="First Year Second semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("First Year Second semester","sub4"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizFirstYearSecondSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub4' AND semester = 'First Year Second semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub4' AND semester = 'First Year Second semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub4)
            
            elif semester=="Second Year First semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("Second Year First semester","sub4"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizSecondYearFirstSemester.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub4' AND semester = 'Second Year First semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub4' AND semester = 'Second Year First semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub4)
            
            elif semester=="Second Year Second semester":
                sqlAttempt = "SELECT attempts FROM attempt_details WHERE semester = %s AND subject=%s"
                cursor.execute(sqlAttempt, ("Second Year Second semester","sub4"))
                semesterAttempt = cursor.fetchone()
             
                if semesterAttempt is not None and semesterAttempt[0] >= 3:
                    message = "Maximum Attempts reached"
                    return render_template('quizSecondYearSecondSem.html', message=message)
                else:
                    sql = "SELECT questions, answers FROM questions WHERE subject = 'sub4' AND semester = 'Second Year Second semester' ORDER BY RAND() LIMIT 10"
                    cursor.execute(sql)
                    question_data = cursor.fetchall()
                    questions = []
                    answers = []
                    for question, correct_answer in question_data:
                        other_cursor = connection.cursor()
                        sql = "SELECT answers FROM questions WHERE subject = 'sub4' AND semester = 'Second Year Second semester' AND answers != %s ORDER BY RAND() LIMIT 2"
                        other_cursor.execute(sql, (correct_answer,))
                        other_answers = [row[0] for row in other_cursor.fetchall()]
                        other_cursor.close()
                        all_answers = [correct_answer] + other_answers
                        random.shuffle(all_answers)
                        questions.append(question)
                        answers.append(all_answers)
                    return render_template('attemptQuiz.html', questions=questions, answers=answers,sub=sub4)
                
            


        else:
            flash("Semester information not found for the user.")
            return redirect(url_for('viewQuiz'))

    except Exception as e:
        print(e)
        flash("An error occurred while fetching questions.", "error")
        return redirect(url_for('viewQuiz'))
    finally:
        cursor.close()
    
   

@app.route('/quizSubmit', methods=['POST'])
def quizSubmit():
    # Initialize variables to store the score and total questions
    subject=request.form.get('subject')
    score = 0
    total_questions = 10  # Total questions are always 10
    questions = [request.form.get('question{}'.format(i+1)) for i in range(total_questions)]
    selected_answers = [request.form.get('answer{}'.format(i)) for i in range(total_questions)]

    # Loop through the questions and retrieve their corresponding answers from the database
    for question_text, selected_answer in zip(questions, selected_answers):
        # Execute a SQL query to retrieve the answer for the current question
        cursor = connection.cursor()
        cursor.execute("SELECT answers FROM questions WHERE questions=%s", (question_text,))
        result = cursor.fetchone()
        if result:
            # Retrieve the correct answer from the database
            correct_answer = result[0]
            print("Selected Answer:", selected_answer)
            print("Correct Answer:", correct_answer)
            # If the selected answer matches the correct answer
            if selected_answer == correct_answer:
                # Increment the score variable by 1
                score += 1
        else:
            print("Question not found in the database:", question_text)
        # Consume all results before closing the cursor
        cursor.fetchall()
        # Close the cursor
        cursor.close()


    # Calculate the percentage
    percentage = (score / total_questions) * 100
    insertMarks(score,subject)
    # Render the result.html template with the score and percentage
    return render_template('result.html', score=score, percentage=percentage)


def insertMarks(score,subject):
    global attempts
    attempts=0
    try:
        cursor = connection.cursor()

        # Retrieve email of the logged-in user
        email = session.get('student')

        # Retrieve index number using email
        cursor.execute("SELECT index_no, semester FROM student_details WHERE email = %s", (email,))
        rows = cursor.fetchall()
        if rows:
            index_no = rows[0][0]  # Assuming only one row is expected
            semester = rows[0][1]
        else:
            flash("User not found.", "error")
            return redirect(url_for('viewQuiz'))
        
       
           
        cursor.execute("SELECT quiz_id FROM quiz WHERE semester = %s AND subject = %s", (semester, subject))
        
        rows = cursor.fetchall()
        if rows:
            quiz_id = rows[0][0]  # Assuming only one row is expected
        else:
            flash("Quiz not found for this semester and subject.", "error")
            return redirect(url_for('viewQuiz'))
            
        # Calculate marks
        marks = score * 10
        grade = 'W' if marks < 35 else 'S' if marks < 55 else 'C' if marks < 65 else 'B' if marks < 75 else 'A'
        
        # Insert marks into the database
        sql_marks = "INSERT INTO quiz_marks(email, index_no, semester, subject, marks, grade, quiz_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_marks, (email, index_no, semester, subject, marks, grade, quiz_id))
        attempts=attempts+1
      
        sql_check_record = "SELECT attempts FROM attempt_details WHERE email = %s AND quiz_id = %s AND semester = %s AND subject = %s"
        cursor.execute(sql_check_record, (session.get('student'), quiz_id, semester, subject))
        existing_record = cursor.fetchone()

        if existing_record:
            # If a record exists, increment the attempts field value by one
            current_attempts = existing_record[0]
            new_attempts = current_attempts + 1
            
            # Update the record
            sql_update_attempts = "UPDATE attempt_details SET attempts = %s WHERE email = %s AND quiz_id = %s AND semester = %s AND subject = %s"
            cursor.execute(sql_update_attempts, (new_attempts, session.get('student'), quiz_id, semester, subject))
        else:
            # If no record exists, insert a new record with attempts set to 1
            sql_insert_record = "INSERT INTO attempt_details(email, quiz_id, semester, subject, attempts) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql_insert_record, (session.get('student'), quiz_id, semester, subject, 1))  # Assuming attempts start from 1
                

        connection.commit()
            
    except Exception as e:
        flash("An error occurred while inserting marks.", "error")
        return redirect(url_for('viewQuiz'))
    finally:
        cursor.close()




@app.route('/generateQuizReport',  methods=['GET'])
def generateQuizReport():
    cursor = connection.cursor(dictionary=True)

    # Assuming you have a way to identify the logged-in student,
    # let's say you have their ID stored in a session variable called student
    student_id = session.get('student')  # You need to implement this function

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query1 = "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query1, (student_id, "First Year First semester"))
    one = cursor.fetchall()

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query2 = "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query2, (student_id, "First Year Second semester"))
    two = cursor.fetchall()

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query3 = "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query3, (student_id, "Second Year First semester"))
    three = cursor.fetchall()

     # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query4= "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query4, (student_id, "Second Year Second semester"))
    four = cursor.fetchall()


    # Close MySQL connection
    cursor.close()
    

    # Pass the organized data to your HTML template for rendering
    return render_template('report.html', one=one,two=two,three=three,four =four)


#default admin dashboard
@app.route('/loadDefaultAdminDashContent',  methods=['GET'])
def loadDefaultAdminDashContent():
    cursor = connection.cursor(dictionary=True)

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query1 = "SELECT index_no,subject, marks, grade FROM quiz_marks WHERE semester = %s"
    cursor.execute(query1, ("First Year First semester",))
    one = cursor.fetchall()

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query2 = "SELECT index_no,subject, marks, grade FROM quiz_marks WHERE semester = %s"
    cursor.execute(query2, ("First Year Second semester",))
    two = cursor.fetchall()

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query3 = "SELECT index_no, subject, marks, grade FROM quiz_marks WHERE semester = %s"
    cursor.execute(query3, ("Second Year First semester",))
    three = cursor.fetchall()

     # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query4= "SELECT index_no,subject, marks, grade FROM quiz_marks WHERE semester = %s"
    cursor.execute(query4, ("Second Year Second semester",))
    four = cursor.fetchall()
    

    # Close MySQL connection
    cursor.close()
    

    # Pass the organized data to your HTML template for rendering
    return render_template('defaultAdminDashContent.html', one=one,two=two,three=three,four =four)



@app.route('/loadAnalysis',  methods=['GET'])
def loadAnalysis():
     
    cursor = connection.cursor(dictionary=True)

    # Assuming you have a way to identify the logged-in student,
    # let's say you have their ID stored in a session variable called student
    student_id = session.get('student')  # You need to implement this function

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query1 = "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query1, (student_id, "First Year First semester"))
    one = cursor.fetchall()

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query2 = "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query2, (student_id, "First Year Second semester"))
    two = cursor.fetchall()

    # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query3 = "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query3, (student_id, "Second Year First semester"))
    three = cursor.fetchall()

     # Fetch quiz details for the logged-in student based on semesters using MySQL query
    query4= "SELECT index_no, semester, subject, marks, grade FROM quiz_marks WHERE email = %s AND semester = %s"
    cursor.execute(query4, (student_id, "Second Year Second semester"))
    four = cursor.fetchall()
    

    # Close MySQL connection
    cursor.close()
    

    # Pass the organized data to your HTML template for rendering
    return render_template('analysis.html', one=one,two=two,three=three,four =four)




@app.route('/loadOverAllAnalysis',  methods=['GET'])
def loadOverAllAnalysis():
    cursor = connection.cursor(dictionary=True)

    # List of semesters and subjects
    semesters = ["First Year First semester", "First Year Second semester", "Second Year First semester", "Second Year Second semester"]
    subjects = ["sub1", "sub2", "sub3", "sub4"]  # Update with your actual subject names

    # Dictionary to store failure counts for each subject in each semester
    failure_counts = {semester: {} for semester in semesters}

    # Iterate through each semester
    for semester in semesters:
        for subject in subjects:
            query = "SELECT COUNT(*) AS count FROM quiz_marks WHERE semester = %s AND subject = %s AND (grade = 'W' OR marks < %s)"
            cursor.execute(query, (semester, subject, 35))
            result = cursor.fetchone()
            failure_counts[semester][subject] = result["count"]

    cursor.close()

    # Convert the failure_counts dictionary to JSON format
    failure_counts_json = json.dumps(failure_counts)
    print(failure_counts_json)

    # Pass the failure counts JSON to the HTML template for rendering
    return render_template('overAllAnalysis.html', failure_counts_json=failure_counts_json)



# default admin dashboard
@app.route('/search', methods=['GET', 'POST'])
def search():
    no_results = False  # Initialize the no_results flag

    if request.method == 'GET':
        search_data = request.args.get('search_data')

        cursor = connection.cursor(dictionary=True)

        # Fetch quiz details for the logged-in student based on semesters using MySQL query
        query1 = "SELECT index_no, subject, marks, grade FROM quiz_marks WHERE semester = %s AND index_no = %s or subject = %s"
        cursor.execute(query1, ("First Year First semester", search_data, search_data))
        one = cursor.fetchall()

        # Fetch quiz details for the logged-in student based on semesters using MySQL query
        query2 = "SELECT index_no, subject, marks, grade FROM quiz_marks WHERE semester = %s AND index_no = %s or subject = %s"
        cursor.execute(query2, ("First Year Second semester", search_data, search_data))
        two = cursor.fetchall()

        # Fetch quiz details for the logged-in student based on semesters using MySQL query
        query3 = "SELECT index_no, subject, marks, grade FROM quiz_marks WHERE semester = %s AND index_no = %s or subject = %s"
        cursor.execute(query3, ("Second Year First semester", search_data, search_data))
        three = cursor.fetchall()

        # Fetch quiz details for the logged-in student based on semesters using MySQL query
        query4 = "SELECT index_no, subject, marks, grade FROM quiz_marks WHERE semester = %s AND index_no = %s or subject = %s"
        cursor.execute(query4, ("Second Year Second semester", search_data, search_data))
        four = cursor.fetchall()

        # Close MySQL connection
        cursor.close()

        # Check if any of the fetched results are empty
        if not (one and two and three and four):
            # Set the no_results flag to True
            no_results = True
            return render_template('defaultAdminDashContent.html', no_results=no_results)

        else :
            # Pass the organized data and the no_results flag to your HTML template for rendering
            return render_template('defaultAdminDashContent.html', one=one, two=two, three=three, four=four, no_results=no_results)
       

    # Handling GET requests
    return render_template('defaultAdminDashContent.html', one=[], two=[], three=[], four=[], no_results=no_results)



@app.route('/feed', methods=['POST'])
def feed():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    cursor = connection.cursor()
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO feedback_details(email, uname, comments) VALUES (%s, %s, %s)"
        val = (email, name, message)
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()
        
       
        return redirect(url_for('index'))
        
    except Error as e:
        print(f"Error: {e}")
        return "There was an error processing your request. Please try again later.", 500

   



        


@app.route('/quizGenerate', methods=['POST'])
def quizGenerate():  
    try:
        # Extract quiz details from the form data
        quiz_id = request.form.get('quizid')
        subject_name = request.form.get('name')
        semester = request.form.get('semester')
        year = request.form.get('year')
        
        cursor = connection.cursor()

        # Generate a unique qid
        linkId= ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        print(linkId)
        base_url = "https://66b3-103-247-51-28.ngrok-free.app/quiz/"
        quiz_url = f"{base_url}{year.replace(' ', '')}/{semester.replace(' ', '')}/{subject_name}/{quiz_id}"


          # Insert quiz details into the quiz table
        sql_quiz = "INSERT INTO quiz(quiz_id,semester, subject, year) VALUES (%s, %s, %s, %s)"
        val_quiz = (quiz_id, semester, subject_name, year)
        cursor.execute(sql_quiz, val_quiz)

          # Insert quiz details into the quiz table
        sql_link = "INSERT INTO link_details(link_id,semester, subject,link,year,quiz_id,admin_email) VALUES (%s, %s, %s, %s,%s,%s,%s)"
        val_link = (linkId, semester, subject_name,quiz_url ,year,quiz_id,session.get('admin'))
        cursor.execute(sql_link, val_link)


        # Extract questions and answers
        for i in range(1, 21):
            question = request.form.get(f'q{i}')
            answer = request.form.get(f'q{i}a1').lower()
             # Generate a unique qid
            qid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

            # Insert each question and answer into the questions table
            sql_question = "INSERT INTO questions( qid, semester, subject, questions, answers,quiz_id) VALUES (%s, %s, %s, %s, %s, %s)"
            val_question = ( qid, semester, subject_name, question, answer,quiz_id)
            cursor.execute(sql_question, val_question)

        
        # Commit the transaction
        connection.commit()
        cursor.close()
        

        flash("Quiz Generated Successfully!", "success")
        return render_template('generateQuiz.html', quiz_url=quiz_url)


 

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('generateQuiz'))





if __name__ == '__main__':
    app.run(debug=True)