from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# URL to test
test_url = "https://www.google.com"

# Path to ChromeDriver (should be in /usr/local/bin if installed as in the Dockerfile)
chrome_driver_path = "/usr/local/bin/chromedriver"

# Set Chrome options for headless mode (no GUI)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-gpu')  # Disables GPU hardware acceleration

# Start ChromeDriver
driver_service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=driver_service, options=options)

try:
    # Open the test URL
    driver.get(test_url)

    # Wait for the page to load
    time.sleep(3)

    # Find the search box element by its name attribute (Google's search box)
    search_box = driver.find_element(By.NAME, "q")

    # Print if we found the element, proving the page loaded
    if search_box:
        print(f"Successfully loaded {test_url} and found search box.")
    else:
        print(f"Failed to load {test_url} or find the search box.")

finally:
    # Quit the driver to free resources
    driver.quit()
