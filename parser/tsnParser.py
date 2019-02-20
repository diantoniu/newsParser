from bs4 import BeautifulSoup
import requests
import re, os
import datetime
import urllib.request
from parser.models import News
import json
from parser.models import *


class TsnParser:
    """
    A class used to represent a parser of https://tsn.ua website

    Attributes
    ----------
    urlStart : str
        the standard start of all tsn.ua URLs, that parser need to parse

    urlEnd : str
        the standard end of all tsn.ua URLs, that parser need to parse

    maxNewsAmountInDay : int
        maximum amount of news parser will parse in one day

    maxDaysAmount : int
        maximum amount of days parser will parse

    source : str
        link to tsn.ua website

    tsnRegex : SRE_Pattern
        regular expression that matches all URLs of tsn.ua

    imgFolder : str
        folder to which images should be saved

    Methods
    -------
    getJsonText(url)
        returns the parsed data in json format

    parseHtml(url)
        returns the parsed data if BeautifulSoup format

    parseNewsPage(url)
        creates News item based on the page data, saves it to the database

    parseNewsListPage(url)
        iterates through the list of news and forward url of each one to the parseNewsPage method

    isLastPage(url)
        check if there are no more news pages in the current day

    getLastPageNum(url)
        return number of the last news page in the current day

    parseNewsDate(url)
        iterates through the news pages of the current day and each page forward to the parseNewsListPage method

    parseNews()
        iterates through the days and forward each one to the parseNewsDate method
    """

    urlStart = 'https://tsn.ua/ajax/archive/'
    urlEnd = '?page='
    maxNewsAmountInDay = 1000
    maxDaysAmount = 3
    source = 'https://tsn.ua'
    tsnRegex = re.compile('^(http|https)://tsn.ua.*')
    imgFolder = 'static/img/'

    def __init__(self):
        self.categories = TsnCategory.objects.all()

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

    def parseHtml(self, url):
        """
        Parse the data form the url

        Parameters
        ----------
        url : str
            url from which to parse the data

        Returns
        -------
        BeautifulSoup object
        """

        return BeautifulSoup(self.getJsonText(url), 'html.parser')

    def parseNewsPage(self, url):
        """
        Creates News item based on the parsed data, saves it to the database

        Parameters
        ----------
        url : str
            url from which to parse the data about news

        Raises
        ------
        Exception
            if can not parse url, title, category or time of the current news

        Returns
        -------
        False
            if in the database already exists the same News item
        """

        if not os.path.exists('static/img'):
            os.makedirs('static/img')

        soup = self.parseHtml(url)
        for div in soup.find_all('div', {'class': 'c-sidebar'}):
            div.decompose()
        news = News()
        try:
            # url
            news.url = url

            # title
            news.title = soup.find('h1', attrs={'class': 'c-post-title'}).text.strip()
            news.lowercaseTitle = news.title.lower()

            # news can exist without the picture
            try:
                # picture
                articlePicture = soup.find('header', attrs={'class': 'c-entry'}).find('img')['src']
                articlePictureName = articlePicture.rsplit('/')[-1]
                articlePicturePath = TsnParser.imgFolder + articlePictureName
                urllib.request.urlretrieve(articlePicture, articlePicturePath)
                news.picture = articlePictureName
            except:
                pass

            # category
            category = news.url.split('/')[3]
            news.categoryId = self.categories.get(name=category).categoryId

            # time
            news.time = soup.find('time', attrs={'class': 'dt-published c-post-time'})['datetime'].strip()

            # content
            articleText = soup.find('div', attrs={'class': 'e-content'}).findAll('p', recursive=False)
            for i in articleText:
                news.text += i.text.strip() + '\n'
            news.lowercaseText = news.text.lower()

            # source
            news.source = TsnParser.source

            # news can exist without the tags
            try:
                # tags
                articleTags = soup.find('ul', attrs={'class': 'c-tag-list'}).findAll('li')
                news.tags = ''
                for i in articleTags:
                    news.tags += '#' + i.text.strip()
                news.lowercaseTags = news.tags.lower()
            except:
                pass

            if News.objects.filter(url=news.url).exists():
                return False
            news.save()

        except Exception as e:
            print('Time: ' + str(datetime.datetime.now()) +
                  '\nError message: ' + str(e) +
                  '\nError occurred while parsing the ' + url + ' page.')

    def parseNewsListPage(self, url):
        """
        Iterates through the list of news and forward url of each one to the parseNewsPage method

        Parameters
        ----------
        url : string
            url from which to parse the data

        Raises
        ------
        Exception
            if can not encode the json data about the page

        Returns
        -------
        False
            if it is necessary to stop parsing the news because all of them already parsed

        True
            it is necessary to stop parsing the news in the current day because there are no more pages of news in
            the day
        """

        try:
            text = json.loads(self.getJsonText(url))
            html = text.get('html')
            soup = BeautifulSoup(html, 'html.parser')

            # categories of news that can be parsed
            allow = re.compile('^(http|https)://.*(/ukrayina/|/politika/|/prosport/'
                               '|/glamur/|/groshi/|/auto/|/nauka_it/|/svit/|/tourism/|/ato/|/kyiv/|/tsikavinki/|/books/)')

            # categories of news that can not be parsed
            avoid = re.compile('(/video/|/video-novini/|/blogi/)')

            # all artcle items
            newsList = soup.findAll('article')
            for news in reversed(newsList):

                # current news url
                newsUrl = news.find(href=True)['href']

                # check if news can be parsed
                if (allow.search(newsUrl) is not None) and (avoid.search(newsUrl) is None):
                    if self.parseNewsPage(newsUrl) is False:
                        return False
            if len(newsList) == 0:
                return True

        except Exception as e:
            print('Time: ' + str(datetime.datetime.now()) +
                  '\nError message: ' + str(e) +
                  '\nError occurred while parsing the ' + url + ' page.')

    def isLastPage(self, url):
        """
        Check if there are no more news pages in the current day

        Parameters
        ----------
        url : string
            url from which to parse the data

        Returns
        -------
        False:
            if there no more in the current day

        True:
            otherwise
        """

        text = json.loads(self.getJsonText(url))
        html = text.get('html')
        if html == '':
            return True
        return False

    def getLastPageNum(self, url):
        """
        Return number of the last news page in the current day

        Parameters
        ----------
        url : string
            url from which to parse the data

        Returns
        -------
        int
            number of the last news page in the current day
        """

        lastPageNum = 1
        for pageNum in range(1, TsnParser.maxNewsAmountInDay):
            currentUrl = url + str(pageNum)
            if self.isLastPage(currentUrl):
                lastPageNum = pageNum - 1
                break
        return lastPageNum

    def parseNewsDate(self, url):
        """
        Iterates through the news pages of the current day and each page forward to the parseNewsListPage method

        Parameters
        ----------
        url : string
            url from which to parse the data

        Returns
        -------
        False
            if it is necessary to stop parsing the news because all of them already parsed

        True
            it is necessary to stop parsing the news in the current day because there are no more pages of news in
            the day
        """

        lastPageNum = self.getLastPageNum(url)
        for pageNum in range(lastPageNum, 0, -1):
            currentUrl = url + str(pageNum)
            result = self.parseNewsListPage(currentUrl)
            if result is not None:
                return result

    def parseNews(self):
        """
        Iterates through the days and forward each one to the parseNewsDate method
        """

        base = datetime.datetime.today()

        # list of the datetime objects to iterate through
        dateList = [base - datetime.timedelta(days=x) for x in range(0, TsnParser.maxDaysAmount)]
        for i in dateList:
            date = i.date().strftime('%Y/%m/%d')
            currentUrl = TsnParser.urlStart + date + TsnParser.urlEnd
            if self.parseNewsDate(currentUrl) is False:
                return
