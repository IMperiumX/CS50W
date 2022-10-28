from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_UPDATE, LifecycleModel, hook
from model_utils import Choices, FieldTracker
from model_utils.fields import StatusField
from simple_history.models import HistoricalRecords


class Language(models.Model):
    """Language Model for article."""

    language_code = models.CharField(_("Lnaguage code"), max_length=8)
    language_name = models.CharField(_("Language name"), max_length=64)

    class Meta:
        """Meta definition for Language."""

        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def __str__(self):
        """Unicode representation of Language."""
        return f"{self.language_code - self.c}"


class Article(LifecycleModel):
    default_language = models.ForeignKey(Language, on_delete=models.CASCADE)
    article_title = models.CharField(_("Article title"), max_length=255)
    article_text = models.TextField(_("Article text"))
    article_url = models.URLField(_("Article Url"), max_length=200)
    time_created = models.DateTimeField(_("Time article created"), auto_now_add=True)
    time_updated = models.DateTimeField(_("Time Article updated"), auto_now=True)
    time_published = models.DateTimeField(_("Time article piblished"))

    # model utils related fields
    tracker = FieldTracker()
    history = HistoricalRecords()
    
    @hook(AFTER_UPDATE, when="status", was="draft", is_now="published")
    def on_publish(self):
        send_mail(object="An article has published!",
                    message="An article has been published",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_RECIPIENT_EMAILS,])
    class Meta:
        """Meta definition for Article."""

        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        """Unicode representation of Article."""
        return self.article_title


class RelatedArticle(models.Model):
    """Model definition for RelatedArticle."""

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="related"
    )
    related_article_id = models.IntegerField(_("Related article id"))

    
    class Meta:
        """Meta definition for RelatedArticle."""

        verbose_name = "RelatedArticle"
        verbose_name_plural = "RelatedArticles"

    def __str__(self):
        """Unicode representation of RelatedArticle."""
        return f"{self.article} - {self.related_article_id}"


class Category(models.Model):
    """Model definition for Category."""

    category_name = models.CharField(_("Category name"), max_length=128)

    class Meta:
        """Meta definition for Category."""

        verbose_name = "Category"
        verbose_name_plural = "Categorys"

    def __str__(self):
        """Unicode representation of Category."""
        return self.category_name


class SubCategory(models.Model):
    """Model definition for SubCategory."""

    subcategory_name = models.CharField(_("SubCategory name"), max_length=128)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="sub_category"
    )

    class Meta:
        """Meta definition for SubCategory."""

        verbose_name = "SubCategory"
        verbose_name_plural = "SubCategorys"

    def __str__(self):
        """Unicode representation of SubCategory."""
        return


class AssociateSubCategory(models.Model):
    """Model definition for AssociateSubCategory."""

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="associate_sub_category"
    )
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    class Meta:
        """Meta definition for AssociateSubCategory."""

        verbose_name = "AssociateSubCategory"
        verbose_name_plural = "AssociateSubCategorys"

    def __str__(self):
        """Unicode representation of AssociateSubCategory."""
        pass


class Tag(models.Model):
    """Model definition for Tag."""

    tag_name = models.CharField(_("Tag name"), max_length=32)

    class Meta:
        """Meta definition for Tag."""

        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        """Unicode representation of Tag."""
        return self.tag_name


class AssociateTag(models.Model):
    """Model definition for AssociateTag."""

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        """Meta definition for AssociateTag."""

        verbose_name = "AssociateTag"
        verbose_name_plural = "AssociateTags"

    def __str__(self):
        """Unicode representation of AssociateTag."""


class Author(AbstractUser):
    """Model definition for Author."""

    # Ensures that creating new users through proxy models works
    karma = models.PositiveIntegerField(verbose_name="karma", default=0, blank=True)

    class Meta:
        """Meta definition for Author."""

        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        """Unicode representation of Author."""
        return f"{self.username}"


class RelatedAuthor(models.Model):
    """Model definition for RelatedAuthor."""

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        """Meta definition for RelatedAuthor."""

        verbose_name = "RelatedAuthor"
        verbose_name_plural = "RelatedAuthors"

    def __str__(self):
        """Unicode representation of RelatedAuthor."""
        return f"{self.article} - {self.author}"


class ModificationType(models.Model):
    """Model definition for ModificationType."""


    STATUS = Choices('draft', 'published', 'deleted')
    status =StatusField()
    tracker = FieldTracker()
    
    # ANOTHER_CHOICES = Choices('draft', 'unmodifed')
    # untype = StatusField(choices_name='ANOTHER_CHOICES')
    
    class Meta: 
        """Meta definition for ModificationType."""

        verbose_name = "ModificationType"
        verbose_name_plural = "ModificationTypes"

    def __str__(self):
        """Unicode representation of ModificationType."""
        pass


class Modification(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    modification_type = models.ForeignKey(ModificationType, on_delete=models.CASCADE)
    time_modified = models.DateTimeField(
        _("date the article modified by author"), auto_now=True
    )
    tracker = FieldTracker()
    history = HistoricalRecords()
    
    # TODO: article_translation (FK) => ArticleTranslation
    
    class Meta:
        """Meta definition for Modification."""

        verbose_name = "Modification"
        verbose_name_plural = "Modifications"

    def __str__(self):
        """Unicode representation of Modification."""
        return f"{self.article}, Modified at: {self.time_modified} by {self.author}"
