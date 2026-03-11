from django.db import models
from django.contrib.auth.models import User
import uuid

class Order(models.Model):
    """Модель заказа пользователя"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает отправки'),
        ('accepted', 'Принят СДЭК'),
        ('pickup', 'Готов к выдаче'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    
    # Основная информация
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Номер заказа")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    client_email = models.EmailField(verbose_name="Email клиента")
    client_phone = models.CharField(max_length=20, verbose_name="Телефон клиента")
    
    # Данные для СДЭК
    cdek_order_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="ID заказа в СДЭК")
    cdek_track_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Трек-номер СДЭК")
    
    # Статусы
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    cdek_status = models.CharField(max_length=50, null=True, blank=True, verbose_name="Статус от СДЭК")
    cdek_status_code = models.IntegerField(null=True, blank=True, verbose_name="Код статуса СДЭК")
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    last_cdek_check = models.DateTimeField(null=True, blank=True, verbose_name="Последняя проверка СДЭК")
    
    # Детали заказа
    items = models.JSONField(default=dict, verbose_name="Товары")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма заказа")
    
    # Уникальный UUID для публичного доступа (без авторизации)
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ {self.order_number} - {self.get_status_display()}"

class TrackingHistory(models.Model):
    """История изменения статусов (логирование)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=50, verbose_name="Статус")
    status_code = models.IntegerField(null=True, blank=True, verbose_name="Код статуса")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="Город")
    date = models.DateTimeField(verbose_name="Дата события")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "История статуса"
        verbose_name_plural = "История статусов"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status} - {self.date}"
