from datetime import datetime
from urllib import request

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
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


from django.shortcuts import render, get_object_or_404, redirect
from .models import User, ChatRoom, Message


def chat_room_list(request):
  # セッションからログインしているユーザーのnicknameを取得
  user1_nickname = request.session.get('nickname')

  # nicknameに基づいてUserオブジェクトを取得
  user1 = get_object_or_404(User, nickname=user1_nickname)

  # 過去にチャットしたチャットルームを検索（user1がuser2側にいる場合も考慮）
  past_chat_rooms = ChatRoom.objects.filter(user1=user1) | ChatRoom.objects.filter(user2=user1)

  past_users = []

  # 過去にチャットしたユーザーとそのチャットルームIDをリストに追加
  for chatroom in past_chat_rooms:
    # user1以外のユーザー（user2）を取得
    other_user = chatroom.user2 if chatroom.user1 == user1 else chatroom.user1
    past_users.append({
      'nickname': other_user.nickname,
      'chatroom_id': chatroom.id  # チャットルームIDを追加
    })

  # 結果を渡してチャットルーム画面を表示
  return render(request, 'past_chatroom_list.html', {
    'past_users': past_users
  })


def chat_room_check(request):
    user1_nickname = request.session.get('nickname')
    user2_nickname = request.GET.get('register')

    # ユーザーオブジェクトを取得
    user1 = User.objects.filter(nickname=user1_nickname).first()
    user2 = User.objects.filter(nickname=user2_nickname).first()

    if user1 and user2:
      # すでにチャットルームが存在するか検索
      chat_room = ChatRoom.objects.filter(user1=user1, user2=user2).first()
      if chat_room:
        return JsonResponse({'chatRoomId': chat_room.id})
      else:
        return JsonResponse({'chatRoomId': None})
    return JsonResponse({'chatRoomId': None})


def chat_room_create(request):
  # クエリパラメータからユーザー1とユーザー2を取得
  user1_nickname = request.session.get('nickname')
  user2_nickname = request.GET.get('register')

  if not user1_nickname or not user2_nickname:
    # 必要なパラメータが不足している場合、エラーメッセージを表示
    return HttpResponse("ユーザー情報が不足しています。", status=400)

  # チャットルームが既に存在するか確認
  existing_chat_room = ChatRoom.objects.filter(user1__nickname=user1_nickname, user2__nickname=user2_nickname).first()

  if existing_chat_room:
    # 既存のチャットルームが見つかった場合
    return redirect('chat-room', chat_room_id=existing_chat_room.id)
  else:
    # 新しいチャットルームを作成
    user1 = User.objects.get(nickname=user1_nickname)
    user2 = User.objects.get(nickname=user2_nickname)

    new_chat_room = ChatRoom.objects.create(user1=user1, user2=user2)

    # 新しいチャットルームの詳細ページにリダイレクト
    return redirect('chat-room', chat_room_id=new_chat_room.id)


def chat_room(request, chat_room_id):
  # チャットルームを取得
  chatroom = get_object_or_404(ChatRoom, id=chat_room_id)

  # 現在ログインしているユーザーを取得
  user = request.session.get('nickname')
  user1 = get_object_or_404(User, nickname=user)

  # チャットルーム内で他のユーザーをユーザー2として設定
  # (ユーザー1以外のユーザーがユーザー2に設定される想定)
  user2 = chatroom.user1 if chatroom.user2 == user1 else chatroom.user2

  # チャットルームのメッセージを取得
  messages = chatroom.messages.all().order_by('timestamp')

  return render(request, 'chatroom.html', {
    'chatroom': chatroom,
    'messages': messages,
    'user1': user1,
    'user2': user2,
  })


def send_message(request, chatroom_id):
  chatroom = get_object_or_404(ChatRoom, id=chatroom_id)
  sender_nickname = request.session.get('nickname')
  sender = User.objects.get(nickname=sender_nickname)

  # POSTリクエストが送信された場合
  if request.method == 'POST':
    text = request.POST.get('text')  # フォームから送信されたテキスト

    if text:
      # メッセージをデータベースに保存
      Message.objects.create(
        chatroom=chatroom,
        sender=sender,
        text=text
      )

      # メッセージ送信後、適切なチャットルームにリダイレクト
      # チャットルーム内のユーザーに基づきリダイレクト先を決定
      recipient_nickname = chatroom.user2.nickname if chatroom.user1 == request.user else chatroom.user1.nickname
      return redirect('chat-room', chat_room_id=chatroom.id)  # チャットルームにリダイレクト

  # GETリクエストの場合（直接ページにアクセスした場合）はフォームを表示
  return render(request, 'chatroom.html', {
    'chatroom': chatroom,
    'messages': chatroom.messages.all().order_by('timestamp'),  # チャットメッセージを順番に表示
  })


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

  return render(request, 'lostitem_register_complete.html')
