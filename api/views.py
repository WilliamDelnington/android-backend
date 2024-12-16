from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAdminUser
from .models import Article, Video, ArticleComment, VideoComment, SearchHistory, CustomUser
from .serializer import *
from .utils import upload_file, list_all_files, get_specific_file, delete_specific_file
from .forms import FileUploadForm, FileUploadFormWithUrl
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import time
import requests

# Create your views here.
class ArticleListCreate(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def delete(self, request, *args, **kwargs):
        Article.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ArticleRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = "pk"

class ArticleList(APIView):
    def get(self, request, format=None):
        key = request.query_params.get("keyword", "")
        k = request.query_params.get("key", "")

        if key and k:
            articles = Article.objects.filter(
                (Q(sourceName__icontains=key) | 
                 Q(articleBrandType__icontains=key)) &
                (Q(title__icontains=k) | 
                 Q(description__icontains=k) | 
                 Q(content__icontains=k))
            )
        elif key:
            articles = Article.objects.filter(
                Q(sourceName__icontains=key) | 
                Q(articleBrandType__icontains=key))
        elif k:
            articles = Article.objects.filter(
                Q(title__icontains=k) |
                Q(description__icontains=k) |
                Q(content__icontains=k)
            )
        else:
            articles = Article.objects.all()

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk, format=None):
        try:
            video = Video.objects.get(pk=pk)
            id = video.videoUniqueId
            delete_specific_file(id)
            video.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
