"""
Django Integration Example for v402 Protocol
This example demonstrates how to integrate v402 protocol with Django
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Custom user model with blockchain integration"""
    public_key = models.CharField(
        max_length=42,
        unique=True,
        validators=[RegexValidator(
            regex=r'^0x[a-fA-F0-9]{40}$',
            message='Invalid Ethereum address format'
        )],
        help_text="Ethereum public key address"
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'public_key'
    REQUIRED_FIELDS = ['username', 'email']

    class Meta:
        db_table = 'v402_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Product(models.Model):
    """Product model for content monetization"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USDC')
    content_url = models.URLField(max_length=500)
    category = models.CharField(max_length=50, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    view_count = models.PositiveIntegerField(default=0)
    purchase_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'v402_products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def conversion_rate(self):
        """Calculate conversion rate"""
        if self.view_count == 0:
            return 0
        return (self.purchase_count / self.view_count) * 100

class Payment(models.Model):
    """Payment model for transaction tracking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_hash = models.CharField(max_length=66, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    block_number = models.PositiveIntegerField(null=True, blank=True)
    gas_used = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'v402_payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['product', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Payment {self.transaction_hash[:10]}... for {self.product.title}"

class AccessLog(models.Model):
    """Access log model for analytics"""
    ACCESS_TYPE_CHOICES = [
        ('view', 'View'),
        ('purchase', 'Purchase'),
        ('access', 'Access'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'v402_access_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'access_type']),
            models.Index(fields=['user', 'access_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['country']),
        ]

    def __str__(self):
        return f"{self.user.username} {self.access_type} {self.product.title}"

class Analytics(models.Model):
    """Analytics model for metrics storage"""
    METRIC_TYPE_CHOICES = [
        ('views', 'Views'),
        ('purchases', 'Purchases'),
        ('revenue', 'Revenue'),
    ]

    PERIOD_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='analytics', null=True, blank=True)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPE_CHOICES)
    metric_value = models.FloatField()
    currency = models.CharField(max_length=10, null=True, blank=True)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    date = models.DateTimeField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'v402_analytics'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['product', 'metric_type']),
            models.Index(fields=['metric_type', 'period']),
            models.Index(fields=['date']),
        ]
        unique_together = ['product', 'metric_type', 'period', 'date']

    def __str__(self):
        return f"{self.metric_type} for {self.product.title if self.product else 'All Products'} on {self.date}"

class WebhookEvent(models.Model):
    """Webhook event model for external integrations"""
    EVENT_TYPE_CHOICES = [
        ('payment.completed', 'Payment Completed'),
        ('payment.failed', 'Payment Failed'),
        ('product.created', 'Product Created'),
        ('product.updated', 'Product Updated'),
        ('access.granted', 'Access Granted'),
        ('access.denied', 'Access Denied'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    retry_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'v402_webhook_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'processed']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"

class Configuration(models.Model):
    """Configuration model for system settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'v402_configurations'
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'

    def __str__(self):
        return self.key
