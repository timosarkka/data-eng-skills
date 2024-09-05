'''
Setting up the scraper, defining URLs, parameters, and assisting dictionaries
'''

# Import needed libraries
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options to mimic browser behavior
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36')

# Initialize a Chrome webdriver with the specified options
driver = webdriver.Chrome(options=options)

# Define the URL to scrape and open URL in Chrome WebDriver instance
url = "https://indeed.com/jobs?q=\"Data Engineer\"&l=\"United States\"&start=1"
driver.get(url)

# Add sleep for 5s to allow the page to load
sleep(5)

# Get the page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser") 

'''
Functionality to get the job listings data
'''

# Function to extract the wanted job listing data and write it to a pandas dataframe
def get_job_data(job_listing):
    # Extract job title
    title = job_listing.find("a").find("span").text.strip()
    
    # Extract company, location, salary, job type, summary if available, otherwise assign an empty string
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
    driver.execute_script("window.open('" + job_url + "');")
    driver.switch_to.window(driver.window_handles[-1])

    # Wait for job details to load
    sleep(3)

    # Get the new page source and parse it
    job_details_soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract salary, job type, full job description
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

    # Close the job details page and switch back to the main page
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # Return a tuple containing all the extracted information
    return (title, company, location, salary, job_type, full_job_description)

'''
Main program that runs the scraper
'''

def main():
    job_listing = soup.find('div', class_='job_seen_beacon')
    job_data_list = []
    data = get_job_data(job_listing)
    job_data_list.append(data)

    # Convert list of records into a pandas dataframe
    df = pd.DataFrame(job_data_list, columns=['Title', 'Company', 'Location', 'Salary', 'Job Type', 'Full Job Description'])

    # Export the dataframe to a CSV file
    df.to_csv('data/raw/data_eng_info_raw.csv', sep=';', index=False)
    print("Raw data saved to CSV file successfully!")

    # Close the Chrome WebDriver instance
    driver.quit()

# Execute the main function
if __name__ == "__main__":
    main()