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
        'articles/updateCommentNumbers/<int:articleId>', 
        views.update_article_comment_number, 
        name="update-article-comment-number"
        ),
    path(
        'articles/comments', 
        views.ArticleCommentListCreate.as_view(), 
        name='create-article-comments'
        ),
    path(
        'articles/comments/<int:pk>', 
        views.ArticleCommnentRetrieveUpdateDestroy.as_view(), 
        name='update-article-comments'
        ),
    path(
        'articles/comments/search', 
        views.ArticleCommentList.as_view(), 
        name='list-article-comments'
        ),
    path(
        "articles/comments/temporary",
        views.TemporaryArticleCommentListCreate.as_view(),
        name="create-temporary-article-comments"
        ),
    path(
        "articles/comments/temporary/<int:pk>",
        views.TemporaryArticleCommnentRetrieveUpdateDestroy.as_view(),
        name="update-temporary-article-comments"
        ),
    path(
        "articles/comments/temporary/search",
        views.TemporaryArticleCommentList.as_view(),
        name="list-temporary-article-comments"
        ),
    path(
        "articles/reactions",
        views.ArticleReactionListCreate.as_view(),
        name="create-article-reactions"
        ),
    path(
        "articles/reactions/<int:pk>",
        views.ArticleReactionRetrieveUpdateDestroy.as_view(),
        name="update-article-reactions"
        ),
    path(
        "articles/reactions/search",
        views.ArticleReactionList.as_view(),
        name="list-article-reactions"
        ),
    path(
        "articles/reactions/temporary",
        views.TemporaryArticleReactionListCreate.as_view(),
        name="create-temporary-article-reactions"
        ),
    path(
        "articles/reactions/temporary/<int:pk>",
        views.TemporaryArticleReactionRetrieveUpdateDestroy.as_view(),
        name="update-temporary-article-reactions"
        ),
    path(
        "articles/reactions/temporary/search",
        views.TemporaryArticleReactionList.as_view(),
        name="list-temporary-article-reactions"
        ),
    path(
        "articles/bookmarks",
        views.ArticleBookmarkListCreate.as_view(),
        name="create-article-bookmarks"
        ),
    path(
        "articles/bookmarks/<int:pk>",
        views.ArticleBookmarkRetrieveUpdateDestroy.as_view(),
        name="update-article-bookmarks"
        ),
    path(
        "articles/bookmarks/search",
        views.ArticleBookmarkList.as_view(),
        name="list-article-bookmarks"
        ),
    path(
        "articles/bookmarks/getArticles",
        views.GetArticlesFromBookmark.as_view(),
        name="get-articles-from-bookmarks"
        ),
    path(
        "articles/bookmarks/temporary",
        views.TemporaryArticleBookmarkListCreate.as_view(),
        name="create-temporary-article-bookmarks"
        ),
    path(
        "articles/bookmarks/temporary/<int:pk>",
        views.TemporaryArticleBookmarkRetrieveUpdateDestroy.as_view(),
        name="update-temporary-article-bookmarks"
        ),
    path(
        "articles/bookmarks/temporary/search",
        views.TemporaryArticleBookmarkList.as_view(),
        name="list-temporary-article-bookmarks"
        ),
    path(
        "articles/bookmarks/temporary/getArticles",
        views.GetArticlesFromTemporaryBookmark.as_view(),
        name="get-articles-from-temporary-bookmarks"),
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
        'videos/updateCommentNumber/<int:videoId>', 
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
        'videos/comments',
        views.VideoCommentListCreate.as_view(), 
        name='create-video-comments'
        ),
    path(
        'videos/comments/<int:pk>',
        views.VideoCommentRetrieveUpdateDestroy.as_view(),
        name='update-video-comments'
        ),
    path(
        'videos/comments/search',
        views.VideoCommentList.as_view(), 
        name='list-video-comments'
        ),
    path(
        "videos/comments/temporary",
        views.TemporaryVideoCommentListCreate.as_view(),
        name='create-temporary-video-comments'
        ),
    path(
        "videos/comments/temporary/<int:pk>",
        views.TemporaryVideoCommentRetrieveUpdateDestroy.as_view(),
        name='update-temporary-video-comments'
        ),
    path(
        "videos/comments/temporary/search",
        views.TemporaryVideoCommentList.as_view(),
        name='list-temporary-video-comments'
        ),
    path(
        "videos/reactions",
        views.VideoReactionListCreate.as_view(),
        name="create-video-reactions"
        ),
    path(
        "videos/reactions/<int:pk>",
        views.VideoReactionRetrieveUpdateDestroy.as_view(),
        name="update-video-reactions"
        ),
    path(
        "videos/reactions/search",
        views.VideoReactionList.as_view(),
        name="list-video-reactions"
        ),
    path(
        "videos/reactions/temporary",
        views.TemporaryVideoReactionListCreate.as_view(),
        name="create-temporary-video-reactions"
        ),
    path(
        "videos/reactions/temporary/<int:pk>",
        views.TemporaryVideoReactionRetrieveUpdateDestroy.as_view(),
        name="update-temporary-video-reactions"
        ),
    path(
        "videos/reactions/temporary/search",
        views.TemporaryVideoReactionList.as_view(),
        name="list-temporary-video-reactions"
        ),
    path(
        "videos/bookmarks",
        views.VideoBookmarkListCreate.as_view(),
        name="create-video-bookmarks"
        ),
    path(
        "videos/bookmarks/<int:pk>",
        views.VideoBookmarkRetrieveUpdateDestroy.as_view(),
        name="update-video-bookmarks"
        ),
    path(
        "videos/bookmarks/search",
        views.VideoBookmarkList.as_view(),
        name="list-video-bookmarks"
        ),
    path(
        "videos/bookmarks/getVideos",
        views.GetVideosFromBookmark.as_view(),
        name="get-videos-from-bookmarks"
        ),
    path(
        "videos/bookmarks/temporary",
        views.TemporaryVideoBookmarkListCreate.as_view(),
        name="create-temporary-video-bookmarks"
        ),
    path(
        "videos/bookmarks/temporary/<int:pk>",
        views.TemporaryVideoBookmarkRetrieveUpdateDestroy.as_view(),
        name="update-temporary-video-bookmarks"
        ),
    path(
        "videos/bookmarks/temporary/search",
        views.TemporaryVideoBookmarkList.as_view(),
        name="list-temporary-video-bookmarks"
        ),
    path(
        "videos/bookmarks/temporary/getVideos",
        views.GetVideosFromTemporaryBookmark.as_view(),
        name="get-videos-from-temporary-bookmarks"
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
        "searchHistory/temporary",
        views.TemporarySearchHistoryCreate.as_view(),
        name="create-temporary-search-history"
        ),
    path(
        "searchHistory/temporary/<int:pk>",
        views.TemporarySearchHistoryRetrieveUpdateDestroy.as_view(),
        name='update-temporary-search-history'
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
        'users/temporary',
        views.TemporaryUserListCreate.as_view(),
        name='create-temporary-users'
        ),
    path(
        "users/temporary/<int:pk>",
        views.TemporaryUserRetrieveUpdateDestroy.as_view(),
        name='update-temporary-users'
        ),
    path(
        "users/temporary/search",
        views.TemporaryUserGet.as_view(),
        name="get-temporary-user"
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
    path(
        'login',
        views.LoginAPIView.as_view(),
        name='login'
        ),
    path(
        'signup',
        views.RegisterAPIView.as_view(),
        name='signup'
        ),
    path(
        "logout",
        views.LogoutAPIView.as_view(),
        name="logout"
        ),
    path(
        'resetPassword',
        views.CustomPasswordResetView.as_view(),
        name='reset-password'
        ),
    path(
        'resetPassword/done',
        views.CustomPasswordResetDoneView.as_view(),
        name='reset-password-done'
        ),
    path(
        'resetPassword/reset/<uidb64>/<token>',
        views.CustomPasswordResetConfirmView.as_view(),
        name='reset-password-confirm'
        ),
    path(
        'resetPassword/complete',
        views.CustomPasswordResetCompleteView.as_view(),
        name='reset-password-complete'
        ),
    path(
        'profile',
        views.profile,
        name='profile'
        ),
    path(
        'password-reset', 
        views.PasswordResetRequestView.as_view(), 
        name='password_reset_request'
        ),
    path(
        'reset-password/<uidb64>/<token>/', 
        views.PasswordResetConfirmationView.as_view(), 
        name='password_reset_confirm'
        ),
]

handler404 = views.get_not_found_page