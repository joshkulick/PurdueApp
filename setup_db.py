from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress a warning message

db = SQLAlchemy(app)

# Define the Items table
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_number = db.Column(db.Integer, nullable=False)
    team_name = db.Column(db.String(255), nullable=False)

# This function will create the table in the database
def create_table():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        create_table()