class VideoListCreate(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def delete(self, request, *args, **kwargs):
        Video.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VideoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    lookup_field = "pk"

class VideoList(APIView):
    def get(self, request, format=None):
        sourceName = request.query_params.get("keyword", "")

        if sourceName:
            articles = Video.objects.filter(sourceName__icontains=sourceName)
        else:
            articles = Video.objects.all()

        serializer = VideoSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ArticleCommentListCreate(generics.ListCreateAPIView):
    queryset = ArticleComment.objects.all()
    serializer_class = ArticleCommentSerializer

    def delete(self, request, *args, **kwargs):
        ArticleComment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ArticleCommnentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = ArticleComment.objects.all()
    serializer_class = ArticleCommentSerializer
    lookup_field = "pk"

class ArticleCommentList(APIView):
    def get(self, request, format=None):
        key = request.query_params.get("keyword", "")

        if key:
            articles = ArticleComment.objects.filter(content__icontains=key)
        else:
            articles = ArticleComment.objects.all()

        serializer = ArticleCommentSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class VideoCommentListCreate(generics.ListCreateAPIView):
    queryset = VideoComment.objects.all()
    serializer_class = VideoCommentSerializer

    def delete(self, request, *args, **kwargs):
        VideoComment.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VideoCommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = VideoComment.objects.all()
    serializer_class = VideoCommentSerializer
    lookup_field = "pk"

class VideoCommentList(APIView):
    def get(self, request, format=None):
        key = request.query_params.get("keyword", "")

        if key:
            articles = VideoComment.objects.filter(content__icontains=key)
        else:
            articles = VideoComment.objects.all()

        serializer = VideoCommentSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SearchHistoryCreate(generics.ListCreateAPIView):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer

    def delete(self, request, *args, **kwargs):
        SearchHistory.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    permission_classes = [IsAdminUser]
    
class SearchHistoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    lookup_field = "pk"

    permission_classes = [IsAdminUser]

class SearchHistoryList(APIView):
    def get(self, request, format=None):
        key = request.query_params.get("userId", "")
        if key:
            history = SearchHistory.objects.filter(user__contains=key)
        else:
            history = SearchHistory.objects.all()

        serializer = SearchHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserListCreate(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        CustomUser.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"

class UserList(APIView):
    def get(self, request, format=None):
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
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.create_user(
                email=serializer.validated_data['email'],
                password=request.data.get('password'),
                username=serializer.validated_data['username']
            )
            return Response({'message': 'User created successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "User registered successfully!", "user_id": user.userId}, status=status.HTTP_201_CREATED)
    
def get_home(request, *args, **kwargs):
    return render(request, 'index.html', {})

# @require_POST

# def create_google_drive_folder(request, *args, **kwargs):
#     if request.method == "POST":
#         folder_name = request.POST.get('folder_name', "New Folder")
#         folder_id = create_folder(folder_name)
#         return JsonResponse({"message": "Folder created successfully.", folder_id: folder_id})
#     else:
#         return JsonResponse({"message": "An error occured", "status": JsonResponse.status_code})

def upload_to_google_drive(request, *args, **kwargs):
    start = time.time()
    
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['files']
            videoBrandType = form.cleaned_data.get("videoBrandType", None)
            author = form.cleaned_data.get('author', None)
            title = form.cleaned_data.get('title', None)
            file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

            # Save the file into temporary path
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Upload to Google Drive
            try:
                file_id = upload_file(file_path, uploaded_file.name)
            except Exception as e:
                message = f"An error occured: {e}"
            finally:
                url = f"https://drive.google.com/file/d/{file_id}/view"
                os.remove(file_path)

                if file_id:
                    try:
                        video = Video.objects.create(
                            videoUniqueId=file_id,
                            videoBrandType=videoBrandType,
                            author=author,
                            title=title,
                            url=url
                        )
                        message = f"File uploaded successfully: {video.id}, {video.videoUniqueId}"
                    except Exception as e:
                        message = f"Error creating model object: {e}"
                else:
                    message = "File upload was not succeed."

            end = time.time()

            total_time = end - start

            return render(request, 'upload_result.html', {
                'message': message, 
                "files": None, 
                "time_message": f"Total time: {total_time}s"
                })
    else:
        form = FileUploadForm()

    return render(request, 'upload_form.html', {
        'form': form, 
        'form_type': "a",
        'data': None
        })

def upload_to_google_drive_with_url(request, *args, **kwargs):
    start = time.time()
    if request.method == 'POST':
        form = FileUploadFormWithUrl(request.POST, request.FILES)
        if form.is_valid():
            action = request.POST.get('action')
            message = ""
            file_path = None
            videoContent = None
            if action == 'get_data':
                url = form.cleaned_data.get("URL")
                try:
                    videoContent = get_video_content(url)
                    file_path = os.path.join(settings.MEDIA_ROOT, "tempvideo.mp4")

                    res = requests.get(url)
                    with open(file_path, 'wb+') as destination:
                        for chunk in res.iter_content(chunk_size=8192):
                            destination.write(chunk)
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
                            'message': "Error getting content from {url}: {e}",
                            'files': None,
                            'time_message': f"Total time: {end - start}s"
                        }
                    )
            elif action == 'upload':
                if not videoContent and not file_path:
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
                    file_id = upload_file(file_path, "tempvideo.mp4")
                except Exception as e:
                    message = f"An error occured while uploading file: {e}"

            end = time.time()
            total_time = end - start
            return render(request, 'upload_result.html', {
                'message': message, 
                "files": None,
                "time_message": f"Total time: {total_time}s"
                })
    else:
        form = FileUploadFormWithUrl()
    return render(request, 'upload_form.html', {
        'form': form, 
        'form_type': "b",
        'data': None
        })

def list_files(request):
    start = time.time()
    files = list_all_files()

    if not files:
        message = "No files were uploaded"
    else:
        message = "List of files: "
    end = time.time()

    total_time = end - start

    return render(request, 'upload_result.html', {'message': message, "files": files, "time_message": f"Total time: {total_time}s"})

def get_file(request, id):
    start = time.time()
    file = get_specific_file(id)

    if not file:
        message = 'File not found'
    else:
        message = f"File {id}"
    end = time.time()

    total_time = end - start

    return render(request, 'upload_result.html', {'message': message, "files": [file], "time_message": f"Total time: {total_time}s"})

def delete_file(request, id):
    start = time.time()
    try:
        file = delete_specific_file(id)
        Video.objects.get(videoUniqueId=id).delete()
        message = f"File deleted successfully: {file}"
    except Exception as e:
        message = f'Error deleting file {id}: {e}'
    end = time.time()

    total_time = end - start

    return render(request, 'upload_result.html', {'message': message, "files": None, "time_message": f"Total time: {total_time}s"})

def fetch_file(request, id):
    file_url = f'https://drive.google.com/uc?export=download&id={id}'
    response = requests.get(file_url)
    if response.status_code == 200:
        return HttpResponse(response.content, content_type=response.headers['Content-Type'])
    else:
        return HttpResponse("Error fetching file", status=400)
    
def get_video_content(url: str):
    if url.startswith("https://www.tiktok.com"):
        while True:
            driver = webdriver.Chrome(service=Service("E:\ChromeDriver\chromedriver.exe"))

            driver.get(url)

            page_source = driver.page_source

            bs = BeautifulSoup(page_source, "html.parser")
            mainContentVideoDetail = bs.find("div", {"id": "app"}).find("div", {"id": "main-content-video_detail"})
            divPlayerContainer = mainContentVideoDetail.find("div", {"class": "eqrezik4"})
            tiktokWebPlayer = divPlayerContainer.find("div", {"class": "tiktok-web-player"})
            videoTag = tiktokWebPlayer.find("video")
            source = videoTag.find_all("source")
            contentContainer = divPlayerContainer.find("div", {"class": "eqrezik17"})
            author = contentContainer.find("div", {"class": "evv7pft3"}).find("span", {"class": "e17fzhrb1"}).text
            title = contentContainer.find("h1", {"data-e2e": "browse-video-desc"}).text

            if source:
                src = source[2].get("src")
            else:
                src = videoTag.get("src")
            driver.quit()
            if src.startswith("https://www.tiktok.com/"):
                return {
                    "author": author,
                    "title": title,
                    "src": src
                }