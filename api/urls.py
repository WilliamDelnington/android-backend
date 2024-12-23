from django.urls import path
import api.views as views

urlpatterns = [
    path(
        'articles', 
        views.ArticleListCreate.as_view(), 
        name="create-article"
        ),
    path(
        'articles/<int:pk>', 
        views.ArticleRetrieveUpdateDestroy.as_view(), 
        name="update-article"
        ),
    path(
        'articles/search', 
        views.ArticleList.as_view(), 
        name="list-article"
        ),
    path(
        'articles/uploadForm',
        views.upload_article,
        name="upload-article-form"
        ),
    path(
        'articles/uploadUrlOnlyForm',
        views.upload_article_with_only_url,
        name="upload-article-form-only-url"
        ),
    path(
        'articles/updateComments/<str:articleId>', 
        views.update_article_comment_number, 
        name="update-article-comment-number"
        ),
    path(
        'videos', 
        views.VideoListCreate.as_view(), 
        name='create-video'
        ),
    path(
        'videos/<int:pk>', 
        views.VideoRetrieveUpdateDestroy.as_view(), 
        name='update-video'
        ),
    path(
        'videos/search', 
        views.VideoList.as_view(), 
        name="list-video"
        ),
    path(
        'videos/uploadForm',
        views.upload_to_google_drive,
        name='upload-to-google-drive'
        ),
    path(
        'videos/uploadUrlOnlyForm',
        views.upload_to_google_drive_with_url,
        name='upload-to-google-drive-with-url'
        ),
    path(
        'videos/listGoogleDrive',
        views.list_files,
        name="list-files-in-google-drive"
        ),
    path(
        'videos/updateComments/<str:videoId>', 
        views.update_video_comment_number, 
        name="update-video-comment-number"
        ),
    path(
        'videos/listGoogleDrive/<str:id>', 
        views.get_file, 
        name='get-file'
        ),
    path(
        'videos/deleteFromDrive/<str:id>',
        views.delete_file, 
        name='delete-file'
        ),
    path(
        'articleComments', 
        views.ArticleCommentListCreate.as_view(), 
        name='create-article-comments'
        ),
    path(
        'articleComments/<int:pk>', 
        views.ArticleCommnentRetrieveUpdateDestroy.as_view(), 
        name='update-article-comments'
        ),
    path(
        'articleComments/search', 
        views.ArticleCommentList.as_view(), 
        name='list-article-comments'
        ),
    path(
        'videoComments',
        views.VideoCommentListCreate.as_view(), 
        name='create-video-comments'
        ),
    path(
        'videoComments/<int:pk>',
        views.VideoCommentRetrieveUpdateDestroy.as_view(),
        name='update-video-comments'
        ),
    path(
        'videoComments/search',
        views.VideoCommentList.as_view(), 
        name='list-video-comments'
        ),
    path(
        'searchHistory', 
        views.SearchHistoryCreate.as_view(),
        name='create-search-history'
        ),
    path(
        'searchHistory/<int:pk>',
        views.SearchHistoryRetrieveUpdateDestroy.as_view(), 
        name='update-search-history'
        ),
    path(
        'searchHistory/search',
        views.SearchHistoryList.as_view(),
        name='list-search-history'
        ),
    path(
        'users',
        views.UserListCreate.as_view(),
        name='create-users'
        ),
    path(
        'users/<int:pk>',
        views.UserRetrieveUpdateDestroy.as_view(),
        name='update-users'
        ),
    path(
        'users/register', 
        views.UserList.as_view(),
        name='get-users'
        ),
    path(
        'register',
        views.RegisterView.as_view(),
        name='register'
        ),
    path(
        'fetch/<str:id>', 
        views.fetch_file, 
        name='load-test-page'
        ),
]

handler404 = views.get_not_found_page