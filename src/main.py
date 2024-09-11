# Main.py is the entry point for the program
# It executes the functions from extract.py, transform.py and load.py

from extract import extract_data
from transform import transform_data
from load import load_data

# URL parameters 
# Modify to search for different jobs and locations, alter sorting and where to start the scraping
job_title = "Data Engineer"
location = "United States"
sort = "date"
start = 160 # 10 is page 2, 20 is page 3 etc. Omit '&start' altogether if you want to start from the first page!

# Run the scraper
extract_data(f"https://indeed.com/jobs?q=\"{job_title}\"&l=\"{location}\"&sort={sort}&start={start}")

# Set the folders for raw and processed data. Don't alter unless necessary.
raw_data_folder = 'data/raw/'
processed_data_folder = 'data/processed/'

# Transform the raw data
transform_data(raw_data_folder, processed_data_folder)

# Load the transformed data into the database
load_data(processed_data_folder)

# Print out a message to confirm that the process is complete
print("Data pipeline has been executed successfully!")