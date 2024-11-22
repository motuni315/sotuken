from datetime import datetime
from urllib import request

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import LostItem


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


def register(request):
  return render(request, 'register.html')


def chat(request):
  return render(request, 'chat.html')


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

