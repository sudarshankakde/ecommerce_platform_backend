from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_wholesaler = models.BooleanField(default=False)
    is_retailer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
      
      


class WholesalerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,limit_choices_to={'is_wholesaler': True})
    company_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=15, unique=True)  # For India
    address = models.TextField()
    company_description = models.TextField(blank=True, null=True)
    years_in_business = models.IntegerField(null=True, blank=True)
    logo = models.ImageField(blank=True, null=True,upload_to='WholeSaler/')
    contact_number = models.CharField(max_length=15)
    # Additional fields for credibility and social proof
    total_sales = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    verified = models.BooleanField(default=False)
    is_spotlight = models.BooleanField(default=False)
    # Payment details fields
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)  # Indian IFSC code
    upi_id = models.CharField(max_length=50, blank=True, null=True)  # UPI ID for digital payments
    payment_phone_number = models.CharField(max_length=15, blank=True, null=True)  # Phone for UPI payments
    
    def __str__(self):
        return f"{self.user.username} - {self.company_name}"
      

class RetailerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,limit_choices_to={'is_retailer': True})
    shop_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    gst_number = models.CharField(max_length=15, unique=True, null=True,blank=True)  # For India
    license_number = models.CharField(max_length=255, null=True,blank=True,unique=True)
    pan_card = models.CharField(max_length=10, null=True,blank=True,unique=True)
    verified = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username} - {self.shop_name}"






class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    def __str__(self):
        return self.name




class Product(models.Model):
    PRODUCT_TYPES = [
        ('medicine', 'Medicine'),
        ('mobile', 'Mobile'),
        ('home_appliance', 'Home Appliance'),
        ('clothing', 'Clothing'),
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'),
        ('toys', 'Toys'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.PROTECT)
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPES)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)  # New field
    images = models.ManyToManyField('ProductImage', blank=True, related_name='products')  # Added related_name
    specifications = models.TextField(blank=True, null=True)  # For HTML content
    is_deal_of_the_day = models.BooleanField(default=False)
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.is_main} - {self.image.url}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()  # Consider using a choice field for 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} review of {self.product.name}"
      
      

class Order(models.Model):
    ORDER_STATUSES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    id = models.CharField(max_length=20, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who placed the order
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUSES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=25)
    portal_code = models.DecimalField(max_digits=6, decimal_places=0)
    order_status_description = models.TextField(blank=True, null=True)

    order_notes = models.TextField(blank=True,null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.id:  # Only set the ID on creation
            last_order = Order.objects.all().order_by('id').last()
            if last_order:
                last_id_number = int(last_order.id.split('ORD')[-1])
                new_id_number = last_id_number + 1
            else:
                new_id_number = 1
            self.id = f'ORD{str(new_id_number).zfill(6)}'  # ORD000001, ORD000002, etc.
        super(Order, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.id}"
      

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        """Calculates the total price of all items in the cart."""
        return sum(item.product.price * item.quantity for item in self.cart_items.all())

    def add_item(self, product, quantity=1):
        """Adds a product to the cart or updates the quantity if it already exists."""
        cart_item, created = self.cart_items.get_or_create(product=product)
        cart_item.quantity += quantity
        cart_item.save()

    def remove_item(self, product):
        """Removes a product from the cart."""
        self.cart_items.filter(product=product).delete()

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def clean(self):
        """Ensures quantity is a positive integer."""
        if self.quantity <= 0:
            raise ValidationError('Quantity must be a positive integer.')

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Cart"


@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """Automatically creates a cart for a new user."""
    if created:
        Cart.objects.create(user=instance)