from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse, HttpResponseRedirect


def index(request):
    if "next" in request.POST:
        return redirect("summary")

    return render(request, 'index.html')

  
def summary(request):
    # validate user data exists before accepting else -> redirect index
    return render(request, 'summary.html')