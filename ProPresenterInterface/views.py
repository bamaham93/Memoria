from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def control(request):
    return render(request, "propresenter/control.html")
