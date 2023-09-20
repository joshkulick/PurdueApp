from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'

# Setting it to False disables Flask-SQLAlchemy's modification tracking system
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    team_number = db.Column(db.Integer, nullable=False)


@app.route('/')
def home():
    return render_template('HomePage.html')

@app.route('/logged_out')
def logged_out():
    return render_template('LoggedOutPage.html')

@app.route('/login')
def login():
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