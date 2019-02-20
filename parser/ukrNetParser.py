import requests
import datetime
from parser.models import *
import json
import pytz
from datetime import datetime
from parser.tsnParser import TsnParser
import re


class UkrNetParser:
    """
    A class used to represent a parser of https://www.ukr.net website

    Attributes
    ----------
    urlStart : str
        the standard start of all ukr.net URLs, that parser need to parse

    urlEnd : str
        the standard end of all ukr.net URLs, that parser need to parse

    maxNewsAmountInCategory: int
        maximum amount of news parser will parse in one category

    source : str
        link to ukr.net website

    ukrNetRegex : SRE_Pattern
        regular expression that matches all URLs of ukr.net

    Methods
    -------
    getJsonText(url)
        returns the parsed data in json format

    parseNewsItem(newsDict, categoryId)
        creates News item and saves it to the database

    parseNewsListPage(url, categoryId)
        iterates through the list of news items and forward each one to the parseNewsItem method

    parseNewsCategory(self, url, categoryId)
        iterates through the category pages and each page forward to the parseNewsListPage method

    parseNews()
        iterates through the all categories of ukr.net and forward each one to the parseNewsCategory method
    """

    urlStart = 'https://www.ukr.net/news/dat/'
    urlEnd = '/'
    maxNewsAmountInCategory = 1000
    source = 'https://www.ukr.net'
    ukrNetRegex = re.compile('^(http|https)://www.ukr.net.*')

    def __init__(self):
        self.categories = UkrNetCategory.objects.all()

    def getJsonText(self, url):
        """
        Parse the data form the url

        Parameters
        ----------
        url : str
            url from which to parse the data

        Returns
        -------
        json string
        """

        r = requests.get(url)
        return r.text

    def parseNewsItem(self, newsDict, categoryId):
        """
         Creates News item and saves it to the database

        Parameters
        ----------
        newsDict : dictionary
            dictionary which represents of news item

        categoryId : int
            the id of current news category

        Returns
        -------
        False
            if in the database already exists the same News item
        """

        news = News()

        # url
        news.url = newsDict.get('Url')

        # title
        news.title = newsDict.get('Title')
        news.lowercaseTitle = news.title.lower()

        # time
        timeStamp = int(newsDict.get('DateCreated'))
        news.time = datetime.fromtimestamp(timeStamp, tz=pytz.UTC)

        # category
        news.categoryId = categoryId

        # source
        news.source = UkrNetParser.source

        if News.objects.filter(url=news.url).exists() and News.objects.get(url=news.url).source == UkrNetParser.source:
            return False
        elif TsnParser.tsnRegex.search(news.url) is None:
            news.save()

    def parseNewsListPage(self, url, categoryId):
        """
        Iterates through the list of news items and forward each one to the parseNewsItem method.

        Parameters
        ----------
        url : string
            url from which to parse the data

        categoryId : int
            the id of current news category

        Raises
        ------
        Exception
            if can not encode the json data about the page

        Returns
        -------
        False
            if it is necessary to stop parsing current category because all news in the category already parsed
            or some error occurred

        True
            if it is necessary to stop parsing current category because there are no more news in the category
        """

        jsonText = self.getJsonText(url)
        try:
            newsDictList = json.loads(jsonText).get('tops')
            for news in newsDictList:
                if self.parseNewsItem(news, categoryId) is False:
                    return False
            if len(newsDictList) == 0:
                return True

        except Exception as e:
            print('\nTime: ' + str(datetime.now()) +
                  '\nError message: ' + str(e) +
                  '\nError occurred while parsing the ' + url + ' page.')
            return False

    def parseNewsCategory(self, url, categoryId):
        """
         Iterates through the category pages and each page forward to the parseNewsListPage method.

        Parameters
        ----------
        url : string
            uncompleted url which includes category name

        categoryId : int
            the id of current news category
        """

        for pageNum in range(1, UkrNetParser.maxNewsAmountInCategory):
            currentUrl = url + str(pageNum) + UkrNetParser.urlEnd

            # stop iterating if no longer needed to analyze the news in current category
            result = self.parseNewsListPage(currentUrl, categoryId)
            if result is not None:
                return

    def parseNews(self):
        """
        Iterates through the all categories of ukr.net and forward each one to the parseNewsCategory method
        """

        for category in self.categories:
            # form url from urlStart and current category name
            currentUrl = UkrNetParser.urlStart + category.name + '/'
            self.parseNewsCategory(currentUrl, category.categoryId)
