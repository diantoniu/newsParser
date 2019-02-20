import time
from threading import Thread
from parser.tsnParser import TsnParser
from parser.ukrNetParser import UkrNetParser


class ParserThread(Thread):
    """
    A class used to represent a parser of news
    """

    def __init__(self, name, secondsUpdating):
        """
        Constructor

        Prameters
        ----------
        name : str
            the name of the thread

        secondsUpdating : int
            sleep time period before next parsing round
        """
        Thread.__init__(self)
        self.name = name
        self.secondsUpdating = secondsUpdating

    def run(self):
        ukrNetParser = UkrNetParser()
        tsnParser = TsnParser()
        while True:
            tsnParser.parseNews()
            ukrNetParser.parseNews()
            time.sleep(self.secondsUpdating)
