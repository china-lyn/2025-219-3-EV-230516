# PROCESS DATA AND GENERATE CHARTS
import pandas as pd
import plotly.express as px # generating graphs

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


# --- Generate 3 pie charts for BMI of people: overall, with sleep apnea and with insomnia ---

def pie_BMIs(data):
    # Initialise counts for each weight category by sleep disorder
    normCount = 0
    overCount = 0
    obeseCount = 0
 
    normCountAp = 0
    overCountAp = 0
    obeseCountAp = 0

    normCountIn = 0
    overCountIn = 0
    obeseCountIn = 0


    for value in data:
        if value['BMI Category'] == 'Normal':
            normCount += 1
            if value['Sleep Disorder'] == 'Sleep Apnea':
                normCountAp += 1
            elif value['Sleep Disorder'] == 'Insomnia':
                normCountIn += 1
               
        elif value['BMI Category'] == 'Overweight':
            overCount += 1
            if value['Sleep Disorder'] == 'Sleep Apnea':
                    overCountAp += 1
            elif value['Sleep Disorder'] == 'Insomnia':
                    overCountIn += 1
               
        elif value['BMI Category'] == 'Obese':
            obeseCount += 1
            if value['Sleep Disorder'] == 'Sleep Apnea':
                obeseCountAp += 1
            elif value['Sleep Disorder'] == 'Insomnia':
                obeseCountIn += 1
        else:
            print('Warning, unrecognised category:', value['BMI Category'])
               
    # Input all data for the chart
    pieData = {
        'Count': [normCount, overCount, obeseCount],
        'Category': ['Normal', 'Overweight', 'Obese']
    }
   
    pieDataAp = {
        'Count': [normCountAp, overCountAp, obeseCountAp],
        'Category': ['Normal', 'Overweight', 'Obese']
    }
   
    pieDataIn = {
        'Count': [normCountIn, overCountIn, obeseCountIn],
        'Category': ['Normal', 'Overweight', 'Obese']
    }

    # Convert pieData to a dataframe for plotly use
    bmiDf = pd.DataFrame(pieData)
    bmiApDf = pd.DataFrame(pieDataAp)
    bmiInDf = pd.DataFrame(pieDataIn)

    # Overall BMIs
    print('Generating BMI pie chart')
    pie = px.pie(bmiDf, names='Category', values='Count', title='BMI', color='Category', color_discrete_sequence=px.colors.qualitative.Pastel1)
    pie.update_layout(legend_title=dict(text="BMIs"), paper_bgcolor='rgba(0, 0, 0, 0)')
    print('Writing BMI.svg file')
    pie.write_image('BMI.svg') # Write chart to SVG file
    print('Done')
   
    # BMI and sleep apnea
    print('Generating BMI apnea pie chart')
    pieAp = px.pie(bmiApDf, names='Category', values='Count', title='BMI of people with Sleep Apnea', color='Category', category_orders={'Category': ['Normal', 'Overweight', 'Obese']}, color_discrete_sequence=px.colors.qualitative.Pastel1)
    pieAp.update_layout(legend_title=dict(text="BMIs"), paper_bgcolor='rgba(0, 0, 0, 0)')
    print('Writing BMIsleepApnea.svg file')
    pieAp.write_image('BMIsleepApnea.svg')
    print('Done')
   
    # BMI and insomnia
    print('Generating BMI insomnia pie chart')
    pieIn = px.pie(bmiInDf, names='Category', values='Count', title='BMI of people with Insomnia',  color='Category', category_orders={'Category': ['Normal', 'Overweight', 'Obese']}, color_discrete_sequence=px.colors.qualitative.Pastel1)
    pieIn.update_layout(legend_title=dict(text="BMIs"), paper_bgcolor='rgba(0, 0, 0, 0)')
    print('Writing BMIinsomnia.svg file')
    pieIn.write_image('BMIinsomnia.svg')
    print('Done')
   
   
# --- Generate interactive bar chart for hours of sleep based on age ---

def bar_sleepAge(data):
    getData = {}
   
    # Each value is own dictionary as title : info
    for value in data:
        age = str(value['Age'])
        if not getData.get(age):
            getData[age] = [value['Sleep Duration']] # Initialises list with first value at top of list
        else:
            getData[age].append(value['Sleep Duration'])
           
    ages = []
    sleep = []
    for age in sorted(getData): # Age = key
        hrs = getData[age]
        avg = sum(hrs) / len(hrs)
        ages.append(age)
        sleep.append(avg)
       
    barData = {
        'Ages': ages,
        'Sleep (average hours)': sleep
    }
   
    df = pd.DataFrame(barData)
    bar = px.bar(df, x='Ages', y='Sleep (average hours)', color='Sleep (average hours)', title='Average hours of sleep by Age', text_auto='.3s', width=1200, color_continuous_scale=px.colors.diverging.Temps[::-1]) # text auto shows the exact figure rounding to 3 significant figures
    bar.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    bar.write_html(file='barsleepAge.html', full_html=True, include_plotlyjs='directory')


# --- Generate bar chart to find BMI under each occupation (Shows a count of people) ---

