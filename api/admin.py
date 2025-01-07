from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .forms import *

# Register your models here.
class CustomUserAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ("email", "username", "is_active", "is_staff", "is_superuser")
    # Fields to filter by in the list view
    list_filter = ("is_active", "is_staff", "is_superuser")
    # Fields to search for in the admin interface
    search_fields = ('email', 'username')
    # Fields to use as readonly
    readonly_fields = ('userId', 'last_login')

    # Fieldsets for organizing fields in the detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )

    # Fields to use when creating a new user in the admin interface
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Ordering of the users in the admin list view
    ordering = ('email',)

    add_form = CustomUserCreationsForm
    form = CustomUserChangeForm

class TemporaryUserAdmin(admin.ModelAdmin):
    form = TemporaryUserCreationForm
    list_display = ("username", "profileImage")
    search_fields = ("username",)

class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "articleUniqueId",
        "articleBrandType",
        "sourceName",
        "author",
        "title",
        "description",
        "url",
        "urlToImage",
        "publishedAt",
        "content"
    )

    fields = (
        "articleUniqueId",
        "articleBrandType",
        "sourceName",
        "author",
        "title",
        "description",
        "url",
        "urlToImage",
        "publishedAt",
        "content"
    )

    search_fields = (
        "articleUniqueId",
    )

    form = ArticleUploadForm

class VideoAdmin(admin.ModelAdmin):
    # list_display = (
    #     "videoUniqueId",
    #     "thumbnailImageId",
    #     "videoBrandType",
    #     "author",
    #     "title",
    #     "url",
    #     "fetchable_url",
    #     "thumbnailImageUrl",
    #     "thumbnailImageFetchableUrl",
    #     "createdTime"
    # )

    form = FileUploadForm

class ArticleCommentAdmin(admin.ModelAdmin):
    form = ArticleCommentForm

class VideoCommentAdmin(admin.ModelAdmin):
    form = VideoCommentForm

class ArticleReactionAdmin(admin.ModelAdmin):
    form = ArticleReactionForm

class VideoReactionAdmin(admin.ModelAdmin):
    form = VideoReactionForm

class ArticleBookmarkAdmin(admin.ModelAdmin):
    form = ArticleBookmarkForm

class VideoBookmarkAdmin(admin.ModelAdmin):
    form = VideoBookmarkForm

class TemporaryArticleCommentAdmin(admin.ModelAdmin):
    form = TemporaryArticleCommentForm

class TemporaryVideoCommentAdmin(admin.ModelAdmin):
    form = TemporaryVideoCommentForm

class TemporaryArticleReactionAdmin(admin.ModelAdmin):
    form = TemporaryArticleReactionForm

class TemporaryVideoReactionAdmin(admin.ModelAdmin):
    form = TemporaryVideoReactionForm

class TemporaryArticleBookmarkAdmin(admin.ModelAdmin):
    form = TemporaryArticleBookmarkForm

class TemporaryVideoBookmarkAdmin(admin.ModelAdmin):
    form = TemporaryVideoBookmarkForm

admin.site.register(TemporaryUser, TemporaryUserAdmin)

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Article, ArticleAdmin)

admin.site.register(Video, VideoAdmin)

admin.site.register(ArticleComment, ArticleCommentAdmin)

admin.site.register(VideoComment, VideoCommentAdmin)

admin.site.register(ArticleReaction, ArticleReactionAdmin)

admin.site.register(VideoReaction, VideoReactionAdmin)

admin.site.register(ArticleBookmark, ArticleBookmarkAdmin)

admin.site.register(VideoBookmark, VideoBookmarkAdmin)

admin.site.register(TemporaryArticleComment, TemporaryArticleCommentAdmin)

admin.site.register(TemporaryVideoComment, TemporaryVideoReactionAdmin)

admin.site.register(TemporaryArticleReaction, TemporaryArticleReactionAdmin)

admin.site.register(TemporaryVideoReaction, TemporaryVideoReactionAdmin)

admin.site.register(TemporaryArticleBookmark, TemporaryArticleBookmarkAdmin)

admin.site.register(TemporaryVideoBookmark, TemporaryVideoBookmarkAdmin)