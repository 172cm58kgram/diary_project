from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class DiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to='diary_images/', blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
