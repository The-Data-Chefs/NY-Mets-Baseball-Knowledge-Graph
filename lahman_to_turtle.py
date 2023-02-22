import pandas as pd
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# Define namespaces
NS = {
    "skos": URIRef("http://www.w3.org/2004/02/skos/core#"),
    "tdc": URIRef("http://thedatachefs.com/tdc/0.1/"),
}


# Read input CS files into pandas dataframes
players = pd.read_csv("data/player_with_wiki.csv") # with more information from WikiData from openrefine
batting = pd.read_csv("data/lahman/Batting.csv")
fielding = pd.read_csv("data/lahman/Fielding.csv")


# Perform data operations using pandas

## Filter players only from mets
mets_players_id_batting = batting[batting.teamID == 'NYN'].playerID.unique().tolist()
mets_players_id_fielding = fielding[fielding.teamID == 'NYN'].playerID.unique().tolist()
mets_player_ids = list(set(mets_players_id_batting).union(set(mets_players_id_fielding)))
mets_players = players[players.playerID.isin(mets_player_ids)]

# expand batting hand and throwing hand columns
met_players = mets_players.replace({'bats': {'R': 'Right', 'L': 'Left', 'B': 'Both'}})
met_players = mets_players.replace({'throws': {'R': 'Right', 'L': 'Left', 'B': 'Both'}})

# Add a boolean field called alive
mask = met_players['date of death'].isna()
met_players.loc[mask, 'alive'] = True
met_players.loc[~mask, 'alive'] = False

##TODO: Later combine information from other tables like batting and fielding stats


# Initialize graph, class and properties
g = Graph()
g.bind('tdc', NS['tdc'])
g.bind('skos', NS['skos'])

BaseballPlayer = URIRef(f"{NS['tdc']}BaseballPlayer")
g.add((BaseballPlayer, RDF.type, RDFS.Class))
g.add((BaseballPlayer, RDFS.label, Literal('Baseball Player')))

properties = [
    {'column': 'birthDate', 'name': 'dateOfBirth', 'type':XSD.date, 'label': 'date of birth', 'altLabel': 'born on'},
    {'column': 'date of death', 'name': 'dateOfDeath', 'type':XSD.date, 'label': 'date of death', 'altLabel': 'died on'},
    {'column': 'place of birth', 'name': 'placeOfBirth', 'type':XSD.string, 'label': 'place of birth', 'altLabel': 'born at'},
    {'column': 'place of death', 'name': 'placeOfDeath', 'type':XSD.string, 'label': 'place of death', 'altLabel': 'died at'},
    {'column': 'place of burial', 'name': 'placeOfBurial', 'type':XSD.string, 'label': 'place of burial', 'altLabel': 'buried at'},
    {'column': 'country of citizenship', 'name': 'country', 'type':XSD.string, 'label': 'country of citizenship', 'altLabel': 'country'},
    {'column': 'educated at', 'name': 'educatedAt', 'type':XSD.string, 'label': 'educated at', 'altLabel': 'went to'},
    {'column': 'given name', 'name': 'givenName', 'type':XSD.string, 'label': 'given name', 'altLabel': 'name given'},
    {'column': 'weight', 'name': 'weight', 'type':XSD.int, 'label': 'weight', 'altLabel': 'weighs'},
    {'column': 'height', 'name': 'height', 'type':XSD.int, 'label': 'height', 'altLabel': 'tall'},
    {'column': 'bats', 'name': 'battingHand', 'type':XSD.string, 'label': 'batting hand', 'altLabel': 'bats with'},
    {'column': 'throws', 'name': 'throwingHand', 'type':XSD.string, 'label': 'throwing hand', 'altLabel': 'throws with'},
    {'column': 'debut', 'name': 'debut', 'type':XSD.date, 'label': 'debut', 'altLabel': 'debut game'},
    {'column': 'finalGame', 'name': 'finalGame', 'type':XSD.date, 'label': 'last game', 'altLabel': 'last performance'},
    {'column': 'image', 'name': 'image', 'type':XSD.anyURI, 'label': 'image', 'altLabel': 'photo'},
    {'column': 'alive', 'name': 'alive', 'type':XSD.boolean, 'label': 'alive', 'altLabel': 'not dead'},
]

for p in properties:
    g.add((URIRef(f"{NS['tdc']}{p['name']}"), RDF.type, RDF.Property))
    g.add((URIRef(f"{NS['tdc']}{p['name']}"), RDFS.domain, BaseballPlayer))
    g.add((URIRef(f"{NS['tdc']}{p['name']}"), RDFS.range, p['type']))
    g.add((URIRef(f"{NS['tdc']}{p['name']}"), RDFS.label, Literal(p['label'])))
    g.add((URIRef(f"{NS['tdc']}{p['name']}"), URIRef(f"{NS['skos']}altLabel"), Literal(p['altLabel'])))
        

# Add data from pandas dataframe to rdflib graph
for index, row in met_players.iterrows():
    subj = URIRef(f"{NS['tdc']}{row['playerID']}")
    g.add((subj, RDF.type, BaseballPlayer))
    for p in properties:
        pred = URIRef(f"{NS['tdc']}{p['name']}")
        obj = Literal(row[p['column']], datatype=p['type'])
        g.add((subj, pred, obj))

# Serialize graph to Turtle format and save to file
g.serialize(destination="rdfs/output.ttl", format="turtle")
