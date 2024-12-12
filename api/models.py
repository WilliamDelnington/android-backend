from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('isStaff', True)
        extra_fields.setdefault('isSuperuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    userId = models.AutoField(primary_key=True, serialize=False)
    username = models.CharField(max_length=100)
    isActive = models.BooleanField(default=True)
    isStaff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class SearchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='search_histories')
    searchValue = models.CharField(max_length=255)
    searchDate = models.DateTimeField(auto_now_add=True)
  
class Article(models.Model):
  articleUniqueId = models.CharField(max_length=100, unique=True, serialize=False)
  articleBrandType = models.CharField(default=None, max_length=30, unique=True)
  sourceName = models.CharField(max_length=100, null=True)
  author = models.CharField(max_length=200, null=True)
  title = models.TextField(null=True)
  description = models.TextField(null=True)
  url = models.TextField(null=True)
  urlToImage = models.TextField(null=True)
  publishedAt = models.DateTimeField(null=False, default=timezone.now)
  content = models.TextField(null=True)
  commentNum = models.IntegerField(null=False, default=0)

class Video(models.Model):
  id = models.BigAutoField(primary_key=True)
  videoUniqueId = models.CharField(default=None, max_length=100, unique=True)
  videoBrandType = models.CharField(max_length=30, null=True)
  author = models.CharField(max_length=200, null=True)
  title = models.TextField(null=True)
  url = models.TextField(null=True)
  createdTime = models.DateTimeField(null=False, default=timezone.now)
  commentNum = models.IntegerField(null=False, default=0)

class ArticleComment(models.Model):
  id = models.BigAutoField(primary_key=True, null=False)
  content = models.TextField(null=True)
  parentId = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
  articleId = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
  user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
  createdTime = models.DateTimeField(null=False, auto_now_add=True)
  likeNum = models.IntegerField(null=False, default=0)

class VideoComment(models.Model):
  id = models.BigAutoField(primary_key=True, null=False)
  content = models.TextField(null=True)
  parentId = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
  videoId = models.ForeignKey(Video, on_delete=models.CASCADE, null=False)
  user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
  createdTime = models.DateTimeField(null=False, auto_now_add=True)
  likeNum = models.IntegerField(null=False, default=0)