# NY-Mets-Baseball-Knowledge-Graph
A New York Mets Major League Baseball Knowlege Graph

# Folder Structure:
    .gitignore
    requirements.txt
    lahman_to_turtle.py
    - data/
        - lahman/
            *.csv
    - rdfs/
        - lahman/
            - *.ttl
    - utils/
    

# Usage
    virtualenv venv 
    source venv/bin/activate
    pip install -r requirements.py
    python lahman_to_turtle.py

# Data Source
    Lahman Database with additional information obtained from reconciling with WikiData
