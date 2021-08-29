from itertools import chain
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.models import User

from common.decorators import ajax_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView

from .models import Post, Profile, Contact
from .forms import UserEditForm, ProfileEditForm, CreatePostForm


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            # Create the user profile
            messages.success(request, 'Account Created successfully')

            Profile.objects.create(user=user)
        except IntegrityError:
            messages.error(request, 'Error Creating your Account')
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data["body"]
            status = form.cleaned_data["status"]
            user = request.user
            Post.objects.create(author=user, body=body, status=status)

        return HttpResponseRedirect(reverse('index'))

    return render(request, "network/post_new.html", {'form': CreatePostForm()})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    posts = user.twitter_posts.all()
    return render(request, 'user/detail.html', {'user': user, 'posts': posts})


@login_required
def following_posts(request, username):
    user = User.objects.get(username=username, is_active=True)
    user_to_set = user.following.all()
    following_posts = [user.twitter_posts.all() for user in user_to_set]
    posts = list(chain.from_iterable(following_posts))

    return render(request, 'network/following.html', {'posts': posts})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        'network/edit.html',
        {'user_form': user_form, 'profile_form': profile_form},
    )


@ajax_required
@login_required
@require_POST
def tweet_like(request):
    tweet_id = request.POST.get('id')
    action = request.POST.get('action')
    if tweet_id and action:
        try:
            tweet = Post.objects.get(id=tweet_id)
            if action == 'like':
                tweet.users_like.add(request.user)
            else:
                tweet.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'error'})


@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'network/index.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'network/post_detail.html'


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'network/post_edit.html'
    fields = ['body', 'status']
    success_url = reverse_lazy('index')


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'network/post_delete.html'
    success_url = reverse_lazy('index')


class UserPostListView(ListView):
    queryset = User.objects.filter(is_active=True).exclude(id=1)
    paginate_by = 10
    context_object_name = 'users'
    template_name = 'user/list.html'
