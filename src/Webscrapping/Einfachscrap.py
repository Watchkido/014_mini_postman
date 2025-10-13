import requests
from bs4 import BeautifulSoup

url = "https://www.scrapethissite.com/pages/forms/"

response = requests.get(url)
content = response.text
soup = BeautifulSoup(content, "html.parser")

teams = soup.find_all("tr", class_="team")

for team in teams:
    team_name = team.find("td", class_="name").text.strip()
    team_wins = team.find("td", class_="wins").text.strip()
    team_losses = team.find("td", class_="losses").text.strip()
    
    # Ausgabe aller Informationen
    print(f"Team: {team_name}, Siege: {team_wins}, Niederlagen: {team_losses}")