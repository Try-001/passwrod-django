from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def TestApp(request):
    if request.method == 'GET':
        data=[1,2,23,4,5,6,7,8]
        return render(request, 'testapp.html', {'lPage': data})


@login_required
def TestApp2(request):
    if request.method == 'GET':
        return HttpResponse({
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })


@login_required
def videotest(request):
    if request.method=='GET':
        return render(request,'video-test.html')
