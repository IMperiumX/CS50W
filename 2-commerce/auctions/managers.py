from django.db import models
from django.db.models import Q, Prefetch, OuterRef, Subquery, Value


class AuctionsQuerySet(models.QuerySet):
    def filter_active_auctions(self):
        return self.filter(sold=False)

    def filter_active_comments(self):
        return self.filter(Q(comments__active=True))

    def annotate_comments_count(self):
        return self.annotate(comments_count=models.Count("comments"))

    def annotate_auctions_comments(self):
        from .models import Comment

        return self.prefetch_related(
            Prefetch(
                "comments",
                queryset=Comment.objects.select_related(
                    "post"
                ).filter_active_comments(),
                to_attr="auctions_comments",
            )
        ).select_related("user")
        # return self.annotate(
        #     auctions_comments=Subquery(
        #         Comment.objects.filter(post=OuterRef("pk"), active=Value(True))[
        #             :1
        #         ].values_list("body", flat=True),
        #         output_field=models.CharField(),
        #     )
        # )


class AuctionsManager(models.Manager.from_queryset(AuctionsQuerySet)):
    pass


class CommentQuerySet(models.QuerySet):
    def filter_active_comments(self):
        return self.filter(active=True)


class CommentManager(models.Manager.from_queryset(CommentQuerySet)):
    pass


class WatchlistQuerySet(models.QuerySet):
    def annotate_auctions(self):
        from .models import Auctions

        return self.prefetch_related(
            Prefetch(
                "item",
                queryset=Auctions.objects.select_related("user"),
                to_attr="watchlist_auctions",
            )
        ).select_related("user")


class WatchlistManager(models.Manager.from_queryset(WatchlistQuerySet)):
    pass
