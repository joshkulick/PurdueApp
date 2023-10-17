from flask import Flask, render_template, request, redirect, url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = 'Secret123'
# Create a serializer
s = URLSafeTimedSerializer(app.secret_key)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'

#MAIL INFORMATION
# Automatic Email Config for Reset Password
# Setting it to False disables Flask-SQLAlchemy's modification tracking system
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'PurdueCapstone@gmail.com'
app.config['MAIL_PASSWORD'] = 'vbla evma tqpz umof'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

#DATABASE INFORMATION
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    team_number = db.Column(db.Integer, nullable=False)

#FILE UPLOAD INFORMATION
UPLOAD_FOLDER = os.getcwd() + r'/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Functions

#If the user is not logged in they will not be able to access certain pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#Web Decoration
@app.route('/home')
@login_required
def home():
    return render_template('HomePage.html')

@app.route('/logged_out')
def logged_out():
    session.pop('user_id', None)
    return render_template('LoggedOutPage.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Email is required.', 'danger')
            return redirect(url_for('forgot_password'))
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with that email.', 'danger')
            return redirect(url_for('forgot_password'))
        
        # Sending the reset email
        msg = Message("Password Reset Request", sender="PurdueCapstone@gmail.com", recipients=[email])
        
        token = s.dumps(user.email, salt='password-reset-salt')
        reset_url = url_for('reset_password', token=token, _external=True)

        msg.body = f"Click the following link to reset your password: {reset_url}"
        mail.send(msg)
        flash('Password reset link sent to your email.', 'success')
        return redirect(url_for('login'))
    else:
        # This is the part that was missing. Return a template for the GET request.
        return render_template('ForgotPassword.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token is valid for 1 hour
    except:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('Both fields are required.', 'danger')
            return render_template('ResetPassword.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('ResetPassword.html')

        # Assuming you have a method to update the user's password
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = password  # In the future I need to hash the password or safety
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))
        else:
            flash('An error occurred. Please try again.', 'danger')
            return render_template('ResetPassword.html')

    return render_template('ResetPassword.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(request.form)
    if request.method == 'POST':
        #Get information from form
        email = request.form.get('email')
        password = request.form.get('password')
        
        #Checks to make sure that the user actually filled out the form
        if email and password:
            email = email.lower()
            user = User.query.filter_by(email=email).first()
        else:
            # Handle the case where email is a Nonetype (nothing populated)
            flash('Both Email and Password are required.', 'danger')
            return redirect(url_for('login'))
        
        #Validation
        print(f"Email from form: {email}")
        print(f"Password from form: {password}")

        if user and user.password == password:  # Note: This is a simple check. Hashed Password future state?
            # Log the user in (you might want to use Flask-Login for session management)
            session['user_id'] = user.id
            print("Logged in succesfully")
            return redirect(url_for('home'))  # home route
        else:
            flash('Invalid credentials. Please sign up if you do not have an account.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('LoginPage.html')

@app.route('/prf_status')
@login_required
def prf_status():
    return render_template('PrfStatus.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        team_number = request.form['tnum']

        if password != confirm_password:
            # The passwords do not match, return an error message
            return "Passwords do not match", 400

        # Check if a user with the given email address already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # A user with the given email address already exists, return an error message
            return "A user with this email address already exists", 400
        
        new_user = User(email=email, password=password, team_number=team_number)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))  # Redirect to the login page after successful registration
    return render_template('RegistrationPage.html')


#PRFSub Endpoints
@app.route('/prfsub')
@login_required
def prfsub():
    return render_template('prfsub.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('prfsub'))
    file = request.files['file']

    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('prfsub'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File successfully uploaded')
        return redirect(url_for('prfsub'))

    else:
        flash('Allowed file types are .xlsx')
        return redirect(url_for('prfsub'))
    
#Maintenence Endpoints
@app.route('/clear_database')
@login_required
def clear_database():
    try:
        # Delete all rows in the User table
        num_rows_deleted = db.session.query(User).delete()
        db.session.commit()
        return f"Successfully deleted {num_rows_deleted} rows."
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {str(e)}"

@app.route('/show_users')
@login_required
def show_users():
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Password: {user.password}, Team Number: {user.team_number}")
    return "Users printed in console", 200

if __name__ == '__main__':
    app.run(debug=True)