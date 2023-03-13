from django.urls import path

from . import views

urlpatterns = [
    path("listings/", views.AuctionsListView.as_view(), name="index"),
    path(
        "listings/<int:pk>/", views.AuctionsDetailView.as_view(), name="listing_detail"
    ),
    path("create/", views.AuctionsCreateView.as_view(), name="create"),
    path("watchlisting/", views.WatchlistListView.as_view(), name="watchlisting"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/register/", views.register, name="register"),
    path("watchlist/<int:pk>/", views.watchlist_add, name="watchlist_add"),
    path("remove/<int:pk>/", views.watchlist_remove, name="watchlist_remove"),
    path("close/<int:pk>/", views.bidding_close, name="bidding_close"),
    path("bidding/<int:pk>/", views.bidding, name="bidding"),
    path("categories/", views.category, name="categories"),
]
