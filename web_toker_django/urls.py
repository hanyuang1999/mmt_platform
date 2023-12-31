"""web_toker_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from tokerApp import views
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('my_view', views.My_Server.as_view(), name='my_view'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # path('login/', views.login, name='login'),
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('login', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', accounts_views.signup, name='signup'),
    path('logout/', auth_views.LoginView.as_view(), name='logout'),
    path('upload_folder/', views.upload_file, name='upload_folder'),
    path('records/', views.record_list, name='record_list'),
    path('records/add/', views.add_record, name='add_record')
    
]
