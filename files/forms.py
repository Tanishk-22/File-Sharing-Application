from django import forms
from .models import UserFile

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')  # Add other fields if needed

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UserFile
        fields = ['file']
