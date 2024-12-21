from django import forms
from django.utils import timezone
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
    videoBrandType = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }))
    
    author = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Enter file's author"
        }))
    
    title = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Enter file's title"
        }))
    
    createdTime = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control'
        }))
    
    files = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_createdTime(self):
        createdTime = self.cleaned_data.get("createdTime")
        if not createdTime:
            return timezone.now()
        return createdTime

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
    videoBrandType = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={
            'class': "form-control"
        }))
    
    createdTime = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control'
        }))

    URL = forms.URLField(
        max_length=400,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'URL'
        })
    )

    def clean_createdTime(self):
        createdTime = self.cleaned_data.get("createdTime")
        if not createdTime:
            return timezone.now()
        return createdTime

class CustomUserCreationsForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'is_active', 'is_staff', 'is_superuser')

class ArticleUploadForm(forms.Form):
    articleId = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Article's ID"
        }))

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
    articleBrandType = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }))

    sourceName = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            "placeholder": "Enter Article's Source"
        }))

    author = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Author's Name"
        }))

    title = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Enter Article's Title"
        }))

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Enter Article's Description"
        }))

    url = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Article's URL"
        }))

    urlToImage = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Article's URL Display Image"
        }))

    publishedAt = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={
            "type": "datetime-local",
            "class": "form-control"
        })
    )

    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Enter Article's Content"
        }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["articleId"].label = "Article Id:"
        self.fields["articleBrandType"].label = "Source Type:"
        self.fields["sourceName"].label = "Source Name:"
        self.fields["author"].label = "Author:"
        self.fields["title"].label = "Title:"
        self.fields["description"].label = "Description:"
        self.fields["url"].label = "URL:"
        self.fields["urlToImage"].label = "URL to image:"
        self.fields["publishedAt"].label = "Time Published:"
        self.fields["content"].label = "Content:"

    def clean_publishedAt(self):
        publishedAt = self.cleaned_data.get("publishedAt")
        if not publishedAt:
            return timezone.now()
        return publishedAt
    
class ArticleUploadFromWithUrl(forms.Form):
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["url"].label = "URL:"