#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classifier. Tells if the news content is violent or not,
then updates the document in the database.
"""
__title__ = 'Classifier'
__author__ = 'Ivan Fernando Galaviz Mendoza'
import pickle
from threading import Thread, Condition

from pymongo import MongoClient

import constants


class Classifier(Thread):
    def __init__(self):
        super().__init__()
        self._vectorizer = deserialize(
            constants.SERIALIZED_COUNT_VECTORIZER_FILENAME)
        self._classifier = deserialize(constants.SERIALIZED_CLASSIFIER_FILENAME)
        self._work = False
        self._cond = Condition()
        self._client = MongoClient()
        self._db = self._client['test']

    def run(self):
        """
        Finds news that haven't been classified and updates info in database.
        Info updated:
        * is_classified -> set to True.
        * is_violent -> asks to the classifier if the news content
            was found as violent or not.
        """
        while True:
            self._cond.acquire()
            while not self._work:
                self._cond.wait()
            self._cond.release()
            for article in self._db.test.find({constants.IS_CLASSIFIED: False}):
                self._db.update_one(
                    {constants.MONGO_ID: article[constants.MONGO_ID]},
                    {"$set": {constants.IS_CLASSIFIED: True,
                              constants.IS_VIOLENT: self.is_violent(
                                  self.text_to_tokens(
                                      article[constants.TEXT]))}}
                )
            self._work = False

    def text_to_tokens(self, text):
        """
        Transform a given text to a matrix of token counts.
        :param text: text to be converted.
        :return: matrix of token counts.
        """
        return self._vectorizer.transform(text)

    def is_violent(self, transformed_text):
        """
        Asks to the classifier if the received text is related to violence.
        :param transformed_text: token counts matrix
            to determine if it's violent.
        :return: if the text is violent or not.
        """
        prediction = self._classifier.predict_proba(transformed_text)
        return prediction[0][constants.NON_VIOLENT_CLASS_ID] \
               < prediction[0][constants.VIOLENT_CLASS_ID]

    def notify(self):
        self._cond.acquire()
        self._work = True
        self._cond.notify()
        self._cond.release()


def deserialize(filename):
    """
    Loads object from file.
    :param filename: name of the file where the object was serialized.
    :return: object deserialized.
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)
