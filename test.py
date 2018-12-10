#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask app for querying scraped news.
"""
__title__ = 'mmld'
__author__ = 'Ivan Fernando Galaviz Mendoza'

from wtforms import TextAreaField, SubmitField, validators
from wtforms.fields.html5 import DateTimeLocalField, SearchField
from flask import Flask, render_template
from flask_navigation import Navigation
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from tables import NewsTable
from config import Config
import constants
from scheduler import ScraperScheduler
from NewsScraper import scrape_news

ScraperScheduler(scrape_news)

# This prefix is used for deployment
# Change it to an empty string for debugging (running the app locally)
PREFIX = "/news-scraper"

app = Flask(
    __name__,
    static_url_path=PREFIX
    )

app.config.from_object(Config)
nav = Navigation(app)

mongo = PyMongo(app)


class NewsSearchForm(FlaskForm):
    START_DATE_LABEL = 'Start Date'
    END_DATE_LABEL = 'End Date'

    newspaper = SearchField('Newspaper',
                            validators=(validators.Optional(),),
                            render_kw={"placeholder": "Name of the newspaper..."})
    title = SearchField('Title', validators=(validators.Optional(),),
                        render_kw={"placeholder": "Title of the article..."})
    content = TextAreaField('Content', validators=(validators.Optional(),),
                            render_kw={"placeholder": "Content of the article..."})
    #    state = SelectField('State', choices=)
    pub_date_from = DateTimeLocalField(START_DATE_LABEL,
                                       validators=(validators.Optional(),),
                                       format='%Y-%m-%dT%H:%M')
    pub_date_to = DateTimeLocalField(END_DATE_LABEL,
                                     validators=(validators.Optional(),),
                                     format='%Y-%m-%dT%H:%M')
    extract_date_from = DateTimeLocalField(START_DATE_LABEL,
                                           validators=(validators.Optional(),),
                                           format='%Y-%m-%dT%H:%M')
    extract_date_to = DateTimeLocalField(END_DATE_LABEL,
                                         validators=(validators.Optional(),),
                                         format='%Y-%m-%dT%H:%M')

    submit = SubmitField('Search')


nav.Bar('top', [
    nav.Item('News Search', 'submit'),
    nav.Item('About', 'about')
])


@app.route(PREFIX + '/', methods=('GET', 'POST'))
def submit():
    form = NewsSearchForm()
    if form.validate_on_submit():
        return search_results(form)
    return render_template('index.html', form=form)


@app.route(PREFIX + '/about')
def about():
    return render_template('about.html')


@app.route(PREFIX + '/results')
def search_results(search):
    query = {}

    newspaper_data = search.newspaper.data
    title_data = search.title.data
    content_data = search.content.data
    pub_date_from_data = search.pub_date_from.data
    pub_date_to_data = search.pub_date_to.data
    extract_date_from_data = search.extract_date_from.data
    extract_date_to_data = search.extract_date_to.data

    if newspaper_data is not "":
        query[constants.NEWSPAPER] = generate_regex_dict(newspaper_data)
    if title_data is not "":
        query[constants.TITLE] = generate_regex_dict(title_data)
    if content_data is not "":
        query[constants.TEXT] = generate_regex_dict(content_data)
    if pub_date_from_data is not None and pub_date_to_data is not None:
        query[constants.PUB_DATE] = generate_date_search_dict(
            pub_date_from_data, pub_date_to_data)
    if extract_date_from_data is not None and extract_date_to_data is not None:
        query[constants.EXTRACT_DATE] = generate_date_search_dict(
            extract_date_from_data, extract_date_to_data)

    items = mongo.db.test.find(query)
    table = NewsTable(items)

    return render_template('results.html', table=table)


def generate_regex_dict(search_field):
    """
    Adds 'like' functionality as in a SQL query
    also adds non case-sensitive option.
    :param search_field: field that wants to be searched as a 'like' in SQL.
    :return: dict for a mongodb query, contemplating non case-sensitivity.
    """
    return {
        '$regex': '.*{}.*'.format(search_field),
        '$options': 'i'
    }


def generate_date_search_dict(start_date, end_date):
    """
    Generates a dict that allows to search in a date range with mongodb.
    :param start_date: date to begin search.
    :param end_date: date to end search.
    :return: compatible mongodb query dict.
    """
    return {
        '$gte': start_date,
        '$lt': end_date
    }


if __name__ == '__main__':
    app.run(debug=False)
