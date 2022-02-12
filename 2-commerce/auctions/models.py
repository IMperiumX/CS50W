from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from django.db import models


class User(AbstractUser):
    pass


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(sold=False)


class Auctions(models.Model):
    CATEGORY_CHOICES = (
        ('electronics', 'Electronics'),
        ('beauty', 'Beauty'),
        ('art', 'Art'),
        ('baby', 'Baby'),
        ('books', 'Books'),
        ('business', 'Business'),
        ('industrial', 'Industrial'),
        ('cameras', 'Cameras'),
        ('cell', 'Cell'),
        ('phones', 'Phones'),
        ('accessories', 'Accessories'),
        ('clothing,', 'Clothing,'),
        ('shoes', 'Shoes'),
        ('coins', 'Coins'),
        ('collectibles', 'Collectibles'),
        ('computers,tablets', 'Computers,Tablets'),
        ('consumer', 'Consumer'),
        ('electronics', 'Electronics'),
        ('crafts', 'Crafts'),
        ('dolls', 'Dolls'),
        ('dvds', 'DVDs'),
        ('motors', 'Motors'),
        ('entertainment', 'Entertainment'),
        ('memorabilia', 'Memorabilia'),
        ('gift', 'Gift'),
        ('cards', 'Cards'),
        ('health', 'Health'),
        ('jewelry', 'Jewelry'),
        ('music', 'Music'),
        ('pet', 'Pet'),
        ('supplies', 'Supplies'),
        ('pottery', 'Pottery'),
        ('real', 'Real'),
        ('estate', 'Estate'),
        ('specialty', 'Specialty'),
        ('services', 'Services'),
        ('sporting', 'Sporting'),
        ('goods', 'Goods'),
        ('sports', 'Sports'),
        ('mem', 'Mem'),
        ('stamps', 'Stamps'),
        ('tickets', 'Tickets'),
        ('toys', 'Toys'),
        ('travel', 'Travel'),
        ('video', 'Video'),
        ('games', 'Games'),
        ('antiques', 'Antiques'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_auctions'
    )
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.IntegerField(default=0)
    image = models.URLField(null=True)
    sold = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()  # The default manager.
    active = PublishedManager()  # Our custom manager.

    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='electronics'
    )

    def __str__(self):
        return f"{self.title} posted by {self.user}"

    class Meta:
        ordering = ('-date_added',)

    def get_absolute_url(self):
        return reverse('index')


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ManyToManyField(Auctions)

    def __str__(self):
        return f"{self.user}'s WatchList"


class Bid(models.Model):
    auction = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    new_bid = models.IntegerField()


class Comment(models.Model):
    post = models.ForeignKey(
        Auctions, on_delete=models.CASCADE, related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)
