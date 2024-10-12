from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, WholesalerProfile, RetailerProfile, Product, Order, OrderItem
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum, Avg, Count,F
from django.utils import timezone
from datetime import timedelta
from .serializers import OrderHistorySerializer,ProductSerializer
from .permission import IsWholesaler
@api_view(['GET'])
@permission_classes([AllowAny ])
def wholesalerDashbordView(request):
    user = request.user

    # Get the period from the query parameters, default to "thisMonth"
    period = request.GET.get('period', 'thisMonth')
    
    # Set date range based on the selected period
    now = timezone.now()
    
    if period == 'today':
        start_date = now.date()
    elif period == 'thisWeek':
        start_date = now - timedelta(days=now.weekday())  # Start of the week (Monday)
    elif period == 'thisMonth':
        start_date = now.replace(day=1)  # Start of the current month
    elif period == 'thisYear':
        start_date = now.replace(month=1, day=1)  # Start of the current year
    else:
        start_date = now.replace(day=1)  # Default to the current month if period is not valid

    # Filter Orders containing products created by the wholesaler and within the selected period
    orders = Order.objects.filter(order_items__product__creator=user, created_at__gte=start_date).distinct()

    # Serialize orders
    orders_serializer = OrderHistorySerializer(orders, many=True)

    # Total revenue from all sales (sum total price from each order)
    total_revenue = orders.aggregate(total_revenue=Sum('total_price'))['total_revenue']

    # Total number of sales (sum of all quantities from OrderItems in each order)
    total_sales = OrderItem.objects.filter(product__creator=user, order__created_at__gte=start_date).aggregate(total_sales=Sum('quantity'))['total_sales']

    # Average order value
    average_order_value = orders.aggregate(average_value=Avg('total_price'))['average_value']

    # Pending orders
    pending_orders = orders.filter(order_status='confirmed').count()

    # Active products (products with stock > 0)
    active_products = Product.objects.filter(creator=user, stock__gt=0).count()

    # Product performance (number of orders per product)
    product_performance = OrderItem.objects.filter(product__creator=user, order__created_at__gte=start_date).values('product__name').annotate(total_orders=Count('order', distinct=True)).order_by('-total_orders')

    # Top customers (based on number of orders placed)
    top_customers = orders.values('user__username','user__retailerprofile__shop_name').annotate(total_orders=Count('id')).order_by('-total_orders')

    data = {
        'orders': orders_serializer.data,
        'total_revenue': total_revenue or 0,  # Default to 0 if no data
        'total_sales': total_sales or 0,
        'average_order_value': average_order_value or 0,
        'pending_orders': pending_orders,
        'active_products': active_products,
        'product_performance': product_performance,
        'top_customers': top_customers[:5],  # Top 5 customers
    }

    return Response(data, status=status.HTTP_200_OK)

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permission import IsWholesaler  # Assuming this custom permission exists
from .models import Order

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsWholesaler])
def update_order_status(request, order_id):
    try:
        # Retrieve the order object by the given order ID
        order = get_object_or_404(Order, id=order_id)

        # Check if the user has the necessary permissions (already handled by IsWholesaler)
        if request.user.is_wholesaler:
            # Get the new status and optional description from the request
            new_status = request.GET.get('status')
            new_description = request.GET.get('description', '')  # Default to an empty string if not provided

            # Validate the new status against the available choices
            valid_statuses = [status[0] for status in Order.ORDER_STATUSES]
            if new_status not in valid_statuses:
                return JsonResponse({'error': 'Invalid status'}, status=400)

            # Update the order status and optional description
            order.order_status = new_status
            if new_description:
                order.order_status_description = new_description

            # Save the changes
            order.save()

            # Return a success response
            return JsonResponse({'message': 'Order status updated successfully', 'order_status': new_status, 'order_status_description': new_description}, status=200)

        else:
            return JsonResponse({'error': 'You do not have permission to update this order.'}, status=403)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, ProductImage
from django.forms import modelformset_factory
from django.views.decorators.http import require_http_methods
from django.core import serializers


