# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ScraperScheduler. Creates a scheduler for scraping news
at a certain time of the day.
"""
__title__ = 'ScraperScheduler'
__author__ = 'Ivan Fernando Galaviz Mendoza'
from time import sleep
from threading import Thread
from schedule import Scheduler
from constants import TIME_TO_SCRAPE_ARTICLES


class ScraperScheduler(Thread):
    def __init__(self, job):
        super(ScraperScheduler, self).__init__()
        self._scheduler = Scheduler()
        self._scheduler.every().day.at(TIME_TO_SCRAPE_ARTICLES).do(job)
        self.start()

    def run(self):
        while True:
            self._scheduler.run_pending()
            sleep(1)
