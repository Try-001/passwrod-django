from password.views import *
from django.urls import path
from testapp.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('table/', table, name='table-url'),
    path('table/change/', change_table, name='change-table-url'),
    path('table/delete/', delete_table, name='delete-table-url'),
    path('table/decode/', decode_password, name='decode-password-url'),
    path('TestApp1', TestApp, name='TestApp1-usrl'),
    path('TestApp2', TestApp2, name='TestApp1-usr2'),
    path('videotest',videotest,name='videotest'),

]
