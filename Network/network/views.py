from itertools import chain

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, DetailView, ListView, UpdateView


from .forms import CreatePostForm, ProfileEditForm, UserEditForm
from .models import Post, Profile


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
            messages.success(request, "Account Created successfully")

            Profile.objects.create(user=user)
        except IntegrityError:
            messages.error(request, "Error Creating your Account")
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

        return HttpResponseRedirect(reverse("index"))

    return render(request, "network/post_new.html", {"form": CreatePostForm()})


def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    posts = user.twitter_posts.all()
    return render(request, "user/detail.html", {"user": user, "posts": posts})


@login_required
def following_posts(request, username):
    user = User.objects.get(username=username, is_active=True)
    user_to_set = user.following.all()
    following_posts = [user.twitter_posts.all() for user in user_to_set]
    posts = list(chain.from_iterable(following_posts)).sort()

    return render(request, "network/following.html", {"posts": posts})


@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
        else:
            messages.error(request, "Error updating your profile")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        "network/edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
@csrf_exempt
def like(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        is_liked = request.POST.get('is_liked')
        try:
            post = Post.objects.get(id=post_id)
            if is_liked == 'no':
                post.users_like.add(request.user)
                is_liked = 'yes'
            elif is_liked == 'yes':
                post.users_like.remove(request.user)
                is_liked = 'no'
            post.save()

            return JsonResponse(
                {
                    'like_count': post.users_like.count(),
                    'is_liked': is_liked,
                    "status": 201,
                }
            )
        except:
            return JsonResponse({'error': "Post not found", "status": 404})
    return JsonResponse({}, status=400)


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 10
    template_name = "network/index.html"


class PostDetailView(DetailView):
    model = Post
    template_name = "network/post_detail.html"


class PostUpdateView(UpdateView):
    model = Post
    template_name = "network/post_edit.html"
    fields = ["body", "status"]
    success_url = reverse_lazy("index")


class PostDeleteView(DeleteView):
    model = Post
    template_name = "network/post_delete.html"
    success_url = reverse_lazy("index")


class UserPostListView(ListView):
    queryset = User.objects.filter(is_active=True).exclude(id=1)
    paginate_by = 10
    context_object_name = "users"
    template_name = "user/list.html"
