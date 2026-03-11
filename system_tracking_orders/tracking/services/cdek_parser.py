import requests
import json
from bs4 import BeautifulSoup

class CdekParser:
    """Парсер для отслеживания заказов СДЭК"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    # ----- МЕТОД 1: Парсинг сайта (работает без авторизации) -----
    def parse_website(self, track_number):
        """Парсинг публичной страницы отслеживания"""
        try:
            url = f"https://www.cdek.ru/ru/tracking?order_id={track_number}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Здесь логика парсинга HTML
                return {"status": "найден на сайте", "data": response.text[:200]}
        except:
            pass
        return None
    
    # ----- МЕТОД 2: Официальное API (требует авторизацию) -----
    def track_cdek_public(self, track_number):
        """
        Использование публичного API СДЭК
        ВНИМАНИЕ: API требует авторизации, возвращает 401 без токена
        """
        url = f"https://api.cdek.ru/v2/orders?cdek_number={track_number}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 401:
                print(f"API требует авторизации. Код: 401")
                return {"error": "Требуется авторизация API"}
        except Exception as e:
            print(f"Ошибка API: {e}")
        
        return None
    
    # ----- МЕТОД 3: Комбинированный поиск -----
    def get_tracking_info(self, track_number):
        """Пытается получить информацию всеми доступными способами"""
        
        # Сначала пробуем API (если вдруг заработает)
        api_result = self.track_cdek_public(track_number)
        if api_result and 'error' not in api_result:
            return api_result
        
        # Если API не работает, парсим сайт
        website_result = self.parse_website(track_number)
        if website_result:
            return website_result
        
        # Если ничего не помогло
        return {
            'track_number': track_number,
            'status': 'Информация временно недоступна',
            'note': 'Попробуйте проверить позже или на сайте cdek.ru'
        }
