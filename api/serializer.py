from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate

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

class ArticleReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleReaction
        fields = '__all__'

class VideoReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoReaction
        fields = '__all__'

class ArticleBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleBookmark
        fields = '__all__'

class VideoBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoBookmark
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
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
        else:
            raise serializers.ValidationError("Must include both email and password.")

        data['user'] = user
        return data
    
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

class TemporaryArticleReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryArticleReaction
        fields = '__all__'

class TemporaryVideoReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryVideoReaction
        fields = '__all__'

class TemporaryArticleBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryArticleBookmark
        fields = '__all__'

class TemporaryVideoBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryVideoBookmark
        fields = '__all__'