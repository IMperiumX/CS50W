from django.contrib import admin
from .models import Auctions, Watchlist, Bid, Comment

# Register your models here.

admin.site.register(Auctions)
admin.site.register(Watchlist)
admin.site.register(Bid)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
