"""webpanel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from .views import index, create_dashboard, dashboard_details, delete_dashboard, rename_dashboard,\
    create_chart, edit_chart, delete_chart

urlpatterns = [
    path('', index, name='main'),
    path('create/', create_dashboard, name='create'),
    path('details/', dashboard_details, name='details'),
    path('delete/', delete_dashboard, name='delete'),
    path('rename/', rename_dashboard, name='rename'),
    path('create-chart/', create_chart, name='create_chart'),
    path('edit-chart/', edit_chart, name='edit_chart'),
    path('delete-chart/', delete_chart, name='delete_chart'),
]
