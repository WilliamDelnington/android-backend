from django.shortcuts import render, redirect
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Article, Video, ArticleComment, VideoComment, SearchHistory, CustomUser
from .serializer import *
from .utils import upload_file, list_all_files, get_specific_file, delete_specific_file
from .forms import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# from selenium.common.exceptions import WebDriverException
# from TikTokApi import TikTokApi
# from pytube import YouTube
from datetime import datetime
import os
import time
import requests
import pyktok as pyk
import yt_dlp
import json
import shutil
import pandas as pd

# Create your views here.
class ArticleListCreate(generics.ListCreateAPIView):

    """
    A view for creating articles or delete the whole articles list.
    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def delete(self, request, *args, **kwargs):

        """
        Delete all article objects at once. Only admin users can perform this action.
        """

        Article.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return super().get_permissions()


class ArticleRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying article data and get the data using id.
    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()


class ArticleList(APIView):

    """
    List all articles or specific articles using keywords.
    """

    def get(self, request, format=None):

        """
        A get request that get all specific articles using keywords.

        For example, if you set the view path as "/ArticleList", to get all the articles
        that has keyword "max" in article's source name or brand type, type "/ArticleList?originKey=max",
        or to get all the articles that has keyword "dashing" in article's content, type 
        "/ArticleList?contentKey=dashing". You can also filter using both keywords like this: 
        "/ArticleList?originKey=max&contentKey=dashing"
        """

        source = request.query_params.get("source", "")
        vidType = request.query_params.get("type", "")
        content_keyword = request.query_params.get("contentKey", "")

        if all(source, vidType, content_keyword):
            # Return all articles that contains both needed keywords.
            articles = Article.objects.filter(
                Q(sourceName__icontains=source) & 
                 Q(articleBrandType__contains=vidType) &
                (Q(title__icontains=content_keyword) | 
                 Q(description__icontains=content_keyword) | 
                 Q(content__icontains=content_keyword))
            )
        elif all(source, vidType):
            # Return all articles that contains keywords in source name or brand type.
            articles = Article.objects.filter(
                Q(sourceName__icontains=source) &
                Q(articleBrandType__icontains=vidType))
        elif all(source, content_keyword):
            # Return all articles that contains keywords in article's content.
            articles = Article.objects.filter(
                Q(sourceName__icontains=source) &
                (Q(title__icontains=content_keyword) |
                Q(description__icontains=content_keyword) |
                Q(content__icontains=content_keyword))
            )
        elif all(vidType, content_keyword):
            articles = Article.objects.filter(
                Q(vidType__contains=vidType) &
                (Q(title__icontains=content_keyword) |
                Q(description__icontains=content_keyword) |
                Q(content__icontains=content_keyword))
            )
        elif source:
            articles = Article.objects.filter(sourceName__icontains=source)
        elif vidType:
            articles = Article.objects.filter(vidType__contains=vidType)
        elif content_keyword:
            articles = Article.objects.filter(
                Q(title__icontains=content_keyword) |
                Q(description__icontains=content_keyword) |
                Q(content__icontains=content_keyword)
            )
        else:
            # If no keywords are used, return all articles.
            articles = Article.objects.all()

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class VideoListCreate(generics.ListCreateAPIView):

    """
    A view for creating videos or delete all the video list
    """

    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    # A delete request that delete all video objects at once.
    def delete(self, request, *args, **kwargs):

        """
        Delete all video objects at once. Only admin users can perform this action.
        """

        Video.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()

class VideoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) videos data and get the data using id.
    """

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()


class VideoList(APIView):

    """
    A view that get all specific videos using keyword.
    """

    def get(self, request, format=None):

        """
        A get request that get all specific article comments using keywords.

        For example, if you set the view path as "/VideoList", to get all the articles
        that has keyword "max" in video's brand type or author, use "/VideoList?keyword=max",
        or to get all the articles that has keyword "inside" in video's title, use "/VideoList?key=inside".
        You can use both keyword filtering like this: "/VideoList?keyword=max?key=inside"
        """

        origin_keyword = request.query_params.get("originKey", "")
        content_keyword = request.query_params.get("contentKey", "")

        if origin_keyword and content_keyword:
            # Get all the objects that contain both keywords.
            video = Video.objects.filter(
                (Q(videoBrandType__contains=origin_keyword) |
                Q(author__icontains=origin_keyword)) & 
                (Q(title__icontains=content_keyword))
            )
        elif origin_keyword:
            # Get all the video objects which author or brand type contains the keyword,.
            video = Video.objects.filter(
                Q(videoBrandType__contains=origin_keyword) |
                Q(author__icontains=origin_keyword)
            )
        elif content_keyword:
            # Get all the video objects which 
            video = Video.objects.filter(
                title__icontains=content_keyword
            )
        else:
            # If no filter are used, return all video objects.
            video = Video.objects.all()

        serializer = VideoSerializer(video, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk, format=None):

        """
        A delete request that delete specific video using id.
        """

        try:
            video = Video.objects.get(pk=pk)
            id = video.videoUniqueId
            # The object has been deleted in the database but not in Google Drive.
            # We have to delete it in Google Drive as well.
            delete_specific_file(id)
            video.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    

class ArticleCommentListCreate(generics.ListCreateAPIView):

    """
    A view that get all article comments or delete all article comments data.
    """

    queryset = ArticleComment.objects.all()
    serializer_class = ArticleCommentSerializer

    def get(self, request, *args, **kwargs):
        """
        Get all article comment data.
        """
        response = super().get(request, *args, **kwargs)

        data = response.data

        returned_data = []

        for small_data in data:
            user = small_data["user"]
            userObject = CustomUser.objects.get(id=user)
            username = userObject.username
            small_data["username"] = username

            returned_data.append(small_data)

        return Response(returned_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):

        """
        Delete all article comment objects at once. Only admin users can perform this action.
        """

        ArticleComment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, *args, **kwargs):
        """
        Create article comment and update the article's comment number.
        """

        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # articleId = data.get("articleId")
        # article = Article.objects.get(id=articleId)
        # article.commentNum = article.commentNum + 1 if article.commentNum else 1
        # article.save(update_fields=["commentNum"])

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()


class ArticleCommnentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) article comments data and get the data using id.
    """

    queryset = ArticleComment.objects.all()
    serializer_class = ArticleCommentSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        """
        Delete the article comment and update the number of comments associated to the article.
        """

        articleComment = self.get_object()
        id = articleComment.id
        # articleId = articleComment.articleId

        # article = Article.objects.get(id=articleId.id)
        # article.commentNum = article.commentNum - 1 if article.commentNum > 0 else 0
        # article.save(update_fields=["commentNum"])

        response = super().delete(request, *args, **kwargs)

        response.data = {"message": f"Article Comment {id} deleted successfully"}
        return Response(response.data, status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()


class ArticleCommentList(APIView):

    """
    A view that get all specific article comments using keyword.
    """

    def get(self, request, format=None):

        """
        Get all specific article comments using keywords/queries.

        For example, when you set the view path as "/ArticleCommentList", to get all the article comments
        that has keyword "max" in content, use "/ArticleCommentList?keyword=max".
        """

        key = request.query_params.get("key", None)
        user = request.query_params.get("user", None)
        articleId = request.query_params.get("articleId", None)

        filters = Q()

        if key:
            filters &= Q(content__icontains=key)
        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(articleId=articleId)

        if any([key, user, articleId]):
            # Return all objects which content contains the keyword.
            articleComments = ArticleComment.objects.filter(filters)
        else:
            # If no filters are used, return all objects.
            articleComments = ArticleComment.objects.all()

        returned_data = []

        for comment in articleComments:
            user = comment.user
            username = user.username
            serializer = ArticleCommentSerializer(comment)
            data = serializer.data
            data["username"] = username

            returned_data.append(data)

        return Response(returned_data, status=status.HTTP_200_OK)
    

class VideoCommentListCreate(generics.ListCreateAPIView):

    """
    A view that get all video comments or delete all video comments at once.
    """

    queryset = VideoComment.objects.all()
    serializer_class = VideoCommentSerializer

    def get(self, request, *args, **kwargs):
        """
        Get all video comment objects.
        """
        response = super().get(request, *args, **kwargs)

        data = response.data

        returned_data = []

        for small_data in data:
            user = small_data["user"]
            userObject = CustomUser.objects.get(id=user)
            username = userObject.username
            small_data["username"] = username

            returned_data.append(returned_data)

        return Response(returned_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):

        """
        Delete all video comment objects at once. Only admin users can perform this action.
        """

        VideoComment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, *args, **kwargs):

        """
        A post request that both create a video comment and update the video's comments number.
        """

        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # videoId = data.get("videoId")
        # video = Video.objects.get(id=videoId)
        # video.commentNum = video.commentNum + 1 if video.commentNum else 0
        # video.save(update_fields=["commentNum"])

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()


class VideoCommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) video comments data and get the data using id.
    """

    queryset = VideoComment.objects.all()
    serializer_class = VideoCommentSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        """
        Deletes the video comment and update the number of comments associated with the video.
        """
        videoComment = self.get_object()
        id = videoComment.id
        # videoId = videoComment.videoId

        # video = Video.objects.get(id=videoId.id)
        # video.commentNum = video.commentNum - 1 if video.commentNum > 0 else 0
        # video.save(update_fields=["commentNum"])

        response = super().delete(request, *args, **kwargs)

        response.data = {"message": f"Video Comment {id} deleted successfully"}
        return Response(response.data, status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()


class VideoCommentList(APIView):

    """
    A view that get all specific video comments using keyword.
    """

    def get(self, request, format=None):

        """
        A get request that get all specific video comments using keywords.

        For example, when you set the view path as "/VideoCommentList", to get all the video comments
        that has keyword "max" in content, use "/VideoCommentList?keyword=max".
        """

        key = request.query_params.get("key", None)
        user = request.query_params.get("user", None)
        videoId = request.query_params.get("videoId", None)

        filters = Q()

        if key:
            filters &= Q(content__icontains=key)
        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        if any(key, user, videoId):
            # Return all objects which content contains the keyword.
            videoComments = VideoComment.objects.filter(filters)
        else:
            # If no filters are used, return all objects.
            videoComments = VideoComment.objects.all()

        serializer = VideoCommentSerializer(videoComments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ArticleReactionListCreate(generics.ListCreateAPIView):

    """
    A view that get all article comments or delete all article comments data.
    """

    queryset = ArticleReaction.objects.all()
    serializer_class = ArticleReactionSerializer

    def delete(self, request, *args, **kwargs):

        """
        Delete all article comment objects at once. Only admin users can perform this action.
        """

        ArticleReaction.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, *args, **kwargs):
        """
        Create a new article reaction and update the number of reactions the article receives.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # articleId = data.get("articleId")
        # article = Article.objects.get(id=articleId)
        # article.likeNum = article.likeNum + 1 if article.likeNum else 1
        # article.save(update_fields=["likeNum"])

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()
    
class ArticleReactionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) article comments data and get the data using id.
    """

    queryset = ArticleReaction.objects.all()
    serializer_class = ArticleReactionSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        """
        Deletes a specific article reaction using its id and update the number of reactions the article receives.
        """
        articleReaction = self.get_object()
        # id = articleReaction.id
        # articleId = articleReaction.articleId

        # article = Article.objects.get(id=articleId.id)
        # article.likeNum = article.likeNum - 1 if article.likeNum > 0 else 0
        # article.save(update_fields=["likeNum"])

        response = super().delete(request, *args, **kwargs)

        response.data = {"message": f"Article Reaction {id} deleted successfully"}
        return Response(response.data, status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class ArticleReactionList(APIView):

    """
    A view that get all specific article reactions using keyword/queries.
    """

    def get(self, request, format=None):

        """
        Get all specific article reactions using keywords/queries.

        For example, if you set the view path as "/ArticleReactionList", to get all the article reactions
        from a specific user, use the user's id, for example "/ArticleReationList?user=6". You can also get
        the reactions from a specific article, like "/ArticleReactionList?articleId=5"

        To use both queries, use the format like "articleId=<articleId>&user=<userId>"
        """

        user = request.query_params.get("user", None)
        articleId = request.query_params.get("articleId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(articleId=articleId)

        if any([user, articleId]):
            # Return all objects which content contains the keyword.
            articleReactions = ArticleReaction.objects.filter(filters)
        else:
            # If no filters are used, return all objects.
            articleReactions = ArticleReaction.objects.all()

        serializer = ArticleReactionSerializer(articleReactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, format=None):
        """
        Delete specific article's reaction using queries and update the number of reactions the article gets.

        Note that this only delete only one reaction objects. If there are multiple objects for deleting, it
        will return an error. Please use both queries like this: articleId=<articleId>&user=<userId>
        """
        user = request.query_params.get("user", None)
        articleId = request.query_params.get("articleId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(videoId=articleId)

        try:
            articleReaction = ArticleReaction.objects.get(filters)
            articleReaction.delete()

            # article = Article.objects.get(id=articleId)
            # article.likeNum = article.likeNum - 1
            # article.save(update_fields=["likeNum"])

            return Response({"message": "Object successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        except ArticleReaction.DoesNotExist:
            return Response({"message": "Object does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except ArticleReaction.MultipleObjectsReturned:
            return Response({"message": "Multiple objects returned"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Error deleting reaction: {e.message}"}, status=status.HTTP_400_BAD_REQUEST)
    
class VideoReactionListCreate(generics.ListCreateAPIView):

    """
    A view that get all video comments or delete all video comments at once.
    """

    queryset = VideoReaction.objects.all()
    serializer_class = VideoReactionSerializer

    def delete(self, request, *args, **kwargs):

        """
        Delete all video comment objects at once. Only admin users can perform this action.
        """

        VideoReaction.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, *args, **kwargs):
        """
        Create a video reaction and update the number of reactions the video receives.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # videoId = data.get("videoId")
        # video = Video.objects.get(id=videoId)
        # video.likeNum = video.likeNum + 1 if video.likeNum else 1
        # video.save(update_fields=["likeNum"])

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()
    
class VideoReactionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) video comments data and get the data using id.
    """

    queryset = VideoReaction.objects.all()
    serializer_class = VideoReactionSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        """
        Deletes a specific video reaction using its id and updates the number of video reactions.
        """
        videoReaction = self.get_object()
        id = videoReaction.id
        # videoId = videoReaction.videoId

        # video = Video.objects.get(id=videoId.id)
        # video.likeNum = video.likeNum - 1 if video.likeNum > 0 else 0
        # video.save(update_fields=["likeNum"])

        response = super().delete(request, *args, **kwargs)

        response.data = {"message": f"Video Reaction {id} deleted successfully"}
        return Response(response.data, status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class VideoReactionList(APIView):

    """
    A view that get all specific video comments using keyword.
    """

    def get(self, request, format=None):

        """
        A get request that get all specific video reactions using keywords/queries.

        For example, if you set the view path as "/VideoReactionList", to get all the video reactions
        from a specific user, use the user's id, for example "/VideoReationList?user=6". You can also get
        the reactions from a specific video, like "/VideoReactionList?videoId=5"

        To use both queries, use the format like "videoId=<videoId>&user=<userId>"
        """

        user = request.query_params.get("user", None)
        videoId = request.query_params.get("videoId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        if any([user, videoId]):
            # Return all objects which content contains the keyword.
            videoReaction = VideoReaction.objects.filter(filters)
        else:
            # If no filters are used, return all objects.
            videoReaction = VideoReaction.objects.all()

        serializer = VideoReactionSerializer(videoReaction, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, format=None):
        """
        Delete specific video's reaction using queries and update the number of reactions the article gets.

        Note that this only delete only one reaction objects. If there are multiple objects for deleting, it
        will return an error. Please use both queries like this: videoId=<videoId>&user=<userId>
        """
        user = request.query_params.get("user", None)
        videoId = request.query_params.get("videoId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        try:
            videoReaction = VideoReaction.objects.get(filters)
            videoReaction.delete()

            video = Video.objects.get(id=videoId)
            video.likeNum = video.likeNum - 1
            video.save(update_fields=["likeNum"])

            return Response({"message": "Object successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        except VideoReaction.DoesNotExist:
            return Response({"message": "Object does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except VideoReaction.MultipleObjectsReturned:
            return Response({"message": "Multiple objects returned"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Error deleting reaction: {e.message}"}, status=status.HTTP_400_BAD_REQUEST)
        
class ArticleBookmarkListCreate(generics.ListCreateAPIView):
    """
    A view that creates article bookmark object or deletes all the objects at once.
    """
    queryset = ArticleBookmark.objects.all()
    serializer_class = ArticleBookmarkSerializer

    def delete(self, request, *args, **kwargs):
        """
        Delete all article bookmark objects at once. Only admin users can perform this action.
        """
        ArticleBookmark.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]

        return super().get_permissions()
    
class ArticleBookmarkRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    A view that get, update, or delete the article bookmark object using its id.
    """
    queryset = ArticleBookmark.objects.all()
    serializer_class = ArticleBookmarkSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class ArticleBookmarkList(APIView):
    """
    A view that get or delete article bookmark objects using keywords/queries.
    """
    def get(self, request, *args, **kwargs):
        """
        Get all specific article bookmarks using queries.

        For example, when you set the view path as "/ArticleBookmarkList", to get all the article bookmarks
        from a specific user, use the user's id, for example "/ArticleBookmarkList?user=6". You can also get
        the bookmarks from a specific article, like "/ArticleBookmarkList?articleId=5"

        To use both queries, use the format like "articleId=<articleId>&user=<userId>"
        """
        user = request.query_params.get("user", None)
        articleId = request.query_params.get("articleId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(articleId=articleId)

        if any([user, articleId]):
            articleBookmarks = ArticleBookmark.objects.filter(filters)
        else:
            articleBookmarks = ArticleBookmark.objects.all()

        serializer = ArticleBookmarkSerializer(articleBookmarks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):

        """
        Delete a specific article bookmark using queries and update the number of bookmarks of the article.

        Note that this only delete only one bookmark. If there are multiple objects for deleting, it will
        return an error. Please use both queries like this: articleId=<articleId>&user=<userId>
        """

        user = request.query_params.get("user", None)
        articleId = request.query_params.get("articleId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(articleId=articleId)

        try:
            articleBookmark = ArticleBookmark.objects.get(filters)
            articleBookmark.delete()
            return Response({"message": "Article Bookmark Object Successfully Deleted"}, status=status.HTTP_204_NO_CONTENT)
        except ArticleBookmark.DoesNotExist:
            return Response({"message": "Article Bookmark Object Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except ArticleBookmark.MultipleObjectsReturned:
            return Response({"message": "Too Many Article Bookmark Objects Returned"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"An Error Deleting Article Bookmark Object: {e}"}, status=status.HTTP_400_BAD_REQUEST)

class GetArticlesFromBookmark(APIView):
    """
    A view to get every article from bookmark.
    """
    def get(self, request, *args, **kwargs):
        user = request.query_params.get("user")

        returned_articles = []

        if not user:
            return Response({"message": "user id does not specified"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            articleBookmarks = ArticleBookmark.objects.filter(user=user)
            for articleBookmark in articleBookmarks:
                article = Article.objects.get(id=articleBookmark.articleId.id)
                article_serializer = ArticleSerializer(article)
                returned_articles.append(article_serializer.data)
            return Response(returned_articles, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"An error getting article: {e}"}, status=status.HTTP_400_BAD_REQUEST)

class VideoBookmarkListCreate(generics.ListCreateAPIView):
    """
    A view that creates video bookmark object or deletes all the objects at once.
    """
    queryset = VideoBookmark.objects.all()
    serializer_class = VideoBookmarkSerializer

    def delete(self, request, *args, **kwargs):
        """
        Delete all video bookmark objects at once. Only admin users can perform this action.
        """
        TemporaryVideoBookmark.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]

        return super().get_permissions()
    
class VideoBookmarkRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    A view that get, update, or delete the video bookmark object using its id.
    """
    queryset = VideoBookmark.objects.all()
    serializer_class = VideoBookmarkSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class VideoBookmarkList(APIView):
    def get(self, request, *args, **kwargs):

        """
        Get all specific video bookmarks using queries.

        For example, when you set the view path as "/VideoBookmarkList", to get all the video bookmarks
        from a specific user, use the user's id, for example "/VideoBookmarkList?user=6". You can also get
        the bookmarks from a specific video, like "/VideoBookmarkList?articleId=5"

        To use both queries, use the format like "videoId=<videoId>&user=<userId>"
        """

        user = request.query_params.get("user", None)
        videoId = request.query_params.get("videoId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        if any([user, videoId]):
            videoBookmarks = VideoBookmark.objects.filter(filters)
        else:
            videoBookmarks = VideoBookmark.objects.all()

        serializer = TemporaryVideoBookmarkSerializer(videoBookmarks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        """
        Delete specific video's bookmark using queries and update the number of bookmarks of the video.

        Note that this only delete only one bookmark objects. If there are multiple objects for deleting, it
        will return an error. Please use both queries like this: videoId=<videoId>&user=<userId>
        """
        user = request.query_params.get("user", None)
        videoId = request.query_params.get("videoId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        try:
            videoBookmark = VideoBookmark.objects.get(filters)
            videoBookmark.delete()
            return Response({"message": "Video Bookmark Object Successfully Deleted"}, status=status.HTTP_204_NO_CONTENT)
        except VideoBookmark.DoesNotExist:
            return Response({"message": "Video Bookmark Object Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except VideoBookmark.MultipleObjectsReturned:
            return Response({"message": "Too Many Video Bookmark Objects Returned"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"An Error Deleting Video Bookmark Object: {e}"}, status=status.HTTP_400_BAD_REQUEST)

class GetVideosFromBookmark(APIView):
    """
    A view to get every video from bookmarks.
    """
    def get(self, request, *args, **kwargs):
        user = request.query_params.get('user')

        returned_videos = []

        if not user:
            return Response({"message": "user id does not specified"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            videoBookmarks = VideoBookmark.objects.filter(user=user)
            for videoBookmark in videoBookmarks:
                video = Video.objects.get(id=videoBookmark.videoId.id)
                video_serializer = VideoSerializer(video)
                returned_videos.append(video_serializer.data)
            return Response(returned_videos, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"An error getting video: {e}"}, status=status.HTTP_400_BAD_REQUEST)

class SearchHistoryCreate(generics.ListCreateAPIView):

    """
    A view that get all users search histories or delete all search histories at once.
    """

    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer

    def delete(self, request, *args, **kwargs):

        """
        Delete all search history objects at once. Only admin users can perform this action.
        """

        SearchHistory.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()
    

class SearchHistoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) search histories data and get the data using id.
    """

    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()


class SearchHistoryList(APIView):

    """
    A view that get all specific search histories using keyword.
    """

    def get(self, request, format=None):

        """
        A get request that get all specific article comments using keywords.

        For example, when you set the view path as "/SearchHistoryList", to get all the search histories
        that has keyword "max" in the value, use "/SearchHistoryList?keyword=max".
        """

        user = request.query_params.get("user", None)
        if user:
            history = SearchHistory.objects.filter(user=user)
        else:
            history = SearchHistory.objects.all()

        serializer = SearchHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserListCreate(generics.ListCreateAPIView):

    """
    A view that get all users data or delete all users at once.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):

        """
        Delete all user objects at once. Only admin users can perform this action.
        """

        CustomUser.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()
    

class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) user data and get the data using id.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()


class UserList(APIView):

    """
    A view that get all specific users using keyword or registering new users
    """

    def get(self, request, format=None):

        """
        A get request that get all specific users using keywords.

        For example, when you set the view path as "/UserList", to get all the users
        that has keyword "max" in userId or username, use "/UserList?key=max".
        """

        key = request.query_params.get("key", "")
        if key:
            user = CustomUser.objects.filter(
                Q(userId__icontains=key) |
                Q(username__icontains=key)
            )
        else:
            user = CustomUser.objects.all()

        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):

        """
        A post request that creates user.
        """

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Validate the serializer before creating the user
            user = CustomUser.objects.create_user(
                email=serializer.validated_data['email'],
                password=request.data.get('password'),
                username=serializer.validated_data['username']
            )
            return Response({'message': f'User created successfully: {user.email}'}, status=status.HTTP_201_CREATED)
        # If the serializer is not valid, return bad request
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegisterView(generics.CreateAPIView):

    """
    A view to register a user
    """

    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):

        """
        Make a create request that registers a user
        """

        serializer = self.get_serializer(data=request.data)
        # Check if the serializer is valid. Otherwise, raise an error.
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User registered successfully!",
                "user_id": user.userId
            }, 
            status=status.HTTP_201_CREATED
        )
    
class TemporaryUserListCreate(generics.ListCreateAPIView):
    """
    A view to create a temporary user.
    """
    queryset = TemporaryUser.objects.all()
    serializer_class = TemporaryUserSerializer

class TemporaryUserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    A view to update, get, or delete user using its id.
    """
    queryset = TemporaryUser.objects.all()
    serializer_class = TemporaryUserSerializer
    lookup_field = "pk"

class TemporaryUserGet(APIView):
    """
    Get the temporary user using username.
    """
    def get(self, request, *args, **kwargs):
        username = request.query_params.get("username")

        if username:
            try:
                user = TemporaryUser.objects.get(username=username)
            except:
                return Response({"message": f"User {username} does not exist"} ,status=status.HTTP_404_NOT_FOUND)
        else:
            user = TemporaryUser.objects.all()
        serializer = TemporaryUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TemporarySearchHistoryCreate(generics.ListCreateAPIView):

    """
    A view that get all temporary users' search histories or delete all search histories at once.
    """

    queryset = TemporarySearchHistory.objects.all()
    serializer_class = TemporarySearchHistorySerializer

    def delete(self, request, *args, **kwargs):

        """
        Delete all search history objects at once. Only admin users can perform this action.
        """

        TemporarySearchHistory.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()
    
class TemporarySearchHistoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) search histories data and get the data using id.
    """

    queryset = TemporarySearchHistory.objects.all()
    serializer_class = TemporarySearchHistorySerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class TemporarySearchHistoryList(APIView):
    def get(self, request, format=None):
        user = request.query_params.get("user", None)

        if user:
            temporarySearchHistories = TemporarySearchHistory.objects.filter(user=user)
        else:
            temporarySearchHistories = TemporarySearchHistory.objects.all()
        
        serializer = TemporarySearchHistorySerializer(temporarySearchHistories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TemporaryVideoCommentListCreate(generics.ListCreateAPIView):

    """
    Get all temporary video comments or delete all of them at once.
    """

    queryset = TemporaryVideoComment.objects.all()
    serializer_class = TemporaryVideoCommentSerializer

    def get(self, request, *args, **kwargs):
        """
        Get all temporary video comments.
        """
        response = super().get(request, *args, **kwargs)

        data = response.data

        returned_data = []

        for small_data in data:
            user = small_data["user"]
            userObject = TemporaryUser.objects.get(id=user)
            username = userObject.username
            small_data["username"] = username

            returned_data.append(small_data)

        return Response(returned_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):

        """
        Delete all temporary video comment objects at once. Only admin user can do this.
        """

        TemporaryVideoComment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, *args, **kwargs):
        """
        Create a temporary video comment and update the number of comments associated with the video.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # videoId = data.get("videoId")
        # video = Video.objects.get(id=videoId)
        # video.commentNum = video.commentNum + 1 if video.commentNum else 0
        # video.save(update_fields=["commentNum"])

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()

class TemporaryVideoCommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) temporary video comments data and get the data using id.
    """

    queryset = TemporaryVideoComment.objects.all()
    serializer_class = TemporaryVideoCommentSerializer
    lookup_field = "pk"
    
    def delete(self, request, *args, **kwargs):
        """
        Deletes the temporary video comment using its id and updates number of comments associated with the video.
        """
        temporaryVideoComment = self.get_object()
        id = temporaryVideoComment.id
        # videoId = temporaryVideoComment.articleId

        # video = Video.objects.get(id=videoId.id)
        # video.commentNum = video.commentNum - 1 if video.commentNum > 0 else 0
        # video.save(update_fields=["commentNum"])

        response = super().delete(request, *args, **kwargs)

        response.data = {"message": f"Temporary Video Comment {id} deleted successfully"}
        return Response(response.data, status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class TemporaryVideoCommentList(APIView):

    """
    A view that get all specific temporary video comments using keywords/queries
    """

    def get(self, request, format=None):

        """
        Get all specific temporary video comments using keywords/queries.

        For example, when you set the view path as "/TemporaryVideoCommentList", to get all the video comments
        that has keyword "max" in content, use "/TemporaryVideoCommentList?keyword=max".

        To get the comments in specific video, use /TemporaryVideoCommentList?videoId=<videoId>

        To get the comments from specific user, use /TemporaryVideoCommentList?user=<userId>

        To use multiple queries, use &, for example, videoId=<videoId>&user=<userId>
        """

        key = request.query_params.get("key", None)
        user = request.query_params.get("user", None)
        videoId = request.query_params.get("videoId", None)

        filters = Q()

        if key:
            filters &= Q(content__icontains=key)
        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        if any([key, user, videoId]):
            # Return all objects which content contains the keyword.
            temporaryVideoComments = TemporaryVideoComment.objects.filter(filters)
        else:
            # If no filters are used, return all objects.
            temporaryVideoComments = TemporaryVideoComment.objects.all()

        response_data = []

        for comment in temporaryVideoComments:
            user = comment.user
            username = user.username
            serializer = TemporaryVideoCommentSerializer(comment)
            data = serializer.data
            data["username"] = username

            response_data.append(data)

        # serializer = TemporaryVideoCommentSerializer(temporaryVideoComments, many=True)

        return Response(response_data, status=status.HTTP_200_OK)
    

class TemporaryArticleCommentListCreate(generics.ListCreateAPIView):

    """
    A view that get all article comments or delete all article comments data.
    """

    queryset = TemporaryArticleComment.objects.all()
    serializer_class = TemporaryArticleCommentSerializer

    def get(self, request, *args, **kwargs):
        """
        Get all article comments.
        """
        response = super().get(request, *args, **kwargs)

        data = response.data

        returned_data = []

        for small_data in data:
            user = small_data["user"]
            userObject = TemporaryUser.objects.get(id=user)
            username = userObject.username
            small_data["username"] = username

            returned_data.append(small_data)

        return Response(returned_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):

        """
        Delete all article comment objects at once. Only admin users can perform this action.
        """

        TemporaryArticleComment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, *args, **kwargs):
        """
        A post request that create a new temporary article comment and update article's comments number.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # articleId = data.get("articleId")
        # article = Article.objects.get(id=articleId)
        # article.commentNum = article.commentNum + 1 if article.commentNum else 1
        # article.save(update_fields=["commentNum"])

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()

class TemporaryArticleCommnentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) temporary article comments data and get the data using id.
    """

    queryset = TemporaryArticleComment.objects.all()
    serializer_class = TemporaryArticleCommentSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        """
        Deletes the temporary article comment and update the number of comments associated with the article.
        """
        temporaryArticleComment = self.get_object()
        id = temporaryArticleComment.id
        articleId = temporaryArticleComment.articleId

        # article = Article.objects.get(id=articleId.id)
        # article.commentNum = article.commentNum - 1 if article.commentNum > 0 else 0
        # article.save(update_fields=["commentNum"])

        response = super().delete(request, *args, **kwargs)

        response.data = {"message": f"Temporary Article Comment {id} deleted successfully"}
        return Response(response.data, status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class TemporaryArticleCommentList(APIView):

    """
    A view that get all specific article comments using keyword.
    """

    def get(self, request, format=None):

        """
        A get request that get all specific article comments using keywords.

        For example, when you set the view path as "/TemporaryArticleCommentList", to get all the article comments
        that has keyword "max" in content, use "/TemporaryArticleCommentList?keyword=max".

        To get the comments in specific article, use /TemporaryArticleCommentList?articleId=<articleId>

        To get the comments from specific user, use /TemporaryArticleCommentList?user=<userId>

        To use multiple queries, use &, for example, articleId=<articleId>&user=<userId>
        """

        key = request.query_params.get("key", None)
        user = request.query_params.get("user", None)
        articleId = request.query_params.get("articleId", None)

        filters = Q()

        if key:
            filters &= Q(content__icontains=key)
        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(articleId=articleId)

        if any([key, user, articleId]):
            # Return all objects which content contains the keyword.
            temporaryArticleComments = TemporaryArticleComment.objects.filter(filters)
        else:
            # If no filters are used, return all objects.
            temporaryArticleComments = TemporaryArticleComment.objects.all()

        serializer = TemporaryArticleCommentSerializer(temporaryArticleComments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class TemporaryArticleReactionListCreate(generics.ListCreateAPIView):

    """
    A view that get all temporary article reactions or delete all their data.
    """

    queryset = TemporaryArticleReaction.objects.all()
    serializer_class = TemporaryArticleReactionSerializer

    def delete(self, request, *args, **kwargs):

        """
        Delete all article reactions objects at once. Only admin users can perform this action.
        """

        TemporaryArticleReaction.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, *args, **kwargs):
        """
        Create a new temporary reaction and update the number of reactions the article receives.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # articleId = data.get("articleId")
        # article = Article.objects.get(id=articleId)
        # article.likeNum = article.likeNum + 1 if article.likeNum else 1
        # article.save(update_fields=["likeNum"])

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()
    
class TemporaryArticleReactionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) temporary article reaction data and get the data using its id.
    """

    queryset = TemporaryArticleReaction.objects.all()
    serializer_class = TemporaryArticleReactionSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        """
        Deletes the temporary article reaction and update the article's reaction number.
        """
        temporaryArticleReaction = self.get_object()
        id = temporaryArticleReaction.id
        articleId = temporaryArticleReaction.videoId

        # article = Article.objects.get(id=articleId.id)
        # article.likeNum = article.likeNum - 1 if article.likeNum > 0 else 0
        # article.save(update_fields=["likeNum"])

        response = super().delete(request, *args, **kwargs)

        response.data = {"message": f"Temporart Article Reaction {id} deleted successfully"}
        return Response(response.data, status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class TemporaryArticleReactionList(APIView):

    """
    A view that get all specific temporary article reactions using queries.
    """

    def get(self, request, format=None):

        """
        A get request that get all specific temporary article reactions using queries

        Assuming you set the path like "/TemporaryArticleReactionlist".

        To get the reactions in specific article, use "/TemporaryArticleReactionList?articleId=<articleId>"

        To get the reactions from specific user, use "/TemporaryArticleReactionList?user=<userId>"

        To use multiple queries, use &, for example, "articleId=<articleId>&user=<userId>"
        """

        user = request.query_params.get("user", None)
        articleId = request.query_params.get("articleId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(articleId=articleId)

        if any([user, articleId]):
            # Return all objects which content contains the keyword.
            temporaryArticleReactions = TemporaryArticleReaction.objects.filter(filters)
        else:
            # If no filters are used, return all objects.
            temporaryArticleReactions = TemporaryArticleReaction.objects.all()

        serializer = TemporaryArticleReactionSerializer(temporaryArticleReactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, format=None):
        """
        Delete a specific temporary article reaction using queries.

        Note that this only delete only one reaction. If there are multiple objects for deleting, it will
        return an error. Please use both queries like this: articleId=<articleId>&user=<userId>
        """
        user = request.query_params.get('user', None)
        articleId = request.query_params.get('articleId', None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(articleId=articleId)

        try:
            temporaryArticleReaction = TemporaryArticleReaction.objects.get(filters)
            temporaryArticleReaction.delete()

            # article = Article.objects.get(id=articleId)
            # article.likeNum = article.likeNum - 1
            # article.save(update_fields=["likeNum"])

            return Response({"message": "Object successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        except TemporaryArticleReaction.DoesNotExist:
            return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        except TemporaryArticleReaction.MultipleObjectsReturned:
            return Response({"message": "Multiple objects returned"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Error deleting object: {e.message}"}, status=status.HTTP_400_BAD_REQUEST)
    
class TemporaryVideoReactionListCreate(generics.ListCreateAPIView):

    """
    A view that get all temporary video reactions or delete all of them at once.
    """

    queryset = TemporaryVideoReaction.objects.all()
    serializer_class = TemporaryVideoReactionSerializer

    def delete(self, request, *args, **kwargs):

        """
        Delete all temporary video comment objects at once. Only admin users can perform this action.
        """

        TemporaryVideoReaction.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, *args, **kwargs):
        """
        Creates a new video reaction and updates the number of reactions the video receives.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # videoId = data.get("videoId")
        # video = Video.objects.get(id=videoId)
        # video.likeNum = video.likeNum + 1 if video.likeNum else 1
        # video.save(update_fields=["likeNum"])

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return super().get_permissions()
    
class TemporaryVideoReactionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):

    """
    A view for modifying (updating, deleting) temporary video reaction data and get the data using its id.
    """

    queryset = TemporaryVideoReaction.objects.all()
    serializer_class = TemporaryVideoReactionSerializer
    lookup_field = "pk"

    def delete(self, request, *args, **kwargs):
        """
        Deletes the temporary video reaction and update the number of reactions the video receives.
        """
        temporaryVideoReaction = self.get_object()
        id = temporaryVideoReaction.id
        # videoId = temporaryVideoReaction.videoId

        # video = Video.objects.get(id=videoId.id)
        # video.likeNum = video.likeNum - 1 if video.likeNum > 0 else 0
        # video.save(update_fields=["likeNum"]) 

        response = super().delete(request, *args, **kwargs)

        response.data = {"message": f"Article Comment {id} deleted successfully"}
        return Response(response.data, status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class TemporaryVideoReactionList(APIView):

    """
    A view that get all specific temporary video reaction using queries.
    """

    def get(self, request, format=None):

        """
        A get request that get all specific temporary video reaction using queries.

        Assuming you set the view path as "/TemporaryVideoReactionList".

        To get the reactions in specific video, use "/TemporaryVideoReactionList?videoId=<videoId>"

        To get the reactions from specific user, use "/TemporaryVideoReactionList?user=<userId>"

        To use multiple queries, use &, for example, "videoId=<videoId>&user=<userId>"
        """

        user = request.query_params.get("user", None)
        videoId = request.query_params.get("videoId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        if any([user, videoId]):
            # Return all objects which content contains the keyword.
            temporaryVideoReactions = TemporaryVideoReaction.objects.filter(filters)
        else:
            # If no filters are used, return all objects.
            temporaryVideoReactions = TemporaryVideoReaction.objects.all()

        serializer = TemporaryVideoReactionSerializer(temporaryVideoReactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, format=None):
        """
        Delete a specific video reaction using queries.

        Note that this only delete only one reaction. If there are multiple objects for deleting, it will
        return an error. Please use both queries like this: videoId=<videoId>&user=<userId>
        """
        user = request.query_params.get('user', None)
        videoId = request.query_params.get('videoId', None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        try:
            temporaryVideoReaction = TemporaryVideoReaction.objects.get(filters)
            temporaryVideoReaction.delete()

            # video = Video.objects.get(id=videoId)
            # video.likeNum = video.likeNum - 1
            # video.save(update_fields=["likeNum"])

            return Response({"message": "Object deleted"}, status=status.HTTP_204_NO_CONTENT)
        except TemporaryVideoReaction.DoesNotExist:
            return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        except TemporaryVideoReaction.MultipleObjectsReturned:
            return Response({"message": "Multiple objects returned"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Error deleting reaction: {e.message}"}, status=status.HTTP_400_BAD_REQUEST)

class TemporaryArticleBookmarkListCreate(generics.ListCreateAPIView):
    """
    A view that get all temporary article bookmarks or delete all of them at once.
    """
    queryset = TemporaryArticleBookmark.objects.all()
    serializer_class = TemporaryArticleBookmarkSerializer

    def delete(self, request, *args, **kwargs):
        """
        Delete all tempoarary article bookmarks. Only admin user can perform this action.
        """
        TemporaryArticleBookmark.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]

        return super().get_permissions()
    
class TemporaryArticleBookmarkRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    A view to get, update, or delete a temporary article bookmark using its id.
    """
    queryset = TemporaryArticleBookmark.objects.all()
    serializer_class = TemporaryArticleBookmarkSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class TemporaryArticleBookmarkList(APIView):
    """
    A view that get or delete temporary article bookmark using queries.
    """
    def get(self, request, *args, **kwargs):
        """
        Get all specific temporary article bookmarks using queries

        Assuming you set the path like "/TemporaryArticleBookmarklist".

        To get the bookmarks for specific article, use "/TemporaryArticleBookmarkList?articleId=<articleId>"

        To get the bookmarks from specific user, use "/TemporaryArticleBookmarkList?user=<userId>"

        To use multiple queries, use &, for example, "articleId=<articleId>&user=<userId>"
        """
        user = request.query_params.get("user", None)
        articleId = request.query_params.get("articleId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(articleId=articleId)

        if any([user, articleId]):
            temporaryArticleBookmarks = TemporaryArticleBookmark.objects.filter(filters)
        else:
            temporaryArticleBookmarks = TemporaryArticleBookmark.objects.all()

        serializer = TemporaryArticleBookmarkSerializer(temporaryArticleBookmarks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        """
        Delete a specific temporary article bookmark using queries.

        Note that this only delete only one bookmark. If there are multiple objects for deleting, it will
        return an error. Please use both queries like this: articleId=<articleId>&user=<userId>
        """
        user = request.query_params.get("user", None)
        articleId = request.query_params.get("articleId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if articleId:
            filters &= Q(articleId=articleId)

        try:
            temporaryArticleBookmark = TemporaryArticleBookmark.objects.get(filters)
            temporaryArticleBookmark.delete()
            return Response({"message": "Article Bookmark Object Successfully Deleted"}, status=status.HTTP_204_NO_CONTENT)
        except TemporaryArticleBookmark.DoesNotExist:
            return Response({"message": "Article Bookmark Object Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except TemporaryArticleBookmark.MultipleObjectsReturned:
            return Response({"message": "Too Many Article Bookmark Objects Returned"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"An Error Deleting Article Bookmark Object: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        
class GetArticlesFromTemporaryBookmark(APIView):
    """
    A view to get all articles from a specific user.
    """
    def get(self, request, *args, **kwargs):
        user = request.query_params.get("user")
        username = request.query_params.get("username")

        returned_articles = []

        if not any([user, username]):
            return Response({"message": "user's id/username does not specified"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if user:
                temporaryArticleBookmarks = TemporaryArticleBookmark.objects.filter(user=user)
            elif username:
                temporaryArticleBookmarks = TemporaryArticleBookmark.objects.filter(username=username)
            for articleBookmark in temporaryArticleBookmarks:
                article = Article.objects.get(id=articleBookmark.articleId.id)
                article_serializer = ArticleSerializer(article)
                returned_articles.append(article_serializer.data)
            return Response(returned_articles, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"An error getting article: {e}"}, status=status.HTTP_400_BAD_REQUEST)

class TemporaryVideoBookmarkListCreate(generics.ListCreateAPIView):
    """
    A view that get all temporary video bookmarks or delete all of them at once.
    """
    queryset = TemporaryVideoBookmark.objects.all()
    serializer_class = TemporaryVideoBookmarkSerializer

    def delete(self, request, *args, **kwargs):
        """
        Delete all tempoarary video bookmarks. Only admin user can perform this action.
        """
        TemporaryVideoBookmark.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]

        return super().get_permissions()
    
class TemporaryVideoBookmarkRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = TemporaryVideoBookmark.objects.all()
    serializer_class = TemporaryVideoBookmarkSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        return super().get_permissions()
    
class TemporaryVideoBookmarkList(APIView):
    """
    A view that get or delete temporary video bookmark using queries.
    """
    def get(self, request, *args, **kwargs):
        """
        Get all specific temporary video bookmarks using queries

        Assuming you set the path like "/TemporaryVideoBookmarklist".

        To get the bookmarks for specific video, use "/TemporaryVideoBookmarkList?videoId=<videoId>"

        To get the bookmarks from specific user, use "/TemporaryVideoBookmarkList?user=<userId>"

        To use multiple queries, use &, for example, "videoId=<videoId>&user=<userId>"
        """
        user = request.query_params.get("user", None)
        videoId = request.query_params.get("videoId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        if any([user, videoId]):
            temporaryVideoBookmarks = TemporaryVideoBookmark.objects.filter(filters)
        else:
            temporaryVideoBookmarks = TemporaryVideoBookmark.objects.all()

        serializer = TemporaryVideoBookmarkSerializer(temporaryVideoBookmarks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        """
        Delete a specific temporary video bookmark using queries.

        Note that this only delete only one bookmark. If there are multiple objects for deleting, it will
        return an error. Please use both queries like this: videoId=<videoId>&user=<userId>
        """
        user = request.query_params.get("user", None)
        videoId = request.query_params.get("videoId", None)

        filters = Q()

        if user:
            filters &= Q(user=user)
        if videoId:
            filters &= Q(videoId=videoId)

        try:
            temporaryVideoBookmark = TemporaryVideoBookmark.objects.get(filters)
            temporaryVideoBookmark.delete()
            return Response({"message": "Video Bookmark Object Successfully Deleted"}, status=status.HTTP_204_NO_CONTENT)
        except TemporaryVideoBookmark.DoesNotExist:
            return Response({"message": "Video Bookmark Object Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except TemporaryVideoBookmark.MultipleObjectsReturned:
            return Response({"message": "Too Many Video Bookmark Objects Returned"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"An Error Deleting Video Bookmark Object: {e}"}, status=status.HTTP_400_BAD_REQUEST)

class GetVideosFromTemporaryBookmark(APIView):
    """
    A view to get all videos from a specific user.
    """
    def get(self, request, *args, **kwargs):
        user = request.query_params.get('user')
        username = request.query_params.get("username")

        returned_videos = []

        if not any[user, username]:
            return Response({"message": "user's id/username does not specified"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if user:
                temporaryVideoBookmarks = TemporaryVideoBookmark.objects.filter(user=user)
            elif username:
                temporaryVideoBookmarks = TemporaryVideoBookmark.objects.filter(username=username)
            for videoBookmark in temporaryVideoBookmarks:
                video = Video.objects.get(id=videoBookmark.videoId.id)
                video_serializer = VideoSerializer(video)
                returned_videos.append(video_serializer.data)
            return Response(returned_videos, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"An error getting video: {e}"}, status=status.HTTP_400_BAD_REQUEST)

def get_home(request, *args, **kwargs):
    return render(request, 'index.html', {})

def upload_to_google_drive(request, *args, **kwargs):

    """
    Upload to Google Drive is the form is valid. The form include the following fields:
    - videoBrandType: The technology topic of the video.
    - author: The video's owner.
    - title: The video's title, or head content.
    - file: The video's file, supporting video/mp4.
    If the form requests 
    """

    start = time.time()
    
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_uploaded_file = request.FILES['videoFiles']
            print(video_uploaded_file)
            thumbnail_image_file = request.FILES['thumbnailImageFiles']
            videoBrandType = form.cleaned_data.get("videoBrandType", None)
            author = form.cleaned_data.get('author', None)
            title = form.cleaned_data.get('title', None)
            video_file_path = os.path.join(settings.MEDIA_ROOT, video_uploaded_file.name)
            thumbnail_image_path = os.path.join(settings.IMAGE_DIR, thumbnail_image_file.name)

            # Save the file into temporary path
            with open(video_file_path, 'wb+') as destination:
                for chunk in video_uploaded_file.chunks():
                    destination.write(chunk)

            with open(thumbnail_image_path, 'wb+') as destination:
                for chunk in thumbnail_image_file.chunks():
                    destination.write(chunk)

            # Upload to Google Drive
            try:
                video_file_id = upload_file(video_file_path, video_uploaded_file.name)
                image_file_id = upload_file(thumbnail_image_path, thumbnail_image_file.name, "image/jpeg")
            except Exception as e:
                message = f"An error occured: {e}"
            finally:
                video_url = f"https://drive.google.com/file/d/{video_file_id}/view"
                video_fetchable_url = f"fetch/{video_file_id}"
                image_url = f"https://drive.google.com/file/d/{image_file_id}/view"
                image_fetchable_url = f"fetch/{image_file_id}"
                os.remove(video_file_path)
                os.remove(thumbnail_image_path)

                if video_file_id:
                    try:
                        video = Video.objects.create(
                            videoUniqueId=video_file_id,
                            thumbnailImageId=image_file_id,
                            videoBrandType=videoBrandType,
                            author=author,
                            title=title,
                            url=video_url,
                            fetchable_url=video_fetchable_url,
                            thumbnailImageUrl=image_url,
                            thumbnailImageFetchableUrl=image_fetchable_url
                        )
                        message = f"File uploaded successfully: {video.id}, {video.videoUniqueId}"
                    except Exception as e:
                        print(e)
                        return delete_file(request, [video_file_id, image_file_id])
                else:
                    message = "File upload was not succeed."

            end = time.time()

            total_time = end - start

            return render(
                request, 
                'upload_result.html', 
                {
                    'message': message, 
                    "time_message": f"Total time: {total_time}s"
                }
            )
    else:
        form = FileUploadForm()

    return render(
        request, 
        'upload_form.html', 
        {
            'form': form, 
            'form_type': "a",
        }
    )

def upload_to_google_drive_with_url(request, *args, **kwargs):

    """
    A function that manages the uploading form using url only. However, this function
    only applies to specific website like Tiktok. The others have not been supported yet.
    """

    start = time.time()
    if request.method == 'POST':
        form = FileUploadFormWithUrl(request.POST, request.FILES)
        if form.is_valid():
            message = ""
            video_file_path = None
            image_file_path = None # The file path that stores videos temporarily.
            videoContent = None # The stored data value
            if "get_data" in request.POST:
                url = form.cleaned_data.get("URL")
                try:
                    videoContent = get_video_content(url, settings.MEDIA_ROOT, "tempvideo.mp4")
                    if videoContent.get("csv_file", None):
                        csv_file = videoContent.pop("csv_file")
                        # os.remove(csv_file)
                    with open('temp.txt', "w") as f:
                        json.dump(videoContent, f, indent=4)
                    
                    return render(
                        request,
                        'upload_form.html',
                        {
                            'form': form,
                            'form_type': 'b',
                            'data': videoContent
                        })
                except Exception as e:
                    end = time.time()
                    return render(
                        request,
                        'upload_result.html',
                        {
                            'message': f"Error getting content from {url}: {e}",
                            'files': None,
                            'time_message': f"Total time: {end - start}s"
                        }
                    )
            elif 'upload' in request.POST:
                video_file_path = os.path.join(settings.MEDIA_ROOT, "tempvideo.mp4")
                image_file_path = os.path.join(settings.IMAGE_DIR, "thumbnail.jpg")
                with open("temp.txt", "r") as file:
                    videoContent = json.load(file)
                if not videoContent or not (os.path.exists(video_file_path) ):
                    end = time.time()
                    return render(
                        request,
                        'upload_result.html',
                        {
                            'message': "Data hasn't occured yet.",
                            'files': None,
                            'time_message': f"Total time: {end - start}s"
                        }
                    )
                videoBrandType = form.cleaned_data.get("videoBrandType", None)
                try:
                    video_file_id = upload_file(video_file_path, "tempvideo.mp4")
                    image_file_id = upload_file(image_file_path, "thumbnail.jpg", "image/jpeg") if os.path.exists(image_file_path) else None
                except Exception as e:
                    message = f"An error occured while uploading file: {e}"
                finally:
                    video_view_url = f"https://drive.google.com/file/d/{video_file_id}/view"
                    video_fetchable_url = f"fetch/{video_file_id}"
                    image_view_url = f"https://drive.google.com/file/d/{image_file_id}/view" if image_file_id else None
                    image_fetchable_url = f"fetch/{image_file_id}" if image_file_id else None
                    os.remove(video_file_path)
                    os.remove(image_file_path)

                    if video_file_id:
                        message = f"Brand type: {videoBrandType}, title: {videoContent.get('title', '')}, author: {videoContent.get('author', '')}"  
                        try:
                            video = Video.objects.create(
                                videoUniqueId=video_file_id,
                                thumbnailImageId=image_file_id,
                                videoBrandType=videoBrandType,
                                author=videoContent["author"],
                                title=videoContent["title"],
                                url=video_view_url,
                                fetchable_url=video_fetchable_url,
                                thumbnailImageUrl=image_view_url,
                                thumbnailImageFetchableUrl=image_fetchable_url
                            )
                            message = f"Video uploaded successfully: {video.id} - {video.videoUniqueId}"
                        except Exception as e:
                            return delete_file(request, video_file_id, e + message)
            elif 'reset' in request.POST:
                video_file_path = os.path.join(settings.MEDIA_ROOT, "tempvideo.mp4")
                image_file_path = os.path.join(settings.IMAGE_DIR, "thumbnail.jpg")
                if os.path.exists(video_file_path):
                    os.remove(video_file_path)
                if os.path.exists(image_file_path):
                    os.remove(image_file_path)
                return render(
                    request,
                    'upload_form.html',
                    {
                        "form": form,
                        "form_type": "b"
                    }
                )
            end = time.time()
            total_time = end - start
            return render(
                request, 
                'upload_result.html', 
                {
                    'message': message, 
                    "time_message": f"Total time: {total_time}s"
                }
            )
    else:
        form = FileUploadFormWithUrl()
    return render(
        request, 
        'upload_form.html', 
        {
            'form': form, 
            'form_type': "b",
        }
    )

def upload_article(request, *args, **kwargs):
    start = time.time()
    if request.method == 'POST':
        form = ArticleUploadForm(request.POST)
        if form.is_valid():
            articleId = form.cleaned_data.get("articleId")
            articleBrandType = form.cleaned_data.get("articleBrandType")
            sourceName = form.cleaned_data.get("sourceName")
            author = form.cleaned_data.get("author", "")
            title = form.cleaned_data.get("title")
            description = form.cleaned_data.get("description", "")
            url = form.cleaned_data.get("url", "")
            urlToImage = form.cleaned_data.get("urlToImage", "")
            publishedAt = form.cleaned_data.get("publishedAt")
            content = form.cleaned_data.get("content")

            try:
                article = Article.objects.create(
                    articleUniqueId=articleId,
                    articleBrandType=articleBrandType,
                    sourceName=sourceName,
                    author=author,
                    title=title,
                    description=description,
                    url=url,
                    urlToImage=urlToImage,
                    publishedAt=publishedAt,
                    content=content
                )
                message = f"Article object created successfully: {article.articleUniqueId}"
            except Exception as e:
                message = f"An error creating Article object: {e}"
            end = time.time()
            return render(
                request,
                "upload_result.html",
                {
                    "message": message,
                    "time_message": f"Total time: {end - start}"
                }
            )
    else:
        form = ArticleUploadForm()

    return render(
        request, 
        'index.html',
        {
            'form': form,
            'form_type': "c"
        }
    )

def upload_article_with_only_url(request, *args, **kwargs):
    start = time.time()
    if request.method == 'POST':
        form = ArticleUploadFromWithUrl(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get("url")
            articleBrandType = form.cleaned_data.get("articleBrandType")
            articleContent = None

            if "get_data" in request.POST:
                try:
                    articleContent = get_article_content(url)
                    articleContent["articleBrandType"] = articleBrandType

                    with open("temp2.txt", "w") as f:
                        json.dump(articleContent, f, indent=4)

                    return render(
                        request,
                        "upload_form.html",
                        {
                            "form": form,
                            "form_type": "d",
                            "data": articleContent
                        }
                    )
                except Exception as e:
                    end = time.time()
                    return render(
                        request,
                        "upload_result.html",
                        {
                            "message": f"Error getting content from url {url}: {e}",
                            "files": None,
                            "time_message": f"Totel time: {end - start}s"
                        }
                    )
            elif "upload" in request.POST:
                with open("temp2.txt", "r") as f:
                    articleContent = json.load(f)
                if not articleContent:
                    end = time.time()
                    return render(
                        request,
                        'upload_result.html',
                        {
                            'message': "Data hasn't occured yet.",
                            'files': None,
                            'time_message': f"Total time: {end - start}s"
                        }
                    )
                try:
                    article = Article.objects.create(
                        title=articleContent["title"],
                        author=articleContent["author"],
                        description=articleContent["description"],
                        articleUniqueId=articleContent["articleUniqueId"],
                        content=articleContent["content"],
                        urlToImage=articleContent["urlToImage"],
                        articleBrandType=articleBrandType
                    )
                    end = time.time()
                    return render(
                        request,
                        'upload_result.html',
                        {
                            "message": f"Successfully create article object: {article.articleUniqueId}",
                            "time_message": f"Total time: {end - start}s"
                        }
                    )
                except Exception as e:
                    end = time.time()
                    return render(
                        request,
                        "upload_result.html",
                        {
                            "message": f"Error creating article object: {e}",
                            "time_message": f"Total time: {end - start}s"
                        }
                    )
            elif "reset" in request.POST:
                articleContent = None
                return render(
                    request,
                    "upload_form.html",
                    {
                        "form_type": "d",
                        "form": form
                    }
                )

    else:
        form = ArticleUploadFromWithUrl()

    return render(
        request,
        'upload_form.html',
        {
            "form": form,
            'form_type': "d"
        }
    )

def list_files(request):
    """
    Listing all stored videos in google drive if they exist.
    """
    start = time.time()
    files = list_all_files()

    if not files:
        message = "No files were uploaded"
    else:
        message = "List of files: "
    end = time.time()

    return render(
        request, 
        'upload_result.html', 
        {
            'message': message, 
            "files": files, 
            "time_message": f"Total time: {end - start}s"
        }
    )

def get_file(request, id):

    """
    Get specific file based on its id.
    """

    start = time.time()
    file = get_specific_file(id)

    if not file:
        message = 'File not found'
    else:
        message = f"File {id}"
    end = time.time()

    return render(
        request, 
        'upload_result.html', 
        {
            'message': message, 
            "files": [file], 
            "time_message": f"Total time: {end - start}s"
        }
    )

def delete_file(request, id: str, message=None, model=Video):

    """
    Delete the video files from database and Google Drive existance.

    For ids parameter, set the file id in the first position.
    For example, if you want to delete a video but it contains another file as well,
    type [video_id, ...]
    """

    start = time.time()
    try:
        video = model.objects.get(videoUniqueId=id)
        thumbnailImage = video.thumbnailImageId
        # Delete file from Google Drive
        video_file = delete_specific_file(id)
        thumbnail_file = delete_specific_file(thumbnailImage)
        # Delete file from database
        video.delete()
        if not message:
            message = f"File deleted successfully: {video_file}"
    except Video.DoesNotExist:
        if not message:
            message = "Video does not exist in database."
    except Exception as e:
        if not message:
            message = f'Error deleting file {id}: {e}'
    end = time.time()

    return render(
        request, 
        'upload_result.html', 
        {
            'message': message, 
            "time_message": f"Total time: {end - start}s"
        })

def fetch_file(request, id):
    file_url = f'https://drive.google.com/uc?export=download&id={id}'
    response = requests.get(file_url)
    if response.status_code == 200:
        return HttpResponse(
            response.content, 
            content_type=response.headers['Content-Type']
        )
    else:
        return HttpResponse(
            "Error fetching file", 
            status=status.HTTP_400_BAD_REQUEST
        )
    
def get_video_content(url: str, output_folder: str = None, output_file: str = None):

    """
    Returns the author, title, and video src from tiktok url.
    """
    
    if url.startswith("https://www.tiktok.com"):
        pyk.specify_browser("chrome")

        # When this line executes, it will download all its content to the path it executed.
        pyk.save_tiktok(
            url,
            True,
            'data.csv'
        )

        time.sleep(5)

        files = os.listdir(".")
        csv_file_path = None
        for file in files:
            if os.path.isfile(f"./{file}") and file.endswith((".mp4", ".mkv")):
                try:
                    # Move the mp4 (video file) to the destination
                    shutil.move(f"./{file}", os.path.join(output_folder, output_file))
                except FileNotFoundError:
                    raise Exception(f"Could not found the file {file}.")
                except PermissionError:
                    raise Exception(f"Permission denied when moving: {file}")
                except Exception as e:
                    raise Exception(f"An error occured: {e}")
            elif os.path.isfile(f"./{file}") and file.endswith(".csv"):
                csv_file_path = os.path.join(".", file)

        if not csv_file_path or not os.path.exists(csv_file_path):
            n1 = "\n"
            raise Exception(f"An error occured getting csv file: {csv_file_path}, file list: {n1.join([f for f in files])}")
        saved_data = pd.read_csv(csv_file_path)
        author = saved_data.iloc[saved_data.shape[0] - 1]['author_name']
        title = saved_data.iloc[saved_data.shape[0] - 1]['video_description']
        return {
            "author": author,
            "title": title,
            "src": url,
            "thumbnail_url": None,
            "csv_file": csv_file_path
        }

    elif url.startswith("https://www.youtube.com"):
        try:
            # Library pytube, deprecated (does not work).
            # 
            # yt = YouTube(url)
            # os.makedirs(output_folder, exist_ok=True)

            # title = yt.title
            # author = yt.author

            # stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
            # stream.download(output_path=output_folder, filename=output_file)

            # return {
            #     "author": author,
            #     "title": title,
            #     "src": url
            # }
            
            video_opts = {
                'format': 'mp4/best',
                "outtmpl": os.path.join(output_folder, output_file)
            }

            thumbnail_opts = {
                'skip_download': True,
                'write_thumbnail': True,
                "outtmpl": os.path.join(settings.IMAGE_DIR, "thumbnail.jpg"),
                'postprocessors': [
                    {
                        "key": 'FFmpegThumbnailsConvertor',
                        'format': "jpg"
                    }
                ]
            }

            with yt_dlp.YoutubeDL({}) as ydl:
                info_dict = ydl.extract_info(url, download=True)

                title = info_dict.get("title", None)
                author = info_dict.get("uploader", None)
                thumbnail_url = info_dict.get("thumbnail", None)

            with yt_dlp.YoutubeDL(video_opts) as ydl:
                ydl.download([url])

            with yt_dlp.YoutubeDL(thumbnail_opts) as ydl:
                ydl.download([url])

                return {
                    "author": author,
                    "title": title,
                    "src": url,
                    "thumbnail_url": thumbnail_url
                }

        except Exception as e:
            raise Exception(e)
    else:
        raise ValueError("URL does not exist or has not been supported yet.")
    
def load_and_write(url, folder, filename):
    driver = webdriver.Chrome(service=Service("E:\ChromeDriver\chromedriver.exe"))
    driver.get(url)

    video_element = driver.find_element(By.TAG_NAME, "video")
    video_src = video_element.get_attribute("src")
    if not video_src:
        video_src = driver.find_element(By.TAG_NAME, "source").get_attribute("src")
        if not video_src:
            raise Exception("Could not find video.")
        
    response = requests.get(video_src, stream=True)
    if response.status_code == 200:
        with open(os.path.join(folder, filename), "wb") as destination:
            for chunk in response.iter_content(chunk_size=2048):
                destination.write(chunk)
        print("Writing complete.")
    else:
        raise requests.exceptions.HTTPError(f"Status code is not 200: {response.status_code}")
    driver.quit()

def update_video_comment_number(request, videoId):

    """
    Update the number of comments in the video.
    """

    start = time.time()
    try:
        video = Video.objects.get(id=videoId)
        videoCommentsNum = VideoComment.objects.filter(videoId=videoId).count()

        video.commentNum = videoCommentsNum
        message = "Update video comment number successfully"
    except Exception as e:
        message = f"Error updating comment number: {e}"
    end = time.time()
    return render(
        request,
        "upload_result.html",
        {
            "message": message,
            "time_message": f"Total time: {end - start}s"
        }
    )

def update_article_comment_number(request, articleId):

    """
    Update the number of comments for the article.
    """

    start = time.time()
    try:
        article = Article.objects.get(id=articleId)
        articleCommentsNum = ArticleComment.objects.filter(articleId=articleId).count()

        article.commentNum = articleCommentsNum
        message = "Update video comment number successfully"
    except Exception as e:
        message = f"Error updating comment number: {e}"
    end = time.time()
    return render(
        request,
        "upload_result.html",
        {
            "message": message,
            "time_message": f"Total time: {end - start}s"
        }
    )

def get_not_found_page(request, exception):
    return render(request, '404_not_found.html', status=status.HTTP_404_NOT_FOUND)

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect("/")
            else:
                form.add_error('username_or_email', 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(
        request,
        'auth_config.html',
        {
            'form': form,
            'action': 'login'
        }
    )
    
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
        else:
            form.add_error(None, 'Something went wrong registering account.')
    else:
        form = SignupForm()

    return render(
        request,
        'auth_config.html',
        {
            'form': form,
            'action': 'signup'
        }
    )

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'auth_config.html'
    extra_context = {
        'action': 'reset_password'
    }
    success_url = "/resetPassword/done"

    def form_valid(self, form):
        return super().form_valid(form)
    
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth_config.html'
    extra_context = {
        'action': 'reset_password_done'
    }

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth_config.html'
    extra_context = {
        'action': 'reset_password_confirm'
    }
    success_url = "/resetPassword/complete"

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'auth_config.html'
    extra_context = {
        'action': 'reset_password_complete'
    }

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        domain = get_current_site(request).domain
        protocol = "https" if request.is_secure() else "http"
        if not email:
            return Response({"message": "email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{protocol}://{domain}/reset-password/{uid}/{token}/"

        # Send the reset link via email
        send_mail(
            'Password Reset Request',
            f'Click the link below to reset your password:\n\n{reset_link}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({'message': 'Password reset link sent'}, status=status.HTTP_200_OK)
    
class PasswordResetConfirmationView(APIView):
    def get(self, request, uidb64, token):
        # Render an HTML form when the reset link is opened
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return HttpResponse("<h3>Invalid or expired reset link</h3>", status=400)

        if default_token_generator.check_token(user, token):
            # Render password reset form if the token is valid
            return render(request, 'password_reset_form.html', {'uidb64': uidb64, 'token': token})
        else:
            return HttpResponse("<h3>Invalid or expired reset link</h3>", status=400)

    def post(self, request, uidb64, token):
        new_password = request.data.get('password')

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'email': user.email,
                    'username': user.username,
                    'userId': user.userId,
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User created successfully",
                "user": {
                    "email": user.email,
                    "username": user.username,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def update_profile(request, *args, **kwargs):
    user = request.user
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get("password")

            if new_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
            if form.cleaned_data.get("username") and form.cleaned_data.get("username") != user.username:
                user.username = form.cleaned_data.get("username")
            if form.cleaned_data.get("email") and form.cleaned_data.get("email") != user.email:
                user.email = form.cleaned_data.get("email")
            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=user)

@login_required
def profile(request, *args, **kwargs):
    user = request.user

def get_article_content(url="ggg"):
    res = requests.get(url)

    if not res.ok:
        raise Exception(f"Error getting article: {res.status}")
    bs = BeautifulSoup(res.content, "html.parser")

    timenow = datetime.now()
    formatted = timenow.strftime("%Y-%m-%d-%H-%M-%S")
    if url.startswith("https://news.samsung.com"):
        container = bs.find("div", {"class": "container"})
        title = container.find("h1", {"class": "title"}).text
        cont = container.find("div", {"class": "text_cont"})
        description = cont.find("h3", {"class": "subtitle"}).text
        content_ps = cont.find_all(lambda tag: tag.name in ["div", "h3"] and not tag.hasAttr("class"))

        for tag in content_ps:
            if tag.find("img"):
                urlToImage = tag.find("img").get("src", None)

        content = "\n\n".join(c.text for c in content_ps)

        articleUniqueId = "samsung-" + formatted

        author = "Samsung"

    elif url.startswith("https://www.apple.com"):
        article = bs.find("article", {"class": "article"})
        title = article.find("h1", {"class": "hero-headline"})
        figure = article.find("figure", {"class": "image"})
        urlToImage = figure.find("img").get("src", None)

        content_text = ""

        pagebodies = article.find_all("div", {"class": "pagebody"})
        for pagebody in pagebodies:
            pagebodyCopies = pagebody.find_all("div", {"class": "pagebody-copy"})
            for pagebodyCopy in pagebodyCopies:
                content_text += pagebodyCopy.text + "\n\n"

        articleUniqueId = "apple-" + formatted
        description = ""
        author = "Apple"

    elif url.startswith("https://www.mi.com/"):
        article = bs.find("section", {"class": "new-detail__main"})
        title = article.find("div", {"class": "new-detail__title"}).text
        content_ps = article.find("div", {"class": "new-detail__content"}).find_all("p")

        content = "\n\n".join(c.text for c in content_ps)

        articleUniqueId = "xiaomi-" + formatted

        description = ""
        urlToImage = ""
        author = "Xiaomi"

    elif url.startswith("https://huawei.com"):
        article = bs.find("div", {"class": "main"})
        title = article.find("div", {"class": "container-custom"})
        content_ps = article.find("div", {"class": "news-detail-content"}).find_all("p")

        content = "\n\n".join(c.text for c in content_ps)

        articleUniqueId = "huawei-" + formatted

        description = ""
        urlToImage = ""
        author = "Huawei"

    elif url.startswith("https://www.asus.com"):
        article = bs.find("div", {"class": "NewsContentPage__newsContent__2nfMh"})
        title = article.find("h1", {"class": "NewsContentPage__title__1sZvm"})
        mainArticle = article.find("article")
        urlToImage = mainArticle.find("img").get("src", None)
        content_ps = article.find_all("p")

        content = "\n\n".join(c.text for c in content_ps)

        articleUniqueId = "asus-" + formatted

        description = ""
        author = "Asus"

    elif url.startswith("https://www.dell.com"):
        article = bs.find("article")
        header = article.find("header")
        title = header.find("h1", {"class": "entry-title"}).text
        description = header.find("div", {"class": "entry-excerpt"}).text

        entryMeta = header.find("div", {"class": "entry-meta"})
        author = entryMeta.find("a", {"rel": "author"}).text
        
        urlToImage = article.find("img", {"class": "signle-featured-image-header-thumbnail-big"}).get("src", None)
        content_ps = article.find("div", {"class": "entry-content"}).find_all(["p", "h3", "h4"])

        content = "\n\n".join(c.text for c in content_ps)

        articleUniqueId = "dell-" + formatted

    else:
        raise Exception("The url does not exist or is not supported.")
    
    return {
        "title": title,
        "description": description,
        "author": author,
        "urlToImage": urlToImage,
        "content": content,
        "articleUniqueId": articleUniqueId
    }