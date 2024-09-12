# Extract.py is used to scrape job listings from a given website
# This raw data will then be further transformed in transform.py

'''
Setting up libraries and Chrome driver options
'''

# Import needed libraries
import pandas as pd
import random
import re
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from time import sleep

# Set up Chrome options to mimic browser behavior
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--headless")

'''
Functionality to extract the job listings data
'''

# Function to extract the wanted job listing data and write it to a pandas dataframe
def get_job_data(job_listing, url):

    # Iimportant! Initialize driver again to establish a new fresh connection for each listing
    # Without initializing, the run will fail after 2-3 listings
    driver = webdriver.Chrome(options=options)

    # Extract job_id and job title. These will always be present
    job_id = job_listing.find("a")["id"]
    title = job_listing.find("a").find("span").text.strip()
    
    # Extract company and location
    try:
        company = job_listing.find('span', class_='css-63koeb eu4oa1w0').text.strip()
    except AttributeError:
        company = None
    
    try:
        location  = job_listing.find('div', class_='css-1p0sjhy eu4oa1w0').text.strip()
    except AttributeError:
        location = None

    # Simulate clicking on the job to reveal additional details, like salary, job type, full job description
    # Switch to the new tab
    job_link = job_listing.find('a')['href']
    job_url = f"https://indeed.com{job_link}"
    driver.execute_script("window.open('{}')".format(job_url))
    driver.switch_to.window(driver.window_handles[-1])

    # Wait for job details to load
    sleep(random.uniform(1, 3))

    # Get the opened job details page source and parse it
    job_details_soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract salary, job type, full job description from job details page
    try:
        salary = job_details_soup.find('span', class_="css-19j1a75 eu4oa1w0").text.strip()
    except AttributeError:
        salary = None
    
    try:
        job_type = job_details_soup.find('span', class_='css-k5flys eu4oa1w0').text.strip()
    except AttributeError:
        job_type = None

    try:
        full_job_description = job_details_soup.find(id="jobDescriptionText", class_="jobsearch-JobComponent-description css-16y4thd eu4oa1w0").text
        # Clean up whitespace while preserving paragraphs
        paragraphs = re.split(r'\n\s*\n', full_job_description)
        cleaned_paragraphs = [' '.join(p.split()) for p in paragraphs]
        full_job_description = '\n\n'.join(cleaned_paragraphs)
    except AttributeError:
        full_job_description = None

    try:
        # Close the job details page
        driver.close()
        
        # Check if there are any remaining window handles
        if driver.window_handles:
            # Switch back to the main page (now the first handle)
            driver.switch_to.window(driver.window_handles[0])
        else:
            # If no handles left, reinitialize the driver and load the main page
            driver.quit()
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            sleep(5)  # Allow time for the page to load
    except Exception as e:
        print(f"Error switching windows: {e}")
        # In case of error, reinitialize the driver and load the main page
        driver.quit()
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        sleep(5)  # Allow time for the page to load


    # Random sleep after each listing
    sleep(random.uniform(1, 3))

    # Return a tuple containing all the extracted information
    return (job_id, title, company, location, salary, job_type, full_job_description)


'''
Main program that runs the scraper
'''

def extract_data(input_url):
    # Initialize a Chrome webdriver with the specified options
    driver = webdriver.Chrome(options=options)

    # Define the URL to scrape and open URL in Chrome WebDriver instance
    url = input_url
    driver.get(url)

    # Add sleep for 5s to allow the page to load
    sleep(5)

    # Get the main page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser") 

    # Find all job listings, i.e. divs with 'job_seen_beacon' -class
    job_listings = soup.find_all('div', class_='job_seen_beacon')
    job_data_list = []

    # Loop over the job listings
    for index, job_listing in enumerate(job_listings):
        data = get_job_data(job_listing, url)
        job_data_list.append(data)
        print(f"Successfully extracted data for job listing {index + 1}")
        # Add a longer sleep every 5 listings
        if (index + 1) % 5 == 0:
            sleep(random.uniform(5, 10))

    # Convert list of records into a pandas dataframe
    df = pd.DataFrame(job_data_list, columns=['Job ID', 'Title', 'Company', 'Location', 'Salary', 'Job Type', 'Full Job Description'])

    # Define the container and file name
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    CONTAINER_NAME = "dataraw"
    BLOB_NAME = f'data_eng_info_raw_{current_time}.csv'

    # Set up Azure Key Vault client
    key_vault_url = "https://timokeyvault.vault.azure.net/"
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

    # Retrieve the connection string from Azure Key Vault
    secret_name = "azure-storage-blob-connection-string"
    PASS_TOKEN = secret_client.get_secret(secret_name).value

    # Create the BlobServiceClient using the retrieved connection string
    BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(PASS_TOKEN)

    # Create a blob client
    blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)

    # Upload the DataFrame directly to Azure Blob Storage
    csv_data = df.to_csv(sep=";", index=False).encode('utf-8')
    blob_client.upload_blob(csv_data, overwrite=True)
    print(f"Data uploaded to blob {BLOB_NAME} in container {CONTAINER_NAME}.")

    # Close the Chrome WebDriver instance
    driver.quit()