from django.shortcuts import render
from .models import Document
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from .models import Document

@login_required
def document_list(request):
    sort = request.GET.get("sort", "desc")  # default: descending (newest first)

    docs = Document.objects.all()
    if sort == "asc":
        docs = docs.order_by("uploaded_at")     # oldest → newest
    else:
        docs = docs.order_by("-uploaded_at")    # newest → oldest

    year = request.GET.get("year")
    month = request.GET.get("month")

    if year:
        docs = docs.filter(uploaded_at__year=year)
    if month:
        docs = docs.filter(uploaded_at__month=month)

    years = Document.objects.dates("uploaded_at", "year", order="DESC")
    months = [
        ("01", "January"), ("02", "February"), ("03", "March"),
        ("04", "April"), ("05", "May"), ("06", "June"),
        ("07", "July"), ("08", "August"), ("09", "September"),
        ("10", "October"), ("11", "November"), ("12", "December"),
    ]

    return render(request, "records/document_list.html", {
        "docs": docs,
        "years": years,
        "months": months,
        "selected_year": year,
        "selected_month": month,
        "selected_sort": sort,
    })



def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")  # after signup, go to login
    else:
        form = UserCreationForm()
    return render(request, "records/signup.html", {"form": form})
