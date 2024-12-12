from rest_framework import serializers
from .models import *

class ArticleSerializer(serializers.Serializer):
    class Meta:
        model = Article
        fields = '__all__'

class VideoSerializer(serializers.Serializer):
    class Meta:
        model = Video
        fields = '__all__'

class ArticleCommentSerializer(serializers.Serializer):
    class Meta:
        model = ArticleComment
        fields = '__all__'

class VideoCommentSerializer(serializers.Serializer):
    class Meta:
        model = VideoComment
        fields = '__all__'

class SearchHistorySerializer(serializers.Serializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'

    