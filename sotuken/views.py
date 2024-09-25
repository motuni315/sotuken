from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
  return render(request, 'index.html')


def map(request):
  return render(request, 'map.html')

def search(request):
  if request.method == 'GET':
    search_condition = request.GET.get['search-condition']
    if search_condition == "場所":
      search = request.GET.get('search')
    return render(request,'map.html',{'search':search})
