"""
Django Views for v402 Protocol Integration
"""

import json
import logging
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Product, Payment, AccessLog, WebhookEvent
from .serializers import (
    ProductSerializer, PaymentSerializer
)
from .services import PaymentService, AnalyticsService, WebhookService

logger = logging.getLogger(__name__)

class ProductListView(View):
    """List and create products"""

    def get(self, request):
        """Get paginated list of products"""
        try:
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            category = request.GET.get('category')
            status = request.GET.get('status')
            search = request.GET.get('search')

            queryset = Product.objects.all()

            # Apply filters
            if category:
                queryset = queryset.filter(category=category)
            if status:
                queryset = queryset.filter(status=status)
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search)
                )

            # Pagination
            paginator = Paginator(queryset, limit)
            products_page = paginator.get_page(page)

            serializer = ProductSerializer(products_page.object_list, many=True)

            return JsonResponse({
                'products': serializer.data,
                'total': paginator.count,
                'page': page,
                'limit': limit,
                'has_next': products_page.has_next(),
                'has_prev': products_page.has_previous()
            })

        except Exception as e:
            logger.error(f"Error listing products: {e}")
            return JsonResponse({'error': 'Failed to list products'}, status=500)

    @method_decorator(login_required)
    def post(self, request):
        """Create a new product"""
        try:
            data = json.loads(request.body)
            data['author'] = request.user.id

            serializer = ProductSerializer(data=data)
            if serializer.is_valid():
                product = serializer.save()

                # Log access
                AccessLog.objects.create(
                    product=product,
                    user=request.user,
                    access_type='view',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )

                return JsonResponse(serializer.data, status=201)
            else:
                return JsonResponse({'errors': serializer.errors}, status=400)

        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return JsonResponse({'error': 'Failed to create product'}, status=500)

class ProductDetailView(View):
    """Get, update, or delete a specific product"""

    def get(self, request, product_id):
        """Get a specific product"""
        try:
            product = get_object_or_404(Product, id=product_id)

            # Increment view count
            product.view_count += 1
            product.save()

            # Log access
            AccessLog.objects.create(
                product=product,
                user=request.user if request.user.is_authenticated else None,
                access_type='view',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )

            serializer = ProductSerializer(product)
            return JsonResponse(serializer.data)

        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return JsonResponse({'error': 'Failed to get product'}, status=500)

    @method_decorator(login_required)
    def put(self, request, product_id):
        """Update a product"""
        try:
            product = get_object_or_404(Product, id=product_id, author=request.user)
            data = json.loads(request.body)

            serializer = ProductSerializer(product, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            else:
                return JsonResponse({'errors': serializer.errors}, status=400)

        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return JsonResponse({'error': 'Failed to update product'}, status=500)

    @method_decorator(login_required)
    def delete(self, request, product_id):
        """Delete a product"""
        try:
            product = get_object_or_404(Product, id=product_id, author=request.user)
            product.delete()
            return JsonResponse({'message': 'Product deleted successfully'}, status=204)

        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return JsonResponse({'error': 'Failed to delete product'}, status=500)

class PaymentView(View):
    """Handle payment processing"""

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Process a payment"""
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ['product_id', 'amount', 'currency', 'user_address', 'nonce', 'signature']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            # Get product
            product = get_object_or_404(Product, id=data['product_id'])

            # Process payment using service
            payment_service = PaymentService()
            payment_result = payment_service.process_payment(
                product=product,
                amount=data['amount'],
                currency=data['currency'],
                user_address=data['user_address'],
                nonce=data['nonce'],
                signature=data['signature']
            )

            if payment_result['success']:
                # Create payment record
                payment = Payment.objects.create(
                    transaction_hash=payment_result['transaction_hash'],
                    product=product,
                    user=request.user if request.user.is_authenticated else None,
                    amount=data['amount'],
                    currency=data['currency'],
                    status='completed',
                    block_number=payment_result.get('block_number'),
                    gas_used=payment_result.get('gas_used')
                )

                # Increment purchase count
                product.purchase_count += 1
                product.save()

                # Log access
                AccessLog.objects.create(
                    product=product,
                    user=request.user if request.user.is_authenticated else None,
                    access_type='purchase',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )

                # Send webhook
                webhook_service = WebhookService()
                webhook_service.send_event('payment.completed', {
                    'payment_id': str(payment.id),
                    'product_id': str(product.id),
                    'amount': data['amount'],
                    'currency': data['currency'],
                    'transaction_hash': payment_result['transaction_hash']
                })

                serializer = PaymentSerializer(payment)
                return JsonResponse(serializer.data, status=201)
            else:
                return JsonResponse({'error': payment_result['error']}, status=400)

        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return JsonResponse({'error': 'Failed to process payment'}, status=500)

class AccessCheckView(View):
    """Check user access to a product"""

    def post(self, request):
        """Check access for a product"""
        try:
            data = json.loads(request.body)

            product_id = data.get('product_id')
            user_address = data.get('user_address')

            if not product_id or not user_address:
                return JsonResponse({'error': 'Missing product_id or user_address'}, status=400)

            product = get_object_or_404(Product, id=product_id)

            # Check if user has paid for this product
            has_payment = Payment.objects.filter(
                product=product,
                user__public_key=user_address,
                status='completed'
            ).exists()

            response_data = {
                'has_access': has_payment,
                'reason': 'Payment verified' if has_payment else 'No payment found'
            }

            if has_payment:
                response_data['expires_at'] = int((timezone.now() + timedelta(days=30)).timestamp())

            return JsonResponse(response_data)

        except Exception as e:
            logger.error(f"Error checking access: {e}")
            return JsonResponse({'error': 'Failed to check access'}, status=500)

class AnalyticsView(View):
    """Get analytics data"""

    @method_decorator(login_required)
    def post(self, request):
        """Get analytics for products"""
        try:
            data = json.loads(request.body)

            product_id = data.get('product_id')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            period = data.get('period', 'daily')

            analytics_service = AnalyticsService()
            analytics_data = analytics_service.get_analytics(
                product_id=product_id,
                start_date=start_date,
                end_date=end_date,
                period=period
            )

            return JsonResponse(analytics_data)

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return JsonResponse({'error': 'Failed to get analytics'}, status=500)

class WebhookView(View):
    """Handle webhook events"""

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Receive webhook events"""
        try:
            data = json.loads(request.body)

            event_type = data.get('event_type')
            payload = data.get('payload', {})

            if not event_type:
                return JsonResponse({'error': 'Missing event_type'}, status=400)

            # Create webhook event
            webhook_event = WebhookEvent.objects.create(
                event_type=event_type,
                payload=payload
            )

            # Process webhook
            webhook_service = WebhookService()
            webhook_service.process_event(webhook_event)

            return JsonResponse({'message': 'Webhook received'}, status=200)

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return JsonResponse({'error': 'Failed to process webhook'}, status=500)

class HealthCheckView(View):
    """Health check endpoint"""

    def get(self, request):
        """Return system health status"""
        try:
            # Check database connection
            Product.objects.count()
            db_status = 'healthy'
        except Exception:
            db_status = 'unhealthy'

        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0',
            'database_status': db_status
        })
