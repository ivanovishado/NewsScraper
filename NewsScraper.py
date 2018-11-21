#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
News scraper, scrapes articles from a newspaper then adds them to a database.
"""
__title__ = 'mmld'
__author__ = 'Ivan Fernando Galaviz Mendoza'

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
# TODO: Crear index a partir de datos para evitar registros repetidos (db.profiles.create_index())


def try_to_get_utc(date):
    try:
        return datetime.utcfromtimestamp(mktime(date))
    except Exception as e:
        print(e)
        return date


def print_invalid_text_warning():
    print("Ignoring article due to invalid body.")


def start_classification():
    Classifier()


def scrape_news():
    # Loads the JSON file with news sites
    with open(constants.NEWSPAPERS_PATH) as newspapers_file:
        companies = json.load(newspapers_file)

    # Initialize database connection
    client = MongoClient()

    # Assign database
    db = client.test

    print('Companies: ', companies)
    for company, info in companies.items():
        # If a RSS link is provided in the JSON file,
        # this will be the first choice.
        # Reason for this is that,
        # RSS feeds often give more consistent and correct data.
        # If you do not want to scrape from the RSS-feed,
        # just leave the RSS attr empty in the JSON file.
        if 'rss' in info:
            parse_rss(company, info, db)
        else:
            parse_link(company, info, db)

    # Close DB connection
    client.close()

    start_classification()


def parse_link(company, info, db):
    print("Building site for", company)
    paper = build(info['link'], language='es')
    none_type_count = 0
    article_count = 0
    for article in paper.articles:
        print("Processing article", article_count)
        if article_count > constants.ARTICLES_TO_DOWNLOAD:
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
            print(article_count, " Article has date of type None...")
            none_type_count += 1
            if none_type_count > 10:
                print("Too many noneType dates, aborting...")
                break
            article_count += 1
            continue
        article_text = article.text
        if not article_text:
            print_invalid_text_warning()
            continue
        db.test.insert_one({
            constants.NEWSPAPER: company,
            constants.TITLE: article.title,
            constants.TEXT: article_text,
            constants.TAGS: list(article.tags),
            constants.LINK: article.url,
            constants.PUB_DATE: article.publish_date,
            constants.EXTRACT_DATE: datetime.utcnow(),
            constants.HAS_BEEN_CLASSIFIED: False,
            constants.IS_VIOLENT: None
        })


def parse_rss(company, info, db):
    parsed_dict = fp.parse(info['rss'])
    print("Downloading articles from", company)
    article_count = 0
    for entry in parsed_dict.entries:
        # Check if publish date is provided, if no the article is skipped.
        # This is done to keep consistency in the data
        # and to keep the script from crashing.
        if not hasattr(entry, 'published'):
            continue
        if article_count > constants.ARTICLES_TO_DOWNLOAD:
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
        article_text = article.text
        if not article_text:
            print_invalid_text_warning()
            continue
        db.test.insert_one({
            constants.NEWSPAPER: company,
            constants.TITLE: article.title,
            constants.TEXT: article_text,
            constants.TAGS: list(article.tags),
            constants.LINK: entry.link,
            constants.PUB_DATE: try_to_get_utc(entry.published_parsed),
            constants.EXTRACT_DATE: datetime.utcnow(),
            constants.HAS_BEEN_CLASSIFIED: False,
            constants.IS_VIOLENT: None
        })
