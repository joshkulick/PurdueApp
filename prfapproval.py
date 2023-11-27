from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect,text

# Connecting to DB
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress a warning message

db = SQLAlchemy(app)

# Get Data
@app.route('/getAdminData', methods=['GET'])
def getAdminData():
    """ query = 'SELECT * FROM user'
    result = db.session.execute(query)

    df = pd.DataFrame()
    for data in result:
        df2 = pd.DataFrame(list(data)).T
        df = pd.concat([df, df2])

    return df.to_html('templates/sql-data.html') """
    query = 'SELECT * FROM user'
    result = db.engine.execute(query)

    # Process the result into a list of dictionaries
    users = [dict(row) for row in result]

    return render_template('sql-data.html', users=users)