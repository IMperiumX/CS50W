from django.contrib.auth import authenticate, login, logout
from django.views.generic import CreateView, ListView, DetailView, FormView

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


class WatchlistListView(LoginRequiredMixin, ListView):
    model = Watchlist
    paginate_by = 10

    def get_queryset(self):
        return Watchlist.objects.select_related("user").filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["auctions"] = self.get_queryset()
        return context


class AuctionsCreateView(LoginRequiredMixin, CreateView):
    model = Auctions
    fields = ["title", "description", "starting_bid", "image", "category", "sold"]
    success_url = "/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AuctionsListView(ListView):
    model = Auctions
    paginate_by = 10

    def get_queryset(self):
        return Auctions.objects.filter_active_auctions()


class AuctionsDetailView(DetailView):
    model = Auctions

    def get_queryset(self):
        return Auctions.objects.annotate_auctions_comments()

    def get_context_data(self, **kwargs):
        print(self)
        context = super().get_context_data(**kwargs)
        context["comments"] = self.get_object().auctions_comments
        context["new_comment"] = None
        context["comment_form"] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = self.object
            new_comment.save()
            return self.get(request, *args, **kwargs)
        else:
            form = CommentForm()
        return render(request, self.get_template_names, {"form": form})


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


import pysnooper


@pysnooper.snoop()
def category(request):
    category = None
    auctions = None
    values = [c[0] for c in Auctions.CATEGORY_CHOICES]
    if request.method == "POST":
        from pprint import pprint

        pprint(request.POST.values())
        category = request.POST["categories"]
        auctions = Auctions.objects.filter(category=category)

    return render(
        request,
        "auctions/categories.html",
        {"category": category, "auctions": auctions, "values": values},
    )
