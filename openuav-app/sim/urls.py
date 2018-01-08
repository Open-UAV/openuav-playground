from django.urls import path

from . import views

urlpatterns = [
	path('console/', views.console, name='console'),
	path('unsecure_console/', views.unsecure_console, name='unsecure_console'),
    	path('', views.index, name='index'),
]
