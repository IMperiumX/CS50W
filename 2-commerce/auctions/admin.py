# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import User, Auctions, Watchlist, Bid, Comment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "password",
        "last_login",
        "is_superuser",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
    )
    raw_id_fields = ("groups", "user_permissions")


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Auctions)
class AuctionsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "category",
        "title",
        "description",
        "starting_bid",
        "image",
        "sold",
        "date_added",
    )
    list_filter = ("sold", "date_added")
    raw_id_fields = ("user",)
    inlines = [CommentInline]


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    raw_id_fields = ("user",)


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "auction", "user", "new_bid")
    raw_id_fields = ("auction", "user")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "post",
        "name",
        "email",
        "body",
        "created_on",
        "active",
    )
    list_filter = ("created_on", "active")
    search_fields = ("name", "email", "body")
    raw_id_fields = ("post",)
    actions = ["approve_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
