import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup


IDS = [
# # "89110", big
# "891111",
# "89112",
# "89113",
# "89132",
# "89133",
# "891195",
# # "891200", big
# "891262",
# "89230",
# "89231",
# "89263",
# "892197",
# "89220",
# "892226",
# "89213",
# "892511",

# "89333", no

# "892322",
# "89385",
# "893311",
# "893210",
# "893312",
# "895581",
# "895509",
# "895570",
# "895656",
# "89200",
# "89214",
# "89256",
# "893226",
# "893592",
# "89512",
# "89518",

# "89528", no
# "895222", no

# "895223",
# "895224",
# "895227",
# "895229",
# "895350",
# "89542",
# "89546",

# "89547", no

# "89550",
# "89553",

# "895555", no

# "89560",
# "89561",

# "89575", no

# "895993",
# "89602",

# "89604", no

# "896561",
# "89669",
# "89679",
# "89680",
# "89685",
# "896876",
]
DEPARTMENT_VALUE = "1"

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

# Ensure CSV folder exists
csv_dir = "csv"
os.makedirs(csv_dir, exist_ok=True)



driver.get(TARGET_URL)

# Select department 84 from dropdown
dept_select = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_cmbDepartments"))))
dept_select.select_by_value(DEPARTMENT_VALUE)

# Submit the form
submit_button = driver.find_element(By.ID, "ContentPlaceHolder1_btnSearch")
submit_button.click()

# Wait for captcha to be solved and page to load
print("Waiting for page to load after captcha (if any)...")
time.sleep(5)  # Give time for manual captcha solving

# Check what's on the page and wait for results
try:
    wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_gvLessons")))
    print("Results table found!")
except:
    print("Results table not found. Let's check what's on the page...")
    print("Page title:", driver.title)
    print("Current URL:", driver.current_url)
    
    # Try to find any table elements
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Found {len(tables)} table(s) on the page")
    
    # Try to find the specific div that might contain results
    content_divs = driver.find_elements(By.ID, "ContentPlaceHolder1")
    if content_divs:
        print("Found ContentPlaceHolder1 div")
    
    # Check for any error messages or captcha
    page_source_snippet = driver.page_source[:1000]
    if "captcha" in page_source_snippet.lower() or "robot" in page_source_snippet.lower():
        print("Captcha might still be present")
    
    # Take a screenshot for debugging
    driver.save_screenshot("debug_page.png")
    print("Saved screenshot as debug_page.png")
    
    # Exit gracefully
    driver.quit()
    exit()

i = 2
page_number = 1

