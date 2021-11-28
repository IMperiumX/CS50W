from django.urls import path

from . import views

urlpatterns = [
    path("", views.AuctionsListingView.as_view(), name="index"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/register/", views.register, name="register"),
    path("create/", views.AuctionsCreateView.as_view(), name='create'),
    path('watchlisting/', views.watchlist_list, name='watchlisting'),
    path('listings/<int:pk>/', views.listing_detail, name='listing_detail'),
    path("watchlist/<int:pk>/", views.watchlist_add, name="watchlist_add"),
    path("remove/<int:pk>/", views.watchlist_remove, name="watchlist_remove"),
    path('close/<int:pk>/', views.bidding_close, name='bidding_close'),
    path("bidding/<int:pk>/", views.bidding, name="bidding"),
    path("categories/", views.category, name="categories"),
]
