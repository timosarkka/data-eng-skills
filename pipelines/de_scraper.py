'''
Setting up the scraper, defining URLs and parameters
'''

# Import needed libraries
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

# Set up Chrome options to mimic browser behavior
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36')

# Initialize a Chrome webdriver with the specified options
driver = webdriver.Chrome(options=options)

# Define the URL to scrape and open URL in Chrome WebDriver instance
url = "https://indeed.com/jobs?q=\"Data Engineer\"&l=\"United States\"&start=1"
driver.get(url)

# Add sleep for 10s to allow the page to load
sleep(10)

# Get the page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser") 


'''
Functionality to get the job listings data
'''

def get_job_data(job_listing):
    title = job_listing.find("a").find("span").text.strip()
    return title

'''
Main program that runs the scraper
'''

job_listings = soup.find_all('div', class_='job_seen_beacon') 
for job_listing in job_listings:
    data = get_job_data(job_listing)
    print(data)

# Close the Chrome WebDriver instance
driver.quit()
