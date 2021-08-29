from django.urls import path

from . import views

urlpatterns = [
    # AUTH URLs
    path("", views.PostListView.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # Post related URLs
    path('like/', views.tweet_like, name='like'),
    path('post/new', views.create_post, name='post_new'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    # User action realted URLs
    path('edit/', views.edit, name='edit'),
    path('users/', views.UserPostListView.as_view(), name='user_list'),
    path('users/follow/', views.user_follow, name='user_follow'),
    path('users/<username>/following/', views.following_posts, name='user_following'),
    path('users/<username>/', views.user_detail, name='user_detail'),
]
