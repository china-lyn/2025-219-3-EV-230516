# Import necessary modules
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import plotly.express as px

from flask import Flask, render_template

# --- FORM ---
# Generate bar chart for hour of sleep and activty from user input, sorted by gender
def bar_sleepAct(forms):
    data = {
        'Male': {
            'sleep': [],
            'activity': []
        },
       
        'Female': {
            'sleep': [],
            'activity': []
        }
    }
   
    for value in forms.values():
        data[value['Gender']]['sleep'].append(value['Hours of sleep'])
        data[value['Gender']]['activity'].append(value['Daily Activity (mins)'])
       
    male_sleep = data['Male']['sleep']
    female_sleep = data['Female']['sleep']
    male_act = data['Male']['activity']
    female_act = data['Female']['activity']
   
    if not all([male_sleep, female_sleep, male_act, female_act]):
        return '<h2>Cannot display chart. Values missing from firebase form!</h2>'
   
    male_sleep_avg = sum(male_sleep) / len(male_sleep)
    female_sleep_avg = sum(female_sleep) / len(female_sleep)
    male_exer_avg = sum(male_act) / len(male_act) / 60 # Minutes to hours
    female_exer_avg = sum(female_act) / len(female_act) / 60
   
    chart = {
        'Gender': ['Male',  'Male',     'Female', 'Female'],
        'Data':   ['Sleep', 'Exercise', 'Sleep',  'Exercise'],
        'Hours':  [male_sleep_avg, male_exer_avg, female_sleep_avg, female_exer_avg]
    }
   
    df = pd.DataFrame(chart)
    bar = px.bar(df, color='Gender', y='Hours', x='Data', title='Sleep and Activity Hours by Gender', barmode='group', color_discrete_sequence=px.colors.qualitative.Safe)
    bar.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    return bar.to_html(full_html=False, include_plotlyjs='cdn')

# Generate pie chart for % of different ages from data input
def pie_age(forms):
    ages = []
    count = []
   
    for value in forms.values():
        age = value['Age']
        ages.append(age)
        count.append('1')
       
    pieData = {
        'Count': count,
        'Age': ages
    }
   
    df = pd.DataFrame(pieData)
    pie = px.pie(df, names='Age', values='Count', title='Pie Chart of Ages', color='Age', color_discrete_sequence=px.colors.qualitative.Pastel1)
    pie.update_layout(legend_title=dict(text="Ages"), paper_bgcolor='rgba(0, 0, 0, 0)')
    return pie.to_html(full_html=False, include_plotlyjs='cdn')
 
# --- RECOMMENDATIONS ---
 
# Calculate average hours of sleep under each occupation in form of a dictionary
# SLEEP HOURS FOR JOB
def job_sleep(data):
    jobs_sleep = {}
   
    for category in data:
        job = category['Occupation']
        sleephrs = category['Sleep Duration']
        if not jobs_sleep.get(job):
            jobs_sleep[job] = [sleephrs]
        else:
            jobs_sleep[job].append(sleephrs)
           
    avgs = {}
    for job in jobs_sleep:
        avg = round(sum(jobs_sleep[job]) / len(jobs_sleep[job]), 2)
        avgs[job] = avg
       
    
    # Didn't end up using these values!
    # Key with max value
    max_key = max(avgs, key=avgs.get)
    max_value = avgs[max_key]
   
    # Key with min value
    min_key = min(avgs, key=avgs.get)
    min_value = avgs[min_key]
    #print('Max:', max_key, max_value)
    #print('Min:', min_key, min_value)
    return avgs


# Calculate the average daily steps under each BMI category
# STEPS FOR BMI 
def bmi_steps(data):
    bmi_steps = {}
   
    for category in data:
        bmi = category['BMI Category']
        #actMins = category['Physical Activity (mins)'] # Decided not to include this value
        dailySteps = category['Daily Steps']
        if not bmi_steps.get(bmi):
            bmi_steps[bmi] = [dailySteps]
        else:
            bmi_steps[bmi].append(dailySteps)
           
    avgs = {}
    for bmi in bmi_steps:
        avg = sum(bmi_steps[bmi]) // len(bmi_steps[bmi])
        avgs[bmi] = avg
       
    return avgs

# --- FLASK ---

app = Flask(__name__)

# Routes
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/form.html', methods=['GET', 'POST'])
def form():
    formref = db.reference('/Forms') # Reference to 'Forms' of database
    forms = formref.get()
    print(forms)
    pie_chart = pie_age(forms)
    bar_chart = bar_sleepAct(forms)
    return render_template(
        'form.html',
        bar_chart=bar_chart,
        pie_chart=pie_chart
    )

@app.route('/recommendations.html')
def recommendations():
    ref = db.reference('/Dataset') # Reference to 'Dataset' of database
    data = ref.get()
    jobSleep = job_sleep(data)
    bmiSteps = bmi_steps(data)
    return render_template(
        'recommendations.html',
        job_sleep=jobSleep,
        bmi_steps=bmiSteps
    )
 
if __name__ == '__main__':
    # Load credentials from json file on disk
    cred = credentials.Certificate("firebase-admin.json")
    # Connect and initialise firebase instance
    firebase_admin.initialize_app(cred, {'databaseURL':'https://lc-sandbox-c942a-default-rtdb.europe-west1.firebasedatabase.app/'})
   
    app.run(host='0.0.0.0', port=5001, debug=False)