while True:
    time.sleep(1)  # Ensure full load

    # Extract table HTML
    table_elem = driver.find_element(By.ID, "ContentPlaceHolder1_gvLessons")
    table_html = table_elem.get_attribute("outerHTML")


    try:
        soup = BeautifulSoup(table_html, "html.parser")
        table = soup.find("table")

        csv_rows = []
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 6:
                continue

            cell_text = cells[5].get_text(strip=True)
            if "סמסטר" not in cell_text:
                continue

            processed_row = []
            for cell in cells:
                # Replace <br> with newline manually
                for br in cell.find_all("br"):
                    br.replace_with(";")

                text = cell.get_text(strip=True)
                clean_text = text.replace(",", ";").replace("\r", ";").replace("\n", ";")
                processed_row.append(clean_text)

            csv_rows.append(",".join(processed_row))

        if csv_rows:
            csv_path = f"{csv_dir}/department_{DEPARTMENT_VALUE}_page_{page_number}.csv"
            with open(csv_path, "w", encoding="utf-8-sig") as f:
                f.write("\n".join(csv_rows))
            print(f"Saved page {page_number} → {csv_path}")
        else:
            print(f"No valid rows on page {page_number}")

    except Exception as e:
        print(f"Failed to parse table on page {page_number}: {e}")
        

    # try:
    #     df = pd.read_html(table_html)[0]

    #     # Clean DataFrame:
    #     def clean_cell(val):
    #         if isinstance(val, str):
    #             return val.strip().replace("\n", ";").replace(",", ";")
    #         return val

    #     df = df.applymap(clean_cell)

    #     # Keep rows where 6th column (index 5) contains "סמסטר"
    #     df_filtered = df[df.iloc[:, 5].astype(str).str.contains("סמסטר")]

    #     csv_path = f"{csv_dir}/department_{DEPARTMENT_VALUE}_page_{page_number}.csv"
    #     df_filtered.to_csv(csv_path, index=False, header=False)
    #     print(f"Saved page {page_number} → {csv_path}")

    # except Exception as e:
    #     print(f"Failed to parse table on page {page_number}: {e}")
    #     break


    # Try to find pagination link for page i (starting from 2)
    try:
        table_rows = table_elem.find_elements(By.TAG_NAME, "tr")
        last_row = table_rows[-1]

        a_elements = last_row.find_elements(By.TAG_NAME, "a")
        
        # Try to find direct match with current page number
        page_link = None
        for a in a_elements:
            if a.text.strip() == str(i):
                page_link = a
                break

        # If no direct match, look for "..." links for pagination
        if not page_link:
            dotdot_links = [a for a in a_elements if "..." in a.text.strip()]
            
            # Check if there is more than one "..." link
            if len(dotdot_links) > 1:
                page_link = dotdot_links[-1]  # Use the LAST one
            elif len(dotdot_links) == 1:
                page_link = dotdot_links[0]  # Use the only one available
            else:
                # If no "..." link found, stop the pagination process
                print("No '...' link found, stopping pagination.")
                break

        if page_link:
            i += 1
            page_number += 1
            
            # Scroll the element into view first
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", page_link)
                time.sleep(1)  # Wait for scroll to complete
            except Exception as scroll_error:
                print(f"Scroll failed: {scroll_error}")
            
            # Try multiple click strategies
            click_success = False
            
            # Strategy 1: Regular click
            try:
                page_link.click()
                click_success = True
                print(f"Regular click successful for page {i}")
            except Exception as click_error:
                print(f"Regular click failed: {click_error}")
                
                # Strategy 2: JavaScript click
                try:
                    driver.execute_script("arguments[0].click();", page_link)
                    click_success = True
                    print("JavaScript click successful")
                except Exception as js_error:
                    print(f"JavaScript click failed: {js_error}")
                    
                    # Strategy 3: ActionChains click
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(driver)
                        actions.move_to_element(page_link).click().perform()
                        click_success = True
                        print("ActionChains click successful")
                    except Exception as action_error:
                        print(f"ActionChains click failed: {action_error}")
                        
                        # Strategy 4: Send Enter key to the element
                        try:
                            from selenium.webdriver.common.keys import Keys
                            page_link.send_keys(Keys.ENTER)
                            click_success = True
                            print("Enter key successful")
                        except Exception as enter_error:
                            print(f"Enter key failed: {enter_error}")
            
            if not click_success:
                print(f"All click strategies failed for page {i}. Stopping pagination.")
                break
                
            time.sleep(2)  # Longer wait after click
        else:
            break  # No valid link found, end pagination

    except Exception as e:
        print(f"Pagination ended or error on page {page_number}: {e}")
        break


driver.quit()



# for lesson_id in IDS:
#     driver.get(TARGET_URL)

#     # Fill the input field
#     input_box = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txLessonCode")))
#     input_box.clear()
#     input_box.send_keys(lesson_id)

#     # Click the submit button and wait for navigation
#     submit_button = driver.find_element(By.ID, "ContentPlaceHolder1_btnSearch")
#     submit_button.click()

#     # Wait for the results table
#     wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_gvLessons")))
#     time.sleep(1)  # extra delay to ensure full load if needed

#     # Extract table HTML
#     table_elem = driver.find_element(By.ID, "ContentPlaceHolder1_gvLessons")
#     table_html = table_elem.get_attribute("outerHTML")

#     # Parse HTML table with pandas
#     try:
#         df = pd.read_html(table_html)[0]
#         # Optional: drop header row if necessary
#         # df = df.iloc[1:]
#         csv_path = f"csv/{lesson_id}.csv"
#         df.iloc[1:].to_csv(csv_path, index=False, header=None)
#         print(f"Saved CSV for ID {lesson_id} → {csv_path}")
#     except Exception as e:
#         print(f"Failed to parse table for ID {lesson_id}: {e}")

# driver.quit()



"""
chromium-chromedriver

google-chrome --version
chromedriver --version


which google-chrome
which chromedriver
"""