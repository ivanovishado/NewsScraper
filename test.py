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
from wtforms.fields.html5 import DateField
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


class CustomDateField(DateField):
    def __init__(self, label, **kwargs):
        super().__init__(label,
                         validators=(validators.Optional(),),
                         default=datetime.date.today(),
                         **kwargs)



class NewsSearchForm(FlaskForm):
    START_DATE_LABEL = 'Start Date'
    END_DATE_LABEL = 'End Date'

    newspaper = StringField('Newspaper', validators=(validators.Optional(),))
    title = StringField('Title', validators=(validators.Optional(),))
    content = TextAreaField('Content', validators=(validators.Optional(),))
    #    state = SelectField('State', choices=)
    pub_date_from = CustomDateField(START_DATE_LABEL)
    pub_date_from = DateField(START_DATE_LABEL,
                              validators=(validators.Optional(),),
                              default=datetime.date.today())
    pub_date_to = DateField(END_DATE_LABEL,
                            validators=(validators.Optional(),),
                            default=datetime.date.today())
    extract_date_from = DateField(START_DATE_LABEL,
                                  validators=(validators.Optional(),),
                                  default=datetime.date.today())
    extract_date_to = DateField(END_DATE_LABEL,
                                validators=(validators.Optional(),),
                                default=datetime.date.today())

    submit = SubmitField('Submit')


nav.Bar('top', [
    nav.Item('Home', 'submit')
])


@app.route('/', methods=('GET', 'POST'))
def submit():
    form = NewsSearchForm()
    if form.validate_on_submit():
        return search_results(form)
    return render_template('index.html', form=form)


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
