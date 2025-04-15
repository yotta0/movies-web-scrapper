import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
from time import time, sleep
from random import randint
from IPython.display import clear_output
from warnings import warn

headers = {
    "Accept-Language": "en-US, en;q=0.5",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

pages = [str(i) for i in range(1,5)]
years_url = [str(i) for i in range(2020,2025)]

names = []
years = []
imdb_ratings = []
metascores = []
votes = []

# Preparing the monitoring of the loop
start_time = time()
requests_count = 0
# For every year in the interval 2000-2017
for year_url in years_url:
    # For every page in the interval 1-4
    for page in pages:
        scrap_url = 'http://www.imdb.com/search/title/?title_type=feature&release_date=' + year_url + '&sort=num_votes,desc&page=' + page
        print(scrap_url)
        response = requests.get(scrap_url, headers = headers)

        # Pause the loop
        sleep(randint(8,15))

        # Monitor the requests
        requests_count += 1
        elapsed_time = time() - start_time
        print(f'Request:{requests_count}; Frequency: {requests_count/elapsed_time} requests/s')
        clear_output(wait = True)

        # Throw a warning for non-200 status codes
        if response.status_code != 200:
            warn(f'Request: {requests_count}; Status code: {response.status_code}')

        # Break the loop if the number of requests is greater than expected
        if requests_count > 72:
            warn('Number of requests was greater than expected.')
            break

        # Parse the content of the request with BeautifulSoup
        page_html = BeautifulSoup(response.text, 'html.parser')
        # Select all the 50 movie containers from a single page
        mv_containers = page_html.find_all('li', class_='ipc-metadata-list-summary-item')

        # For every movie of these 50
        for container in mv_containers:
            # Scrape the name
            name = container.h3.text.split('.', 1)[1].strip()
            names.append(name)

            # Scrape the year
            year = container.find('span', class_='dli-title-metadata-item').text
            years.append(year)

            # Scrape the IMDB rating
            imdb_rating = container.find('span', class_='ipc-rating-star--rating').text
            imdb_ratings.append(float(imdb_rating))

            # Scrape the Metascore
            movie_metascore = container.find('span', class_='sc-b0901df4-0 bXIOoL metacritic-score-box')
            if movie_metascore:
                metascores.append(movie_metascore.text)
            else:
                metascores.append('N/A')

            # Scrape the number of votes
            movie_vote_count = container.find('span', class_='ipc-rating-star--voteCount').text
            votes.append(movie_vote_count)

movie_ratings_df = pd.DataFrame({
    'movie': names,
    'year': years,
    'imdb': imdb_ratings,
    'metascore': metascores,
    'votes': votes
})
movie_ratings_df

movie_ratings_df = movie_ratings_df[['movie', 'year', 'imdb', 'metascore', 'votes']]
movie_ratings_df['year'] = movie_ratings_df['year'].str[-4:].astype(int)

# Normalize to 0-100 scale to plot in future and create dataset
movie_ratings_df['n_imdb'] = movie_ratings_df['imdb'] * 10
movie_ratings_df.to_csv('movie_ratings.csv')
