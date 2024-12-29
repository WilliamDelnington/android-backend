from rest_framework import serializers
from .models import *

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class ArticleCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleComment
        fields = '__all__'

class VideoCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoComment
        fields = '__all__'

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = ['userId']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password", "confirm_password"]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password from the data
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username']
        )
        return user
    
class TemporaryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryUser
        fields = '__all__'

class TemporarySearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporarySearchHistory
        fields = '__all__'

class TemporaryArticleCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryArticleComment
        fields = '__all__'

class TemporaryVideoCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryVideoComment
        fields = '__all__'