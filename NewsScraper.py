#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
News scraper, scrapes articles from a newspaper then adds them to a database.
"""
__title__ = 'mmld'
__author__ = 'Ivan Fernando Galaviz Mendoza'

import argparse
from datetime import datetime
from time import mktime
import json
from pymongo import MongoClient
from newspaper import Article, build
import feedparser as fp
import constants
from classifier import Classifier

# TODO: Asignar timezones pertinentes al estado -- time.localtime().tm_isdst
# TODO: Crear diccionario temporal para cuando se pierda la conexión con la base de datos
# TODO: Schedule parse_news()
# TODO: Unfork project


p = argparse.ArgumentParser("NewsScraper")
p.add_argument("-f", "--filename", default="./resources/NewsPapers.json",
               type=str, action="store", dest="filename",
               help="File to get news [NewsPaper.json]")

opts = p.parse_args()

# Set the limit for number of articles to download
ARTICLES_TO_DOWNLOAD = 10

# Loads the JSON file with news sites
with open(opts.filename) as data_file:
    companies = json.load(data_file)


def try_to_get_utc(date):
    try:
        return datetime.utcfromtimestamp(mktime(date))
    except Exception as e:
        print(e)
        return date


# Initialize database connection
client = MongoClient()

# Assign database
db = client.test


def is_valid_text(text):
    return text is not None and text != ""


def print_invalid_text_warning():
    print("Ignoring article due to invalid body.")


def scrape_news():
    for company, info in companies.items():
        # If a RSS link is provided in the JSON file,
        # this will be the first choice.
        # Reason for this is that,
        # RSS feeds often give more consistent and correct data.
        # If you do not want to scrape from the RSS-feed,
        # just leave the RSS attr empty in the JSON file.
        if 'rss' in info:
            article_to_insert = parse_rss(company, info)
        else:
            article_to_insert = parse_link(company, info)
        db.test.insert_one(article_to_insert)


def parse_link(company, info):
    print("Building site for", company)
    paper = build(info['link'], language='es')
    none_type_count = 0
    count = 0
    for article in paper.articles:
        print("Processing article", count)
        if count > ARTICLES_TO_DOWNLOAD:
            break
        try:
            article.download()
            article.parse()
        except Exception as e:
            print(e)
            print("continuing...")
            continue
        # Again, for consistency, if there is no found publish date
        # the article will be skipped.
        # After 10 downloaded articles from the same newspaper
        # without publish date, the company will be skipped.
        if article.publish_date is None:
            print(count, " Article has date of type None...")
            none_type_count += 1
            if none_type_count > 10:
                print("Too many noneType dates, aborting...")
                break
            count += 1
            continue
        if not is_valid_text(article.text):
            print_invalid_text_warning()
            continue
        return {
            constants.NEWSPAPER: company,
            constants.TITLE: article.title,
            constants.TEXT: article.text,
            constants.TAGS: list(article.tags),
            constants.LINK: article.url,
            constants.PUB_DATE: article.publish_date,
            constants.EXTRACT_DATE: datetime.utcnow(),
            constants.HAS_BEEN_CLASSIFIED: False,
            constants.IS_VIOLENT: None
        }


def parse_rss(company, info):
    parsed_dict = fp.parse(info['rss'])
    print("Downloading articles from", company)
    count = 0
    for entry in parsed_dict.entries:
        # Check if publish date is provided, if no the article is skipped.
        # This is done to keep consistency in the data
        # and to keep the script from crashing.
        if not hasattr(entry, 'published'):
            continue
        if count > ARTICLES_TO_DOWNLOAD:
            break
        try:
            article = Article(entry.link, fetch_images=False)
            article.download()
            article.parse()
        except Exception as e:
            # If the download for some reason fails (ex. 404)
            # the script will continue downloading the next article.
            print(e)
            print("continuing...")
            continue
        if not is_valid_text(article.text):
            print_invalid_text_warning()
            continue
        return {
            constants.NEWSPAPER: company,
            constants.TITLE: article.title,
            constants.TEXT: article.text,
            constants.TAGS: list(article.tags),
            constants.LINK: entry.link,
            constants.PUB_DATE: try_to_get_utc(entry.published_parsed),
            constants.EXTRACT_DATE: datetime.utcnow(),
            constants.HAS_BEEN_CLASSIFIED: False,
            constants.IS_VIOLENT: None
        }


# Close DB connection
client.close()

clf = Classifier()
clf.start()
clf.notify()
