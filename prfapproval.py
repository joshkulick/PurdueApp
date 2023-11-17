from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)


# Assuming you have already set up the Flask app and initialized SQLAlchemy as 'db'

def retrieve_submission_data():
    # Fetch the latest submission data from the database
    latest_submission = team_procurement_detail.query.order_by(team_procurement_detail.id.desc()).first()
    print("in retrieving")
    # Check if there is any data available
    if latest_submission:
        submission_time = latest_submission.file_last_modified.strftime('%Y-%m-%d %H:%M')
        file_name = latest_submission.file_last_modified # Replace 'file_name' with the appropriate field name

        return submission_time, file_name
    
    # If there's no data in the database, return default values or handle the case accordingly
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Default File.xlsx"
@app.route('/PrfStatus')
def display_status():
    submission_time, file_name = retrieve_submission_data()
    print("in disp")
    # Render the HTML template and pass the data to it
    return render_template('PrfStatus.html', submission_time=submission_time , file_name=file_name)