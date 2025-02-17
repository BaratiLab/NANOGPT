from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import os
import string

def scrape_and_extract_nature_urls(url):
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


    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Get the page source
        page_source = driver.page_source

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all instances of the pattern that contain 'springeropen.com/articles'
        pattern = re.compile(r'springeropen\.com/articles/\S+')
        matches = pattern.findall(str(soup))

        # Clean up any extraneous characters and get the first 5 unique matches
        unique_urls = []
        for match in matches:
            cleaned_url = match.rstrip('"')
            cleaned_url= f"https://{cleaned_url}"
            if cleaned_url not in unique_urls:
                unique_urls.append(cleaned_url)
            if len(unique_urls) == 1:
                break

    finally:
        # Close the browser
        driver.quit()

    return unique_urls

# # Example usage
# def format_nature_query(user_input):
#     # Remove leading/trailing spaces and replace internal spaces with '+'
#     formatted_query = user_input.strip().replace(' ', '+')
#     return formatted_query


def format_nature_query(user_input):
    # Remove punctuation
    no_punctuation = user_input.translate(str.maketrans('', '', string.punctuation))
    # Remove leading/trailing spaces and replace internal spaces with '+'
    formatted_query = no_punctuation.strip().replace(' ', '+')
    return formatted_query
