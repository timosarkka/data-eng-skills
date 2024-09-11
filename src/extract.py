# This script is used to scrape job listings from indeed.com for the role of a Data Engineer based in the United States
# Job title, company name, location, salary, job type and the full job description are extracted
# This raw data will then be further transformed in de_processor.py

'''
Setting up libraries and Chrome driver options
'''

# Import needed libraries
import pandas as pd
import random
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from datetime import datetime

# Set up Chrome options to mimic browser behavior
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--headless")





'''
Functionality to get the job listings data
'''

# Function to extract the wanted job listing data and write it to a pandas dataframe
def get_job_data(job_listing, url):

    # Initialize driver again to establish a new fresh connection for each run
    driver = webdriver.Chrome(options=options)

    # Extract job_id and job title
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
        # Reinitialize the driver and load the main page
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

def main():
    # Initialize a Chrome webdriver with the specified options
    driver = webdriver.Chrome(options=options)

    # Define the URL to scrape and open URL in Chrome WebDriver instance
    url = "https://indeed.com/jobs?q=\"Data Engineer\"&l=\"United States\"&sort=date&start=70"
    driver.get(url)

    # Add sleep for 5s to allow the page to load
    sleep(5)

    # Get the main page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser") 

    # Define the soup from the job listings and initialize an empty list to store job data
    job_listings = soup.find_all('div', class_='job_seen_beacon')
    job_data_list = []

    # Loop over the job listings on the main page
    for index, job_listing in enumerate(job_listings):
        data = get_job_data(job_listing, url)
        job_data_list.append(data)
        print(f"Successfully extracted data for job listing {index + 1}")
        # Add a longer delay every 5 listings
        if (index + 1) % 5 == 0:
            sleep(random.uniform(5, 10))

    # Convert list of records into a pandas dataframe
    df = pd.DataFrame(job_data_list, columns=['Job ID', 'Title', 'Company', 'Location', 'Salary', 'Job Type', 'Full Job Description'])

    # Export the dataframe to a CSV file
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'data/raw/data_eng_info_raw_{current_time}.csv'
    df.to_csv(filename, sep=';', index=False)
    print("Raw data saved to CSV file successfully!")

    # Close the Chrome WebDriver instance
    driver.quit()

# Execute the main function
if __name__ == "__main__":
    main()
