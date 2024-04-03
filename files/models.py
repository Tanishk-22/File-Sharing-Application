from django.db import models
from django.contrib.auth.models import User


class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='user_files/')
    shared_with = models.ManyToManyField(User, related_name='shared_files', blank=True)
    file_hash = models.CharField(max_length=64, blank=True)
    encryption_key = models.BinaryField()

    def __str__(self):
        return f"{self.user.username}'s file"