def bar_jobBMIs(data):
    # Lists with all diff occupations and overall different BMIs
    jobs = []
    bmis = []
   
    for value in data:
        jobs.append(value['Occupation'])
        bmis.append(value['BMI Category'])
       
    # Format data for use in the chart
    lineData = {
        'Occupation': jobs,
        'BMIs': bmis
    }
   
    df = pd.DataFrame(lineData)
   
    # Data grouped by occupation
    df_grouped = df.groupby(['Occupation', 'BMIs']).size().reset_index(name='Count')
   
   
    # Get COUNT of people with particular BMI
    bar_count = px.bar(df_grouped, x='Occupation', y='Count', color='BMIs', title='BMI under different Occupations', barmode='group', color_discrete_sequence=px.colors.qualitative.Safe)
    bar_count.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    bar_count.write_html('barjobCount.html', full_html=False, include_plotlyjs='directory')
   
    # Get PERCENTAGE of people with particular BMI (sum of all count in occupation)
    df_grouped['Percentage'] = df_grouped['Count'] / df_grouped.groupby('Occupation')['Count'].transform('sum') * 100
    bar_percent = px.bar(df_grouped, x='Occupation', y='Percentage', color='BMIs', title='BMI under different Occupations %', color_discrete_sequence=px.colors.qualitative.Safe, barmode='group')
    bar_percent.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    bar_percent.write_html('barjobPercent.html', full_html=False, include_plotlyjs='directory' )


# --- Generate bar chart for average step count under each occupation ---

def bar_jobSteps(data):
    jobsSteps = {}

    for value in data:
        job = value['Occupation']
        steps = value['Daily Steps']
        if not jobsSteps.get(job):
            jobsSteps[job] = [steps]
        else:
            jobsSteps[job].append(steps)
           
    jobs = []
    steps = []
   
    for job in sorted(jobsSteps):
        step = jobsSteps[job] # List of step counts for people with this profession
        avg = sum(step) / len(step)
        jobs.append(job)
        steps.append(avg)
       
    barData = {
        'Occupation': jobs,
        'Steps': steps
        }
   
    df = pd.DataFrame(barData)
    bar = px.bar(df, x='Occupation', y='Steps', title='Average Step Count for each Occupation', color='Occupation', color_discrete_sequence=px.colors.qualitative.Pastel1)
    bar.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    bar.write_html(file='barjobSteps.html', full_html=False, include_plotlyjs='directory')


# --- Calculate the sleep quality based on age, sorted by gender as a line chart ---

def line_squalityAge(data):
    # Create dictionaries for male and female, age is the key and the sleep quality values added to a list
    females = {}
    males = {}
   
    for value in data:
        age = value['Age']
        quality = value['Quality of Sleep'] # Integer out of 10
        gender = value['Gender']
       
        if gender == 'Female':
            if not females.get(age):
                females[age] = [quality]
            else:
                females[age].append(quality)
        elif gender == 'Male':
            if not males.get(age):
                males[age] = [quality]
            else:
                males[age].append(quality)
               
    femages = []
    femsleepQuality = []
    for age in sorted(females):
        quality = females[age]
        avg = sum(quality) / len(quality)
        femages.append(age)
        femsleepQuality.append(avg)
       
    maleages = []
    malesleepQuality = []
    for age in sorted(males):
        quality = males[age]
        avg = sum(quality) / len(quality)
        maleages.append(age)
        malesleepQuality.append(avg)
       
    lineData_female = {
         'Ages': femages,
         'Sleep Quality': femsleepQuality,
         'Gender': ['Females'] * len(femages)
    }
   
    lineData_male = {
         'Ages': maleages,
         'Sleep Quality': malesleepQuality,
         'Gender': ['Males'] * len(maleages) # Need every list in the dictionary to have the same length thats why we mulitply it out!!
    }
   
    # Create dataFrames from data
    df_males = pd.DataFrame(lineData_male)
    df_females = pd.DataFrame(lineData_female)
   
    # Combine dataFrames
    df = pd.concat([df_females, df_males]) # needs the ages to be string in order to sort correctly!!
   
    # Create line chart and save as html file
    line = px.line(df, x='Ages', y='Sleep Quality', title='Sleep Quality based on Age and Gender', color='Gender', symbol='Gender', markers=True, color_discrete_map={'Females':'#DD4477','Males':'#2E91E5'})
    # text auto shows the exact figure rounding to 3 significant figures
   
    line.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    line.write_html(file='lineagequality.html', full_html=False, include_plotlyjs='directory')


def main():
    cred = credentials.Certificate("firebase-admin.json")
    firebase_admin.initialize_app(cred, {'databaseURL':'https://lc-sandbox-c942a-default-rtdb.europe-west1.firebasedatabase.app/'})
   
    ref = db.reference('Dataset') # Reference to 'Dataset' of database
    data = ref.get()
   
    pie_BMIs(data)
    bar_sleepAge(data)
    bar_jobBMIs(data)
    bar_jobSteps(data)
    line_squalityAge(data)
   
if __name__ == '__main__':
    main()