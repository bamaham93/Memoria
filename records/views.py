from django.shortcuts import render
from .models import Document
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def document_list(request):
    docs = Document.objects.all().order_by("-uploaded_at")
    return render(request, "records/document_list.html", {"docs": docs})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")  # after signup, go to login
    else:
        form = UserCreationForm()
    return render(request, "records/signup.html", {"form": form})
