#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask app for querying scraped news.
"""
__title__ = 'mmld'
__author__ = 'Ivan Fernando Galaviz Mendoza'

import datetime
from wtforms import StringField, TextAreaField, SubmitField, validators, \
    SelectField
from wtforms.fields.html5 import DateTimeLocalField, SearchField
from flask import Flask, render_template
from flask_navigation import Navigation
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from tables import NewsTable
from config import Config
import constants

app = Flask(__name__)
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
                                       format='%d-%m-%YT%H:%M')
    pub_date_to = DateTimeLocalField(END_DATE_LABEL,
                                     validators=(validators.Optional(),),
                                     format='%d-%m-%YT%H:%M')
    extract_date_from = DateTimeLocalField(START_DATE_LABEL,
                                           validators=(validators.Optional(),))
    extract_date_to = DateTimeLocalField(END_DATE_LABEL,
                                         validators=(validators.Optional(),))

    submit = SubmitField('Search')


nav.Bar('top', [
    nav.Item('News Search', 'submit'),
    nav.Item('About', 'about')
])


@app.route('/', methods=('GET', 'POST'))
def submit():
    form = NewsSearchForm()
    print('Pubdate_from =', form.pub_date_from)
    print('Pubdate_from =', form.pub_date_from.data)
    print('Pubdate_to=', form.pub_date_to)
    print('Pubdate_to=', form.pub_date_to.data)
    if form.validate_on_submit():
        return search_results(form)
    return render_template('index.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/results')
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
        query[constants.NEWSPAPER] = newspaper_data
    if title_data is not "":
        query[constants.TITLE] = title_data
    if content_data is not "":
        query[constants.TEXT] = content_data
    if pub_date_from_data is not None and pub_date_to_data is not None:
        query[constants.PUB_DATE] = {
            '$gte': pub_date_from_data,
            '$lt': pub_date_to_data
        }
    if extract_date_from_data is not None and extract_date_to_data is not None:
        query[constants.EXTRACT_DATE] = {
            '$gte': extract_date_from_data,
            '$lt': extract_date_to_data
        }

    items = mongo.db.test.find(query)
    table = NewsTable(items)

    return render_template('results.html', table=table)


if __name__ == '__main__':
    app.run()
