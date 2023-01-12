from django.shortcuts import render

  
def index(request):
    # validate user data exists before accepting else -> redirect index
    return render(request, 'index.html')


