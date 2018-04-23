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

# TODO: Crear clase para los estados con sus periódicos
# TODO: Asignar timezones pertinentes al estado -- time.localtime().tm_isdst
# TODO: Diseñar base de datos para guardar por [estado][periodico] -> articulos
# TODO: Crear diccionario temporal para cuando se pierda la conexión con la base de datos

# Set the limit for number of articles to download
LIMIT = 4

data = {}
data['newspapers'] = {}

articles = []

# Loads the JSON files with news sites
with open('NewsPapers2.json') as data_file:
    companies = json.load(data_file)


def get_utc(timestamp):
    """Converts a timestamp to UTC."""
    local = pytz.timezone(get_localzone())
    naive = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)
    return local_dt.astimezone(pytz.utc)


# Initialize database connection
client = MongoClient()
db = client.test

count = 1

# Iterate through each news company
for company, value in companies.items():
    # If a RSS link is provided in the JSON file, this will be the first choice.
    # Reason for this is that, RSS feeds often give more consistent and correct data.
    # If you do not want to scrape from the RSS-feed, just leave the RSS attr empty in the JSON file.
    if 'rss' in value:
        d = fp.parse(value['rss'])
        print("Downloading articles from ", company)
        newsPaper = {
            "rss": value['rss'],
            "link": value['link'],
            "articles": []
        }
        for entry in d.entries:
            # Check if publish date is provided, if no the article is skipped.
            # This is done to keep consistency in the data and to keep the script from crashing.
            if hasattr(entry, 'published'):
                if count > LIMIT:
                    break
                try:
                    content = Article(entry.link, fetch_images=False)
                    content.download()
                    content.parse()
                    content.nlp()
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
                           constants.PUB_DATE: datetime.utcfromtimestamp(
                               mktime(entry.published_parsed)),
                           constants.EXTRACT_DATE: datetime.utcnow(),
                           constants.CATEGORY: None}
                db.test.insert_one(article)
                newsPaper['articles'].append(article)
                print(count, "articles downloaded from", company, ", url: ", entry.link)
                count = count + 1
    else:
        # This is the fallback method if a RSS-feed link is not provided.
        # It uses the python newspaper library to extract articles
        print("Building site for ", company)
        paper = newspaper.build(value['link'], language='es')
        newsPaper = {
            "link": value['link'],
            "articles": []
        }
        noneTypeCount = 0
        for content in paper.articles:
            if count > LIMIT:
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
            article = {'newspaper': company,
                       'title': content.title,
                       'text': content.text,
                       'tags': list(content.tags),
                       'link': content.url,
                       'published': get_utc(content.publish_date),
                       'extracted': datetime.utcnow(),
                       'topics': []}
            db.test.insert_one(article)
            newsPaper['articles'].append(article)
            print(count, "articles downloaded from", company, " using newspaper, url: ", content.url)
            count = count + 1
            noneTypeCount = 0
    count = 1
    data['newspapers'][company] = newsPaper

# Close DB connection
client.close()

# Finally it saves the articles as a JSON-file.
"""
try:
    with open('scraped_articles.json', 'w') as outfile:
        json.dump(data, outfile)
except Exception as e: print(e)
"""
