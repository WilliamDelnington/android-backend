from django.shortcuts import render, redirect
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Article, Video, ArticleComment, VideoComment, SearchHistory, CustomUser
from .serializer import *
from .utils import upload_file, list_all_files, get_specific_file, delete_specific_file
from .forms import *
# from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# from selenium.common.exceptions import WebDriverException
# from TikTokApi import TikTokApi
# from pytube import YouTube
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
        A delete request that delete all article objects at once.
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

        For example, when you set the view path as "/ArticleList", to get all the articles
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
        A delete request that delete all video objects at once.
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

        For example, when you set the view path as "/VideoList", to get all the articles
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

    def delete(self, request, *args, **kwargs):

        """
        A delete request that delete all article comment objects at once.
        """

        ArticleComment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
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
        A get request that get all specific article comments using keywords.

        For example, when you set the view path as "/ArticleCommentList", to get all the article comments
        that has keyword "max" in content, use "/ArticleCommentList?keyword=max".
        """

        key = request.query_params.get("keyword", "")

        if key:
            # Return all objects which content contains the keyword.
            articleComments = ArticleComment.objects.filter(content__icontains=key)
        else:
            # If no filters are used, return all objects.
            articleComments = ArticleComment.objects.all()

        serializer = ArticleCommentSerializer(articleComments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class VideoCommentListCreate(generics.ListCreateAPIView):

    """
    A view that get all video comments or delete all video comments at once.
    """

    queryset = VideoComment.objects.all()
    serializer_class = VideoCommentSerializer

    def delete(self, request, *args, **kwargs):

        """
        A delete request that delete all video comment objects at once.
        """

        VideoComment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
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
        A get request that get all specific article comments using keywords.

        For example, when you set the view path as "/VideoCommentList", to get all the video comments
        that has keyword "max" in content, use "/VideoCommentList?keyword=max".
        """

        key = request.query_params.get("keyword", "")

        if key:
            # Return all objects which content contains the keyword.
            videoComments = VideoComment.objects.filter(content__icontains=key)
        else:
            # If no filters are used, return all objects.
            videoComments = VideoComment.objects.all()

        serializer = VideoCommentSerializer(videoComments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SearchHistoryCreate(generics.ListCreateAPIView):

    """
    A view that get all users search histories or delete all search histories at once.
    """

    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer

    def delete(self, request, *args, **kwargs):

        """
        A delete request that delete all search history objects at once.
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
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        elif self.request.method in ["PUT", "PATCH"]:
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

        key = request.query_params.get("keyword", "")
        if key:
            history = SearchHistory.objects.filter(searchValue__contains=key)
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
        A delete request that delete all user objects at once.
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
            video_uploaded_file = request.FILES['file_one']
            thumbnail_image_file = request.FILES['file_two']
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
                image_file_id = upload_file(thumbnail_image_path, thumbnail_image_file.name)
            except Exception as e:
                message = f"An error occured: {e}"
            finally:
                video_url = f"https://drive.google.com/file/d/{video_file_id}/view"
                video_fetchable_url = f"https://drive.google.com/uc?export=download?id={video_file_id}"
                image_url = f"https://drive.google.com/file/d/{image_file_id}/view"
                image_fetchable_url = f"https://drive.google.com/uc?export=download?id={image_file_id}"
                os.remove(video_file_path)
                os.remove(thumbnail_image_path)

                if video_file_id:
                    try:
                        video = Video.objects.create(
                            videoUniqueId=video_file_id,
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
                    image_file_id = upload_file(image_file_path, "thumbnail.jpg") if os.path.exists(image_file_path) else None
                except Exception as e:
                    message = f"An error occured while uploading file: {e}"
                finally:
                    video_view_url = f"https://drive.google.com/file/d/{video_file_id}/view"
                    video_fetchable_url = f"https://drive.google.com/uc?export=download?id={video_file_id}"
                    image_view_url = f"https://drive.google.com/file/d/{image_file_id}/view" if image_file_id else None
                    image_fetchable_url = f"https://drive.google.com/uc?export=download?id={image_file_id}" if image_file_id else None
                    os.remove(video_file_path)
                    os.remove(image_file_path)

                    if video_file_id:
                        message = f"Brand type: {videoBrandType}, title: {videoContent.get('title', '')}, author: {videoContent.get('author', '')}"  
                        try:
                            video = Video.objects.create(
                                videoUniqueId=video_file_id,
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
                            return delete_file(request, [video_file_id, image_file_id], e + message)
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
    if request.method == 'POST':
        form = ArticleUploadFromWithUrl(request.POST)

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

def delete_file(request, ids: list, message=None, model=Video):

    """
    Delete the video files from database and Google Drive existance.

    For ids parameter, set the file id in the first position.
    For example, if you want to delete a video but it contains another file as well,
    type [video_id, ...]
    """

    start = time.time()
    try:
        for id in ids:
        # Delete file from Google Drive
            file = delete_specific_file(id)
        # Delete file from database
        model.objects.get(videoUniqueId=ids[0]).delete()
        if not message:
            message = f"File deleted successfully: {file}"
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