import os
from dotenv import load_dotenv
from companies_house_api_client import CompaniesHouse
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Create a Companies House API client instance
ch = CompaniesHouse()

# Prepare to store results
found_companies = []

# Define the search parameters
search_query = " "  # Replace with your search term (e.g., part of the company name)

try:
    # Call the search method (make sure the method name matches your client)
    response = ch.search_companies(search_query)  # Adjust to actual search method
    if response.status_code == 200:
        results = response.json().get('items', [])
        
        # Iterate over results and filter by type
        for company in results:
            if company.get('type') == 'ltd':  # Filter for private limited companies
                found_companies.append(company)

        # Print results
        for company in found_companies:
            print(f"Company Name: {company['company_name']}, Company Number: {company['company_number']}, Date of Creation: {company['date_of_creation']}")

    else:
        print(f"Error: Received response code {response.status_code}")

except Exception as e:
    print(f"An error occurred: {e}")
