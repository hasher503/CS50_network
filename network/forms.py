"""all forms for network app"""
from django.forms import ModelForm, TextInput, Textarea, EmailInput, ClearableFileInput

from .models import User, Post


class UserForm(ModelForm):
    """update a User"""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'avatar')
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': EmailInput(attrs={'class': 'form-control'}),
            'avatar': ClearableFileInput(attrs={'class': 'form-control'})
        }

class PostForm(ModelForm):
    """submit a Post"""
    class Meta:
        model = Post
        fields = ('body',)
        widgets = {'body': Textarea(attrs={'class': 'form-control', 'rows': 4})}
        labels = {'body': 'New Post'}
        