from rest_framework import generics, permissions
from .models import Order, OrderItem , Product
from .serializers import OrderSerializer, OrderHistorySerializer
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from .permission import IsRetailer,IsWholesaler

class WholesalerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsWholesaler]

    def get_queryset(self):
        # Get the current user (wholesaler)
        user = self.request.user
        # Filter orders where the order items are linked to the wholesaler's products
        return Order.objects.filter(orderitem__product__creator=user).distinct()

class RetailerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsRetailer]

    def get_queryset(self):
        # Get the current user (retailer)
        user = self.request.user
        # Filter orders where the order belongs to the retailer
        return Order.objects.filter(user=user)

from rest_framework import generics, permissions
import razorpay
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    data = request.data
    items = data.get('order_items', [])
    total_price = 0

    # Validate and calculate total price based on the items in the request
    for item in items:
        try:
            product = Product.objects.get(id=item['product'])
            quantity = item['quantity']
            total_price += product.price * quantity

        except Product.DoesNotExist:
            return Response({"error": f"Product with id {item['product']} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    # Serialize the data to create an Order
    serializer = OrderSerializer(data=data)
    if serializer.is_valid():
        order = serializer.save(user=user, total_price=total_price)

        # Initialize Razorpay client
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        total_price_decimal = Decimal(total_price)
        charge_amount = total_price_decimal * Decimal(0.03) * Decimal(100)

        # Create Razorpay order (amount should be in paise, so multiply by 100)
        try:
            razorpay_order = razorpay_client.order.create({
                "amount": int((total_price * 100) + charge_amount),
                "currency": "INR",
                "payment_capture": 1  # Auto capture after payment
            })

            # Save the Razorpay order ID to the order instance
            order.razorpay_order_id = razorpay_order['id']
            order.save()

            # Return Razorpay order details to the frontend
            return Response({
                "order_id": order.id,
                "razorpay_order_id": razorpay_order['id'],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "amount": int(total_price_decimal * Decimal(100)),    # Send amount in paise
                "currency": "INR"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": "Failed to create Razorpay order", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView

class RazorpayPaymentVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')

        try:
            # Verify the Razorpay signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            razorpay_client.utility.verify_payment_signature(params_dict)

            # Update the order status to 'confirmed'
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.order_status = 'confirmed'
            order.save()

            return Response({"status": "Payment successful and order confirmed"})

        except razorpay.errors.SignatureVerificationError:
            return Response({"status": "Payment verification failed"}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list_view(request):
    # Get the orders for the authenticated user
    orders = Order.objects.filter(user=request.user)

    # Serialize the orders
    serializer = OrderHistorySerializer(orders, many=True)

    # Return the response with the serialized data
    return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

@api_view(['GET'])
@permission_classes([IsRetailer])  # Use the custom permission
def cart_detail_view(request):
    """Retrieve the cart for the logged-in user, creating it if it doesn't exist."""
    # Try to get the cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Serialize the cart data
    serializer = CartSerializer(cart)

    return Response(serializer.data, status=status.HTTP_200_OK)


from django.shortcuts import get_object_or_404
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsRetailer])
def cart_item_create_view(request):
    """Create or update a cart item for the logged-in user's cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product_id = request.data.get('product')
    product = get_object_or_404(Product, id=product_id)
    serializer = CartItemSerializer(data=request.data)
    if serializer.is_valid():
        # Check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            quantity= request.data.get('quantity', 1)
        )
        if not created:
            # If the cart item exists, update the quantity
            cart_item.quantity += request.data.get('quantity', 1)
            cart_item.save()
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsRetailer])
def cart_item_delete_view(request, item_id):
    """Delete a specific cart item."""
    try:
        cart_item = CartItem.objects.filter(product_id=item_id, cart__user=request.user)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except CartItem.DoesNotExist:
        return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_details(request, id):
  try:
    order = get_object_or_404(Order, id=id)
    serializer = OrderHistorySerializer(order)
    return Response(serializer.data,status=status.HTTP_200_OK)
  except Order.DoesNotExist:
    return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)