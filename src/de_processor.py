# This script is used to process the raw data extracted from de_scraper.py
# It is used to clean and transform the data and prepare it for further analysis
# E.g. string cleaning, salary parsing, job description is mapped against a skills/technologies list and new columns are created to list them

# Import needed libraries and setup some pandas options
import pandas as pd
import re
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Import the raw data
df = pd.read_csv('data/raw/data_eng_info_raw.csv', sep=";", header=0)

# Clean up the location column. Remove "Hybrid work in" and "Remote in".
# Also remove ZIP codes as they're not needed in our case
df['Location'] = df['Location'].str.replace('Hybrid work in', '').str.replace('Remote in', '')
df['Location'] = df['Location'].str.replace(r'\b\d{5}\b$', '', regex=True).str.strip()

# Clean and split the salary range into two, with a lower range and an upper range
df['Salary'] = df['Salary'].str.replace('$', '')
df['Salary'] = df['Salary'].str.replace('a year', '').str.strip()
df[['Salary_Lower', 'Salary_Upper']] = df['Salary'].str.split('-', expand=True)
df['Salary_Lower'] = df['Salary_Lower'].str.rstrip().astype(int, errors='ignore')
df['Salary_Upper'] = df['Salary_Upper'].str.rstrip().astype(int, errors='ignore')

print(df)