"""Models for Network app"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User with profile picture"""
    avatar = models.ImageField(upload_to='avatars', blank=True)
    following = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="followers")


class Post(models.Model):
    """A status update"""
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    timestamp = models.DateTimeField(auto_now_add=True)
    body = models.CharField(max_length=280)
    likes = models.ManyToManyField("User", blank=True, related_name="liked_posts")
