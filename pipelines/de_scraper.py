# Import needed libraries
import requests
import pandas as pd
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

# Add sleep for 5s to allow the page to load
sleep(5)

# Get the page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser") 