# Main.py is the entry point for the program
# It executes the functions from extract.py, transform.py and load.py

# Import needed libraries and functions
from extract import extract_data
from transform import transform_data
from load import load_data
from config import get_job_title, get_location, get_sort, get_start, get_base_url

# URL parameters 
# Modify config.py to search for different jobs and locations, alter sorting and where to start the scraping
def main():
    # Fetch parameters from config.py
    job_title = get_job_title()
    location = get_location()
    sort = get_sort()
    start = get_start() # Note! If you want to start from first page, you need to omit &start={start} completely
    base_url = get_base_url()

    # Run the scraper
    extract_data(f"{base_url}/jobs?q=\"{job_title}\"&l=\"{location}\"&sort={sort}&start={start}")

    # Transform the raw data
    transform_data()

    # Load the transformed data into the database
    load_data()

    # Print out a message to confirm that the process is complete
    print("Data pipeline has been executed successfully!")

if __name__ == "__main__":
    main()
