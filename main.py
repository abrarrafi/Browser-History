import requests
import pandas as pd
from datetime import datetime

# Constants
API_KEY = ""  # Replace with your Companies House API key
BASE_URL = "https://api.company-information.service.gov.uk"

# Input criteria
company_type = "ltd"  # Private Limited Company
incorporation_year = input("Enter incorporation year (e.g., 2021): ")
officer_residence_country = ["England", "United Kingdom"]
date_from = input("Enter 'Accounts Due from' date (YYYY-MM-DD): ")
date_to = input("Enter 'Accounts Due to' date (YYYY-MM-DD): ")
output_file = "company_due_report.xlsx"

# Function to get companies data
def get_company_data(company_number):
    url = f"{BASE_URL}/company/{company_number}"
    response = requests.get(url, auth=(API_KEY, ''))
    return response.json() if response.status_code == 200 else None

# Function to get officers data
def get_officers_data(company_number):
    url = f"{BASE_URL}/company/{company_number}/officers"
    response = requests.get(url, auth=(API_KEY, ''))
    if response.status_code != 200:
        return None
    
    officers = response.json().get('items', [])
    non_uk_officers = [officer['nationality'] for officer in officers 
                       if officer.get('country_of_residence') not in officer_residence_country]
    return non_uk_officers

# Function to check if due date is within specified range
def is_due_date_within_range(due_date, start_date, end_date):
    due_date = datetime.strptime(due_date, "%Y-%m-%d")
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    return start_date <= due_date <= end_date

# Fetch companies
def fetch_due_companies():
    company_list = []
    url = f"{BASE_URL}/advanced-search/companies"
    
    params = {
        "company_type": company_type,
        "incorporation_from": f"{incorporation_year}-01-01",
        "incorporation_to": f"{incorporation_year}-12-31",
        "size": 50  # Adjust according to API rate limits
    }

    response = requests.get(url, params=params, auth=(API_KEY, ''))
    companies = response.json().get('items', []) if response.status_code == 200 else []
    print(companies)

    for company in companies:
        company_number = company['company_number']
        company_name = company['company_name']
        incorporation_date = company['date_of_creation']

        # Fetch officer details and check for non-UK officers
        non_uk_officers = get_officers_data(company_number)

        # Check Accounts and Confirmation Statement due dates
        accounts_due = company.get("accounts", {}).get("next_due")
        confirmation_due = company.get("confirmation_statement", {}).get("next_due")

        due_type = []
        if accounts_due and is_due_date_within_range(accounts_due, date_from, date_to):
            due_type.append("Accounts")
        if confirmation_due and is_due_date_within_range(confirmation_due, date_from, date_to):
            due_type.append("Confirmation Statement")
        
        if due_type:
            company_list.append({
                "Company No": company_number,
                "Company Name": company_name,
                "Non-British Officers' Nationalities": ", ".join(non_uk_officers) if non_uk_officers else "None",
                "Due Dates": ", ".join(due_type),
                "Incorporation Date": incorporation_date
            })

    return company_list

# Main function to run the script
def main():
    print("Fetching data... This may take a few moments.")
    companies_data = fetch_due_companies()

    if not companies_data:
        print("No companies found matching the criteria.")
        return
    
    # Convert to DataFrame and save to Excel
    df = pd.DataFrame(companies_data)
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
