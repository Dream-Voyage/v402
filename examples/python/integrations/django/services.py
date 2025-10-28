"""
Django Services for v402 Protocol Integration
"""

import hashlib
import logging
import time
from datetime import datetime, timedelta
from django.db.models import Count, Sum
from django.utils import timezone
from typing import Dict, Any, Optional, List

from .models import Product, Payment, AccessLog, Analytics, WebhookEvent

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for handling payment operations"""

    def __init__(self):
        self.v402_base_url = "https://api.v402.network"
        self.timeout = 30

    def process_payment(self, product: Product, amount: str, currency: str,
                      user_address: str, nonce: str, signature: str) -> Dict[str, Any]:
        """Process a payment for a product"""
        try:
            # Validate signature (simplified for example)
            if not self._verify_signature(user_address, nonce, signature):
                return {
                    'success': False,
                    'error': 'Invalid signature'
                }

            # Mock blockchain transaction
            transaction_hash = self._generate_transaction_hash()

            # In a real implementation, you would:
            # 1. Call the v402 API to process the payment
            # 2. Wait for blockchain confirmation
            # 3. Handle any errors

            return {
                'success': True,
                'transaction_hash': transaction_hash,
                'block_number': 12345678,
                'gas_used': 50000
            }

        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _verify_signature(self, user_address: str, nonce: str, signature: str) -> bool:
        """Verify the signature (simplified for example)"""
        # In a real implementation, you would verify the cryptographic signature
        # For this example, we'll just check if the signature is not empty
        return bool(signature and len(signature) > 10)

    def _generate_transaction_hash(self) -> str:
        """Generate a mock transaction hash"""
        timestamp = str(int(time.time()))
        return f"0x{hashlib.sha256(timestamp.encode()).hexdigest()[:64]}"

    def get_payment_history(self, user_address: str, limit: int = 10) -> List[Payment]:
        """Get payment history for a user"""
        return Payment.objects.filter(
            user__public_key=user_address,
            status='completed'
        ).order_by('-created_at')[:limit]

    def calculate_revenue(self, product: Product, start_date: datetime,
                         end_date: datetime) -> Dict[str, Any]:
        """Calculate revenue for a product in a date range"""
        payments = Payment.objects.filter(
            product=product,
            status='completed',
            created_at__range=[start_date, end_date]
        )

        total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
        payment_count = payments.count()

        return {
            'total_revenue': float(total_revenue),
            'payment_count': payment_count,
            'average_payment': float(total_revenue / payment_count) if payment_count > 0 else 0
        }

class AnalyticsService:
    """Service for handling analytics operations"""

    def get_analytics(self, product_id: Optional[str] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     period: str = 'daily') -> Dict[str, Any]:
        """Get analytics data"""
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = timezone.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            # Base queryset
            products_qs = Product.objects.all()
            if product_id:
                products_qs = products_qs.filter(id=product_id)

            # Get basic metrics
            total_products = products_qs.count()
            total_views = AccessLog.objects.filter(
                product__in=products_qs,
                access_type='view',
                created_at__range=[start_date, end_date]
            ).count()

            total_purchases = Payment.objects.filter(
                product__in=products_qs,
                status='completed',
                created_at__range=[start_date, end_date]
            ).count()

            total_revenue = Payment.objects.filter(
                product__in=products_qs,
                status='completed',
                created_at__range=[start_date, end_date]
            ).aggregate(total=Sum('amount'))['total'] or 0

            # Calculate conversion rate
            conversion_rate = (total_purchases / total_views * 100) if total_views > 0 else 0

            # Get top countries
            top_countries = AccessLog.objects.filter(
                product__in=products_qs,
                created_at__range=[start_date, end_date],
                country__isnull=False
            ).values('country').annotate(
                count=Count('id')
            ).order_by('-count')[:10]

            # Get top referrers
            top_referrers = AccessLog.objects.filter(
                product__in=products_qs,
                created_at__range=[start_date, end_date],
                referrer__isnull=False
            ).values('referrer').annotate(
                count=Count('id')
            ).order_by('-count')[:10]

            return {
                'product_id': product_id,
                'views': total_views,
                'purchases': total_purchases,
                'revenue': str(total_revenue),
                'currency': 'USDC',
                'period': period,
                'generated_at': timezone.now(),
                'conversion_rate': round(conversion_rate, 2),
                'top_countries': list(top_countries),
                'top_referrers': list(top_referrers)
            }

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {
                'error': str(e),
                'views': 0,
                'purchases': 0,
                'revenue': '0.00',
                'currency': 'USDC',
                'period': period,
                'generated_at': timezone.now(),
                'conversion_rate': 0,
                'top_countries': [],
                'top_referrers': []
            }

    def generate_daily_metrics(self, date: datetime) -> None:
        """Generate daily metrics for all products"""
        try:
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            products = Product.objects.all()

            for product in products:
                # Views
                views_count = AccessLog.objects.filter(
                    product=product,
                    access_type='view',
                    created_at__range=[start_of_day, end_of_day]
                ).count()

                if views_count > 0:
                    Analytics.objects.update_or_create(
                        product=product,
                        metric_type='views',
                        period='daily',
                        date=start_of_day,
                        defaults={'metric_value': views_count}
                    )

                # Purchases
                purchases_count = Payment.objects.filter(
                    product=product,
                    status='completed',
                    created_at__range=[start_of_day, end_of_day]
                ).count()

                if purchases_count > 0:
                    Analytics.objects.update_or_create(
                        product=product,
                        metric_type='purchases',
                        period='daily',
                        date=start_of_day,
                        defaults={'metric_value': purchases_count}
                    )

                # Revenue
                revenue = Payment.objects.filter(
                    product=product,
                    status='completed',
                    created_at__range=[start_of_day, end_of_day]
                ).aggregate(total=Sum('amount'))['total'] or 0

                if revenue > 0:
                    Analytics.objects.update_or_create(
                        product=product,
                        metric_type='revenue',
                        period='daily',
                        date=start_of_day,
                        defaults={'metric_value': float(revenue), 'currency': 'USDC'}
                    )

            logger.info(f"Generated daily metrics for {date.date()}")

        except Exception as e:
            logger.error(f"Error generating daily metrics: {e}")

class WebhookService:
    """Service for handling webhook operations"""

    def __init__(self):
        self.webhook_urls = {
            'payment.completed': 'https://example.com/webhooks/payment-completed',
            'payment.failed': 'https://example.com/webhooks/payment-failed',
            'product.created': 'https://example.com/webhooks/product-created',
            'product.updated': 'https://example.com/webhooks/product-updated',
            'access.granted': 'https://example.com/webhooks/access-granted',
            'access.denied': 'https://example.com/webhooks/access-denied',
        }

    def send_event(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """Send a webhook event"""
        try:
            webhook_event = WebhookEvent.objects.create(
                event_type=event_type,
                payload=payload
            )

            # In a real implementation, you would send HTTP request to webhook URL
            # For this example, we'll just mark it as processed
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            logger.info(f"Sent webhook event: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Error sending webhook event: {e}")
            return False

    def process_event(self, webhook_event: WebhookEvent) -> None:
        """Process a received webhook event"""
        try:
            # In a real implementation, you would process the webhook event
            # For this example, we'll just mark it as processed
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            logger.info(f"Processed webhook event: {webhook_event.event_type}")

        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")
            webhook_event.error_message = str(e)
            webhook_event.save()

    def retry_failed_events(self, max_retries: int = 3) -> int:
        """Retry failed webhook events"""
        try:
            failed_events = WebhookEvent.objects.filter(
                processed=False,
                retry_count__lt=max_retries
            )

            retry_count = 0
            for event in failed_events:
                # In a real implementation, you would retry sending the webhook
                event.retry_count += 1
                event.save()
                retry_count += 1

            logger.info(f"Retried {retry_count} failed webhook events")
            return retry_count

        except Exception as e:
            logger.error(f"Error retrying failed events: {e}")
            return 0

class NotificationService:
    """Service for handling notifications"""

    def send_payment_notification(self, payment: Payment) -> bool:
        """Send payment notification"""
        try:
            # In a real implementation, you would send email/SMS notification
            logger.info(f"Payment notification sent for payment {payment.id}")
            return True

        except Exception as e:
            logger.error(f"Error sending payment notification: {e}")
            return False

    def send_access_notification(self, user: Any, product: Product) -> bool:
        """Send access notification"""
        try:
            # In a real implementation, you would send access notification
            logger.info(f"Access notification sent for user {user.id} and product {product.id}")
            return True

        except Exception as e:
            logger.error(f"Error sending access notification: {e}")
            return False
