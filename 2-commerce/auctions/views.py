from django.contrib.auth import authenticate, login, logout
from django.views.generic import CreateView, ListView, DetailView

from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from django.urls import reverse

from .models import User, Auctions, Watchlist, Bid
from .forms import CommentForm


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
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


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
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def watchlist_add(request, pk):
    item_to_save = get_object_or_404(Auctions, pk=pk)
    # Check if the item already exists in that user watchlist
    if Watchlist.objects.filter(user=request.user, item=pk).exists():
        messages.add_message(
            request, messages.ERROR, "You already have it in your watchlist."
        )
        return HttpResponseRedirect(reverse("watchlisting"))
    # Get the user watchlist or create it if it doesn't exists
    user_list, created = Watchlist.objects.get_or_create(user=request.user)
    # Add the item through the ManyToManyField (Watchlist => item)
    user_list.item.add(item_to_save)
    messages.add_message(
        request, messages.SUCCESS, "Successfully added to your watchlist"
    )
    return render(request, "auctions/watchlist.html")


@login_required
def watchlist_remove(request, pk):
    item_to_remove = get_object_or_404(Auctions, pk=pk)
    # Check if the item already exists in that user watchlist
    if Watchlist.objects.filter(user=request.user, item=pk).exists():
        user_list, created = Watchlist.objects.get_or_create(user=request.user)
        # remove the item through the ManyToManyField (Watchlist => item)
        user_list.item.remove(item_to_remove)
        messages.add_message(
            request, messages.SUCCESS, "Successfully removed from your watchlist"
        )

    return render(request, "auctions/watchlist.html")


@login_required
def watchlist_list(request):
    user_list = Watchlist.objects.get(user=request.user)
    auctions = user_list.item.all()
    return render(request, "auctions/watchlist.html", {"auctions": auctions})


class AuctionsCreateView(LoginRequiredMixin, CreateView):
    model = Auctions
    fields = ["title", "description", "starting_bid", "image", "category", "sold"]
    success_url = "/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AuctionsListingView(ListView):
    queryset = Auctions.active.all()


@login_required
def listing_detail(request, pk):
    template_name = "auctions/listing_detail.html"
    listing = get_object_or_404(Auctions, id=pk)
    comments = listing.comments.filter(active=True)
    new_comment = None
    exists = Watchlist.objects.filter(user=request.user, item=pk).exists()

    # Comment posted
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = listing
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(
        request,
        template_name,
        {
            "auctions": listing,
            "comments": comments,
            "new_comment": new_comment,
            "comment_form": comment_form,
            "exists": exists,
        },
    )


@login_required
def bidding(request, pk):
    auctions = get_object_or_404(Auctions, id=pk)
    if request.method == "POST":
        bid = request.POST["bid"]
        auctions.starting_bid = int(bid)
        auctions.save()
        messages.add_message(
            request,
            messages.SUCCESS,
            f"You have a Bid on {auctions.title} with ${bid}!",
        )
        Bid.objects.create(user=request.user, new_bid=bid, auction=auctions)

    return render(request, "auctions/listing_detail.html", {"auctions": auctions})


@login_required
def bidding_close(request, pk):
    auctions = get_object_or_404(Auctions, id=pk)
    price = auctions.starting_bid
    winner = Bid.objects.get(auction=auctions, new_bid=price).user
    auctions.sold = True
    auctions.save()
    if winner == request.user:
        messages.add_message(
            request,
            messages.SUCCESS,
            f"CONGRATS: You have WON the bid on {auctions.title} for"
            f" ${auctions.starting_bid}",
        )
    else:
        messages.add_message(
            request,
            messages.SUCCESS,
            f"{winner} have WON the bid on {auctions.title} for"
            f" ${auctions.starting_bid}",
        )

    return render(request, "auctions/close_bidding.html", {"auctions": auctions})

    return render(request, 'auctions/close_bidding.html', {'auctions': auctions})


def category(request):
    category = None
    auctions = None
    values = [c[0] for c in Auctions.CATEGORY_CHOICES]
    if request.method == "POST":
        category = request.POST["categories"]
        auctions = Auctions.objects.filter(category=category)

    return render(
        request,
        "auctions/categories.html",
        {"category": category, "auctions": auctions, "values": values},
    )
