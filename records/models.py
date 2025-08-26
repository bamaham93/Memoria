from django.db import models
from datetime import datetime




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to="pdfs/")
    uploaded_at = models.DateTimeField(default=datetime.now)


    def __str__(self):
        return self.title

    @property
    def short_description(self):
        """Return a truncated version of the description (for previews)."""
        if not self.description:
            return ""
        return (self.description[:75] + "…") if len(self.description) > 75 else self.description
