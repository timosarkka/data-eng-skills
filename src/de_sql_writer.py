# This script takes the processed .csv-file and its data and writes it into a PostgreSQL database on Azure.

# Import necessary libraries
import csv
import psycopg2
from psycopg2 import sql
from config import config

# Establish connection
conn = psycopg2.connect(**config())
cursor = conn.cursor()

# Create necessary tables
cursor.execute("""CREATE TABLE IF NOT EXISTS jobs (
        job_id CHAR(32) PRIMARY KEY,
        title VARCHAR(255),
        company VARCHAR(255),
        location VARCHAR(255),
        salary_lower DECIMAL(10, 2),           
        salary_avg DECIMAL(10, 2),
        salary_upper DECIMAL(10, 2),
        job_type VARCHAR(255),
        req_skill VARCHAR(255)[]
);""")

# Commit the table creation
conn.commit()

# Read the CSV-file and insert job data row by row
with open('data/processed/data_eng_info_processed.csv', 'r') as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        # Convert req_skills to a PostgreSQL-compatible array
        # Convert decimal columns to None if no value is present
        # Convert job_type to None if value is nan
        skills_array = '{' + ', '.join(f'"{skill.strip()}"' for skill in eval(row['Req_Skills'])) + '}'
        salary_lower = None if row['Salary_Lower'] == '' else row['Salary_Lower']
        salary_avg = None if row['Salary_Avg'] == '' else row['Salary_Avg']
        salary_upper = None if row['Salary_Upper'] == '' else row['Salary_Upper']
        job_type = None if row['Job Type'] == 'nan' else row['Job Type']
        # Insert job
        cursor.execute("""
            INSERT INTO jobs (job_id, title, company, location, salary_lower, salary_avg, salary_upper, job_type, req_skill)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (job_id) DO NOTHING
        """, (row['Job ID'], row['Title'], row['Company'], row['Location'], salary_lower, salary_avg, salary_upper, job_type, skills_array))

conn.commit()
conn.close()

print("Wrote data to SQL table successfully!")