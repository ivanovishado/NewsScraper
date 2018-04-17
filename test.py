#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask app for searching scraped news.
"""
__title__ = 'mmld'
__author__ = 'Ivan Fernando Galaviz Mendoza'

from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, validators, SelectField
from wtforms.fields.html5 import DateField
from flask_pymongo import PyMongo
from config import Config
from tables import NewsTable

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)


class NewsSearchForm(FlaskForm):
    START_DATE_LABEL = 'Start Date'
    END_DATE_LABEL = 'End Date'

    newspaper = StringField('Newspaper', validators=(validators.Optional(),))
    title = StringField('Title', validators=(validators.Optional(),))
    content = TextAreaField('Content', validators=(validators.Optional(),))
#    state = SelectField('State', choices=)
    pub_date_start = DateField(START_DATE_LABEL,
                               validators=(validators.Optional(),),
                               default="")
    pub_date_end = DateField(END_DATE_LABEL,
                             validators=(validators.Optional(),),
                             default="")
    extract_date_start = DateField(START_DATE_LABEL,
                                   validators=(validators.Optional(),),
                                   default="")
    extract_date_end = DateField(END_DATE_LABEL,
                                 validators=(validators.Optional(),),
                                 default="")

    submit = SubmitField('Submit')


@app.route('/', methods=('GET', 'POST'))
def submit():
    form = NewsSearchForm()
    if form.validate_on_submit():
        return search_results(form)
    return render_template('submit.html', form=form)


@app.route('/results')
def search_results(search):
    query_dict = {}

    newspaper_data = search.newspaper.data
    title_data = search.title.data
    content_data = search.content.data

    if newspaper_data is not "":
        query_dict['newspaper'] = newspaper_data
    if title_data is not "":
        query_dict['title'] = title_data
    if content_data is not "":
        query_dict['content'] = content_data
    if search.pub_date_start.data is not None \
        and search.pub_date_end.data is not None:
        pass

    print("date= ", search.pub_date_start.data)
    print("date2= ", search.pub_date_end.data)

    items = mongo.db.test.find(query_dict)
    table = NewsTable(items)

    return render_template('results.html', table=table)


if __name__ == '__main__':
    app.run()
