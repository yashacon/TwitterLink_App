from django.db import models


# Create your models here.
class Tweets(models.Model):    
    id = models.CharField(max_length=100,primary_key = True)
    Name = models.CharField(max_length=100)
    User = models.CharField(max_length=1000)
    Tweet_id = models.CharField(max_length=100)
    Text = models.CharField(max_length=1000)    
    Domain = models.CharField(max_length=1000)
    Display_picture = models.CharField(max_length=100)