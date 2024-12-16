from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class FileUploadForm(forms.Form):
    CHOICES = [
        ("Samsung", "Samsung"),
        ("Apple", "Apple"),
        ("Nokia", "Nokia"),
        ("Microsoft", "Microsoft"),
        ("Google", "Google"),
        ("Dell", "Dell"),
        ("Asus", "Asus"),
        ("Huawei", "Huawei"),
        ("Xiaomi", "Xiaomi")
    ]
    videoBrandType = forms.ChoiceField(choices=CHOICES)
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

class FileUploadFormWithUrl(forms.Form):
    CHOICES = [
        ("Samsung", "Samsung"),
        ("Apple", "Apple"),
        ("Nokia", "Nokia"),
        ("Microsoft", "Microsoft"),
        ("Google", "Google"),
        ("Dell", "Dell"),
        ("Asus", "Asus"),
        ("Huawei", "Huawei"),
        ("Xiaomi", "Xiaomi")
    ]
    videoBrandType = forms.ChoiceField(choices=CHOICES)
    URL = forms.URLField(
        max_length=400,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'URL'
        })
    )

class CustomUserCreationsForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'is_active', 'is_staff', 'is_superuser')