from django.shortcuts import render
from .models import Document

def document_list(request):
    docs = Document.objects.all().order_by("-uploaded_at")
    return render(request, "document_list.html", {"docs": docs})
