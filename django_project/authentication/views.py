from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render, redirect

from .decorators import unauthenticated_user  



@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is not correct')
        
    context = {}
    return render(request, 'registration/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('loginPage')



# # activate user account
# def activate(request, uidb64, token):
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         login(request, user)
#         return redirect('setpasswordfirst')
#     else:
#         return HttpResponse('Activation link is invalid!')



# def setpasswordfirst(request):
#     form = UpdatePasswordForm(request)
#     if request.method == 'POST':
#         form = UpdatePasswordForm(data=request.POST, user=request.user)
        
#         if form.is_valid():
#             user = form.save()
#             user.save()
#             return redirect('newloginPage')


#     context = {'form':form}
#     return render(request, 'registration/change_password_first.html', context)



# def firstLogin(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect('home')
#         else:
#             messages.info(request, 'Username or password is not correct')
        

#     context = {}
#     return render(request, 'registration/first_login.html', context)



# def register(request):
#     form = CreateUserForm()
    
#     if request.method == 'POST':
#         form = CreateUserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.save()
            
#             group = request.user.groups.values_list('name', flat=True).first()
#             root_group = Group.objects.get(name=group)
#             user_group = Group.objects.get(name='students')
#             user.groups.add(root_group)
#             user.groups.add(user_group)
#             user = form.cleaned_data.get('username')
#             messages.success(request, 'Account was created for ' + user)
            
#             return redirect('/')

#     context = {'form':form}
#     return render(request, 'registration/register.html', context)