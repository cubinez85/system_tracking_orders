from django.shortcuts import render
from django.http import JsonResponse
from .services.simple_tracker import SimpleTracker

def track_order(request):
    """Страница отслеживания заказа"""
    track_number = request.GET.get('track', '')
    tracking_info = None
    
    if track_number:
        tracker = SimpleTracker()
        tracking_info = tracker.track(track_number)
    
    return render(request, 'tracking/track.html', {
        'track_number': track_number,
        'info': tracking_info
    })

def api_track(request):
    """API endpoint для отслеживания"""
    if request.method == 'GET':
        track_number = request.GET.get('track')
        if not track_number:
            return JsonResponse({'error': 'Укажите track_number'}, status=400)
        
        tracker = SimpleTracker()
        result = tracker.track(track_number)
        
        return JsonResponse(result)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def test(request):
    from django.http import HttpResponse
    return HttpResponse("✅ Тестовый view работает!")

from django.urls import get_resolver
import json

def debug_urls(request):
    """Показать все зарегистрированные URL маршруты"""
    resolver = get_resolver()
    urls = []
    for pattern in resolver.url_patterns:
        urls.append(str(pattern.pattern))
    return JsonResponse({
        'urls': urls,
        'total': len(urls)
    })
