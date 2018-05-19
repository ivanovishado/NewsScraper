#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
News scraper, scrapes articles from a newspaper then adds them to a database.
"""
__title__ = 'mmld'
__author__ = 'Ivan Fernando Galaviz Mendoza'

from tzlocal import get_localzone
from datetime import datetime
from time import mktime
import json
import pytz
from pymongo import MongoClient
from newspaper import Article
import feedparser as fp
import newspaper
import constants

# TODO: Asignar timezones pertinentes al estado -- time.localtime().tm_isdst
# TODO: Crear diccionario temporal para cuando se pierda la conexión con la base de datos
# TODO: Validar si el contenido no está vacío

# Set the limit for number of articles to download
ARTICLES_TO_DOWNLOAD = 10

data = {}
data['newspapers'] = {}

train = {}

articles = []

# Loads the JSON files with news sites
with open('resources/NewsPapers2.json') as data_file:
    companies = json.load(data_file)

try:
    f = open(constants.ID_FILENAME)
except IOError:
    current_id = 0
else:
    with f:
        current_id = int(f.read())


def try_to_get_utc(date):
    try:
        return datetime.utcfromtimestamp(mktime(date))
    except Exception as e:
        print(e)
        return date


# Initialize database connection
# client = MongoClient()
# db = client.test

count = 1

# Iterate through each news company
for company, value in companies.items():
    # If a RSS link is provided in the JSON file, this will be the first choice.
    # Reason for this is that, RSS feeds often give more consistent and correct data.
    # If you do not want to scrape from the RSS-feed, just leave the RSS attr empty in the JSON file.
    if 'rss' in value:
        d = fp.parse(value['rss'])
        print("Downloading articles from", company)
        newsPaper = {
            "rss": value['rss'],
            "link": value['link'],
            "articles": []
        }
        for entry in d.entries:
            # Check if publish date is provided, if no the article is skipped.
            # This is done to keep consistency in the data and to keep the script from crashing.
            if hasattr(entry, 'published'):
                if count > ARTICLES_TO_DOWNLOAD:
                    break
                try:
                    content = Article(entry.link, fetch_images=False)
                    content.download()
                    content.parse()
                except Exception as e:
                    # If the download for some reason fails (ex. 404) the script will continue downloading
                    # the next article.
                    print(e)
                    print("continuing...")
                    continue
                article = {constants.NEWSPAPER: company,
                           constants.TITLE: content.title,
                           constants.TEXT: content.text,
                           constants.TAGS: list(content.tags),
                           constants.LINK: entry.link,
                           constants.PUB_DATE: try_to_get_utc(
                               entry.published_parsed),
                           constants.EXTRACT_DATE: datetime.utcnow(),
                           constants.CATEGORY: None}
                # db.test.insert_one(article)
                train[current_id] = {
                    'title': content.title,
                    'content': content.text
                }
                newsPaper['articles'].append(article)
                print(count, "articles downloaded from", company, ",url:", entry.link)
                count = count + 1
                current_id += 1
    else:
        # This is the fallback method if a RSS-feed link is not provided.
        # It uses the python newspaper library to extract articles
        print("Building site for", company)
        paper = newspaper.build(value['link'], language='es')
        newsPaper = {
            "link": value['link'],
            "articles": []
        }
        noneTypeCount = 0
        for content in paper.articles:
            print("Processing article", count)
            if count > ARTICLES_TO_DOWNLOAD:
                break
            try:
                content.download()
                content.parse()
            except Exception as e:
                print(e)
                print("continuing...")
                continue
            # Again, for consistency, if there is no found publish date the article will be skipped.
            # After 10 downloaded articles from the same newspaper without publish date, the company will be skipped.
            if content.publish_date is None:
                print(count, " Article has date of type None...")
                noneTypeCount += 1
                if noneTypeCount > 10:
                    print("Too many noneType dates, aborting...")
                    noneTypeCount = 0
                    break
                count = count + 1
                continue
            article = {constants.NEWSPAPER: company,
                       constants.TITLE: content.title,
                       constants.TEXT: content.text,
                       constants.TAGS: list(content.tags),
                       constants.LINK: content.url,
                       constants.PUB_DATE: content.publish_date,
                       constants.EXTRACT_DATE: datetime.utcnow(),
                       constants.CATEGORY: []}
            # db.test.insert_one(article)
            train[current_id] = {
                'title': content.title,
                'content': content.text
            }
            newsPaper['articles'].append(article)
            print(count, "articles downloaded from", company,
                  "using newspaper, url:", content.url)
            count = count + 1
            noneTypeCount = 0
            current_id += 1
    count = 1
    data['newspapers'][company] = newsPaper

# Close DB connection
# client.close()

# Updates current ID to file
with open(constants.ID_FILENAME, 'w') as f:
    f.write(str(current_id))

# Finally it saves the articles as a JSON-file.
try:
    with open('scraped_articles_' + str(current_id) + '.json', 'a') as outfile:
        json.dump(train, outfile, indent=2)
except Exception as e:
    print(e)
