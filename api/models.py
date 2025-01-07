from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from .storage import S3MediaStorage
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
           raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
           raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    userId = models.AutoField(primary_key=True, serialize=False)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True, db_column="isActive")
    is_staff = models.BooleanField(default=False, db_column="isStaff")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
       verbose_name = "CustomUser"
       verbose_name_plural = "CustomUsers"

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
   likeNum = models.IntegerField(null=False, default=0)
   bookmarkNum = models.IntegerField(null=False, default=0)

   def save(self, *args, **kwargs):
      if not self.author:
         self.author = self.sourceName
      if not self.articleUniqueId:
         self.articleUniqueId = self.sourceName + "-" + str(self.publishedAt)
      
      super().save(*args, **kwargs)

class Video(models.Model):
  id = models.BigAutoField(primary_key=True)
  videoUniqueId = models.CharField(default=None, max_length=100, unique=True)
  thumbnailImageId = models.CharField(default=None, max_length=100, null=True)
  videoBrandType = models.CharField(max_length=30, null=True)
  author = models.CharField(max_length=200, null=True)
  title = models.TextField(null=True)
  url = models.TextField(null=True)
  fetchable_url = models.TextField(null=True)
  thumbnailImageUrl = models.TextField(null=True)
  thumbnailImageFetchableUrl = models.TextField(null=True)
  createdTime = models.DateTimeField(null=False, default=timezone.now)
  commentNum = models.IntegerField(null=False, default=0)
  likeNum = models.IntegerField(null=False, default=0)
  bookmarkNum = models.IntegerField(null=False, default=0)

  def save(self, *args, **kwargs):
      if self.videoUniqueId:
         self.fetchable_url = f"fetch/{self.videoUniqueId}"

      if self.thumbnailImageId:
         self.fetchable_url = f"fetch/{self.thumbnailImageId}"
      
      super().save(*args, **kwargs)

class ArticleComment(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   content = models.TextField(null=True)
   parentId = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
   articleId = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
   user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, db_column='user')
   createdTime = models.DateTimeField(null=False, auto_now_add=True)
   likeNum = models.IntegerField(null=False, default=0)

   def save(self, *args, **kwargs):
      if self.articleId:
         self.articleId.commentNum = self.articleId.commentNum + 1 if self.articleId.commentNum else 0
         self.articleId.save(update_fields=["commentNum"])

      return super().save(args, kwargs)
   
   def delete(self, *args, **kwargs):
      if self.articleId:
         self.articleId.commentNum = self.articleId.commentNum - 1 if self.articleId.commentNum > 0 else 0
         self.articleId.save(update_fields=["commentNum"])

      return super().delete(args, kwargs)

class VideoComment(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   content = models.TextField(null=True)
   parentId = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
   videoId = models.ForeignKey(Video, on_delete=models.CASCADE, null=False)
   user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, db_column='user')
   createdTime = models.DateTimeField(null=False, auto_now_add=True)
   likeNum = models.IntegerField(null=False, default=0)

   def save(self, *args, **kwargs):
      if self.videoId:
         self.videoId.commentNum = self.videoId.commentNum + 1 if self.videoId.commentNum else 1
         self.videoId.save(update_fields=["commentNum"])
      
      return super().save(args, kwargs)
   
   def delete(self, *args, **kwargs):
      if self.videoId:
         self.videoId.commentNum = self.videoId.commentNum - 1 if self.videoId.commentNum > 0 else 0
         self.videoId.save(update_fields=["commentNum"])

      return super().delete(args, kwargs)

class ArticleReaction(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
   articleId = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=["user", "articleId"], name="unique_article_reaction")
      ]

   def save(self, *args, **kwargs):
      if self.articleId:
         self.articleId.likeNum = self.articleId.likeNum + 1 if self.articleId.likeNum else 1
         self.articleId.save(update_fields=["likeNum"])

      return super().save(args, kwargs)
   
   def delete(self, *args, **kwargs):
      if self.articleId:
         self.articleId.likeNum = self.articleId.likeNum - 1 if self.articleId.likeNum > 0 else 0
         self.articleId.save(update_fields=["likeNum"])

      return super().delete(args, kwargs)

