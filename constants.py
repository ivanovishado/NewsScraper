#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constants for maintaining order between the scraper and the web app.
"""

MONGO_ID = '_id'
NEWSPAPER = 'newspaper'
TITLE = 'title'
TEXT = 'text'
TAGS = 'tags'
LINK = 'link'
PUB_DATE = 'pub_date'
EXTRACT_DATE = 'extract_date'
HAS_BEEN_CLASSIFIED = 'is_classified'
IS_VIOLENT = 'is_violent'
ID_FILENAME = 'cur_id.txt'
NON_VIOLENT_CLASS_ID = 0
VIOLENT_CLASS_ID = 1
SERIALIZED_COUNT_VECTORIZER_FILENAME = 'CV.pkl'
SERIALIZED_CLASSIFIER_FILENAME = 'clf.pkl'
ARTICLES_TO_DOWNLOAD = 10
NEWSPAPERS_PATH = './resources/NewsPapers.json'
TIME_TO_SCRAPE_ARTICLES = '03:00'
LOG_FILENAME = 'app.log'
