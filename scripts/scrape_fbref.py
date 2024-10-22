import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
from datetime import datetime
import time
import random
from requests.adapters import HTTPAdapter, Retry
import traceback

# Constants
BASE_URL = "https://fbref.com/en"
SEASON = "2024-2025"
PL_STATS_URL = f"{BASE_URL}/comps/9/{SEASON}/{SEASON}-Premier-League-Stats#all_results{SEASON}91"
COMPETITION = "c9" # 9: Premier League
MAX_RETRIES = 5
BACKOFF_FACTOR = 0.3
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0',
]

def get_soup(url: str) -> BeautifulSoup:
    """
    Fetch the HTML content of a URL and return a BeautifulSoup object.
    
    Args:
        url (str): The URL to fetch.
    
    Returns:
        BeautifulSoup: Parsed HTML content.
    
    Raises:
        requests.RequestException: If there's an error fetching the URL.
    """
    print(f"Attempting to fetch URL: {url}")
    session = requests.Session()
    retry = Retry(total=MAX_RETRIES, backoff_factor=BACKOFF_FACTOR, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    for attempt in range(MAX_RETRIES):
        try:
            if attempt > 0:  # Add delay before retries
                time.sleep(3 + random.uniform(0, 1))
            
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            print(f"Request attempt {attempt + 1} with User-Agent: {headers['User-Agent']}")
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if the response content is valid HTML
            if not response.text.strip().startswith('<!DOCTYPE html>'):
                raise ValueError("Response content is not valid HTML")
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Check if the parsed content contains expected elements
            if not soup.find('body'):
                raise ValueError("Parsed content does not contain a body element")
            
            print(f"Successfully fetched and parsed URL: {url}")
            return soup
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching or parsing URL {url} (attempt {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                wait_time = BACKOFF_FACTOR * (2 ** attempt)
                print(f"Waiting {wait_time:.2f} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print(f"Max retries reached. Unable to fetch or parse URL: {url}")
                return None

    # Add delay after successful request
    time.sleep(3 + random.uniform(0, 1))
    return soup

def get_team_names_and_id(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    """
    Extract team names from the Premier League table.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content of the Premier League stats page.
    
    Returns:
        List[str]: List of team names.
    """
    teams = []
    pl_table = soup.find("table", {"id": f"results{SEASON}91_overall"})
    if pl_table:
        for row in pl_table.find_all("tr")[1:]:  # Skip the header row
            team_cell = row.find("td", {"data-stat": "team"})
            if team_cell and team_cell.find("a"):
                team_link = team_cell.find("a")["href"]
                # Extract team name from the href
                team_name = team_link.split("/")[-1].replace("-Stats", "")
                team_id = team_link.split("/")[3]
                teams.append((team_name, team_id))
    return teams

def get_match_log_urls(team: Tuple[str, str]) -> Dict[str, str]:
    """
    Generate URLs for different match log types for a given team.
    
    Args:
        team (str): The team name.
    
    Returns:
        Dict[str, str]: A dictionary of match log types and their corresponding URLs.
    """
    team_name = team[0]
    team_id = team[1]

    base_match_log_url = f"{BASE_URL}/squads/{team_id}/{SEASON}/matchlogs/{COMPETITION}"
    return {
        "shooting": f"{base_match_log_url}/shooting/{team_name}-Match-Logs-Premier-League",
        "keeper": f"{base_match_log_url}/keeper/{team_name}-Match-Logs-Premier-League",
        "passing": f"{base_match_log_url}/passing/{team_name}-Match-Logs-Premier-League",
        "gca": f"{base_match_log_url}/gca/{team_name}-Match-Logs-Premier-League",
        "defense": f"{base_match_log_url}/defense/{team_name}-Match-Logs-Premier-League",
        "possession": f"{base_match_log_url}/possession/{team_name}-Match-Logs-Premier-League",
        "misc": f"{base_match_log_url}/misc/{team_name}-Match-Logs-Premier-League",
    }

def scrape_match_logs():
    """
    Scrape match logs for all Premier League teams.
    
    This function fetches the Premier League stats page, extracts team names,
    generates URLs for different types of match logs for each team, and scrapes the stats for each team.
    """
    
    print("Starting to scrape match logs...")
    try:
        soup = get_soup(PL_STATS_URL)
        if not soup:
            print(f"Failed to fetch the main page: {PL_STATS_URL}")
            return

        teams = get_team_names_and_id(soup)
        print(f"Found {len(teams)} teams")
        
        for team in teams:
            print(f"Processing team: {team[0]}")
            match_log_urls = get_match_log_urls(team)
            
            for log_type, url in match_log_urls.items():
                print(f"  Scraping {log_type} data from {url}")
                soup = get_soup(url)
                if not soup:
                    print(f"  Failed to fetch {log_type} data for {team[0]}")
                    continue
                stats_table = soup.find("table", {"id": "matchlogs_for"})
                if not stats_table:
                    print(f"  No stats table found for {team[0]} - {log_type}")
                    continue

                rows = stats_table.find_all("tr")
                if len(rows) < 3:
                    print(f"  Not enough rows in stats table for {team[0]} - {log_type}")
                    continue

                # Get column names from the second row (index 1)
                headers = [th.text.strip() for th in rows[1].find_all("th")]

                # Define the columns we want to keep
                columns_to_keep = ["Date", "Time", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Sh", "SoT", "SoT%", "G/Sh", "G/SoT", "FK",
                                    "PK", "PKAtt", "xG", "npxG", "npxG/Sh", "G-xG", "np:G-xG"]

                # Find indices of columns we want to keep
                indices_to_keep = [headers.index(col) for col in columns_to_keep if col in headers]

                # Extract data from rows
                match_data = []
                for row in rows[2:-1]:  # Skip the first two rows (useless header and column names)
                    cells = row.find_all(["th", "td"])
                    if len(cells) > max(indices_to_keep):
                        match_data.append([cells[i].text.strip() for i in indices_to_keep])

                # Process the match_data as needed (e.g., store in a database, write to a file, etc.)
                print(f"  Extracted {len(match_data)} matches for {team[0]} - {log_type}")
                
                # Add a delay of at least 3 seconds between requests
                time.sleep(3 + random.uniform(0, 1))

        print("Finished scraping match logs.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    scrape_match_logs()
