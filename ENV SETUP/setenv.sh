#!/bin/bash

# Set Environment Variables Script

#Make it executable: Run chmod +x setenv.sh to make the script executable.
#Execute the script: Run ./setenv.sh to set the environment variables.
#Verification: After execution, verify the variables by typing echo $SECRET_KEY or any other variable name.

# Define environment variable values
SECRET_KEY='Secret123'
DATABASE_URL='mysql+pymysql://capstonepro:blowfish-orange-840@mysql.ecn.purdue.edu/capstonepro'
MAIL_USERNAME='PurdueCapstone@gmail.com'
MAIL_PASSWORD='vbla evma tqpz umof'

# Write to .bashrc or .bash_profile
echo "export SECRET_KEY='$SECRET_KEY'" >> ~/.bashrc
echo "export DATABASE_URL='$DATABASE_URL'" >> ~/.bashrc
echo "export MAIL_USERNAME='$MAIL_USERNAME'" >> ~/.bashrc
echo "export MAIL_PASSWORD='$MAIL_PASSWORD'" >> ~/.bashrc

echo "Environment variables have been set."

# Reload .bashrc or .bash_profile
source ~/.bashrc
