from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from modelCore.models import User

# Create your views here.
def Login(request):
    phone = request.POST.get('phone')
    password = request.POST.get('password')
    if User.objects.filter(phone=phone,password=password):
        result = 'login'
        return JsonResponse({'phone':phone,'result':result})
    else:
        result = 'not allowed'
        return JsonResponse({'result':result})

