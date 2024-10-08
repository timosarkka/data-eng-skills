# Transform.py is used to clean and transform the raw data extracted from extract.py
# E.g. string cleaning, salary parsing, job description mapped against a skills/technologies list

# Import needed libraries
import numpy as np
import os
import pandas as pd
import re
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from datetime import datetime
from data_eng_skills import data_engineering_skills
from io import StringIO

# Load all .csv-files from the raw data folder to one dataframe
def load_raw_data():
    # Set up Azure Key Vault client
    key_vault_url = os.environ.get('AZURE_KEY_VAULT_URL')
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

    # Retrieve the connection string from Azure Key Vault
    connection_string = secret_client.get_secret(os.environ.get('AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME')).value

    # Create the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    container_name = os.environ.get('AZURE_RAW_STORAGE_CONTAINER_NAME')
    container_client = blob_service_client.get_container_client(container_name)

    # List all blobs in the container
    blob_list = container_client.list_blobs()

    all_df = []
    for blob in blob_list:
        if blob.name.endswith('.csv'):
            # Download the blob content
            blob_client = container_client.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().readall().decode('utf-8')
            
            # Create a DataFrame from the blob data
            df = pd.read_csv(StringIO(blob_data), sep=";", header=0)
            all_df.append(df)

    return pd.concat(all_df, ignore_index=True)

# Clean the data
# Remove unnecessary words and characters from the data
def clean_data(df):
    df['Job ID'] = df['Job ID'].str.replace('job_', '')
    df['Location'] = df['Location'].str.replace('Hybrid work in', '').str.replace('Remote in', '')
    df['Location'] = df['Location'].str.replace(r'\b\d{5}\S*', '', regex=True).str.strip() # Remove zip codes from 'Location'
    df['Location'] = df['Location'].str.replace(r'\([^)]*\)', '', regex=True).str.strip() # Remove trailing words inside parentheses
    df['Job Type'] = df['Job Type'].str.replace(r'(?<!\w)-(?!\w)', '', regex=True).str.strip() # Remove single dashes when they're not part of a word
    df['Job Type'] = df['Job Type'].str.split().str[0] # Remove trailing words from 'Job Type' 
    df['Job Type'] = df['Job Type'].str.rstrip(',')
    df['Job Type'] = df['Job Type'].str.replace('Temporary', 'Part-time').str.replace('Permanent', 'Full-time').str.replace('Temp-to-hire', 'Part-time')
    df['Salary'] = df['Salary'].str.replace('$', '').str.replace('From', '').str.replace('a year', '').str.replace('an hour', '').str.strip() # Remove non-numeric strings from Salary
    df[['Salary_Lower', 'Salary_Upper']] = df['Salary'].str.split('-', expand=True) # Split salary to a range located in two columns
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
    
    # If salary is lower than 1000, it's most likely an hourly rate. Split these to their own columns.
    salary_cond_low = df['Salary_Lower'] < 1000
    salary_cond_upp = df['Salary_Upper'] < 1000
    df.loc[salary_cond_low, 'Hourly_Rate_Lower'] = df.loc[salary_cond_low, 'Salary_Lower']
    df.loc[salary_cond_upp, 'Hourly_Rate_Upper'] = df.loc[salary_cond_upp, 'Salary_Upper']
    df.loc[salary_cond_low, 'Salary_Lower'] = np.nan
    df.loc[salary_cond_upp, 'Salary_Upper'] = np.nan

    # Cast hourly rate columns to numeric
    df['Hourly_Rate_Lower'] = pd.to_numeric(df['Hourly_Rate_Lower'], errors='coerce')
    df['Hourly_Rate_Upper'] = pd.to_numeric(df['Hourly_Rate_Upper'], errors='coerce')
    return df

# Transform the data
# Calculate average salary, extract key skills and technologies from the job description
def process_data(df):
    df['Salary_Avg'] = df[['Salary_Upper', 'Salary_Lower']].mean(axis=1, skipna=True)
    df['Hourly_Rate_Avg'] = df[['Hourly_Rate_Lower', 'Hourly_Rate_Upper']].mean(axis=1, skipna=True)
    df['Req_Skills'] = df['Full Job Description'].apply(lambda desc: extract_skills(desc, data_engineering_skills))
    return df[['Job ID', 'Title', 'Company', 'Location', 'Salary_Lower', 'Salary_Avg', 'Salary_Upper', 'Hourly_Rate_Lower', 'Hourly_Rate_Avg', 'Hourly_Rate_Upper', 'Job Type', 'Req_Skills']]

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

# Save the processed data to a .csv-file on Azure Blob Storage
def save_processed_data(df):
    # Define the container and file name
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    CONTAINER_NAME = os.environ.get('AZURE_PROCESSED_STORAGE_CONTAINER_NAME')
    BLOB_NAME = f'data_eng_info_processed_{current_time}.csv'

    # Set up Azure Key Vault client
    key_vault_url = os.environ.get('AZURE_KEY_VAULT_URL')
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

    # Retrieve the connection string from Azure Key Vault
    PASS_TOKEN = secret_client.get_secret(os.environ.get('AZURE_STORAGE_CONNECTION_STRING_SECRET_NAME')).value

    # Create the BlobServiceClient using the retrieved connection string
    BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(PASS_TOKEN)

    # Create a blob client
    blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)

    # Upload the DataFrame directly to Azure Blob Storage
    csv_data = df.to_csv(sep=';', index=False).encode('utf-8')
    blob_client.upload_blob(csv_data, overwrite=True)
    print(f"Processed data uploaded to blob {BLOB_NAME} in container {CONTAINER_NAME}.")

# Main function to transform the data
def transform_data():
    df = load_raw_data()
    df = clean_data(df)
    df = process_data(df)
    save_processed_data(df)