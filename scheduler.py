from time import sleep
from threading import Thread
from schedule import Scheduler


class ScraperScheduler(Thread):
    def __init__(self, job):
        super(ScraperScheduler, self).__init__()
        self._scheduler = Scheduler()
        self._scheduler.every().day.at("03:00").do(job)
        self.start()

    def run(self):
        while True:
            self._scheduler.run_pending()
            sleep(1)
