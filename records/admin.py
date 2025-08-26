from django.contrib import admin
from .models import Document, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "uploaded_at", "short_description")
    list_filter = ("category", "uploaded_at")
    search_fields = ("title", "description")
