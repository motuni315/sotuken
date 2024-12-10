from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('map/', views.map, name='map'),
  path('search/', views.search, name='search'),
  path('notice/', views.notice, name='notice'),
  path('route/', views.route, name='route'),
  path('search_items/', views.search_items, name='search_items'),
  path('item/<int:item_id>/', views.item_detail, name='item_detail'),
  path('login/', views.login, name='login'),
  path('User_register/', views.User_register, name='User_register'),
  path('User_register_confirm/', views.User_register_confirm, name='User_register_confirm'),
  path('logout/', views.logout, name='logout'),
  path('chat_room_list/', views.chat_room_list, name='chat_room_list'),
  path('chat-room_check/', views.chat_room_check, name='chat_room_check'),
  path('chat-room_create/', views.chat_room_create, name='chat_room_create'),
  path('chat-room/<int:chat_room_id>/', views.chat_room, name='chat-room'),
  path('chat/send_message/<int:chatroom_id>/', views.send_message, name='send_message'),
  path('lostitem_register/', views.lostitem_register, name='lostitem_register'),
  path('lostitem_register_confirm/', views.lostitem_register_confirm, name='lostitem_register_confirm'),
  path('block_user/<str:user_nickname>/', views.block_user, name='block_user'),
  path('unblock_user/<str:user_nickname>/', views.unblock_user, name='unblock_user'),
]
