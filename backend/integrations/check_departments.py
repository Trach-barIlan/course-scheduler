import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://courses.biu.ac.il/"
CHROMEDRIVER_PATH = "/opt/homebrew/bin/chromedriver"
CHROME_BINARY_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

chrome_options = Options()
chrome_options.binary_location = CHROME_BINARY_PATH
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Start Chrome
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)
wait = WebDriverWait(driver, 20)

try:
    driver.get(TARGET_URL)
    
    # Wait for the department dropdown to load
    dept_select_element = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_cmbDepartments")))
    dept_select = Select(dept_select_element)
    
    print("Available departments:")
    print("=====================")
    
    # Get all options from the dropdown
    for option in dept_select.options:
        value = option.get_attribute("value")
        text = option.text.strip()
        if value and text:  # Skip empty options
            print(f"Value: {value} | Name: {text}")
    
    print("\nTo scrape a different department, change DEPARTMENT_VALUE in the scraper to one of the values above.")
    
except Exception as e:
    print(f"Error getting departments: {e}")
finally:
    driver.quit()
