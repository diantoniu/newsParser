from django.views.generic import ListView
from parser.models import *
from django.db.models import Q
from functools import reduce
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import re

import pytz

class NewsList(ListView):
    """
    Based on the classes are designed to display data. Represents list of objects

    Attributes
    ----------
    model : class

    template_name : str

    Methods
    -------
    normalizeTags(tagsString)
        forms list of tags based on which news will be filtered

    getNewsList(request)
        forms the response on ajax request

    get_context_data(url, categoryId)
        forms response on main page loads event
    """

    model = News
    template_name = 'index.html'

    @staticmethod
    def normalizeTags(tagsString):
        """
        Forms list of tags based on which news will be filtered

        Parameters
        ----------
        tagsString : str
            user requested tags string

        Returns
        -------
        list:
            list of str tags
        """

        # replace all non alphanumeric symbols on whitespace and split by whitespace
        return (re.sub('[^0-9a-zA-Z\u0400-\u04ff\u0400-\u04ff]+', ' ', tagsString)).lower().split(' ')

    @staticmethod
    @csrf_exempt
    def getNewsList(request):
        """
        Forms the response on ajax request

        Parameters
        ----------
        request : WSGIRequest
            user request

        Returns
        -------
        HttpResponse
        """

        tags = NewsList.normalizeTags(str(request.GET.get('namesTags')))
        categories = list(map(int, request.GET.getlist('categories')))
        newsList = list()

        # filter news by requested categories and tags reverse order by time
        if len(categories) > 0:
            newsList = News.objects. \
                filter(reduce(lambda x, y: x | y, [Q(categoryId=id) for id in categories])). \
                filter(reduce(lambda x, y: x & y,
                              [(Q(lowercaseTitle__icontains=tag) | Q(lowercaseText__icontains=tag)) for tag in
                               tags])).order_by('-time')

        # paginator to control max amount of news in one page
        paginator = Paginator(newsList, 10)
        page = request.GET.get('page')
        news = paginator.get_page(page)
        updated = request.GET.copy()

        # delete page parameter from request url
        del updated['page']
        return render(request, 'newsBody.html',
                      {'newsList': news, 'original_request': updated.urlencode(), 'categories': Category.objects.all()})

    def get_context_data(self, **kwargs):
        """
        Forms response on main page loads event

        Parameters
        ----------
        kwargs : dict
            arguments

        Returns
        -------
        context:
            response
        """

        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
