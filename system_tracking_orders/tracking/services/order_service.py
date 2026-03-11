from ..models import Order, TrackingHistory
from .cdek_parser import CdekParser
from django.utils import timezone
import datetime

class OrderService:
    """Сервис для работы с заказами"""
    
    def __init__(self):
        self.parser = CdekParser()
    
    def update_order_status(self, order):
        """Обновление статуса заказа по трек-номеру"""
        if not order.cdek_track_number:
            return False, "Нет трек-номера"
        
        # Получаем информацию от парсера
        tracking_info = self.parser.get_tracking_info(order.cdek_track_number)
        
        if not tracking_info:
            return False, "Не удалось получить информацию"
        
        # Сохраняем текущий статус в историю
        history = TrackingHistory.objects.create(
            order=order,
            status=tracking_info.get('status', 'Unknown'),
            description=tracking_info.get('note', ''),
            date=timezone.now()
        )
        
        # Обновляем основной статус заказа
        old_status = order.cdek_status
        order.cdek_status = tracking_info.get('status')
        order.last_cdek_check = timezone.now()
        
        # Маппинг статусов (можно расширить)
        status_text = tracking_info.get('status', '').lower()
        if 'доставлен' in status_text:
            order.status = 'delivered'
        elif 'выдач' in status_text or 'готов' in status_text:
            order.status = 'pickup'
        elif 'принят' in status_text or 'в пути' in status_text:
            order.status = 'accepted'
        
        order.save()
        
        # Сохраняем детальную историю, если есть
        for detail in tracking_info.get('details', []):
            if 'date' in detail and 'status' in detail:
                TrackingHistory.objects.create(
                    order=order,
                    status=detail.get('status'),
                    city=detail.get('city'),
                    description=detail.get('description'),
                    date=detail.get('date') or timezone.now()
                )
        
        return True, f"Статус обновлён: {tracking_info.get('status')}"
    
    def update_all_orders(self):
        """Обновление статусов всех активных заказов"""
        active_orders = Order.objects.exclude(
            status__in=['delivered', 'cancelled']
        ).exclude(
            cdek_track_number__isnull=True
        ).exclude(
            cdek_track_number=''
        )
        
        results = []
        for order in active_orders:
            try:
                success, message = self.update_order_status(order)
                results.append({
                    'order': order.order_number,
                    'track': order.cdek_track_number,
                    'success': success,
                    'message': message
                })
            except Exception as e:
                results.append({
                    'order': order.order_number,
                    'track': order.cdek_track_number,
                    'success': False,
                    'message': str(e)
                })
        
        return results
    
    def track_by_number(self, track_number):
        """Отслеживание по трек-номеру (для публичного доступа)"""
        try:
            order = Order.objects.get(cdek_track_number=track_number)
            # Обновляем статус
            self.update_order_status(order)
            
            # Возвращаем информацию для отображения
            return {
                'order_number': order.order_number,
                'track_number': order.cdek_track_number,
                'status': order.get_status_display(),
                'cdek_status': order.cdek_status,
                'history': [
                    {
                        'status': h.status,
                        'date': h.date.strftime('%d.%m.%Y %H:%M') if h.date else '',
                        'city': h.city,
                        'description': h.description
                    }
                    for h in order.history.all().order_by('-date')[:20]
                ]
            }
        except Order.DoesNotExist:
            # Если заказа нет в базе, всё равно пытаемся получить статус
            tracking_info = self.parser.get_tracking_info(track_number)
            if tracking_info:
                return {
                    'track_number': track_number,
                    'status': 'Не отслеживается в системе',
                    'cdek_status': tracking_info.get('status'),
                    'history': tracking_info.get('details', [])
                }
            return None
