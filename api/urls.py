from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    WholesalerProfileUpdateView,
    RetailerProfileUpdateView,
    ProductCreateView,
    ProductDetailView,
    ProductListView,
    WholesalerProfileDetailView,
    WholesalerInventoryView,
    UniversalSearchView,
    CategoryDetailView,
    CategoryListView,
    UniversalDataAPIView,
    categories_view,
    update_profile,
    get_profile,update_password,
    register_user
   
)
from .orders_views import (
    WholesalerOrderListView,
    create_order,
    cart_detail_view,
    cart_item_create_view,
    cart_item_delete_view,
    RazorpayPaymentVerifyView,
    order_list_view,
    order_details
)
from .wholesaler_view import (
    wholesalerDashbordView,
    update_order_status,product_edit,product_delete,product_list,create_product
)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Authantication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register_user, name='register_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', get_profile, name='update-profile'),
    path('update-profile/', update_profile, name='update-profile'),
    path('update-password/', update_password, name='update_password'),
    
    # wholesaler
    path('wholesaler/profile/update/', WholesalerProfileUpdateView.as_view(), name='wholesaler-profile-update'),
    path('wholesaler/profile/<int:id>/', WholesalerProfileDetailView.as_view(), name='wholesaler-profile-detail-id'),
    path('wholesaler/inventory/', WholesalerInventoryView.as_view(), name='wholesaler-inventory'),
    path('wholesaler/profile/username/<str:username>/', WholesalerProfileDetailView.as_view(), name='wholesaler-profile-detail-username'), 
    path('orders/wholesaler/', WholesalerOrderListView.as_view(), name='wholesaler-orders'),
    path('order_details/<str:id>', order_details, name='order-details'),
    path('wholesaler/dashboard/', wholesalerDashbordView, name='wholesaler-dashbord'),
    path('orders/<str:order_id>/status/', update_order_status, name='update_order_status'),
    path('inventory/', product_list, name='product_list'),
    path('inventory/create/', create_product, name='product_create'),
    path('inventory/<int:pk>/edit/', product_edit, name='product_edit'),
    path('inventory/<int:pk>/delete/', product_delete, name='product_delete'),
    # retailer
    path('retailer/profile/update/', RetailerProfileUpdateView.as_view(), name='retailer-profile-update'),
    path('categories/', categories_view, name='categories-detail'),
    path('cart/', cart_detail_view, name='cart-detail'),
    path('cart/items/add/', cart_item_create_view, name='cart-item-create'),
    path('cart/items/delete/<int:item_id>/', cart_item_delete_view, name='cart-item-delete'),
    path('orders/create/', create_order, name='order-create'),
     path('razorpay/verify-payment/', RazorpayPaymentVerifyView.as_view(), name='razorpay-verify-payment'),
    path('orders/retailer/', order_list_view, name='retailer-orders'),
    
    # genralized
    path('home-data/', UniversalDataAPIView.as_view(), name='home-data'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('search/', UniversalSearchView.as_view(), name='universal_search'),  
    
    # List all categories
    path('categories/', CategoryListView.as_view(), name='category_list'),
    
    # Retrieve products for a specific category with suggestions
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category_detail'),
    
]
