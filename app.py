from flask import Flask, render_template, request, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.secret_key = 'Secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'

# Setting it to False disables Flask-SQLAlchemy's modification tracking system
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    team_number = db.Column(db.Integer, nullable=False)


@app.route('/home')
def home():
    return render_template('HomePage.html')

@app.route('/logged_out')
def logged_out():
    return render_template('LoggedOutPage.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Handle the form submission for resetting the password
        # For example, you can send an email with a reset link to the user
        email = request.form.get('email')
        if not email:
            flash('Email is required.', 'danger')
            return redirect(url_for('forgot_password'))
        
        # Check if the email exists in the database
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with that email.', 'danger')
            return redirect(url_for('forgot_password'))
        
        # Here, you can send an email to the user with a password reset link
        # (You'll need to integrate with an email service for this)
        
        flash('Password reset link sent to your email.', 'success')
        return redirect(url_for('login'))
    
    return render_template('ForgotPassword.html')

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
            print("Logged in succesfully")
            return redirect(url_for('home'))  # home route
        else:
            flash('Invalid credentials. Please sign up if you do not have an account.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('LoginPage.html')

@app.route('/prf_status')
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

@app.route('/clear_database')
def clear_database():
    try:
        # Delete all rows in the User table
        num_rows_deleted = db.session.query(User).delete()
        db.session.commit()
        return f"Successfully deleted {num_rows_deleted} rows."
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {str(e)}"

@app.route('/prfsub')
def prfsub():
    return render_template('prfsub.html')

@app.route('/show_users')
def show_users():
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Password: {user.password}, Team Number: {user.team_number}")
    return "Users printed in console", 200

if __name__ == '__main__':
    app.run(debug=True)