from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class FileUploadForm(forms.Form):
    videoBrandType = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Video Brand Type: '
        })
    )
    author = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Author'
        })
    )
    title = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Title'
        })
    )
    files = forms.FileField(required=True)

class CustomUserCreationsForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'is_active', 'is_staff', 'is_superuser')