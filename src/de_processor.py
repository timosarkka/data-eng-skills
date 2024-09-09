# This script is used to process the raw data extracted from de_scraper.py
# It is used to clean and transform the data and prepare it for further analysis
# E.g. string cleaning, salary parsing, job description is mapped against a skills/technologies list and new columns are created to list them



# Import needed libraries and setup some pandas options
import pandas as pd
import re
from data_eng_skills import data_engineering_skills
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Import the raw data
df = pd.read_csv('data/raw/data_eng_info_raw.csv', sep=";", header=0)


'''
Cleaning the data
'''

# Clean up the job id column. Remove the "job_" prefix
df['Job ID'] = df['Job ID'].str.replace('job_', '')

# Clean up the location column. 
# Remove "Hybrid work in" and "Remote in". 
# Clean up the job type column.
# Also remove ZIP codes as they're not needed in our case
df['Location'] = df['Location'].str.replace('Hybrid work in', '').str.replace('Remote in', '')
df['Location'] = df['Location'].str.replace(r'\b\d{5}\b$', '', regex=True).str.strip()
df['Job Type'] = df['Job Type'].str.replace(r'(?<!\w)-(?!\w)', '', regex=True).str.strip()

# Clean and split the salary range into two, with a lower range and an upper range
df['Salary'] = df['Salary'].str.replace('$', '')
df['Salary'] = df['Salary'].str.replace('From', '')
df['Salary'] = df['Salary'].str.replace('a year', '').str.strip()
df['Salary'] = df['Salary'].str.replace('an hour', '').str.strip()
df[['Salary_Lower', 'Salary_Upper']] = df['Salary'].str.split('-', expand=True)
df['Salary_Lower'] = df['Salary_Lower'].str.rstrip().str.replace(',', '').fillna(0)
df['Salary_Upper'] = df['Salary_Upper'].str.rstrip().str.replace(',', '').fillna(0)

# Cast columns into proper format
df['Job ID'] = df['Job ID'].astype('str')
df['Title'] = df['Title'].astype('str')
df['Company'] = df['Company'].astype('str')
df['Location'] = df['Location'].astype('str')
df['Salary_Lower'] = df['Salary_Lower'].astype(int)
df['Salary_Upper'] = df['Salary_Upper'].astype(int)
df['Job Type'] = df['Job Type'].astype('str')
df['Full Job Description'] = df['Full Job Description'].astype('str')



'''
Transforming the data
'''

# Calculate the average of lower and upper salary values
df['Salary_Avg'] = df[['Salary_Upper', 'Salary_Lower']].mean(axis=1)

# Map the full job descriptions against the data_engineering_skills dictionary
# If match is found, add the skill into a temp list which is then written back to a new column "Req_Skills"
def extract_skills(description, skills_dict):
    found_skills = []
    description_lower = description.lower()

    for skill, variations in skills_dict.items():
        if any(variation.lower() in description_lower for variation in variations):
            found_skills.append(skill)

    return found_skills

# Apply the function extract_skills to job descriptions
df['Req_Skills'] = df['Full Job Description'].apply(lambda desc: extract_skills(desc, data_engineering_skills))


# Filter out columns that are not needed
df = df[['Job ID', 'Title', 'Company', 'Location', 'Salary_Lower', 'Salary_Avg', 'Salary_Upper', 'Job Type', 'Req_Skills']]



'Write the data to a csv'

df.to_csv('data/processed/data_eng_info_processed.csv', sep=';', index=False)