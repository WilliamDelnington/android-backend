from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username = ..., password = ..., **kwargs):
        return super().authenticate(request, username, password, **kwargs)