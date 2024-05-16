# YouTube Data Harvesting and Warehousing using SQL, MongoDB, and Streamlit

## Introduction
This project aims to harvest data from YouTube using the YouTube Data API, store it in both SQL and MongoDB databases, and provide a user-friendly interface for querying and analyzing the data using Streamlit.

## Technology Stack Used

1. Python
2. <span style="color:blue">PostgreSQL</span>
3. <span style="color:green">MongoDB</span>
4. <span style="color:red">Google Client Library</span>
5. <span style="color:orange">Streamlit</span>


## Features

- **YouTube Data Harvesting**: Utilizes the YouTube Data API to fetch data such as video details, statistics, comments, etc.
- **SQL and MongoDB Storage**: Data is stored in both SQL and MongoDB databases for flexibility and scalability.
- **Streamlit Dashboard**: Provides a user-friendly interface built with Streamlit for querying and visualizing the data.

## Project Overview

1. Begin by implementing a Streamlit application using the Python library "streamlit", offering a user-friendly interface for users to input a YouTube channel ID, explore channel details, and choose channels for migration.

2. Establish a connection to the YouTube API V3 to access channel and video data. This involves leveraging the Google API client library for Python.

3. Implement a method to retrieve data from the previously called API and store it in a MongoDB data lake. MongoDB is selected for its adeptness in handling unstructured and semi-structured data. Data is stored in three distinct collections within the database.

4. Transfer the collected data from various channels, including channels, videos, and comments, to a SQL data warehouse. This involves utilizing a SQL database such as MySQL or PostgreSQL.

5. Employ SQL queries to perform table joins within the SQL data warehouse and retrieve specific channel data based on user input. Properly defining foreign and primary keys within the SQL table is essential for this step.

6. Develop a dashboard using Streamlit, integrating the retrieved data. Offer dropdown options on the dashboard to enable users to select a question from the menu for data analysis. Present the analysis output in a DataFrame Table format.

## Final Output
![Intro GUI](https://github.com/DineshR03/YouTube-Data-Harvesting-and-Warehousing-using-SQL-MongoDB-and-Streamlit/blob/main/Youtube_project_Final_UI_Output.png)

## License

This project is licensed under the [MIT License](LICENSE).
