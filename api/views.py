from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, generics
from .models import Article, Video, ArticleComment, VideoComment, SearchHistory
from .serializer import ArticleSerializer, VideoSerializer, ArticleCommentSerializer, VideoCommentSerializer, SearchHistorySerializer
from .utils import upload_file, list_all_files, get_specific_file, delete_specific_file
from .forms import FileUploadForm
import os
import googleapiclient.errors as GoogleErrors
import time

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
            video.delete()
            
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
    
class SearchHistoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    lookup_field = "pk"

class SearchHistoryList(APIView):
    def get(self, request, format=None):
        key = request.query_params.get("userId", "")
        if key:
            history = SearchHistory.objects.filter(user__contains=key)
        else:
            history = SearchHistory.objects.all()

        serializer = SearchHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
                message = f"An error occured: {e} in"
            finally:
                
                file = get_specific_file(file_id)
                url = f"https://drive.google.com/file/d/{file_id}/view"
                createdTime = file.get('createdTime')
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

            return render(request, 'upload_result.html', {'message': message, "files": None, "time_message": f"Total time: {total_time}s"})
    else:
        form = FileUploadForm()

    return render(request, 'upload_form.html', {'form': form})

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