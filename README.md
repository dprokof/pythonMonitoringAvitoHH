# Documentation for the position monitoring script

## Description:
This script is used to search for a page and position number on popular job advertisement platforms. It utilizes Selenium for web scraping and Google Sheets for data storage.

## Functions:
1. `create_driver()`: Creates a Chrome WebDriver for web scraping.
2. `validator_url_hh(url)`: Validates and modifies the URL for the hh.ru platform.
3. `get_pages_count_hh(vacancy)`: Retrieves the total number of pages for a given vacancy on hh.ru.
4. `search_vacancy_hh(vacancy_url)`: Searches for a specific vacancy URL on hh.ru and records the position and page number.
5. `search_vacancy_avito(vacancy_url)`: Searches for a specific vacancy URL on Avito and records the position and page number.

## Libraries Used:
- re: Regular expressions for string manipulation.
- time: Handling time-related operations.
- gspread: Google Sheets API for interacting with Google Sheets.
- datetime: Managing date and time information.
- multiprocessing.Pool: Running tasks concurrently.
- selenium: Web scraping library for automating web browser actions.

## How to install:
1. Clone this repo
   
2. Install libraries
   ```
   pip install gspread
   
   pip install selenium
   ```
   You can install requirements.txt
   ```
   pip install -r requirements.txt
   ```
3. At str 172 in main.py you need to add your Google API token
   ```
   #172  gc = gspread.service_account(filename='<your_google_api_token>.json')
   ```
4. Also, at str 104 and 165 you need to add name of your sheets
   ```
   wks = gc.open("<name>").sheet1
   ```
5. Run it
   ```
   python3 main.py
   ```

## Execution:
1. The script prompts the user to choose between monitoring HH.ru or Avito.
2. For HH.ru:
   - User provides the vacancy name and URL(s).
   - The script initiates monitoring for the specified URL(s) concurrently.
3. For Avito:
   - User provides the vacancy name and URL(s).
   - The script initiates monitoring for the specified URL(s) concurrently.

## Note:
- This script requires Google Sheets API key to function properly.
- In new selenium version don't need to use a Chromedriver.
