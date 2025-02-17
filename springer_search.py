from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def get_springer_search_results(query):
    # Format the query string for the URL
    formatted_query = query.replace(' ', '+')
    url = f"https://www.springeropen.com/search?query={formatted_query}&searchType=publisherSearch"
    
    # Set up headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (recommended for headless mode)

    # Initialize the Chrome driver with headless mode options
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver = webdriver.Chrome(
    service=Service("/home/ach/.wdm/drivers/chromedriver/linux64/131.0.6778.87/chromedriver-linux64/chromedriver"),
    options=chrome_options
)


    # Open the Springer search results page
    driver.get(url)

    # Wait for the page to fully load (you might need to wait more depending on your internet speed)
    driver.implicitly_wait(10)

    # Get the HTML content of the page
    html_content = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all the elements with data-test="title-link"
    title_links = soup.find_all('a', {'data-test': 'title-link'})

    # Extract the href attributes and return the top 4 URLs
    urls = []
    for link in title_links[:]:
        title_url = link.get('href')
        full_title_url = f"https:{title_url}" if title_url.startswith("//") else title_url
        urls.append(f"{full_title_url}")

    return urls

