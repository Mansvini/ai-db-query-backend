from flask import Flask, request, jsonify
import psycopg
from openai import OpenAI
import os
from dotenv import load_dotenv
from flask_cors import CORS
import logging

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Database connection
def get_db_connection():
    logging.debug("Connecting to the database...")
    conn = psycopg.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        row_factory=psycopg.rows.dict_row
    )
    logging.debug("Database connection established.")
    return conn

# Convert natural language query to SQL
def parse_user_query(user_query):
    logging.debug(f"Parsing user query: {user_query}")
    try:
        # Provide the schema details and instructions in the system message
        
        schema_description = """
        You are a helpful assistant that converts natural language queries into SQL based on the following database schema and sample data:

        Tables and Sample Data:
        - events (event_id, event_logo_url, event_name, event_start_date, event_end_date, event_venue, event_country, event_description, event_url, event_industry)
          Example:
          - event_id: 1, event_name: 'World University Expo', event_start_date: '2023-05-20', event_end_date: '2023-05-22', event_venue: 'SUNTEC Convention Centre', event_country: 'USA', event_description: 'Join our World University Expo', event_url: 'http://expo.overseaseducation.sg/', event_industry: 'Education'

        - companies (company_id, company_name, company_phone, company_address, company_industry, company_overview, homepage_url, linkedin_company_url, homepage_base_url, company_logo_url_on_event_page, company_logo_url, company_logo_match_flag, company_logo_text, relation_to_event, company_revenue, min_employees, max_employees, company_founding_year, event_url)
          Example:
          - company_id: 1, company_name: 'Kerry Consulting', company_phone: '(656) 333-8530', company_address: '6 Temasek Blvd 31, Singapore 038986, SG', company_industry: 'Staffing and Recruiting', homepage_url: 'https://www.kerryconsulting.com/', homepage_base_url: 'kerryconsulting.com', event_url: 'https://apac.commoditytradingweek.com/'

        - people (person_id, first_name, middle_name, last_name, job_title, person_city, person_state, person_country, email_pattern, email, homepage_base_url, duration_in_current_job, duration_in_current_company)
          Example:
          - person_id: 1, first_name: 'Rohail', last_name: 'Khan', job_title: 'Sales Account Manager', email: 'rkhan@isaca.org', homepage_base_url: 'isaca.org'

        Relationships:
        - companies.event_url references events.event_url
        - people.homepage_base_url references companies.homepage_base_url

        Note: Use PostgreSQL syntax and give only the resultant query as response.
        - Use LOWER and LIKE to search text fields.
        - Events can be referred to as conferences, summits, fairs, expos, shows, seminars or similar names.

        Examples of natural language queries and corresponding SQL queries:
        1. Natural Language: Find companies attending technology conferences over the next 6 months.
           SQL: SELECT * FROM companies JOIN events ON companies.event_url = events.event_url WHERE LOWER(events.event_industry) LIKE '%technology%' AND events.event_start_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '6 months';

        2. Natural Language: List marketing managers working for companies attending AI and machine learning events.
           SQL: SELECT people.* FROM people JOIN companies ON people.homepage_base_url = companies.homepage_base_url JOIN events ON companies.event_url = events.event_url WHERE LOWER(events.event_industry) LIKE '%ai%' OR LOWER(events.event_industry) LIKE '%machine learning%' AND LOWER(people.job_title) LIKE '%marketing manager%';

        3. Natural Language: Which events are being attended by companies with more than 500 employees?
           SQL: SELECT events.* FROM events JOIN companies ON events.event_url = companies.event_url WHERE companies.max_employees > 500;

        4. Natural Language: Get the email addresses of CTOs working in tech companies.
           SQL: SELECT people.email FROM people JOIN companies ON people.homepage_base_url = companies.homepage_base_url WHERE LOWER(companies.company_industry) LIKE '%tech%' AND LOWER(people.job_title) LIKE '%cto%';

        Given this information, convert the following natural language query to an SQL query:
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": schema_description},
                {"role": "user", "content": user_query}
            ]
        )
        print(response.choices[0].message.content.strip())
        sql_query = response.choices[0].message.content.strip()
        # Remove any Markdown formatting
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        logging.debug(f"Generated SQL query: {sql_query}")
        return sql_query
    except Exception as e:
        logging.error(f"Error parsing user query: {e}")
        return None

@app.route('/query', methods=['POST'])
def query():
    logging.debug("Query endpoint hit.")
    if not request.is_json:
        logging.error("Request content type is not JSON.")
        return jsonify({"error": "Request content type must be application/json"}), 400

    user_query = request.json.get('query')
    if not user_query:
        logging.error("No query provided in the request.")
        return jsonify({"error": "No query provided"}), 400

    logging.debug(f"Received user query: {user_query}")

    sql_query = parse_user_query(user_query)
    if not sql_query:
        logging.error("Failed to generate SQL query.")
        return jsonify({"error": "Failed to generate SQL query"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        logging.debug(f"Executing SQL query: {sql_query}")
        cursor.execute(sql_query)
        results = cursor.fetchall()
        logging.debug(f"Query results: {results}")
        return jsonify(results)
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        logging.debug("Database connection closed.")

if __name__ == '__main__':
    logging.debug("Starting Flask app...")
    app.run(debug=True, port=int(os.environ.get("BACKEND_PORT", 3002)))