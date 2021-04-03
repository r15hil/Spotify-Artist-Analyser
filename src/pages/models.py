from django.db import models

# Create your models here.

class Artist(models.Model):
    artistID       = models.CharField(max_length = 120)