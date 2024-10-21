from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('map/', views.map, name='map'),
  path('search/', views.search, name='search'),
  path('register/', views.register, name='register'),
  path('chat/', views.chat, name='chat'),
  path('notice/', views.notice, name='notice'),
  path('route/', views.route, name='route'),

]
