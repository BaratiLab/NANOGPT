import os
import json
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import FullDoc
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from get_doi import get_doi_from_title

def elsapy(user_input):
    def format_query(query):
        """Format the user query to be URL-friendly."""
        return query.strip().replace(' ', '+')
    
    # Load environment variables from the .env file
    load_dotenv()

    # Format the query
    formatted_query = format_query(user_input)

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Initialize the Chrome driver
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver = webdriver.Chrome(
    service=Service("/home/ach/.wdm/drivers/chromedriver/linux64/131.0.6778.87/chromedriver-linux64/chromedriver"),
    options=chrome_options
)


    # Navigate to the URL
    driver.get(f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C39&as_ylo=2010&as_yhi=2024&q={formatted_query}+source%3Aelsevier&btnG=")

    # Wait for the page to load completely
    driver.implicitly_wait(10)

    # Get the page source
    page_source = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract all URLs containing '/article/pii/'
    suffixes = []
    for index, link in enumerate(soup.find_all('a', href=True)):
        if '/article/pii/' in link['href']:
            if index % 2 == 0:  # Skip every other URL starting with the first one
                suffix = link['href'].split('/article/pii/')[1]
                suffixes.append(suffix)
                if index == 10:
                    break

    def save_full_text(pii_list):
        """Save the full text documents retrieved from Elsevier API."""
        # Create directory for saving documents
        save_dir = "/home/ach/Downloads/NANOGPT_DEMO/query_docs"
        os.makedirs(save_dir, exist_ok=True)

        # Load API key from environment variables
        api_key = os.getenv('ELSEVIER_API_KEY')
        if not api_key:
            raise ValueError("API key is not set in environment variables.")

        # Initialize client
        client = ElsClient(api_key)
        
        for pii in pii_list:
            # Initialize document with PII
            full_doc = FullDoc(sd_pii=pii)
            
            # Read the full document
            if full_doc.read(client):
                doi = get_doi_from_title(full_doc.title)
                filename = doi.replace('/', '_') + '.json'  # Replace '/' with '_' for valid filename
                # Save the document locally
                filepath = os.path.join(save_dir, filename)
                with open(filepath, 'w') as outfile:
                    json.dump(full_doc.data, outfile)
                print(f"Saved {full_doc.title} to {filepath}")
            else:
                print(f"Failed to read document with PII: {pii}")

    # Save the full texts using the suffixes obtained
    save_full_text(suffixes)
