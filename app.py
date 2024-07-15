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
        - events:
          - event_id: 1, event_logo_url: 'http://expo.overseaseducation.sg/v.fastcdn.co/u/0e18fcd3/57786581-0-Untitled-.png', event_name: 'World University Expo @ SUNTEC', event_start_date: '2023-05-20', event_end_date: '2023-05-22', event_venue: 'SUNTEC Convention Centre', event_country: 'Maryland, USA', event_description: 'Join our World University Expo this Saturday, 6 July 2024 12-6.30pm at SUNTEC whereby you can meet staff members of 50+ Renown Unis & Pathways from UK, Australia, Switzerland, USA & NZ etc. (Many travel from overseas for this event). Fantastic One-Stop Event for you to get all your queries answered and get an in-depth understanding of many Renowned Unis & Pathways.', event_url: 'http://expo.overseaseducation.sg/', event_industry: 'Education'
          - event_id: 2, event_logo_url: 'https://apac.commoditytradingweek.com/wp-content/uploads/2024/02/cropped-ctw-apac-main-2.png', event_name: 'Commodity Trading Week APAC', event_start_date: '2023-06-15', event_end_date: '2023-06-17', event_venue: 'Marina Bay Sands', event_country: 'Singapore', event_description: 'Commodity Trading Week APAC is the premier event in the Asia Pacific region for the commodity industry. It offers a platform for professionals across all sectors of commodity trading to network and gain insights.', event_url: 'https://apac.commoditytradingweek.com/', event_industry: 'Oil & Gas, Energy, Finance'

        - companies:
          - company_id: 1, company_name: 'Kerry Consulting', company_phone: '(656) 333-8530', company_address: '6 Temasek Blvd 31, Singapore 038986, SG', company_industry: 'Staffing and Recruiting', company_overview: '"Kerry Consulting Information Headquartered in Singapore since 2003, Kerry Consulting is Singapore's leading Search & Selection firm. Our consulting team is the most experienced, and amongst the largest, in the ASEAN region. We provide services to many of the world's leading companies and financial institutions. We are committed to creating positive long term outcomes for both our clients and our candidates. Our focus is on "Returning the Human to Resourcing". We believe that every organisation's success is largely determined by the quality of its people. Our ability to consistently provide high quality services to our clients is based on: • Trust • Energy • Market Knowledge • Continuity of relationship • Business understanding Our firm is staffed by professionals with extensive experience of and commitment to the region. Our structure is one which promotes teamwork, individual growth and organizational stability. Our aim is to become a trusted long term business partner rather than to be an intermittent service provider. View Top Employees from Kerry Consulting"', homepage_url: 'https://www.kerryconsulting.com/', linkedin_company_url: 'https://mz.linkedin.com/company/kerry-consulting/about', homepage_base_url: 'kerryconsulting.com', company_logo_url_on_event_page: 'https://apac.commoditytradingweek.com/wp-content/uploads/2022/03/KC_WEB_logo.png', company_logo_url: 'https://d1hbpr09pwz0sk.cloudfront.net/logo_url/kerry-consulting-b606c58b', company_logo_match_flag: 'yes', company_logo_text: 'Kerry Consulting', relation_to_event: 'sponsor', company_revenue: 12000000, min_employees: 114, max_employees: 114, company_founding_year: 2003, event_url: 'https://apac.commoditytradingweek.com/'
          - company_id: 2, company_name: 'HR Maritime', company_phone: '+41 22 732 57 00', company_address: '1-3 Rue De Chantepoulet, Geneva, Geneva 1201, CH', company_industry: 'Maritime Transportation', company_overview: 'HR Maritime is a Geneva based company providing services to the International Trading and Shipping industry. With a client base both within Switzerland and around the globe we offer guidance and implement tailored solutions to the range of problems besetting a company involved in the trading and shipping of commodities. We work with Commodity Traders, Importers and Exporters, Ship Owners and Managers, P&I Clubs, Insurance Underwriters, Trade Financiers, Lawyers and a number of associated service providers.', homepage_url: 'http://www.hr-maritime.com', linkedin_company_url: 'https://ch.linkedin.com/company/hr-maritime/about', homepage_base_url: 'hr-maritime.com', company_logo_url_on_event_page: 'https://apac.commoditytradingweek.com/wp-content/uploads/2022/03/HR_logo-2.png', company_logo_url: 'https://d1hbpr09pwz0sk.cloudfront.net/logo_url/hr-maritime-c13714f3', company_logo_match_flag: 'yes', company_logo_text: 'HR MARITIME', relation_to_event: 'partner', company_revenue: 2000000, min_employees: 2, max_employees: 10, company_founding_year: 2008, event_url: 'https://apac.commoditytradingweek.com/'

        - people:
          - person_id: 1, first_name: 'Rohail', middle_name: 'M', last_name: 'Khan', job_title: 'Sales Account Manager', person_city: 'Peshawar', person_state: 'Khyber Pakhtunkhwa', person_country: 'Pakistan', email_pattern: '[first_initial][last]', email: 'rkhan@isaca.org', homepage_base_url: 'isaca.org', duration_in_current_job: '11 years 6 months in role 11 years 6 months in company', duration_in_current_company: '11 years 6 months'
          - person_id: 2, first_name: 'Oscar', middle_name: 'Ruben', last_name: 'Sordo', job_title: 'Material Handler', person_city: 'Monroe', person_state: 'WA', person_country: 'US', email_pattern: '[first].[last]', email: 'oscar.sordo@collinsaerospace.com', homepage_base_url: 'collinsaerospace.com', duration_in_current_job: '2 years in role 2 years in company', duration_in_current_company: '2 years'

        Relationships:
        - companies.event_url references events.event_url
        - people.homepage_base_url references companies.homepage_base_url

        Note: Use PostgreSQL syntax and give only the resultant query as response.
        - Use LOWER and LIKE to search text fields.
        - If the query is related to company_industry, then search company_industry from company_overview and company_industry.
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