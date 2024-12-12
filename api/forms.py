from django import forms

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