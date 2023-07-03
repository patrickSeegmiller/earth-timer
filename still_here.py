import datetime
import os
import random
import re
import requests
import sys
import tweepy

from bs4 import BeautifulSoup

# Get the current date and time
now = datetime.datetime.now()             

def get_prediction():
    # Scrape https://en.wikipedia.org/wiki/List_of_dates_predicted_for_apocalyptic_events for dates
    # and times of predicted apocalyptic events
    url = 'https://en.wikipedia.org/wiki/List_of_dates_predicted_for_apocalyptic_events'
    r = requests.get(url)
    html_contents = r.text

    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_contents, 'html.parser')

    # Randomly select a table from the page (excluding the table of Far Future dates
    tables = soup.select('table.wikitable')
    random_table = random.choice(tables[:-1])

    # Randomly select a row from the table (excluding the header row)
    rows = random_table.select('tr')
    random_row = random.choice(rows[1:])

    # Get the text from the row and split it on the newline character
    prediction = random_row.getText().split('\n')

    # Remove the empty strings from the list and the citations in brackets
    prediction = [item for item in prediction if item != '']
    prediction = [item for item in prediction if not item.startswith('[')]

    return prediction

def parse_prediction(prediction):
    # Use a regular expression to extract the year(s) from the prediction. Years can vary in number of
    # digits on the page from 2 to 4 digits, so the regular expression is written to match 2 to 4 digits
    # in a row. 
    year = re.findall(r'\d{2,4}', prediction[0])

    # Select the latter year if a range of years is given, since if it was in the past, the prediction
    # would have already come true. If the prediction is for the future, the latter year is more optimistic
    # on our part. :D
    if len(year) > 1:
        year = year[-1]
    elif len(year) == 0:
        sys.exit()
    else:
        year = year[0]

    # If we can't find a year, exit the program
    if not year:
        sys.exit()

    # Check if the year is in the past or future
    is_past = int(year) < now.year

    # Select the predictor from the prediction. 
    # If there are multiple names for the prediction, randomly select one.
    predictors = prediction[1].split(',')
    predictor = random.choice(predictors)

    # Check to be sure the predictor won't target a specific religious group, text, or person. We aren't trying to be
    # offensive here. We can add to this list as we find more words that should be protected.
    protected_words = ['Jesus', 'Christ', 'God', 'Allah', 'Jehovah', 'Yahweh', 'Buddha', 'Muhammad',
                    'Talmud', 'Torah', 'Quran', 'Bible', 'Koran', 'Judaism', 'Christianity',
                        'Muslim', 'Christian', 'Jew', 'Islam', 'Jewish', 'Catholic', 'Protestant',
                            'Hindu', 'Hinduism', 'Buddhism', 'Buddhist', 'Sikh', 'Sikhism', 'Shinto',
                            'Shintoism', 'Confucianism', 'Confucian', 'Taoism', 'Taoist', 'Zoroastrianism',
                            'Zoroastrian', 'Jainism', 'Jain', 'Bahai', 'Bahaiism', 'Bahaii', 'Bahaiiism',
                            'Atheism', 'Atheist', 'Agnostic', 'Agnosticism', 'Deism', 'Deist', 'Pagan',
                            'Paganism', 'Wicca', 'Wiccan' 'Jehovahs', 'Jehovah\'s', 'Jehovahs\'', 'Christians',
                            'Jews', 'Muslims', 'Catholics', 'Protestants', 'Hindus', 'Buddhists', 'Sikhs',
                            'Shintos', 'Confucians', 'Taoists', 'Zoroastrians', 'Jains', 'Bahais', 'Atheists'
    ]

    # If the predictor is contained in the protected words list, randomly select a new one
    while predictor.strip() in protected_words:
        predictor = random.choice(predictors)  

    return year, is_past, predictor

def construct_tweet(year, is_past, predictor):
    # A list of possible formats for the tweet
    past_formats = [
        'According to {predictor}, the world ended in {year}. #wewillrebuild',
        '{predictor} thought the world would end in {year}. #foolishmortal',
        'The world ended in {year}, according to {predictor}. #whoknew',
        'So, yeah, the world ended in {year}, {predictor}? #aboutthat...',
        'Solid prediction, {predictor}. The world ended in {year}. #eyeroll',
        'I\'m pretty sure the world did not end in {year}, {predictor}. #mycondolences',
        'Only {now.year} years since the world ended, according to {predictor}. #whatevershallwedo',
        'Oh no! The world ended in {year}, {predictor}? #thehumansaredead',
        'The world ended in {year}, according to {predictor}. #goodthing{predictor.replace(' ', '')}isanidiot'
    ]

    future_formats = [
        'According to {predictor}, the world will end in {year}. #yikes',
        '{predictor} thinks the world will end in {year}. #goodthing{predictor}isanidiot',
        'The world will end in {year}, according to {predictor}. #washyourunderwear',
        'So, yeah, the world is supposed to end in {year}, {predictor}? #wanttobuyabridge',
        'Solid prediction, {predictor}. The world will TOTALLY end in {year}. #eyeroll',
        'I\'m pretty sure the world will not end in {year}, {predictor}. #mycondolences',
        'Only {year - now.year} years until the world ends, according to {predictor}. #eatthatextrapieceofcake',
        'Oh no! The world will end in {year}, {predictor}? #whyareyouthewayyouare',
    ]

    # Select a format based on whether the prediction is in the past or future
    if is_past:
        tweet = random.choice(past_formats)
    else:
        tweet = random.choice(future_formats)

    # Construct the tweet
    tweet = tweet.format(year=year, predictor=predictor, now=now)

    return tweet


def get_api():
    """Get the API"""
    # Get the keys from the environment variables
    consumer_key = os.environ.get('CONSUMER_KEY')
    consumer_secret = os.environ.get('CONSUMER_SECRET')
    access_token = os.environ.get('ACCESS_TOKEN')
    access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

    # Authenticate
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Get the API
    api = tweepy.API(auth)

    return api

def tweet(api, tweet):
    """Tweet the tweet"""
    api.update_status(tweet)

def main():
    """Main function"""
    api = get_api()
    tweet(api, tweet)

if __name__ == '__main__':
    main()