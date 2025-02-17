from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os

def scrape_and_save_nature_html(url, save_directory):
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


    # Extract the DOI from the URL and format the filename
    doi = url.split('/articles/')[-1]
    filename = doi.replace('/', '_') + ".txt"
    
    # Combine the save directory with the filename
    filepath = os.path.join(save_directory, filename)

    # Navigate to the URL
    driver.get(url)

    # Wait for the page to load completely
    driver.implicitly_wait(10)

    # Get the page source
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'lxml')

    # Extract and clean the text from the HTML
    text = soup.get_text()
    cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])

    # Save the cleaned text to a file
    with open(filepath, 'w', encoding='utf-8') as text_file:
        text_file.write(cleaned_text)

    # Close the browser
    driver.quit()
