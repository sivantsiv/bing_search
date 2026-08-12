import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    Each selector attempt is wrapped individually so that a failure on one selector
    never prevents the remaining selectors from being tried.
    """
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


def create_driver():
    """
    Creates and returns a new Microsoft Edge WebDriver instance.
    Extracted into its own function to allow mocking in tests.

    :return: A Selenium Edge WebDriver instance
    """
    return webdriver.Edge()


def perform_search(driver, keyword, timeout=EDGE_DRIVER_TIMEOUT):
    """
    Performs a single Bing search for the given keyword.

    Waits for the search box, clears it, types the keyword, submits,
    and waits for the results page to load.

    :param driver: A Selenium WebDriver instance
    :param keyword: The search term to enter
    :param timeout: Maximum seconds to wait for page elements
    """
    try:
        # Wait for the search box to be present (Bing's search bar has id "sb_form_q")
        search_box = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "sb_form_q"))
        )

        # Clear the search box (in case there's any pre-filled text from a previous search)
        search_box.clear()

        # Type the keyword
        print(f"Typing '{keyword}' into the search box...")
        search_box.send_keys(keyword)

        # Submit the search (pressing Enter)
        print("Submitting search...")
        search_box.send_keys(Keys.RETURN)

        # Wait for search results to load
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "b_results"))
        )
        print(f"Search results for '{keyword}' loaded.")

        # Auto-accept cookies on results page (if any pop up again)
        auto_accept_cookies(driver)

    except Exception as e:
        print(f"An error occurred while searching for '{keyword}': {e}")


def run_searches(driver, keywords, timeout=EDGE_DRIVER_TIMEOUT,
                 min_delay=MIN_DELAY_SECONDS, max_delay=MAX_DELAY_SECONDS):
    """
    Iterates over the list of keywords and performs a Bing search for each one.
    Adds a random delay between searches to mimic human behaviour.

    :param driver: A Selenium WebDriver instance
    :param keywords: List of search terms
    :param timeout: Maximum seconds to wait for page elements
    :param min_delay: Minimum seconds to sleep between searches
    :param max_delay: Maximum seconds to sleep between searches
    """
    for i, keyword in enumerate(keywords):
        print(f"\nSearching for keyword ({i + 1}/{len(keywords)}): '{keyword}'")

        perform_search(driver, keyword, timeout)

        # Add a random delay before the next search (if not the last keyword)
        if i < len(keywords) - 1:
            delay = random.randint(min_delay, max_delay)
            print(f"Waiting for {delay} seconds before next search...")
            time.sleep(delay)

    print("\nAll keywords have been searched.")


def main():
    """Entry point: initialises Edge, loads keywords, navigates to Bing and runs searches."""
    driver = None

    try:
        # --- Attempt to initialise Microsoft Edge WebDriver ---
        try:
            print("Attempting to start Microsoft Edge WebDriver...")
            driver = create_driver()
            driver.maximize_window()
            print("Microsoft Edge WebDriver started successfully.")
        except Exception as e_edge:
            print(f"Could not start Microsoft Edge WebDriver: {e_edge}")
            print("Please ensure you have msedgedriver.exe installed and configured correctly.")
            print("Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            return

        # Read the topics from a text file
        keywords = read_file_to_list("topics.txt")
        if not keywords:
            print("No topics found in topics.txt. Please add topics to search.")
            driver.quit()
            return
        print(keywords)

        # Automatic login (current user)
        login_to_current_user(driver)

        # Navigate to Bing
        print(f"Navigating to {BING_URL}...")
        driver.get(BING_URL)

        # Auto-accept cookies on Bing home page
        auto_accept_cookies(driver)

        # Run searches for all keywords
        run_searches(driver, keywords)

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


if __name__ == "__main__":  # pragma: no cover
    main()