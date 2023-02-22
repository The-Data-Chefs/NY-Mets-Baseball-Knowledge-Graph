import pandas as pd
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, XSD
from urllib.parse import quote

# Define namespaces
tdc = Namespace("http://thedatachefs.com/tdc/0.1/")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")


# Read input CSV files into pandas dataframes
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
met_players = mets_players.replace({'bats': {'R': 'Right', 'L': 'Left', 'B': 'Both'}, 
                                    'throws': {'R': 'Right', 'L': 'Left', 'B': 'Both'}})

# Add a boolean field called alive
mask = met_players['date of death'].isna()
met_players.loc[mask, 'alive'] = True
met_players.loc[~mask, 'alive'] = False

##TODO: Later combine information from other tables like batting and fielding stats


# Initialize graph, class and properties
g = Graph()
g.bind('tdc', tdc)
g.bind('skos', skos)

BaseballPlayer = tdc.BaseballPlayer
g.add((BaseballPlayer, RDF.type, RDFS.Class))
g.add((BaseballPlayer, RDFS.label, Literal('Baseball Player')))

properties = [
    {'column': 'birthDate', 'name': tdc.dateOfBirth, 'type':XSD.date, 'label': 'date of birth', 'altLabel': 'born on'},
    {'column': 'date of death', 'name': tdc.dateOfDeath, 'type':XSD.date, 'label': 'date of death', 'altLabel': 'died on'},
    {'column': 'place of birth', 'name': tdc.placeOfBirth, 'type':XSD.string, 'label': 'place of birth', 'altLabel': 'born at'},
    {'column': 'place of death', 'name': tdc.placeOfDeath, 'type':XSD.string, 'label': 'place of death', 'altLabel': 'died at'},
    {'column': 'place of burial', 'name': tdc.placeOfBurial, 'type':XSD.string, 'label': 'place of burial', 'altLabel': 'buried at'},
    {'column': 'country of citizenship', 'name': tdc.country, 'type':XSD.string, 'label': 'country of citizenship', 'altLabel': 'country'},
    {'column': 'educated at', 'name': tdc.educatedAt, 'type':XSD.string, 'label': 'educated at', 'altLabel': 'went to'},
    {'column': 'given name', 'name': tdc.givenName, 'type':XSD.string, 'label': 'given name', 'altLabel': 'name given'},
    {'column': 'weight', 'name': tdc.weight, 'type':XSD.integer, 'label': 'weight', 'altLabel': 'weighs'},
    {'column': 'height', 'name': tdc.height, 'type':XSD.integer, 'label': 'height', 'altLabel': 'tall'},
    {'column': 'bats', 'name': tdc.battingHand, 'type':XSD.string, 'label': 'batting hand', 'altLabel': 'bats with'},
    {'column': 'throws', 'name': tdc.throwingHand, 'type':XSD.string, 'label': 'throwing hand', 'altLabel': 'throws with'},
    {'column': 'debut', 'name': tdc.debut, 'type':XSD.date, 'label': 'debut', 'altLabel': 'debut game'},
    {'column': 'finalGame', 'name': tdc.finalGame, 'type':XSD.date, 'label': 'last game', 'altLabel': 'last performance'},
    {'column': 'image', 'name': tdc.image, 'type':XSD.anyURI, 'label': 'image', 'altLabel': 'photo'},
    {'column': 'alive', 'name': tdc.alive, 'type':XSD.boolean, 'label': 'alive', 'altLabel': 'not dead'},
]

for p in properties:
    g.add((p['name'], RDF.type, RDF.Property))
    g.add((p['name'], RDFS.domain, BaseballPlayer))
    g.add((p['name'], RDFS.range, p['type']))
    g.add((p['name'], RDFS.label, Literal(p['label'])))
    g.add((p['name'], skos.altLabel, Literal(p['altLabel'])))
        

# Add data from pandas dataframe to rdflib graph
for index, row in met_players.iterrows():
    subj = URIRef(f"{tdc}{row['playerID']}")
    g.add((subj, RDF.type, BaseballPlayer))
    g.add((subj, RDFS.label, Literal(row['nameFull'])))
    g.add((subj, skos.altLabel, Literal(row['given name'])))
    for p in properties:
        pred = p['name']
        if p['column'] == 'image':
            obj = URIRef(quote(f"https://commons.wikimedia.org/wiki/Special:FilePath/{row[p['column']]}").replace('%3A', ':'))
        else:
            obj = Literal(row[p['column']], datatype=p['type'])
        g.add((subj, pred, obj))

# Serialize graph to Turtle format and save to file
output = "rdfs/output.ttl"
g.serialize(destination=output, format="turtle")

# Notify success
print('Successful!')
print('You can find the turtle file at: ' + output)