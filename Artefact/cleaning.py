# Clean dataset and upload to Firebase.
# Also save cleaned data as new csv file
 
# Import the modules needed
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Read the csv file in as a dataframe preserving 'None' values
sleepData = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv', keep_default_na=False)
# 'keep_default_na=False' means that when a value is 'None' it keeps it as 'None'

# Removing and replacing unnecessary data
# Dataset inconsistent for weight field using both
# 'Normal' and 'Normal Weight'. Convert all to 'Normal'.
sleepData = sleepData.replace('Normal Weight', 'Normal')
sleepData = sleepData.replace('Salesperson', 'Sales Representative')

# Rename confusing fields
sleepData = sleepData.rename(columns={'Physical Activity Level': 'Physical Activity (mins)'})

# Remove unused fields
sleepData = sleepData.drop(columns = 'Person ID')
sleepData = sleepData.drop(columns = 'Blood Pressure')

# Save cleaned data as a csv file WITHOUT the numbers in index
sleepData.to_csv('Cleaned.csv', index=False)
 
# Save data as a dictionary by rows where each person is own dictionary
dataDict = sleepData.to_dict(orient='index')
 
# Upload info to database
cred = credentials.Certificate("firebase-admin.json")
firebase_admin.initialize_app(cred, {'databaseURL':'https://lc-sandbox-c942a-default-rtdb.europe-west1.firebasedatabase.app/'})

#print(dataDict)
ref = db.reference('/Dataset/') # Reference to root node of database
ref.set(dataDict)
print('Done')