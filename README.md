# NY-Mets-Baseball-Knowledge-Graph
A New York Mets Major League Baseball Knowlege Graph

# Folder Structure:
    .gitignore
    requirements.txt
    lahman_to_turtle.py
    from_wiki.py
    - data/
        - lahman/
            *.csv
    - rdfs/
        - output.ttl
        - lahman/       # old ttls
            - *.ttl
    - wikitexts/
        - *.txt

# Setup
```
virtualenv venv 
source venv/bin/activate
pip install -r requirements.py
```

# Usage 1: Lahman database to RDF Turtle format
```
python lahman_to_turtle.py
```

# Usage 2: get text from wikipedia title. (eg. Barry_Bonds for https://en.wikipedia.org/wiki/Barry_Bonds )
```
python from_wiki.py <wiki_title>
```

# Data Source
    Lahman Database with additional information obtained from reconciling with WikiData
