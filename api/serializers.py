from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import WholesalerProfile, RetailerProfile,Product, Category, ProductImage,ProductReview , Brand

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_wholesaler', 'is_retailer']

    def create(self, validated_data):
        # Pop the password and create the user
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create associated profile (wholesaler or retailer)
        if user.is_wholesaler:
            WholesalerProfile.objects.create(user=user)
        elif user.is_retailer:
            RetailerProfile.objects.create(user=user)
            
        return user


class WholesalerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WholesalerProfile
        fields = [
            'id',
            'company_name', 
            'gst_number', 
            'address', 
            'company_description', 
            'years_in_business', 
            'total_sales', 
            'rating', 
            'verified',
            'logo'
        ]
  
class RetailerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetailerProfile
        fields = [
            'shop_name', 
            'contact_number', 
            'address', 
            'gst_number',
            'license_number',
            'pan_card',
        ]





class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description','icon']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description','icon']
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [ 'image', 'is_main']
    def to_representation(self, instance):
          representation = super().to_representation(instance)
          representation['image'] = instance.image.url  # Ensure the URL is returned
          return representation
        
class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    class Meta:
        model = ProductReview
        fields = ['user','rating','comment','created_at']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'category', 
            'product_type', 
            'description', 
            'price', 
            'stock', 
            'created_at', 
            'updated_at', 
            'specifications', 
            'images',
            'creator',  
            'average_rating', 
            'review_count',
            'brand'
        ]
        read_only_fields = ['creator'] 

    def create(self, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        product = Product.objects.create(**validated_data)
        for image in images_data:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.product_type = validated_data.get('product_type', instance.product_type)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.specifications = validated_data.get('specifications', instance.specifications)
        instance.save()

        # Handle product images if provided
        if images_data:
            instance.images.all().delete()  # Optionally remove existing images
            for image in images_data:
                ProductImage.objects.create(product=instance, image=image)

        return instance
      
      
      
class WholesalerProfileSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = WholesalerProfile
        fields = [
            'user',
            'company_name',
            'gst_number',
            'address',
            'company_description',
            'years_in_business',
            'total_sales',
            'rating',
            'verified',
            'products','logo'  # Include products in the serialized response 
        ]
        
        
        
from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price_per_item']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'total_price', 'order_status', 'created_at', 'updated_at',
            'order_items', 'name', 'email', 'address', 'city', 'state', 'portal_code', 'order_notes','order_status_description'
        ]
        read_only_fields = ['user', 'total_price', 'order_status', 'created_at', 'updated_at','order_status_description']

    def create(self, validated_data):
        items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order


from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id','product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_items']



class OrderItemHistorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price_per_item']


class OrderHistorySerializer(serializers.ModelSerializer):
    order_items = OrderItemHistorySerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'total_price', 'order_status', 'created_at', 'updated_at',
            'order_items', 'name', 'email', 'address', 'city', 'state', 'portal_code', 'order_notes','order_status_description'
        ]
        read_only_fields = ['user', 'total_price', 'order_status', 'created_at', 'updated_at']
