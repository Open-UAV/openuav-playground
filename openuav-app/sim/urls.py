from django.urls import path

from . import views

urlpatterns = [
	path('console/', views.console, name='console'),
	path('console1/', views.console1, name='console1'),
	path('console2/', views.console2, name='console2'),
	path('unsecure_console/', views.unsecure_console, name='unsecure_console'),
	path('unsecure_console1/', views.unsecure_console1, name='unsecure_console1'),
	path('unsecure_console2/', views.unsecure_console2, name='unsecure_console2'),
    path('', views.index, name='index'),
]
