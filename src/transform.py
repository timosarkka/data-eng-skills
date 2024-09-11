# Transform.py is used to clean and transform the raw data extracted from extract.py
# E.g. string cleaning, salary parsing, job description mapped against a skills/technologies list

# Import needed libraries
import pandas as pd
import re
import os
from datetime import datetime
from data_eng_skills import data_engineering_skills

# Load all .csv-files from the raw data folder to one dataframe
def load_raw_data(raw_data_folder):
    all_df = []
    for filename in os.listdir(raw_data_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(raw_data_folder, filename)
            df = pd.read_csv(file_path, sep=";", header=0)
            all_df.append(df)
    return pd.concat(all_df, ignore_index=True)

# Clean the data
# Remove unnecessary words and characters from the data
def clean_data(df):
    df['Job ID'] = df['Job ID'].str.replace('job_', '')
    df['Location'] = df['Location'].str.replace('Hybrid work in', '').str.replace('Remote in', '')
    df['Location'] = df['Location'].str.replace(r'\b\d{5}\b$', '', regex=True).str.strip()
    df['Job Type'] = df['Job Type'].str.replace(r'(?<!\w)-(?!\w)', '', regex=True).str.strip()
    
    df['Salary'] = df['Salary'].str.replace('$', '').str.replace('From', '').str.replace('a year', '').str.replace('an hour', '').str.strip()
    df[['Salary_Lower', 'Salary_Upper']] = df['Salary'].str.split('-', expand=True)
    df['Salary_Lower'] = df['Salary_Lower'].str.rstrip().str.replace(',', '')
    df['Salary_Upper'] = df['Salary_Upper'].str.rstrip().str.replace(',', '')
    
    # Cast the data to the correct data types
    df['Job ID'] = df['Job ID'].astype('str')
    df['Title'] = df['Title'].astype('str')
    df['Company'] = df['Company'].astype('str')
    df['Location'] = df['Location'].astype('str')
    df['Salary_Lower'] = pd.to_numeric(df['Salary_Lower'], errors='coerce')
    df['Salary_Upper'] = pd.to_numeric(df['Salary_Upper'], errors='coerce')
    df['Job Type'] = df['Job Type'].astype('str')
    df['Full Job Description'] = df['Full Job Description'].astype('str')
    
    return df

# Transform the data
# Calculate average salary, extract key skills and technologies from the job description
def process_data(df):
    df['Salary_Avg'] = df[['Salary_Upper', 'Salary_Lower']].mean(axis=1, skipna=True)
    df['Req_Skills'] = df['Full Job Description'].apply(lambda desc: extract_skills(desc, data_engineering_skills))
    return df[['Job ID', 'Title', 'Company', 'Location', 'Salary_Lower', 'Salary_Avg', 'Salary_Upper', 'Job Type', 'Req_Skills']]

# Function to extract key skills and technologies from the job description
def extract_skills(description, skills_dict):
    found_skills = []
    description_lower = description.lower()

    # Treat R as a special case, since otherwise the presence of letter 'R' would cause incorrect matches
    r_pattern = r'\b(R\b|R,|R programming|R language|R studio)\b'
    if re.search(r_pattern, description, re.IGNORECASE):
        found_skills.append('R')

    # Extract all other skills and technologies
    for skill, variations in skills_dict.items():
        if any(variation.lower() in description_lower for variation in variations):
            found_skills.append(skill)

    return found_skills

# Save the processed data to a .csv-file
def save_processed_data(df, output_folder):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f'{output_folder}/data_eng_info_processed_{current_time}.csv'
    df.to_csv(output_filename, sep=';', index=False)
    print(f"Processed data saved to {output_filename}")

# Main function to transform the data
def transform_data(raw_data_folder, output_folder):
    df = load_raw_data(raw_data_folder)
    df = clean_data(df)
    df = process_data(df)
    save_processed_data(df, output_folder)