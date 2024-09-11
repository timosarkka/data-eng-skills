# Load takes the processed .csv-files, does some final transformations and writes them into a PostgreSQL database on Azure.

import csv
import os
import psycopg2
from psycopg2 import sql
from config import config

# Create the table and columns if it doesn't exist
def create_table(cursor):
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

# Insert the data into the table
def insert_job_data(cursor, row):
    # PostgreSQL requires the array to be of format {skill1, skill2, skill3}
    skills_array = '{' + ', '.join(f'"{skill.strip()}"' for skill in eval(row['Req_Skills'])) + '}' 

    # If the values are empty, insert nulls
    salary_lower = None if row['Salary_Lower'] == '' else row['Salary_Lower']
    salary_avg = None if row['Salary_Avg'] == '' else row['Salary_Avg']
    salary_upper = None if row['Salary_Upper'] == '' else row['Salary_Upper']
    job_type = None if row['Job Type'] == 'nan' else row['Job Type']
    
    # Insert the data into the table
    cursor.execute("""
        INSERT INTO jobs (job_id, title, company, location, salary_lower, salary_avg, salary_upper, job_type, req_skill)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (job_id) DO NOTHING
    """, (row['Job ID'], row['Title'], row['Company'], row['Location'], salary_lower, salary_avg, salary_upper, job_type, skills_array))

# Clear the processed CSV files so that the staging area stays clean
def clear_processed_files(csv_folder):
    print("Clearing processed CSV files...")
    for filename in os.listdir(csv_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_folder, filename)
            try:
                os.remove(file_path)
                print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
    print("Processed-folder cleared.")

# The main function that loads the data into the database
def load_data(csv_folder):
    conn = psycopg2.connect(**config())
    cursor = conn.cursor()

    create_table(cursor)
    conn.commit()

    for filename in os.listdir(csv_folder):
        if filename.endswith('.csv'):
            with open(os.path.join(csv_folder, filename), 'r') as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    insert_job_data(cursor, row)

    conn.commit()
    conn.close()

    print("Wrote data to SQL table successfully!")
    
    clear_processed_files(csv_folder)