class VideoReaction(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
   videoId = models.ForeignKey(Video, on_delete=models.CASCADE, null=False)

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=["user", "videoId"], name="unique_video_reaction")
      ]

   def save(self, *args, **kwargs):
      if self.videoId:
         self.videoId.likeNum = self.videoId.likeNum + 1 if self.videoId.likeNum else 1
         self.videoId.save(update_fields=["likeNum"])

      return super().save(args, kwargs)
   
   def delete(self, *args, **kwargs):
      if self.videoId:
         self.videoId.likeNum = self.videoId.likeNum - 1 if self.videoId.likeNum else 0
         self.videoId.save(update_fields=["likeNum"])

      return super().delete(args, kwargs)
   
class ArticleBookmark(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
   articleId = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
   savedTime = models.DateTimeField(auto_now_add=True, null=False)

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=["user", "articleId"], name="unique_article_bookmark")
      ]

   def save(self, *args, **kwargs):
      if self.articleId:
         self.articleId.bookmarkNum = self.articleId.bookmarkNum + 1 if self.articleId.bookmarkNum else 1
         self.articleId.save(update_fields=["bookmarkNum"])
      return super().save(*args, **kwargs)
   
   def delete(self, *args, **kwargs):
      if self.articleId:
         self.articleId.bookmarkNum = self.articleId.bookmarkNum - 1 if self.articleId.bookmarkNum > 0 else 0
         self.articleId.save(update_fields=["bookmarkNum"])
      return super().delete(*args, **kwargs)
   
class VideoBookmark(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
   videoId = models.ForeignKey(Video, on_delete=models.CASCADE, null=False)
   savedTime = models.DateTimeField(auto_now_add=True, null=False)

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=["user", "videoId"], name="unique_video_bookmark")
      ]

   def save(self, *args, **kwargs):
      if self.videoId:
         self.videoId.bookmarkNum = self.videoId.bookmarkNum + 1 if self.videoId.bookmarkNum else 1
         self.videoId.save(update_fields=["bookmarkNum"])
      return super().save(*args, **kwargs)
   
   def delete(self, *args, **kwargs):
      if self.videoId:
         self.videoId.bookmarkNum = self.videoId.bookmarkNum - 1 if self.videoId.bookmarkNum > 0 else 0
         self.videoId.save(update_fields=["bookmarkNum"])
      return super().save(*args, **kwargs)

class TemporaryUser(models.Model):
   username = models.CharField(max_length=100, unique=True)
   displayname = models.CharField(max_length=100, null=True)
   profileImage = models.FileField(storage=S3MediaStorage(), upload_to="Uploads/", blank=True)

class TemporarySearchHistory(models.Model):
   user = models.ForeignKey(TemporaryUser, on_delete=models.CASCADE, related_name='search_histories')
   searchValue = models.CharField(max_length=255)
   searchDate = models.DateTimeField(auto_now_add=True)

