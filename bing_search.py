import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService # For specifying EdgeDriver path

# Minimum and maximum delay (in seconds) between searches
MIN_DELAY_SECONDS = 5
MAX_DELAY_SECONDS = 15

# URL for Bing
BING_URL = "https://www.bing.com"

def read_file_to_list(file_path):
    """
    Reads a text file and returns a list of strings, 
    where each string is a line from the file.

    :param file_path: Path to the text file
    :return: List of strings
    """
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        # Remove newline characters from each line
        lines = [line.strip() for line in lines]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}")
    
    return lines

# --- WebDriver Setup ---
# Make sure you have the Microsoft Edge WebDriver (msedgedriver.exe) installed.
# Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
# Ensure msedgedriver.exe is in your system's PATH or provide the explicit path.

# Example using Microsoft Edge:
# If msedgedriver.exe is in your PATH, you can just use:
# driver = webdriver.Edge()
# Otherwise, provide the path to the executable:
# edge_driver_path = '/path/to/msedgedriver.exe'
# service = EdgeService(executable_path=edge_driver_path)
# driver = webdriver.Edge(service=service)

driver = None # Initialize driver to None

try:
    # --- Attempt to initialize Microsoft Edge WebDriver ---
    try:
        print("Attempting to start Microsoft Edge WebDriver...")
        # If msedgedriver.exe is in your PATH:
        # driver = webdriver.Edge()
        # If you need to specify the path to msedgedriver.exe:
        edge_driver_path = "C:\\Temp\\msedgedriver.exe" # Replace with your actual path
        service = EdgeService(executable_path=edge_driver_path)
        driver = webdriver.Edge(service=service)
        print("Microsoft Edge WebDriver started successfully.")
    except Exception as e_edge:
        print(f"Could not start Microsoft Edge WebDriver: {e_edge}")
        print("Please ensure you have msedgedriver.exe installed and configured correctly.")
        print("Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        exit()

    # Navigate to Bing
    print(f"Navigating to {BING_URL}...")
    driver.get(BING_URL)

    # Read the topics from a text file
    KEYWORDS = read_file_to_list("topics.txt")
    print(KEYWORDS)

    # Optional: Handle potential cookie consent pop-ups if they appear
    # This is a generic example, the actual selectors might differ.
    try:
        # Wait for a potential cookie consent button to be clickable and click it
        # Common IDs for cookie banners are "bnp_btn_accept", "L2AGLb" (Google), etc.
        # For Bing, it might be something like "bnp_container" or an accept button within it.
        # We'll use a more general approach by looking for buttons with "accept" or "agree" text.
        # This part is highly dependent on the current Bing UI.
        cookie_accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')] | //button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')] | //button[@id='bnp_btn_accept']"))
        )
        if cookie_accept_button:
            print("Cookie consent pop-up found. Clicking accept.")
            cookie_accept_button.click()
            time.sleep(2) # Wait a bit for the banner to disappear
    except Exception as e_cookie:
        print(f"No cookie consent pop-up found or could not click it: {e_cookie}")


    # --- Loop through keywords and perform searches ---
    for i, keyword in enumerate(KEYWORDS):
        print(f"\nSearching for keyword ({i+1}/{len(KEYWORDS)}): '{keyword}'")

        try:
            # Find the search input field. Bing's search bar usually has id "sb_form_q"
            # Wait for the search box to be present
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "sb_form_q"))
            )

            # Clear the search box (in case there's any pre-filled text from previous search)
            search_box.clear()

            # Type the keyword
            print(f"Typing '{keyword}' into the search box...")
            search_box.send_keys(keyword)

            # Submit the search (pressing Enter)
            print("Submitting search...")
            search_box.send_keys(Keys.RETURN) # or Keys.ENTER

            # Wait for search results to load (optional, but good practice)
            # You can wait for a specific element that appears on the results page.
            # For Bing, the search results are often within an element with id "b_results".
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "b_results"))
            )
            print(f"Search results for '{keyword}' loaded.")

        except Exception as e:
            print(f"An error occurred while searching for '{keyword}': {e}")
            # Optionally, you could try to refresh or navigate back to Bing's homepage
            # driver.get(BING_URL)
            # continue # Skip to the next keyword

        # --- Add a random delay before the next search (if not the last keyword) ---
        if i < len(KEYWORDS) - 1:
            delay = random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
            print(f"Waiting for {delay} seconds before next search...")
            time.sleep(delay)

    print("\nAll keywords have been searched.")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    # --- Close the browser ---
    if driver:
        print("Closing the browser...")
        driver.quit()
        print("Browser closed.")
