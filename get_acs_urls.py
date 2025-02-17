from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import os
def scrape_and_extract_acs_urls(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Initialize the Chrome driver
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver = webdriver.Chrome(
    service=Service("/home/ach/.wdm/drivers/chromedriver/linux64/131.0.6778.87/chromedriver-linux64/chromedriver"),
    options=chrome_options
)


    # Navigate to the URL
    driver.get(url)

    # Wait for the page to load completely
    driver.implicitly_wait(10)

    # Get the page source
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all instances of the pattern
    pattern = re.compile(r'/doi/full/10\.\d{4}/acs\w+\.\d+[a-z\d]+')
    matches = pattern.findall(str(soup))

    # Get the first 5 unique instances and prefix them with the base URL
    urls = []
    for match in matches[:1]:
        full_url = f"https://pubs.acs.org{match}"
        urls.append(full_url)

    # Close the browser
    driver.quit()

    return urls

# Example usage
def format_acs_query(user_input):
    # Remove leading/trailing spaces and replace internal spaces with '+'
    formatted_query = user_input.strip().replace(' ', '+')
    return formatted_query

def scrape_and_save_acs_html(url, save_directory):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Extract the DOI from the URL and format the filename
    doi = url.split('/doi/full/')[-1]
    filename = doi.replace('/', '_') + ".html"
    
    # Combine the save directory with the filename
    filepath = os.path.join(save_directory, filename)

    # Navigate to the URL
    driver.get(url)

    # Wait for the page to load completely
    driver.implicitly_wait(10)

    # Get the page source
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Save the prettified HTML to a file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    # Close the browser
    driver.quit()