import sys
import wikipediaapi

title = sys.argv[1]

wiki_wiki = wikipediaapi.Wikipedia('en')

page = wiki_wiki.page(title)

with open('wikitexts/' + title + '.txt', 'w') as f:
    f.write(page.summary)