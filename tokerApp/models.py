from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class Toker(models.Model):
    host = models.GenericIPAddressField()
    port = models.IntegerField(validators=[MinValueValidator, MaxValueValidator])
    recive = models.TextField()
    res = models.CharField(max_length=1024)
    target_path = models.CharField(max_length=512)
    ini_path = models.CharField(max_length=512)

class Record(models.Model):
    time = models.DateTimeField()
    name = models.CharField(max_length=100)
    remark = models.TextField()

    def __str__(self):
        return self.name 
    

