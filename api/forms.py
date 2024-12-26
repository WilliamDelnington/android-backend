from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser
import re

def validate_password(value):
    if len(value) < 8:
        raise ValidationError("Password must have at least 8 characters.")
    if not re.search(r'\d', value):
        raise ValidationError("Password must have at least 1 number.")
    if not re.search(r'[A - Z]', value):
        raise ValidationError("Password must have at least 1 uppercase letter.")
    
def validate_username(value):
    if not re.search(r'^[a-zA-Z][a-zA-Z0-9_]*$', value):
        raise ValidationError("Username should never contain the symbols except underscores.")

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
        }),
        label="Video Brand Type:"
        )
    
    author = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Enter file's author"
        }),
        label="Author:"
        )
    
    title = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Enter file's title"
        }),
        label="Title:"
        )
    
    createdTime = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        label="Created Time:"
        )
    
    videoFiles = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'video/mp4, video/mpeg, video.ogg'
        }),
        label='Video File: '
        )
    
    thumbnailImageFiles = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg, image/png, image/webp'
        }),
        label="Thumbnail Image File:"
        )

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

class SignupForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username:",
        validators=[validate_username]
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Email:"
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password:",
        validators=[validate_password]
    )

    retype_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Retype password:"
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("retype_password")

        if password != password_confirm:
            raise ValidationError("Password don't match.")
        
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("Email already taken.")
        
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("Username already taken.")
        
    def save(self):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return user
    
class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username:"
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password:"
    )

class GetEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Enter your email:"
    )

class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password:",
        validators=[validate_password]
    )

    retype_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Retype password:"
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("retype_password")

        if password != password_confirm:
            raise ValidationError("Password don't match.")
        
class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to keep the same'
        }),
        label='Change Email:',
        required=False,
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to keep the same'
        }),
        label='Change Username:',
        required=False
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to keep the same'
        }),
        label="Change password:",
        required=False,
        validators=[validate_password]
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Retype your password'
        }),
        label="Reenter password:",
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ["username", 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmed_password = cleaned_data.get("confirm_password")

        if password and password != confirmed_password:
            raise ValidationError("Passwords don't match.")
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("Email already taken.")
        
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("Username already taken.")