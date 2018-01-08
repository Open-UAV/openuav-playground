from django.urls import path

from . import views

urlpatterns = [
	path('console/', views.console, name='console'),
	path('adminconsole', views.adminconsole, name='adminconsole'),
    	path('', views.index, name='index'),
]