# List products for the wholesaler
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsWholesaler])
def product_list(request):
    if not request:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    user = request.user
    products = Product.objects.filter(creator=user).all()
    products = ProductSerializer(products, many=True).data
    # Assuming 'user' is the current user for whom you want to calculate total sales
    total_sales = OrderItem.objects.filter(product__creator=user).aggregate(
        total_sales=Sum(F('price_per_item') * F('quantity'))
    )['total_sales']
    # Filter Orders containing products created by the wholesaler and within the selected period
    orders = Order.objects.filter(order_items__product__creator=user).distinct()


    # Total revenue from all sales (sum total price from each order)
    total_revenue = orders.aggregate(total_revenue=Sum('total_price'))['total_revenue']
    data = {
      "products": list(products),
      "categoires": list(Category.objects.all().values('id', 'name')),
      "total_value": total_revenue,
      "total_sales": total_sales or 0,
      "low_stock": int(Product.objects.filter(stock__lte=10).values().count()),
    }

    return JsonResponse(data, safe=False)



import json
# Edit a product for the wholesaler
@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated, IsWholesaler])
@csrf_exempt
def product_edit(request, pk):
    # Get the product belonging to the authenticated user
    product = get_object_or_404(Product, pk=pk, creator=request.user)

    if product.creator != request.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Load request body as JSON
    data = json.loads(request.body)

    # Update product fields
    product.name = data.get('name', product.name)

    # Handle category - Convert to Category instance if it's provided
    category_data = data.get('category')
    if category_data:
        try:
            category = Category.objects.get(id=category_data.get('id'))
            product.category = category  # Assign Category instance
        except Category.DoesNotExist:
            return JsonResponse({"error": "Invalid category"}, status=400)

    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)

    # Save the updated product
    product.save()

    # Check if new images are provided
    if 'images' in request.FILES:
        # Remove old images only if new images are provided
        old_images = ProductImage.objects.filter(product=product)
        for old_image in old_images:
            old_image.delete()

        # Handle new images
        for image in request.FILES.getlist('images'):
            ProductImage.objects.create(
                product=product,  # Associate the image with the product
                image=image,
                is_main=False  # Set this based on your requirement or logic
            )

    # Return the updated product information
    return JsonResponse({
        'message': 'Product updated successfully',
        'product': {
            'id': product.id,
            'name': product.name,
            'category': product.category.name,  # Return the category name
            'price': product.price,
            'stock': product.stock,
        }
    })
# Delete a product
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsWholesaler])
def product_delete(request, pk):
   # Get the product belonging to the authenticated user
    product = get_object_or_404(Product, pk=pk, creator=request.user)

    if product.creator != request.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    product = get_object_or_404(Product, pk=pk, creator=request.user)

    product.delete()
    return JsonResponse({'message': 'Product deleted successfully'})

from django.core.files.base import ContentFile
import base64
@csrf_exempt
@api_view(['POST'])
def create_product(request):
        # Get the data from the request
        data = request.data
        # Get or create the category
        category_id = data['category']  # This is the string ID from the payload
        category, created = Category.objects.get_or_create(
            id=category_id,  # Use the category ID directly
            defaults={
                # Optional: if you want to create it with a name and description,
                # you can pass these as well, but these should be available in the payload
                'name': data.get('category_name', 'Default Category Name'),  # Provide a default if not present
                'description': data.get('category_description', '')  # Provide a default if not present
            }
        )


        # Create the product
        product = Product.objects.create(
            name=data['name'],
            category=category,
            product_type=data['product_type'],
            description=data['description'],
            price=data['price'],
            stock=data['stock'],
            creator=request.user,
            specifications=data['specifications'],
            is_deal_of_the_day=False
        )

       # Handle images if 'images' key is present
        if 'images' in data:
            for img_data in data['images']:
                image_content = img_data.get('image')  # Use get to avoid KeyError
                is_main = img_data.get('is_main', False)  # Default to False if 'is_main' not provided
                
                if image_content:  # Ensure there's actual image data
                    product_image = ProductImage.objects.create(
                        image=ContentFile(base64.b64decode(image_content), name='product_image.jpg'),  # Adjust file name
                        is_main=is_main
                    )
                    product.images.add(product_image)
        else:
            # Handle the case where 'images' key is not present
            print("No images provided in the payload.")
        product.save()

        return Response({"message": "Product created successfully"}, status=status.HTTP_201_CREATED)

    