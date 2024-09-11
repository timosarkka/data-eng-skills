import csv

# Path to the CSV file
file_path = 'data/processed/data_eng_info_processed_2024-09-11_13-15-30.csv'

# Set to store unique Job IDs
unique_job_ids = set()

# Read the CSV file
with open(file_path, 'r') as file:
    reader = csv.reader(file, delimiter=';')
    for row in reader:
        # Skip empty rows
        if not row:
            continue
        # Add the Job ID (first column) to the set
        unique_job_ids.add(row[0])

# Print the number of unique Job IDs
print(f'Number of unique Job IDs: {len(unique_job_ids)}')