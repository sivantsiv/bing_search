# Bing Search Automation

This project automates Bing searches for a list of topics using Selenium WebDriver and Microsoft Edge. It supports automatic login with the current Windows user and auto-accepts cookie banners for each page.

## Features

- **Automated Bing Searches:** Reads a list of topics from `topics.txt` and performs searches on Bing automatically.
- **Automatic Login:** Uses the current Windows user profile for Edge, so no manual login is required.
- **Auto-Accept Cookies:** Automatically accepts cookie consent popups on Bing and other common banners.
- **Randomized Delays:** Waits a random interval between searches to mimic human behavior.
- **Error Handling:** Handles missing files, search errors, and WebDriver issues gracefully.

## Requirements

- Python 3.7+
- Microsoft Edge browser
- Microsoft Edge WebDriver (`msedgedriver.exe`) matching your Edge version ([download here](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/))
- Selenium Python package (`pip install selenium`)

## Setup

1. **Install Dependencies:**
	- Install [Python](https://www.python.org/downloads/)
	- Install Selenium: `pip install selenium`
	- Download and place `msedgedriver.exe` in your PATH or project folder.

2. **Prepare Topics File:**
	- Edit `topics.txt` and add one search topic per line.

3. **Run the Script:**
	- Run `python bing_search.py` or use the provided `run_script.bat`.

## File Structure

```
bing_search.py        # Main automation script
topics.txt            # List of search topics (one per line)
README.md             # Project documentation
run_script.bat        # Batch file to run the script (optional)
doc/                  # Documentation folder (currently empty)
```

## How It Works

1. **WebDriver Setup:**
	- Launches Microsoft Edge using Selenium WebDriver.
	- Maximizes the browser window.

2. **Login:**
	- Assumes Edge is using the current Windows user profile (automatic login).

3. **Cookie Consent:**
	- Attempts to auto-accept cookie banners on Bing and other common consent popups.

4. **Search Loop:**
	- Reads all topics from `topics.txt`.
	- For each topic:
	  - Navigates to Bing, enters the topic, and submits the search.
	  - Waits for results to load and auto-accepts cookies if prompted again.
	  - Waits a random delay before the next search.

5. **Cleanup:**
	- Closes the browser after all searches are complete.

## Customization

- **topics.txt:** Add or remove topics as needed.
- **Delays:** Adjust `MIN_DELAY_SECONDS` and `MAX_DELAY_SECONDS` in `bing_search.py` to change the random wait time between searches.
- **WebDriver Path:** If `msedgedriver.exe` is not in your PATH, specify its location in the script.

## Troubleshooting

- If Edge WebDriver fails to start, ensure `msedgedriver.exe` matches your Edge version and is accessible.
- If cookie banners are not accepted, update the selectors in `auto_accept_cookies()` in `bing_search.py`.
- For login issues, ensure Edge is using the correct Windows profile or extend the login logic as needed.

## Example topics.txt

```
history of the internet
benefits of meditation
how to learn a new language quickly
... (add more topics as needed)
```

## License

This project is provided as-is for educational and personal use.
