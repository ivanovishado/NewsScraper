#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
News scraper, scrapes articles from a newspaper then adds them to a database.
"""
__title__ = 'NewsScraper'
__author__ = 'Ivan Fernando Galaviz Mendoza'

from datetime import datetime
from time import mktime
import json
import logging
from pymongo import MongoClient
from newspaper import Article, build
import feedparser as fp
import constants
from classifier import Classifier

logging.basicConfig(filename=constants.LOG_FILENAME,
                    format='%(asctime)s-%(levelname)s-%(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

# TODO: Assign timezones accordingly to the region (e.g. Jalisco)
# TODO: Create a temp dict to use when losing connection to the db
# TODO: Create index from the data to prevent repeated registers (db.profiles.create_index())


def try_to_get_utc(date, link):
    try:
        return datetime.utcfromtimestamp(mktime(date))
    except Exception:
        logging.warning(
            'Could not get UTC time from {}'.format(link), exc_info=True)
        return date


def log_invalid_text(link):
    logging.warning('Ignoring {} due to invalid body.'.format(link))


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
    article_link = info['link']
    paper = build(article_link, language='es')
    none_type_count = 0
    article_count = 0
    for article in paper.articles:
        if article_count > constants.ARTICLES_TO_DOWNLOAD:
            break
        try:
            article.download()
            article.parse()
        except Exception:
            logging.warning('Could not download/parse {}'.format(article_link),
                            exc_info=True)
            continue
        # Again, for consistency, if there is no found publish date
        # the article will be skipped.
        # After 10 downloaded articles from the same newspaper
        # without publish date, the company will be skipped.
        if article.publish_date is None:
            none_type_count += 1
            if none_type_count > 10:
                logging.warning(
                    'Skipping {} because of too many noneType dates...'.format(
                        company))
                break
            article_count += 1
            continue
        article_text = article.text
        article_url = article.url
        if not article_text:
            log_invalid_text(article_url)
            continue
        db.test.insert_one({
            constants.NEWSPAPER: company,
            constants.TITLE: article.title,
            constants.TEXT: article_text,
            constants.TAGS: list(article.tags),
            constants.LINK: article_url,
            constants.PUB_DATE: article.publish_date,
            constants.EXTRACT_DATE: datetime.utcnow(),
            constants.HAS_BEEN_CLASSIFIED: False,
            constants.IS_VIOLENT: None
        })


def parse_rss(company, info, db):
    parsed_dict = fp.parse(info['rss'])
    article_count = 0
    for entry in parsed_dict.entries:
        # Check if publish date is provided, if no the article is skipped.
        # This is done to keep consistency in the data
        # and to keep the script from crashing.
        if not hasattr(entry, 'published'):
            continue
        if article_count > constants.ARTICLES_TO_DOWNLOAD:
            break
        article_link = entry.link
        try:
            article = Article(article_link, fetch_images=False)
            article.download()
            article.parse()
        except Exception:
            # If the download for some reason fails (ex. 404)
            # the script will continue downloading the next article.
            logging.warning('Could not download/parse {}'.format(article_link),
                            exc_info=True)
            continue
        article_text = article.text
        if not article_text:
            log_invalid_text(article_link)
            continue
        db.test.insert_one({
            constants.NEWSPAPER: company,
            constants.TITLE: article.title,
            constants.TEXT: article_text,
            constants.TAGS: list(article.tags),
            constants.LINK: article_link,
            constants.PUB_DATE: try_to_get_utc(entry.published_parsed,
                                               article_link),
            constants.EXTRACT_DATE: datetime.utcnow(),
            constants.HAS_BEEN_CLASSIFIED: False,
            constants.IS_VIOLENT: None
        })
