import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime

# Constants
BASE_URL = "https://fbref.com/en"
SEASON = "2024-2025"
PL_STATS_URL = f"{BASE_URL}/comps/9/{SEASON}/{SEASON}-Premier-League-Stats#all_results{SEASON}91"
COMPETITION = "9" # 9: Premier League

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
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def get_team_names(soup: BeautifulSoup) -> List[str]:
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
                team_name = team_cell.find("a").text.strip()
                teams.append(team_name)
    return teams

def get_match_log_urls(team: str) -> Dict[str, str]:
    """
    Generate URLs for different match log types for a given team.
    
    Args:
        team (str): The team name.
    
    Returns:
        Dict[str, str]: A dictionary of match log types and their corresponding URLs.
    """
    base_match_log_url = f"{BASE_URL}/squads/822bd0ba/{SEASON}/matchlogs/{COMPETITION}"
    return {
        "shooting": f"{base_match_log_url}/shooting/{team}-Match-Logs-Premier-League",
        "keeper": f"{base_match_log_url}/keeper/{team}-Match-Logs-Premier-League",
        "passing": f"{base_match_log_url}/passing/{team}-Match-Logs-Premier-League",
        "gca": f"{base_match_log_url}/gca/{team}-Match-Logs-Premier-League",
        "defense": f"{base_match_log_url}/defense/{team}-Match-Logs-Premier-League",
        "possession": f"{base_match_log_url}/possession/{team}-Match-Logs-Premier-League",
        "misc": f"{base_match_log_url}/misc/{team}-Match-Logs-Premier-League",
    }

def scrape_match_logs():
    """
    Scrape match logs for all Premier League teams.
    
    This function fetches the Premier League stats page, extracts team names,
    and generates URLs for different types of match logs for each team.
    """
    soup = get_soup(PL_STATS_URL)
    if not soup:
        return

    teams = get_team_names(soup)
    
    for team in teams:
        match_log_urls = get_match_log_urls(team)
        
        # TODO: Implement the actual scraping of match logs for each URL
        for log_type, url in match_log_urls.items():
            print(f"Scraping {log_type} data for {team}: {url}")
            # Add your scraping logic here



