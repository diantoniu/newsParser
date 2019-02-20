from django.db import models


class Category(models.Model):
    """
    Stores information about news categories
    """

    name = models.TextField()

    def __str__(self):
        return 'Name: %s' % (self.name)


class TsnCategory(models.Model):
    """
    Stores information about news categories in tsn website
    """

    categoryId = models.IntegerField()
    name = models.TextField()

    def __str__(self):
        return 'Category id: %d, Name: %s' % (self.categoryId, self.name)


class UkrNetCategory(models.Model):
    """
    Stores information about news categories in ukr.net website
    """

    categoryId = models.IntegerField()
    name = models.TextField()

    def __str__(self):
        return 'Category id: %d, Name: %s' % (self.categoryId, self.name)


class News(models.Model):
    """
    Stores information about news data
    """

    url = models.TextField(default='')
    title = models.TextField(default='')
    lowercaseTitle = models.TextField(default='')
    time = models.DateTimeField()
    picture = models.TextField(default='')
    categoryId = models.IntegerField(default=-1)
    text = models.TextField(default='')
    lowercaseText = models.TextField(default='')
    source = models.TextField(default='')
    tags = models.TextField(default='')
    lowercaseTags = models.TextField(default='')

    class Meta:
        ordering = ['time']

    def __str__(self):
        return 'Url: %s, Title: %s, Time: %s, Picture: %s, Category id: %d, Text: %s, Tags: %s' % \
               (self.url, self.title, self.time, self.picture, self.categoryId, self.text, self.tags)
