import json

from django.http import JsonResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.shortcuts import render, get_object_or_404

from password.models import Table
from password.backends.crypto import RsaCrypto
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


@login_required
def table(request):
    if request.method == 'GET':
        _lists = Table.objects.all().order_by('id')

        return render(request, 'password/table.html', {'lPage': _lists})

@login_required
def change_table(request):
    if request.method == 'GET':
        try:
            _data = get_object_or_404(Table, id=request.GET.get('id'))

            jsondata = model_to_dict(_data, exclude=['create_time', 'update_time'])
            return JsonResponse({'state': 1, 'message': jsondata})
        except Exception as e:
            return JsonResponse({'state': 0, 'message': 'Get Error: ' + str(e)})

    if request.method == 'POST':
        print(request.body.decode('utf-8'))

        postdata = {}
        for key, value in json.loads(request.body.decode('utf-8')).items():
            # 将接收到的json数据去掉csrf和password之后的数据存入字典postdata
            if key != 'csrfmiddlewaretoken' and key != 'password':
                postdata[key] = value if value != '' else None

            # 判断当key为password时且password有值时，对password进行加密
            if key == 'password' and value:
                _m = RsaCrypto().encrypt(value)
                if _m.get('state'):
                    # 如果加密成功将postdata字典中的password换成密文
                    postdata['password'] = _m.get('message')
                else:
                    # 如果加密失败直接返回错误信息，view结束
                    return JsonResponse({'state': 0, 'message': 'Error: ' + _m.get('message')})

        try:
            # 根据传入的ID判断是新建还是更新
            object, created = Table.objects.update_or_create(
                id=postdata.get('id'),
                defaults=postdata
            )

            if created:
                return JsonResponse({'state': 1, 'message': '创建成功!'})
            else:
                return JsonResponse({'state': 1, 'message': '更新成功!'})
        except Exception as e:
            return JsonResponse({'state': 0, 'message': 'Error: ' + str(e)})

@login_required
def delete_table(request):
    if request.method == 'POST':
        try:
            _t = Table.objects.filter(id=request.POST.get('id'))
            _t.delete()

            return JsonResponse({'state': 1, 'message': '删除成功!'})
        except Exception as e:
            return JsonResponse({'state': 0, 'message': 'Error: ' + str(e)})

@login_required
def decode_password(request):
    if request.method == 'GET':
        try:
            _t = get_object_or_404(Table, id=request.GET.get('id'))

            _m = RsaCrypto().decrypt(_t.password)
            if _m.get('state'):
                return JsonResponse({'state': 1, 'message': _m.get('message'),
                                     'host': '%s:%d' % (_t.host, _t.port),
                                     'username': _t.username
                                     })
            else:
                return JsonResponse({'state': 0, 'message': 'Error: ' + _m.get('message')})
        except Exception as e:
            return JsonResponse({'state': 0, 'message': 'Error: ' + str(e)})

def mylogin(request):
    name = request.POST.get('name')
    password = request.POST.get('password')
    # 验证用户名和密码，验证通过的话，返回user对象
    user = auth.authenticate(username=name, password=password)
    if user:
        # 验证成功 登陆
        auth.login(request, user)
        return HttpResponseRedirect('/password/table/')
        # return render(request, 'password/table.html', {'lPage': _lists})
    else:
        return render(request, 'login.html' ,{'message': '登录失败'})


from django.http import response,HttpResponse
def myregist(request):
        name = request.POST.get('name')
        password = request.POST.get('password')
        email=request.POST.get('email')
        # 此处的User 是 django 自带的model
        try:
            User.objects.create_user(username=name, password=password,email=email)

            # msg = '注册成功!请登录'
            return render(request,'login.html',{'message': '注册成功!请登录'})
        except:

            # msg =  '注册失败!请重新注册!'
            # return JsonResponse(msg)
            return render(request,'login.html',{ 'message': '注册失败!请重新注册!'})


def mylogout(request):

    if request.method == 'GET':
        auth.logout(request)
