#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classifier. Tells if the news content is violent or not,
then updates the document in the database.
"""
__title__ = 'Classifier'
__author__ = 'Ivan Fernando Galaviz Mendoza'
import pickle
from threading import Thread

from pymongo import MongoClient
from bson.objectid import ObjectId

import constants


class Classifier(Thread):
    def __init__(self):
        super().__init__()
        self._vectorizer = deserialize(
            constants.SERIALIZED_COUNT_VECTORIZER_FILENAME)
        self._classifier = deserialize(constants.SERIALIZED_CLASSIFIER_FILENAME)
        self._client = MongoClient()
        self._db = self._client['test']
        self.set_stop_words()
        self.start()

    def run(self):
        """
        Finds news that haven't been classified and updates info in database.
        Info updated:
        * is_classified -> set to True.
        * is_violent -> asks to the classifier if the news content
            was found as violent or not.
        """
        for article in self._db.test.find({constants.HAS_BEEN_CLASSIFIED: False}):
            self._db.test.update_one(
                {constants.MONGO_ID: ObjectId(article[constants.MONGO_ID])},
                {
                    "$set": {
                        constants.HAS_BEEN_CLASSIFIED: True,
                        constants.IS_VIOLENT: self.is_violent(
                            self.text_to_tokens(
                                [article[constants.TEXT]]))
                    }
                }
            )
        self._client.close()

    def set_stop_words(self):
        with open('stopwords-es.txt', encoding="utf-8") as f:
            setattr(self._vectorizer, 'stop_words', f.read().splitlines())

    def text_to_tokens(self, text):
        """
        Transform a given list of texts to a matrix of token counts.
        :param text: list of texts to be converted.
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
        if prediction[0][constants.NON_VIOLENT_CLASS_ID] \
                < prediction[0][constants.VIOLENT_CLASS_ID]:
            return True
        return False


def deserialize(filename):
    """
    Loads object from file.
    :param filename: name of the file where the object was serialized.
    :return: object deserialized.
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)
