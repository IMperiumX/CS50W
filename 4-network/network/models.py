from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.urls import reverse

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(default='default.png', upload_to='users/%Y/%m/%d/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'

    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.id)])


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (('draft', 'Draft'), ('published', 'Published'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='twitter_posts',
        null=True,
    )
    body = models.TextField(max_length=280, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    publish = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    objects = models.Manager()  # The default manager.
    published = PublishedManager()  # Our custom manager.
    users_like = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='liked_user', blank=True
    )
    total_likes = models.PositiveIntegerField(db_index=True, default=0)

    def __str__(self):
        return self.body[:50] + '...'

    class Meta:
        ordering = ('-publish',)

    def get_absolute_url(self):  # new
        return reverse('post_detail', args=[str(self.id)])


class Contact(models.Model):
    '''Intermediary Model >> for not altering User model form django
    and get the time The Realationship was Created
    '''

    user_from = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='rel_from_set', on_delete=models.CASCADE
    )
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='rel_to_set', on_delete=models.CASCADE
    )
    created = models.DateTimeField(
        auto_now_add=True, db_index=True
    )  # Using "db_index" >> improve query performance when ordering QuerySets by this field.

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


# Add following field to User dynamically
user_model = get_user_model()
user_model.add_to_class(
    'following',
    models.ManyToManyField(
        'self', through=Contact, related_name='followers', symmetrical=False
    ),
)
