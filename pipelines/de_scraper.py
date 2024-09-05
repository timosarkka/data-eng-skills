'''
Setting up the scraper, defining URLs, parameters, and assisting dictionaries
'''

# Import needed libraries
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import pandas as pd
from tabulate import tabulate

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
    
    summary = job_listing.find('div', class_='css-9446fg eu4oa1w0').text.strip()
    
    # Return a tuple containing all the extracted information
    return (title, company, location, summary)

'''
Main program that runs the scraper
'''

def main():
    # Find all job listings on the current page
    job_listings = soup.find_all('div', class_='job_seen_beacon')

    # Initialize an empty list to store the job data
    job_data_list = []

    # Loop over the job listings on the current page and extract the data
    for job_listing in job_listings:
        data = get_job_data(job_listing)
        job_data_list.append(data)

    # Convert list of records into a pandas dataframe
    df = pd.DataFrame(job_data_list, columns=['Title', 'Company', 'Location', 'Summary'])
    print(tabulate(df, headers='keys', tablefmt='simple_grid'))

    # Export the dataframe to a CSV file
    df.to_csv('data/raw/data_eng_info_raw.csv', sep=';', index=False)
    print("Raw data saved to CSV file successfully!")

    # Close the Chrome WebDriver instance
    driver.quit()

# Execute the main function
if __name__ == "__main__":
    main()