from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

class Post(models.Model):
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name="author")
    created = models.DateTimeField(default = timezone.now)
    body = models.CharField(max_length = 140)

    def __str__(self):
        return f"User {self.author}'s {self.id} post, created on {self.created.strftime('%d/%m/%Y, %H:%M:%S')}"

class Follow(models.Model):
    user_followed = models.ForeignKey(User, on_delete = models.CASCADE, related_name="user_followed")
    user_following = models.ForeignKey(User, on_delete = models.CASCADE, related_name="user_following")

    def __str__(self):
        return f"{self.user_following} is following {self.user_followed}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="Liked_by_user")
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name="Liked_post")

    def __str__(self):
        return f"{self.post} liked by {self.user}"