class TemporaryArticleComment(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   content = models.TextField(null=True)
   parentId = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
   articleId = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
   user = models.ForeignKey(TemporaryUser, on_delete=models.CASCADE, null=False, db_column='user')
   createdTime = models.DateTimeField(null=False, auto_now_add=True)

   def save(self, *args, **kwargs):
      if self.articleId:
        self.articleId.commentNum = self.articleId.commentNum + 1 if self.articleId.commentNum else 1
        self.articleId.save()

      return super().save(*args, **kwargs)
  
   def delete(self, *args, **kwargs):
      if self.articleId:
         self.articleId.commentNum = self.articleId.commentNum - 1 if self.articleId.commentNum > 0 else 0
         self.articleId.save()

      return super().save(*args, **kwargs)

class TemporaryVideoComment(models.Model):
  id = models.BigAutoField(primary_key=True, null=False)
  content = models.TextField(null=True)
  parentId = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
  videoId = models.ForeignKey(Video, on_delete=models.CASCADE, null=False)
  user = models.ForeignKey(TemporaryUser, on_delete=models.CASCADE, null=False, db_column='user')
  createdTime = models.DateTimeField(null=False, auto_now_add=True)

  def save(self, *args, **kwargs):
     if self.videoId:
        self.videoId.commentNum = self.videoId.commentNum + 1 if self.videoId.commentNum else 1
        self.videoId.save()

     return super().save(*args, **kwargs)

  def delete(self, *args, **kwargs):
     if self.videoId:
        self.videoId.commentNum = self.videoId.commentNum - 1 if self.videoId.commentNum > 0 else 0
        self.videoId.save()

     return super().delete(*args, **kwargs)

class TemporaryArticleReaction(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   user = models.ForeignKey(TemporaryUser, on_delete=models.CASCADE, null=False)
   articleId = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=["user", "articleId"], name="unique_temporary_article_reaction")
      ]

   def save(self, *args, **kwargs):
      if self.articleId:
         self.articleId.likeNum = self.articleId.likeNum + 1 if self.articleId.likeNum else 1
         self.articleId.save()

      return super().save(*args, **kwargs)
   
   def delete(self, *args, **kwargs):
      if self.articleId:
         self.articleId.likeNum = self.articleId.likeNum - 1 if self.articleId.likeNum > 0 else 0
         self.articleId.save()

      return super().save(*args, **kwargs)

class TemporaryVideoReaction(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   user = models.ForeignKey(TemporaryUser, on_delete=models.CASCADE, null=False)
   videoId = models.ForeignKey(Video, on_delete=models.CASCADE, null=False)

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=["user", "videoId"], name="unique_temporary_video_reaction")
      ]

   def save(self, *args, **kwargs):
      if self.videoId:
         self.videoId.likeNum = self.videoId.likeNum + 1 if self.videoId.likeNum else 1
         self.videoId.save()

      return super().save(*args, **kwargs)
   
   def delete(self, *args, **kwargs):
      if self.videoId:
         self.videoId.likeNum = self.videoId.likeNum - 1 if self.videoId.likeNum > 0 else 0
         self.videoId.save()

      return super().delete(*args, **kwargs)
   
class TemporaryArticleBookmark(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   user = models.ForeignKey(TemporaryUser, on_delete=models.CASCADE, null=False)
   articleId = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
   savedTime = models.DateTimeField(auto_now_add=True, null=False)

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=["user", "articleId"], name="unique_temporary_article_bookmark")
      ]

   def save(self, *args, **kwargs):
      if self.articleId:
         self.articleId.bookmarkNum = self.articleId.bookmarkNum + 1 if self.articleId.bookmarkNum else 1
         self.articleId.save(update_fields=["bookmarkNum"])
      return super().save(*args, **kwargs)
   
   def delete(self, *args, **kwargs):
      if self.articleId:
         self.articleId.bookmarkNum = self.articleId.bookmarkNum - 1 if self.articleId.bookmarkNum > 0 else 0
         self.articleId.save(update_fields=["bookmarkNum"])
      return super().delete(*args, **kwargs)

class TemporaryVideoBookmark(models.Model):
   id = models.BigAutoField(primary_key=True, null=False)
   user = models.ForeignKey(TemporaryUser, on_delete=models.CASCADE, null=False)
   videoId = models.ForeignKey(Video, on_delete=models.CASCADE, null=False)
   savedTime = models.DateTimeField(auto_now_add=True, null=False)

   class Meta:
      constraints = [
         models.UniqueConstraint(fields=["user", "videoId"], name="unique_temporary_video_bookmark")
      ]

   def save(self, *args, **kwargs):
      if self.videoId:
         self.videoId.bookmarkNum = self.videoId.bookmarkNum + 1 if self.videoId.bookmarkNum else 1
         self.videoId.save(update_fields=["bookmarkNum"])
      return super().save(*args, **kwargs)
   
   def delete(self, *args, **kwargs):
      if self.videoId:
         self.videoId.bookmarkNum = self.videoId.bookmarkNum - 1 if self.videoId.bookmarkNum > 0 else 0
         self.videoId.save(update_fields=["bookmarkNum"])
      return super().save(*args, **kwargs)