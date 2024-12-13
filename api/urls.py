from django.urls import path
import api.views as views

urlpatterns = [
    path('articles', views.ArticleListCreate.as_view(), name="create-article"),
    path('articles/<int:pk>', views.ArticleRetrieveUpdateDestroy.as_view(), name="update-article"),
    path('articles/search', views.ArticleList.as_view(), name="list-article"),
    path('videos', views.VideoListCreate.as_view(), name='create-video'),
    path('videos/<int:pk>', views.VideoRetrieveUpdateDestroy.as_view(), name='update-video'),
    path('videos/search', views.VideoList.as_view(), name="list-video"),
    path('articleComments', views.ArticleCommentListCreate.as_view(), name='create-article-comments'),
    path('articleComments/<int:pk>', views.ArticleCommnentRetrieveUpdateDestroy.as_view(), name='update-article-comments'),
    path('articleComments/search', views.ArticleCommentList.as_view(), name='list-article-comments'),
    path('videoComments', views.VideoCommentListCreate.as_view(), name='create-video-comments'),
    path('videoComments/<int:pk>', views.VideoCommentRetrieveUpdateDestroy.as_view(), name='update-video-comments'),
    path('videoComments/search', views.VideoCommentList.as_view(), name='list-video-comments'),
    path('searchHistory', views.SearchHistoryCreate.as_view(), name='create-search-history'),
    path('searchHistory/<int:pk>', views.SearchHistoryRetrieveUpdateDestroy.as_view(), name='update-search-history'),
    path('searchHistory/search', views.SearchHistoryList.as_view(), name='list-search-history'),
    path('users', views.UserListCreate.as_view(), name='create-users'),
    path('users/<int:pk>', views.UserRetrieveUpdateDestroy.as_view(), name='update-users'),
    path('users/register', views.UserList.as_view(), name='get-users'),
    path('googleDrive/upload', views.upload_to_google_drive, name='upload-to-google-drive'),
    path('googleDrive/list', views.list_files, name="list-files-in-google-drive"),
    path('googleDrive/list/<str:id>', views.get_file, name='get-file'),
    path('googleDrive/delete/<str:id>', views.delete_file, name='delete-file'),
    path('fetch/<str:id>', views.fetch_file, name='load-test-page'),
]