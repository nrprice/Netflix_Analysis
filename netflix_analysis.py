import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
import requests
import numpy as np
import datetime as dt
import re

pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 400000)
pd.set_option("display.width", 1000)

def get_minutes(title, output_process=False):

    # Formats the show title into a google search URL.
    # Likely need to do a better job of removing punctuation from titles.
    title = (title.replace(" ", "+") + "+imdb").replace(":", "+").replace("'", "")
    google_string = 'https://www.google.com/search?q='
    search_page_url = google_string+title

    # Retrieves all links from the search search_page_url
    search_page_html = requests.get(search_page_url)
    search_soup = BeautifulSoup(search_page_html.text, 'html.parser')
    search_links = str(search_soup.find_all('a'))

    #Finds the index value in the string of 'www.imdb.com'
    #and uses that to find the end of the URL string by find the third /

    try:
        start_string = search_links.find('www.imdb.com')
        imdb_url = search_links[start_string:]
        third_slash = [m.start() for m in re.finditer('/', imdb_url)]
        imdb_url = imdb_url[:third_slash[2]]
        imdb_url = f"http://{imdb_url}"

    except IndexError:
        print (f'URL Could Not be Found for {title}')
        return 0

    #Retrieves html from the IMDB page
    imdb_page_html = requests.get(imdb_url)
    imdb_soup = BeautifulSoup(imdb_page_html.content, 'html.parser')
    time = str(imdb_soup.find_all('time'))
    # Splits up the time HTML information to return the time
    time = time[time.find('>')+1:].strip()
    time = time[0:time.find('<')].rstrip()
    time = time[:-3]

    if time.find('h') == -1:
        pass
    else:
        time = time.split(' ')

        time_0 = int(time[0].replace('h', '')) * 60
        time = str(time_0 + int(time[1]))
    if len(time) == 0:
        return 0

    if output_process:
        print (title, imdb_url, time)

    return int(time)

def time_convert(time):

    if time.find('h') == -1:
        pass
    else:
        time = time.split(' ')

        time_0 = int (time[0].replace('h', '')) * 60
        time = str(time_0 + int(time[1]))
    if len(time) == 0:
        return 0
    return int(time)

answer = input("Want to start again? - Warning. Will take a long time to request all episode times from scratch")
print ('Enter Y for Y, or anything else for N')

if answer.lower() == 'y':
    # Wipes existing data and starts again
    existing_netflix = pd.read_excel('netflix_parsed.xlsx', nrows=0)
else:
    # Pre Existing already calculated netflix data
    existing_netflix = pd.read_excel('netflix_parsed.xlsx')


# Importing and cleaning of the new netflix data.
new_netflix_data = pd.read_excel('NetflixViewingHistory.xlsx')
new_netflix_data.columns = [x.lower() for x in new_netflix_data.columns]
new_netflix_data = new_netflix_data[new_netflix_data['date'].dt.year >= 2020]
new_netflix_data['show_name'] = new_netflix_data['title'].apply(lambda x: x.split(':')[0])

# Merge the new with the old and find length of episode
netflix_combined = pd.concat([existing_netflix, new_netflix_data], ignore_index=True, sort=False).drop_duplicates('title').reset_index(drop=True)
netflix_combined['time'] = netflix_combined['time'].fillna('new')

# For loop checking the status of each row to see if its new
# If it is new, it will get the time with the get_minutes function
for i in range(len(netflix_combined)):

    # if i % 10 == 0:
    #     netflix_combined.to_excel('netflix_parsed_1.xlsx', index=False)

    if netflix_combined['time'][i] == 'new':
        netflix_combined['time'][i] = get_minutes(netflix_combined['title'][i], output_process=True)
    else:
        pass

# Saves new dataframe
netflix_combined.to_excel('netflix_parsed.xlsx', index=False)
