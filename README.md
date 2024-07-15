# AI-Powered Database Query App - API

## Overview

Welcome to the backend API for the AI-powered database query application. This API is designed to handle user queries in natural language, process them using Natural Language Processing (NLP), and execute SQL queries to retrieve relevant data from the database.

## Table of Contents

1. [Data Engineering and Processing](#data-engineering-and-processing)
2. [API Functionalities](#api-functionalities)
3. [Key Challenges](#key-challenges)
4. [Potential Improvements](#potential-improvements)
5. [Setup and Installation](#setup-and-installation)
6. [Usage](#usage)
7. [API Endpoints](#api-endpoints)
8. [Environment Variables](#environment-variables)

## Data Engineering and Processing

### Main Steps and Motivation
	
1. **Data Cleaning**:
    - **Motivation**: Ensure data consistency and integrity.
    - **Steps**:
        - Format dates to a standard format.
	    - Replace empty values with null for standardization.
	    - Remove duplicate entries for clean data.

2. **Data Enrichment**:
    - **Motivation**: Enhance data usability and query capability.
    - **Steps**:
        - Use NLP to tag event industries based on event names and descriptions.
        - Generate emails based on name patterns and company domains for email-related queries.
	    - Generate event industry using LLM for event industry-related queries.
	    - Standardize company revenue to numeric values for arithmetic or comparison operations in database queries.
	    - Clean and split `n_employees` column into `max_employees` and `min_employees` of numeric type for queries like companies that have a number of employees above or below a certain threshold.

## API Functionalities

### Main Functionalities

1. **Natural Language Query Processing**:
    - Converts user queries in natural language into structured SQL queries.

2. **SQL Query Execution**:
    - Executes SQL queries to retrieve data based on user input.

3. **Error Handling**:
    - Provide error handling to manage query failures.

4. **Data Retrieval**:
    - Fetch and return data in a structured format based on user queries.

## Key Challenges

### Challenges Faced

1.	**No Prior LLM Knowledge**:
    -	Learning to use large language models (LLMs) effectively from scratch.

2.	**General Code Bugs**:
    - Debugging and fixing issues in the codebase.

3.	**Finding the Right LLM**:
    -	Identifying and selecting the most suitable LLM for the application.

4.	**Using and Debugging LLM Code**:
    -	Integrating and debugging code to use the LLM.

5.	**Formatting LLM Response**:
    -	Ensuring the responses from LLMs are correctly formatted for further processing.

6.	**NLP Parsing**:
    -	Ensuring accurate or optimal SQL queries from natural language queries.

7.	**Optimizing Prompt and Database**:
    -	Refining prompts and optimizing the database for better performance and results.

## Potential Improvements

### Improvements with More Time

1. **Enhanced NLP Model**:
    - Improve the accuracy of the NLP model by training it with more diverse and extensive datasets.

2. **Caching Mechanism**:
    - Implement caching for frequent queries to improve response time and reduce database load.

3. **Advanced Error Handling**:
    - Develop more sophisticated error handling mechanisms to provide detailed feedback and suggestions to users.

4. **Scalability Enhancements**:
    - Optimize the backend to handle larger datasets and higher query volumes more efficiently.

5. **Support for Non-Database Related Queries**:
	- Extend the capabilities to handle and return results for queries that do not directly involve the database.

6. **Chat-Based Results for Multiple Queries**:
	- Implement a chat interface that allows users to ask multiple related queries in a conversational manner.

7. **Fine-Tuning**:
	- Fine-tune the LLM to better understand and respond to domain-specific queries.

## Setup and Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Steps

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the project root and add the following environment variables:

   ```
   OPENAI_API_KEY=your_openai_api_key
   DB_HOST=localhost
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   ```

5. **Run the Application**

   ```bash
   python app.py
   ```

## Usage

To use the backend service, send a POST request to the `/query` endpoint with the user query in the request body. The backend will process the query, execute the corresponding SQL command, and return the results.

## API Endpoints

### `/query` [POST]

- **Description**: Handles user queries and returns the results.
- **Request Body**:

  ```json
  {
    "query": "Find me companies attending Oil & Gas related events"
  }
  ```

- **Response**:

  ```json
  [
    {
      "company_name": "Company A",
      "event_name": "Oil & Gas Expo 2023",
      ...
    },
    ...
  ]
  ```