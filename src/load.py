# Load takes the processed .csv-files, does some final transformations and writes them into a PostgreSQL database on Azure.

import csv
import os
import psycopg2
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
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
            hourly_rate_lower DECIMAL(10, 2),
            hourly_rate_avg DECIMAL(10, 2),
            hourly_rate_upper DECIMAL(10, 2),
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
    hourly_rate_lower = None if row['Hourly_Rate_Lower'] == '' else row['Hourly_Rate_Lower']
    hourly_rate_avg = None if row['Hourly_Rate_Avg'] == '' else row['Hourly_Rate_Avg']
    hourly_rate_upper = None if row['Hourly_Rate_Upper'] == '' else row['Hourly_Rate_Upper']
    job_type = 'No info' if row['Job Type'] == 'nan' else row['Job Type']
    
    # Insert the data into the table
    cursor.execute("""
        INSERT INTO jobs (job_id, title, company, location, salary_lower, salary_avg, salary_upper, hourly_rate_lower, hourly_rate_avg, hourly_rate_upper, job_type, req_skill)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (job_id) DO NOTHING
    """, (row['Job ID'], row['Title'], row['Company'], row['Location'], salary_lower, salary_avg, salary_upper, hourly_rate_lower, hourly_rate_avg, hourly_rate_upper, job_type, skills_array))

# Clear the processed CSV files so that the staging area stays clean
def clear_processed_files(blob_service_client, container_name):
    print("Clearing processed CSV files from Azure Blob Storage...")
    container_client = blob_service_client.get_container_client(container_name)
    blobs_list = container_client.list_blobs()
    
    for blob in blobs_list:
        if blob.name.endswith('.csv'):
            try:
                blob_client = container_client.get_blob_client(blob.name)
                blob_client.delete_blob()
                print(f"Deleted: {blob.name}")
            except Exception as e:
                print(f"Error deleting {blob.name}: {e}")
    
    print("Processed container cleared.")

# The main function that loads the data into the database
def load_data():
    conn = psycopg2.connect(**config())
    cursor = conn.cursor()

    create_table(cursor)
    conn.commit()

    # Set up Azure Key Vault client
    key_vault_url = os.getenv('AZURE_KEY_VAULT_URL')
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

    # Retrieve the connection string from Azure Key Vault
    secret_name = os.getenv('AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME')
    connection_string = secret_client.get_secret(secret_name).value

    # Create the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    container_name = os.getenv('AZURE_PROCESSED_STORAGE_CONTAINER_NAME')
    container_client = blob_service_client.get_container_client(container_name)

    # List all blobs in the container
    blob_list = container_client.list_blobs()

    for blob in blob_list:
        if blob.name.endswith('.csv'):
            # Download the blob content
            blob_client = container_client.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().readall().decode('utf-8')
            
            # Create a CSV reader from the blob data
            reader = csv.DictReader(blob_data.splitlines(), delimiter=";")
            
            for row in reader:
                insert_job_data(cursor, row)

    conn.commit()
    conn.close()

    print("Wrote data to SQL table successfully!")
    
    clear_processed_files(blob_service_client, container_name)