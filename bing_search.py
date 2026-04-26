import time
import random
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Minimum and maximum delay (in seconds) between searches
MIN_DELAY_SECONDS = 6
MAX_DELAY_SECONDS = 12

# Edge driver wait timeout
EDGE_DRIVER_TIMEOUT = 7

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

def login_to_current_user(driver):
    """
    Ensures the browser is logged in as the current Windows user (Edge profile).
    If Edge is started with the default profile, it should be logged in automatically.
    This function can be extended for more advanced login if needed.
    """
    # For most Windows setups, Edge will use the current user's profile and be logged in automatically.
    # If not, you can add logic here to handle login, e.g., navigating to login.microsoftonline.com.
    print("Assuming Edge is using the current Windows user profile (automatic login).")

def auto_accept_cookies(driver):
    """
    Tries to auto-accept all cookies popups for the current page (Bing and common consent banners).
    """
    try:
        # Try Bing's cookie accept button
        accept_selectors = [
            (By.ID, "bnp_btn_accept"),  # Bing
            (By.XPATH, "//input[@id='onetrust-accept-btn-handler']"),  # OneTrust
            (By.XPATH, "//button[contains(., 'Accept') or contains(., 'accept')]"),
            (By.XPATH, "//button[contains(., 'Agree') or contains(., 'agree')]"),
        ]
        for by, selector in accept_selectors:
            try:
                elem = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((by, selector))
                )
                elem.click()
                print(f"Accepted cookies with selector: {selector}")
                break
            except Exception:
                continue
    except Exception as e:
        print(f"No cookie banner accepted or error: {e}")
  
def main():
    # --- WebDriver Setup ---

    driver = None # Initialize driver to None

    try:
        # --- Attempt to initialize Microsoft Edge WebDriver ---
        try:
            print("Attempting to start Microsoft Edge WebDriver...")
            driver = webdriver.Edge()
            driver.maximize_window()
            print("Microsoft Edge WebDriver started successfully.")
        except Exception as e_edge:
            print(f"Could not start Microsoft Edge WebDriver: {e_edge}")
            print("Please ensure you have msedgedriver.exe installed and configured correctly.")
            print("Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            if driver:
                driver.quit()
            return

        # Read the topics from a text file
        KEYWORDS = read_file_to_list("topics.txt")
        if not KEYWORDS:
            print("No topics found in topics.txt. Please add topics to search.")
            driver.quit()
            return
        print(KEYWORDS)

        # Automatic login (current user)
        login_to_current_user(driver)

        # Navigate to Bing
        print(f"Navigating to {BING_URL}...")
        driver.get(BING_URL)

        # Auto-accept cookies on Bing home page
        auto_accept_cookies(driver)

        # --- Loop through keywords and perform searches ---
        for i, keyword in enumerate(KEYWORDS):
            print(f"\nSearching for keyword ({i+1}/{len(KEYWORDS)}): '{keyword}'")

            try:
                # Find the search input field. Bing's search bar usually has id "sb_form_q"
                # Wait for the search box to be present
                search_box = WebDriverWait(driver, EDGE_DRIVER_TIMEOUT).until(
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

                # Wait for search results to load
                WebDriverWait(driver, EDGE_DRIVER_TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, "b_results"))
                )
                print(f"Search results for '{keyword}' loaded.")

                # Auto-accept cookies on results page (if any pop up again)
                auto_accept_cookies(driver)

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
        if driver:
            driver.quit()
    finally:
        # --- Close the browser ---
        if driver:
            print("Closing the browser...")
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main()