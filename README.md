# Data Engineering in 2024: Which Skills Will Land You the Job?

![image](https://github.com/user-attachments/assets/e964a34c-4a14-4b00-ab37-226280660772)

## 1. Introduction

This project analyzes the current job market for Data Engineering positions in the US, with a focus on identifying the most in-demand skills and technologies.

The data used for this analysis was collected from job postings during the period of August-September 2024.

In essence, this project implements an end-to-end ETL pipeline, complemented by an analysis dashboard in Power BI. The pipeline includes web scraping for data extraction, Python scripts for transformation and loading, and an SQL database for storing the cleansed and processed data.

## 2. Project Structure

The project folders are structured as shown below. **Note that I have not provided config.py itself for security reasons**, but it should be quite straightforward to build your own by looking at how it is called throughout the code.

```
├── src/
|   ├── data_eng_skills.py           # Includes the skills listing for data engineering jobs
│   ├── extract.py                   # Web scraping job listings
│   ├── transform.py                 # Data processing and cleaning
|   ├── load.py                      # Loading data to PostgreSQL
│   ├── main.py                      # Executes the main program
│   └── config.py                    # Configuration and secrets management (NOT on GitHub!)
├── visualization/
│   └── dataeng_jobs_dashboard.pbix  # Power BI visualization dashboard for analysis
└── README.md                        # Project documentation
```

## 3. Tech Stack

My tech stack for this project:

Languages and libraries
* Python, numpy, pandas
* SQL
* Selenium
* BeautifulSoup 
* Azure SDK
* Psycopg2
* Misc. smaller python libraries

Cloud infrastructure
* Azure VM for hosting the scripts and triggers (cron jobs)
* Azure Blog Storage for hosting the raw and staging data
* Azure Database for PostgreSQL flexible server for hosting the cleaned and processed data
* Power BI for final data modeling and visualizations

## 4. Data Pipeline Architecture

Here's the basic architecture of the pipeline. Cron job triggers main.py. Main.py runs the other scripts. Azure Blob Storage acts as the intermediate object storage. PostgreSQL is used to store the final cleaned data for analysis. And finally, Power BI is connected to PostgreSQL to read and visualize the data.

![image](https://github.com/user-attachments/assets/68cca6d5-a08e-4dfd-9042-3c0359760fcf)


## 5. Extracting Data

In a nutshell, here's how extract.py extracts the data:

1. Set up Chrome webdriver and an instance.
2. Open browser and url.
3. Parse the job listings into a soup object (15 per page).
4. Get basic job data first (job id, title, company, location).
5. For each job listing, open the details page in a new tab.
6. Get detailed job data, like salary info, job type and the full description.
7. Read all of the raw data into a pandas dataframe.
8. Save to Azure Blob Storage raw data folder as a .csv-file with timestamp.

See extract.py for more details.

## 6. Transforming Data

After extracting the raw data, transform.py takes care of cleaning and transforming the data.

The process in short:

1. Read all available raw data files contained on Azure Blob Storage raw data folder.
2. Concat all data to one pandas dataframe.
3. Carry out cleaning operations for location, job type, salaries etc.
4. Cast each column with the right variable type.
5. Calculate some salary and hourly rate averages.
6. Extract the key skills and technologies from the job description.
7. Save the cleaned and processed data to Azure Blob Storage as one .csv-file with timestamp.

See transform.py for more details.

## 7. Loading Data

Finally, the data is ready to be loaded into an SQL database.

In short:

1. Load the processed data from the processed data folder from Azure Blob Storage.
2. Create the SQL table with correct columns and variable types if it doesn't exist.
3. If the table already exists, insert the cleaned data into the SQL table row by row.

NOTE! If the job id is already found from the table, the job listing is skipped and nothing is done (as we only want unique listings).

4. Clear the processed data folder and close the connection to the SQL database.

And that's it! We have nice and clean data ready in our Azure PostgreSQL flexible server ready to be consumed by Power BI.

See load.py for more details.

## 8. Automation

After first running the pipeline manually to extract the base data for my SQL table and analysis, I scheduled the full pipeline to run twice per day fully automatically (once at 8 AM and once at 4 PM).

This was simply done by setting up a cron job on the Linux VM and giving it the proper rights to execute the scripts.

As a result, my SQL database and the connected Power BI dashboard keeps updating automatically every day with fresh Data Engineer job listings data! 

## 9. Results and Analysis

All in all, I extracted about ~300 Data Engineer job listings where location was defined as the United States. I sorted the results by date before extracting, that way I'd always get only new data.

![image](https://github.com/user-attachments/assets/1db0a74e-88e1-419a-a8aa-35ea2a42abf7)

The results were pretty interesting. Some key findings:

* Only 24 out of 304 jobs were posted as **fully remote**.
* An overwhelming majority, 216 jobs, were posted as **full-time**.
* Yearly salaries ranged all the way from around **$52K** to as high as **$720K**!
* Median salary was **$140K**, whereas average salary was a bit higher, **$144K**.
* For jobs where hourly rates were mentioned, low end was about **32 $/h**, average **58 $/h** and max hour rate **108 $/h**.

Maybe even more interesting were the top 10 skills that were mentioned across most job ads (see image above).

More than **80% of jobs mentioned SQL** as a key skill, **73% mentioned Python** and **57% mentioned AWS**.

Other tech skills that fit into the top 10 were Scala, Azure, Spark, Git, ORC, Java and GCP. I think it's fair to say that these are probably the foundational tech skills every data engineer needs to know at some level to be hireable. So it could be a good idea to master these first!

What's also interesting are some skills that are maybe less frequently mentioned than I would've expected. For example, only **19% mentioned Power BI** and **15% mentioned R** as a wanted skill. Some (up-and-coming?) Microsoft technologies that I've been studying myself are **Azure Synapse Analytics** and **Fabric**. These were only mentioned in **~4%** and **~8%** of job ads, respectively.

I also did a quick location-dependent average salary analysis. As expected, the highest average salaries can be found from big tech hubs and on the coasts (SF, NY, TX). But plenty of jobs with mid-ranged salaries also elsewhere across the US. In fact, most jobs come with a salary well above > $100K per year, and not so many that are below this threshold.

![image](https://github.com/user-attachments/assets/055ef808-a793-4c72-8a37-72fab56d8d53)

## 10. Future Work

There are many things that could still be done in the future for a more comprehensive analysis:

* Extracting also the job posting date (was not as easy as I thought at first) would allow for time series analysis across weeks, months or years
* Better splitting of location into cities and states separately would allow for multi-level geographical analysis
* The same analysis could be extrapolated to other countries, e.g. in Europe
