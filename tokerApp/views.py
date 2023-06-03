from typing import Any
from django import http
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Toker
from django.views import View
from configparser import ConfigParser
from django.http import HttpResponse, HttpResponseForbidden
from functools import wraps
from django.urls import reverse
from django.utils.decorators import method_decorator


import json
import os
import time
import subprocess

# Create your views here.
# def index(request):
#     return render(request, 'web_UI/index.html')

# 实现装饰器，用于视图保护功能
def login_required_decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("registration/login.html"))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
    

class My_Server(View):
    
    def __init__(self) -> None:
        Toker.target_path = "./tokerApp/Sensorhub_Test"
        Toker.ini_path = "./tokerApp/SH_info.ini"
        Toker.host = '0.0.0.0'
        Toker.port = 29799
        self.config = ConfigParser()
        print("Server start running@: {0}:{1}".format(Toker.host, Toker.port))

    @method_decorator(login_required_decorator)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        return render(request, 'web_UI/index.html')
    
    def post(self, request):
        print("Get POST requst...")
        
        Toker.res = {'result': 'HTTP SERVER OK'}
        
        # datas = request.META.get('HTTP_CONTENT_LENGTH', 'Unknown')
        datas = request.body        
        # print(request.data.decode('uft-8'))
        client_addr = request.META.get('REMOTE_ADDR')
        # print('headers:', request.META)
        print("post:", request.path, client_addr)
        print(datas)
      
        print(json.loads(datas.decode('utf-8'))['SN'])

        self.set_target_ini_item('SH', 'sh_sn', '"'+json.loads(datas.decode('utf-8'))['SN']+'"')
        self.set_target_ini_item('SH', 'test_type', '"'+json.loads(datas.decode('utf-8'))['TestType']+'"')
                
        cmd = "python3 ./tokerApp/Sensorhub_Test/scripts/main.py"
        cmd_res = subprocess.run(cmd.split())
        time.sleep(1)

        while(self.get_target_ini_item("SH", 'running_status') == 'True'):
            print("target running")
            time.sleep(1)

        response = HttpResponse('Return POST request')
        response['Content-type'] = 'application/json'        
        response['Access-Control-Allow-Origin'] = '*'        
        
        print(self.get_target_ini_item("SH", 'testresult'))
        Toker.res = {'testresult:': self.get_target_ini_item("SH", 'testresult')}
        
        response.content = json.dumps(Toker.res).encode()
        return response
    
    def set_target_ini_item(self, session, item, value):
        self.config.read(Toker.ini_path, encoding="utf-8")
        self.config.set(session, item, value)
        self.config.write(open(Toker.ini_path, "w", encoding="utf-8"))
        print("ini set OK")
        
    
    def get_target_ini_item(self, session, item):
        self.config.read(Toker.ini_path, encoding="utf-8")
        _ = self.config.get(session, item)
        return _
    
        
    
    # allowed_referers = ["/root/xhd/web_toker_django/templates/registration/login.html"]

    # def dispatch(self, request, *args, **kwargs):
    #     referer = request.META.get("HTTP_REFERER")
    #     if referer is not None:
    #         for allowed_referer in self.allowed_referers:
    #             if allowed_referer in referer:
    #                 return super().dispatch(request, *args, **kwargs)

    #     return HttpResponseForbidden("Access denied")

