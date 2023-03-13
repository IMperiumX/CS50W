from django import forms
from django.contrib.auth.models import User
from .models import Profile, Post


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("body", "status")


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email")


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("date_of_birth", "photo")
