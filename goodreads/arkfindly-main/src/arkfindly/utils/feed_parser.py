import re
import feedparser

from bs4 import BeautifulSoup

def getLinks(source):
    
   feed = feedparser.parse(source['link'])
   links = [] 

   for entry in feed.entries:

      category_list = []
      published = None
      author = None
      description = None

      if 'tags' in entry:
         for tag in entry.tags:
            if 'term' in tag:
               category_list.append(tag.term)

      if 'published' in entry:
         published = entry.published

      if 'date' in entry:
         published = entry.date

      if 'author' in entry:
         author = entry.author

      if 'description' in entry:
         soup = BeautifulSoup(entry.description, 'html.parser')
         description = soup.get_text(strip=True)
         
      temp_link = {
        'name': source['name'],
        'acronym': source['acronym'],
        'title': entry.title,
        'link': entry.link,
        'published': published,
        'author': author,
        'description': description,
        'categories': category_list
      }

      print(temp_link)
      #links.append(temp_link)
    
   return links

def remove_tags_br(soup):
    for br in soup.find_all('br'):
        br.replace_with(' ')
    return soup

def clean_blank_spaces(text):
    text = re.sub(r'\s+', ' ', text)
    return text