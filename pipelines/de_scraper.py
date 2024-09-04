# Import needed libraries
import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd

# Define headers, URL and parameters for the desired info to be scraped
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
url = "https://indeed.com/jobs?q=\"Data Engineer\"&l=\"United States\"&start=1"
r=requests.get(url, headers=headers)
r.status_code
soup = BeautifulSoup(r.text, "html.parser") 