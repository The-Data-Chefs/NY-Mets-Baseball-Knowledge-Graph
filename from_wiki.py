import pandas as pd
import sys
import requests
import wikipediaapi

# Read input CSV files into pandas dataframes
players = pd.read_csv("data/player_with_wiki.csv") # with more information from WikiData from openrefine
batting = pd.read_csv("data/lahman/Batting.csv")
fielding = pd.read_csv("data/lahman/Fielding.csv")

# Filter players only from mets
mets_players_id_batting = batting[batting.teamID == 'NYN'].playerID.unique().tolist()
mets_players_id_fielding = fielding[fielding.teamID == 'NYN'].playerID.unique().tolist()
mets_player_ids = list(set(mets_players_id_batting).union(set(mets_players_id_fielding)))
mets_players = players[players.playerID.isin(mets_player_ids)]
mets_player_wikiIDs = mets_players.wikiPlayerID
print(mets_player_wikiIDs.shape)


# Define the Wikipedia API URL
url = "https://www.wikidata.org/w/api.php"

for wikiID in mets_player_wikiIDs:
    # Define the API parameters
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": wikiID,
        "props": "sitelinks",
        "sitefilter": "enwiki"
    }

    # Make the API request
    response = requests.get(url, params=params).json()
    print(response)

    # Extract the Wikipedia page title from the API response
    title = response["entities"][wikiID]["sitelinks"]["enwiki"]["title"]

    wiki_wiki = wikipediaapi.Wikipedia('en')

    page = wiki_wiki.page(title)

    with open('wikitexts/' + title.replace('/', '-') + '.txt', 'w') as f:
        f.write(page.summary)