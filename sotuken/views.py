from datetime import datetime
from urllib import request

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import LostItem, User, ChatRoom, Message


# Create your views here.


def index(request):
  return render(request, 'index.html')


def map(request):
  return render(request, 'map.html')


def search(request):
  if request.method == 'GET':
    search_condition = request.GET.get('search-condition')
    if search_condition:
      if search_condition == "場所":
        search = request.GET.get('search')
    return render(request, 'map.html', {'search': search})


def chat(request):
  return render(request, 'map.html')


def route(request):
  return render(request, 'route.html')


def notice(request):
  return render(request, 'notice.html')


def search_items(request):
  try:
    # クエリパラメータの取得
    item_name = request.GET.get('item_name', '').strip()
    prefecture = request.GET.get('prefecture', '').strip()
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # 日時の比較
    if start_date and end_date:
      start_date_obj = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
      end_date_obj = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
      if end_date_obj < start_date_obj:
        return JsonResponse({'error': '日時が正しくありません'}, status=400)

    # 基本のフィルタリング
    items = LostItem.objects.all()
    if item_name:
      items = items.filter(product__icontains=item_name)
    if prefecture:
      items = items.filter(prefecture__icontains=prefecture)

    # 日時検索のフィルタリング
    if start_date:
      start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
      items = items.filter(date_time__gte=start_date)
    if end_date:
      end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
      items = items.filter(date_time__lte=end_date)

    # 結果のシリアライズ
    items_data = [
      {
        'id': item.id,
        'date_time': item.date_time.strftime('%Y-%m-%d %H:%M:%S'),
        'product': item.product,
        'image_url': item.image_url if item.image_url else None,
        'latitude': float(item.latitude),
        'longitude': float(item.longitude),
        'prefecture': item.prefecture,
      }
      for item in items
    ]

    return JsonResponse(items_data, safe=False)
  except Exception as e:
    # エラーログの出力
    print(f"Error in search_items: {e}")
    return JsonResponse({'error': str(e)}, status=500)


def item_detail(request, item_id):
  item = get_object_or_404(LostItem, id=item_id)
  return render(request, 'item_detail.html', {'item': item})


def login(request):
  if request.method == 'GET':
    return render(request, 'login.html')
  elif request.method == 'POST':
    email = request.POST.get('email')
    password = request.POST.get('password')
    try:
      if email and password:
        user = User.objects.get(email=email)
      else:
        return redirect('login')

        # パスワードをチェック
      if password == user.password:
        request.session['nickname'] = user.nickname
        request.session['email'] = user.email
        request.session['password'] = user.password
        return render(request, 'index.html')
      else:
        # パスワードが一致しない場合
        return render(request, 'login.html', {'error': 'メールアドレスかパスワードが違います'})
    except User.DoesNotExist:

      return render(request, 'login.html', {'error': 'メールアドレスかパスワードが違います'})


def User_register(request):
  if request.method == 'GET':
    return render(request, 'User_register.html')
  elif request.method == 'POST':
    nickname = request.POST.get('nickname')
    email = request.POST.get('email')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')

    if User.objects.filter(email=email).exists():
      return render(request, 'User_register.html', {'error': 'このメールアドレスはすでに登録されています'})
    if password1 == password2:
      context = {
        'nickname': nickname,
        'email': email,
        'password': password1
      }
      return render(request, 'User_register_confirm.html', context)
    else:
      return render(request, 'User_register.html', {'error': 'パスワードが異なります'})


def User_register_confirm(request):
  if request.method == 'POST':
    try:
      nickname = request.POST.get('nickname')
      email = request.POST.get('email')
      password = request.POST.get('password')

      if not nickname or not email or not password:
        return render(request, 'User_register_confirm.html', {'error': 'すべての項目を入力してください'})

      user = User.objects.create(
        nickname=nickname,
        email=email,
        password=password
      )
      user.save()
      return render(request, 'User_register_complete.html')
    except Exception as e:
      return render(request, 'User_register_confirm.html', {'error': f'登録中にエラーが発生しました: {str(e)}'})


def logout(request):
  # セッションから情報を削除
  request.session.flush()  # すべてのセッションデータを削除
  return redirect('index')  # ログインページにリダイレクト


@login_required
def chat_room(request, user_id):
  user2 = get_object_or_404(User, id=user_id)
  user1 = request.user

  # チャットルームが存在するか確認し、なければ作成
  chatroom, created = ChatRoom.objects.get_or_create(
    user1=min(user1, user2, key=lambda x: x.id),  # user1はidが小さい方
    user2=max(user1, user2, key=lambda x: x.id)  # user2はidが大きい方
  )

  messages = chatroom.messages.order_by('timestamp')
  return render(request, 'chatroom.html', {'chatroom': chatroom, 'messages': messages, 'user2': user2})


@login_required
def send_message(request, chatroom_id):
  if request.method == 'POST':
    chatroom = get_object_or_404(ChatRoom, id=chatroom_id)
    text = request.POST.get('text')

    if text:
      Message.objects.create(
        chatroom=chatroom,
        sender=request.user,
        text=text
      )
    return redirect('chat_room', user_id=chatroom.user2.id if chatroom.user1 == request.user else chatroom.user1.id)


def lostitem_register(request):
  if request.method == 'GET':
    return render(request, 'lostitem_register.html')
  elif request.method == 'POST':
    image = request.POST.get('image')
    image_url = request.POST.get('image_url')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    date_time = request.POST.get('date_time')
    prefecture = request.POST.get('prefecture')
    comment = request.POST.get('comment')
    product = request.POST.get('product')

    context = {
      'image': image,
      'image_url': image_url,
      'latitude': latitude,
      'longitude': longitude,
      'date_time': date_time,
      'prefecture': prefecture,
      'comment': comment,
      'product': product
    }

    return render(request, 'lostitem_register_confirm.html', context)


def lostitem_register_confirm(request):
  if request.method == 'POST':
    image = request.POST.get('image')
    image_url = request.POST.get('image_url')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    date_time = request.POST.get('date_time')
    prefecture = request.POST.get('prefecture')
    comment = request.POST.get('comment')
    product = request.POST.get('product')
    nickname = request.session.get('nickname')
    email = request.session.get('email')

    lostitem = LostItem.objects.create(
      image=image,
      image_url=image_url,
      latitude=latitude,
      longitude=longitude,
      date_time=date_time,
      prefecture=prefecture,
      comment=comment,
      product=product,
      nickname=nickname,
      email=email
    )
    lostitem.save()

  return render(request,'lostitem_register_complete.html')
