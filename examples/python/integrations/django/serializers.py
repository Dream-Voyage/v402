"""
Django Serializers for v402 Protocol Integration
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Product, Payment, AccessLog, Analytics, WebhookEvent

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'public_key', 'is_verified', 'created_at']
        read_only_fields = ['id', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    """Product serializer"""
    author = UserSerializer(read_only=True)
    conversion_rate = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'currency', 'content_url',
            'category', 'tags', 'author', 'status', 'view_count', 'purchase_count',
            'conversion_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'view_count', 'purchase_count', 'created_at', 'updated_at']

class ProductCreateSerializer(serializers.ModelSerializer):
    """Product creation serializer"""

    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price', 'currency', 'content_url',
            'category', 'tags', 'status'
        ]

    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

    def validate_content_url(self, value):
        """Validate content URL format"""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Content URL must be a valid HTTP/HTTPS URL")
        return value

class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer"""
    product = ProductSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_hash', 'product', 'user', 'amount', 'currency',
            'status', 'block_number', 'gas_used', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PaymentCreateSerializer(serializers.Serializer):
    """Payment creation serializer"""
    product_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=10)
    user_address = serializers.CharField(max_length=42)
    nonce = serializers.CharField(max_length=100)
    signature = serializers.CharField(max_length=200)

    def validate_user_address(self, value):
        """Validate Ethereum address format"""
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError("Invalid Ethereum address format")
        return value

    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value

class AccessLogSerializer(serializers.ModelSerializer):
    """Access log serializer"""
    product = ProductSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = AccessLog
        fields = [
            'id', 'product', 'user', 'access_type', 'ip_address',
            'user_agent', 'referrer', 'country', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AccessLogCreateSerializer(serializers.ModelSerializer):
    """Access log creation serializer"""

    class Meta:
        model = AccessLog
        fields = [
            'product', 'user', 'access_type', 'ip_address',
            'user_agent', 'referrer', 'country'
        ]

class AnalyticsSerializer(serializers.ModelSerializer):
    """Analytics serializer"""
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Analytics
        fields = [
            'id', 'product', 'metric_type', 'metric_value', 'currency',
            'period', 'date', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AnalyticsRequestSerializer(serializers.Serializer):
    """Analytics request serializer"""
    product_id = serializers.UUIDField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    period = serializers.ChoiceField(
        choices=['hourly', 'daily', 'weekly', 'monthly'],
        default='daily'
    )

class WebhookEventSerializer(serializers.ModelSerializer):
    """Webhook event serializer"""

    class Meta:
        model = WebhookEvent
        fields = [
            'id', 'event_type', 'payload', 'processed', 'retry_count',
            'error_message', 'created_at', 'processed_at'
        ]
        read_only_fields = ['id', 'created_at', 'processed_at']

class WebhookEventCreateSerializer(serializers.Serializer):
    """Webhook event creation serializer"""
    event_type = serializers.ChoiceField(choices=[
        ('payment.completed', 'Payment Completed'),
        ('payment.failed', 'Payment Failed'),
        ('product.created', 'Product Created'),
        ('product.updated', 'Product Updated'),
        ('access.granted', 'Access Granted'),
        ('access.denied', 'Access Denied'),
    ])
    payload = serializers.JSONField()

class AccessRequestSerializer(serializers.Serializer):
    """Access request serializer"""
    product_id = serializers.UUIDField()
    user_address = serializers.CharField(max_length=42)
    timestamp = serializers.IntegerField()
    signature = serializers.CharField(max_length=200)

    def validate_user_address(self, value):
        """Validate Ethereum address format"""
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError("Invalid Ethereum address format")
        return value

class AccessResponseSerializer(serializers.Serializer):
    """Access response serializer"""
    has_access = serializers.BooleanField()
    reason = serializers.CharField(required=False)
    expires_at = serializers.IntegerField(required=False)

class ProductListSerializer(serializers.Serializer):
    """Product list response serializer"""
    products = ProductSerializer(many=True)
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    limit = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_prev = serializers.BooleanField()

class PaymentListSerializer(serializers.Serializer):
    """Payment list response serializer"""
    payments = PaymentSerializer(many=True)
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    limit = serializers.IntegerField()

class ErrorResponseSerializer(serializers.Serializer):
    """Error response serializer"""
    error = serializers.CharField()
    detail = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField()

class HealthCheckSerializer(serializers.Serializer):
    """Health check response serializer"""
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    version = serializers.CharField()
    database_status = serializers.CharField(required=False)
    redis_status = serializers.CharField(required=False)
