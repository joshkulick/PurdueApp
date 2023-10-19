import pandas as pd
from sqlalchemy import create_engine

# MySQL database credentials
DB_USERNAME = "capstonepro"
DB_PASSWORD = "blowfish-orange-840"
DB_HOST = "mysql.ecn.purdue.edu"
DB_NAME = "capstonepro"

#HTML Url for file
HTML_URL = "file:///Users/shashwat/Desktop/PurdueApp/PurdueApp/templates/prfsub.html"

# Parse the Excel file into a DataFrame
try:
    dfs = pd.read_html(HTML_URL, header=0)
    if not dfs:
        raise Exception("No tables found in the HTML page.")
except Exception as e:
    print("Error:", str(e))
    exit(1)

# Storage into table 
data = dfs[0]

# Create a connection to your MySQL database
engine = create_engine(f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Store the data in the MySQL database
try:
    data.to_sql('your_table_name', con=engine, if_exists='replace', index=False)
    print("Data has been successfully stored in the MySQL database.")
except Exception as e:
    print("Error:", str(e))

# Close the database connection
engine.dispose()
