from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from modelCore.models import User
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def Login(request):
    phone = request.POST.get('phone')
    password = request.POST.get('password')
    if User.objects.filter(phone=phone,password=password):
        result = 'login'
        return JsonResponse({'phone':phone,'result':result})
    else:
        result = 'not allowed'
        return JsonResponse({'result':result})

