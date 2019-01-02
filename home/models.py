from django.db import models


# Create your models here.
class Usermsg(models.Model):
    name = models.CharField(max_length=50)
    passwd = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.IntegerField()
    isadmin = models.BooleanField()


class Article(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=50)
    detail = models.CharField(max_length=200)
    content = models.TextField()
    uid = models.IntegerField()
    tid = models.IntegerField()


class Typemsg(models.Model):
    typename = models.CharField(max_length=50)


class Comment(models.Model):
    uid = models.IntegerField()
    content = models.TextField()
    aid = models.IntegerField()


class Img(models.Model):
    path = models.CharField(max_length=50, default='')
    out = models.CharField(max_length=50, default='')
    line = models.CharField(max_length=50, default='')
    color = models.CharField(max_length=50, default='')
    type = models.CharField(max_length=20, default='blue')


class Bug(models.Model):
    path = models.CharField(max_length=50, default='')
    line = models.CharField(max_length=50, default='')
    info = models.TextField()


class BugTwo(models.Model):
    path = models.CharField(max_length=50, default='')
    out = models.CharField(max_length=50, default='')
    info = models.TextField()


class BugThree(models.Model):
    path = models.CharField(max_length=50, default='')
    out = models.CharField(max_length=50, default='')
    line = models.CharField(max_length=50, default='')
    info = models.TextField()
