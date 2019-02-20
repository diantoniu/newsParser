from django.conf.urls import url

from parser.parserThread import ParserThread
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.NewsList.as_view()),
    url(r'^getNewsList', views.NewsList.getNewsList, name='getNewsList'),
]

# run parser thread
t = ParserThread('0', 60*5)
t.start()
