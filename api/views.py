from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, WholesalerProfileSerializer, RetailerProfileSerializer,ProductSerializer,ProductReviewSerializer
from .models import WholesalerProfile, RetailerProfile,Product
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.models import User
import re  # Regular expressions for email validation
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# Get the custom User model
User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_identifier = request.data.get('username')  # This can be email or username
        password = request.data.get('password')
        user_type = request.data.get('user_type')  # Get user type from request

        # Try to find the user by email or username
        try:
            user = User.objects.get(Q(username=login_identifier) | Q(email=login_identifier))
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user using their username (not the email they provided)
        user = authenticate(request, username=user.username, password=password)
        
        if user is not None:
            # Check user type
            if user.is_wholesaler and user_type != 'wholesaler':
                return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
            elif user.is_retailer and user_type != 'retailer':
                return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

            # If user is authenticated and user type is valid
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# Permissions to ensure only the user who owns the profile can update it
class IsOwnerProfileOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

# Wholesaler Profile Views
class WholesalerProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = WholesalerProfile.objects.all()
    serializer_class = WholesalerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerProfileOrReadOnly]

    def get_object(self):
        return self.request.user.wholesalerprofile

# Retailer Profile Views
class RetailerProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = RetailerProfile.objects.all()
    serializer_class = RetailerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerProfileOrReadOnly]

    def get_object(self):
        return self.request.user.retailerprofile





class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        # Check if the user is a wholesaler
        if not user.is_wholesaler:
            raise PermissionDenied("Only wholesalers can create products.")
        
        # Save the product with the current user
        serializer.save(creator=user)
        
from .models import Category
from .serializers import CategorySerializer
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can view products

    def get(self, request, *args, **kwargs):
        # Fetching all products
        products = Product.objects.all()
        product_serializer = ProductSerializer(products, many=True)
        
        # Fetching all categories
        categories = Category.objects.all()
        category_serializer = CategorySerializer(categories, many=True)

        # Combine the serialized product and category data into a single response
        responseData = {
            'products': product_serializer.data,
            'categories': category_serializer.data
        }
        
        # Return response with combined data
        return Response(responseData, status=status.HTTP_200_OK)
from django.shortcuts import get_object_or_404

class ProductDetailView(APIView):
    
    permission_classes = [permissions.AllowAny]  
    

    def get(self,request,*args,**kwargs):
        product_id = self.kwargs['pk']
        products = get_object_or_404(Product,id=product_id)
        product_serializer = ProductSerializer(products)
        
        # Fetching all categories
        productReview = ProductReview.objects.filter(product=product_id)
        productReview_serializer = ProductReviewSerializer(productReview, many=True)

        # Combine the serialized product and category data into a single response
        responseData = {
            'products': product_serializer.data,
            'review': productReview_serializer.data
        }
        
        return Response(responseData, status=status.HTTP_200_OK)
      
      
      
from rest_framework.exceptions import NotFound
class WholesalerProfileDetailView(generics.RetrieveAPIView):
    serializer_class = WholesalerProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        wholesaler_id = self.kwargs.get('id')
        username = self.kwargs.get('username')

        # Initialize wholesaler_profile to None
        wholesaler_profile = None

        # Query the WholesalerProfile based on ID or username
        if wholesaler_id:
            try:
                wholesaler_profile = WholesalerProfile.objects.get(user__id=wholesaler_id)
            except WholesalerProfile.DoesNotExist:
                raise NotFound(detail="Wholesaler profile not found.")

        elif username:
            try:
                wholesaler_profile = WholesalerProfile.objects.get(user__username=username)
            except WholesalerProfile.DoesNotExist:
                raise NotFound(detail="Wholesaler profile not found.")

        else:
            raise NotFound(detail="No identifier provided.")

        # Attach the products to the wholesaler profile
        products = Product.objects.filter(creator=wholesaler_profile.user)
        wholesaler_profile.image = wholesaler_profile.logo
        wholesaler_profile.products = products

        return wholesaler_profile
      
      
      
      
      
      
class WholesalerInventoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Check if the user is a wholesaler
        if not user.is_wholesaler:
            raise PermissionDenied("Only wholesalers can view their inventory.")
        
        # Filter products by the wholesaler (creator)
        return Product.objects.filter(creator=user)
      
      
from django.db.models import Q

class UniversalSearchView(generics.GenericAPIView):
    """
    Search for both Wholesalers and Products in a unified way.
    """
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get('q', None)  # The search query parameter
        if not search_query:
            return Response({"detail": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Search WholesalerProfile by company_name or username
        wholesalers = WholesalerProfile.objects.filter(
            Q(company_name__icontains=search_query) | 
            Q(user__username__icontains=search_query)
        )

        # Search Product by name or category
        products = Product.objects.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(creator__wholesalerprofile__company_name__icontains=search_query) |
            Q(creator__username__icontains=search_query)
        )

        # Serialize results
        wholesaler_serializer = WholesalerProfileSerializer(wholesalers, many=True)
        product_serializer = ProductSerializer(products, many=True)

        # Return a combined response
        return Response({
            "wholesalers": wholesaler_serializer.data,
            "products": product_serializer.data
        }, status=status.HTTP_200_OK)
        
        
        
from .models import Category
from .serializers import CategorySerializer
# 1. List all categories and their products
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        category_data = []

        # Loop through categories and fetch related products
        for category in categories:
            products = Product.objects.filter(category=category)
            product_serializer = ProductSerializer(products, many=True)

            category_data.append({
                "category": CategorySerializer(category).data,
                "products": product_serializer.data
            })

        return Response(category_data, status=status.HTTP_200_OK)


# 2. Retrieve products in a specific category with category suggestions
class CategoryDetailView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        category_id = self.kwargs.get('id')
        try:
            # Retrieve the selected category and its products
            category = Category.objects.get(id=category_id)
            products = Product.objects.filter(category=category)
            product_serializer = ProductSerializer(products, many=True)

            # Find related categories (basic example using similar category names)
            related_categories = Category.objects.exclude(id=category.id).filter(name__icontains=category.name[:3])
            related_category_serializer = CategorySerializer(related_categories, many=True)

            return Response({
                "category": CategorySerializer(category).data,
                "products": product_serializer.data,
                "suggestions": related_category_serializer.data
            }, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
          
          
          

from django.db.models import Avg, Count           
from .models import WholesalerProfile ,ProductReview    
class UniversalDataAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        # Fetch featured categories
        featured_categories = Category.objects.filter(is_featured=True)
        featured_categories_data = CategorySerializer(featured_categories, many=True).data
        
        # Fetch deal of the day
        deal_of_the_day = Product.objects.filter(is_deal_of_the_day=True).first()
        deal_of_the_day_data = ProductSerializer(deal_of_the_day).data if deal_of_the_day else None
        
       
        top_rated_products = Product.objects.annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-average_rating')[:10]  # Get the top 10 products

        # Serialize the data
        top_rated_products_data = ProductSerializer(top_rated_products, many=True).data
        # Fetch wholesaler spotlight
        wholesaler_spotlight = WholesalerProfile.objects.filter(is_spotlight=True)
        wholesaler_spotlight_data = WholesalerProfileSerializer(wholesaler_spotlight, many=True).data
        
        # Construct the response data
        response_data = {
            'featured_categories': featured_categories_data,
            'deal_of_the_day': deal_of_the_day_data,
            'top_rated_products': top_rated_products_data,
            'wholesaler_spotlight': wholesaler_spotlight_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
      
      
from rest_framework.decorators import api_view, permission_classes     
@api_view(['GET'])  
@permission_classes([AllowAny])
def categories_view(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    
    if hasattr(user, 'wholesalerprofile'):
        profile = WholesalerProfile.objects.get(user=user)
        serializer = WholesalerProfileSerializer(profile)
    elif hasattr(user, 'retailerprofile'):
        profile = RetailerProfile.objects.get(user=user)
        serializer = RetailerProfileSerializer(profile)
    else:
        return Response({"error": "Profile not found"}, status=404)
    
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user

    # Handle Wholesaler profile update
    if user.is_wholesaler:
        try:
            # Get or create a profile for the wholesaler
            profile, created = WholesalerProfile.objects.get_or_create(user=user)
            # Use the request data along with FILES for logo
            serializer = WholesalerProfileSerializer(profile, data=request.data, partial=True)
            print(request.FILES)
            if 'logo' in request.FILES:
                # Only update the logo if a new one is uploaded
                profile.logo = request.FILES['logo']

            if serializer.is_valid():
                serializer.save()  # Save the updated profile
                return Response({
                    "message": "Wholesaler profile updated successfully",
                    "profile": serializer.data
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handle Retailer profile update
    elif user.is_retailer:
        try:
            # Get or create a profile for the retailer
            profile, created = RetailerProfile.objects.get_or_create(user=user)
            serializer = RetailerProfileSerializer(profile, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()  # Save the updated profile
                return Response({
                    "message": "Retailer profile updated successfully",
                    "profile": serializer.data
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "User type not recognized"}, status=status.HTTP_400_BAD_REQUEST)
from django.contrib.auth import update_session_auth_hash
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    # Check if the old password is correct
    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the new password and confirm password match
    if new_password != confirm_password:
        return Response({"error": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

    # Set the new password
    user.set_password(new_password)
    user.save()

    # Important: Update session so the user doesn't get logged out
    update_session_auth_hash(request, user)

    return Response({"success": "Password updated successfully."}, status=status.HTTP_200_OK)
  
  
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    user_data = request.data

    # Check for password confirmation
    if user_data.get("password") != user_data.get("confirmPassword"):
        return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Set the username as the email
    user_data['username'] = user_data.get("email")

    # Handle user type (wholesaler or retailer)
    if user_data.get("userType") == "wholesaler":
        user_data["is_wholesaler"] = True
    elif user_data.get("userType") == "retailer":
        user_data["is_retailer"] = True

    # Serialize and create the user
    user_serializer = UserSerializer(data=user_data)
    
    if user_serializer.is_valid():
        user = user_serializer.save()  # Save the user instance

        # Handle profile creation based on userType
        if user_data["userType"] == "wholesaler":
            wholesaler_data = {
                "company_name": user_data["companyName"],
                "gst_number": user_data.get("gstNumber", ""),
                "address": user_data.get("address", ""),
                'years_in_business': user_data.get('yearsInBusiness', ''),
                'company_description': user_data.get('companyDescription', ''),
            }
            
            # Retrieve the wholesaler instance for the user
            wholesaler_instance = get_object_or_404(WholesalerProfile, user=user)
            
            # Update the fields manually
            for field, value in wholesaler_data.items():
                setattr(wholesaler_instance, field, value)
            
            # Save the updated instance
            wholesaler_instance.save()
        
        elif user_data["userType"] == "retailer":
            retailer_data = {
                "shop_name": user_data["shop_name"],
                "contact_number": user_data.get("contactNumber", ""),
                "address": user_data.get("address", ""),
                'gst_number': user_data.get('gstNumber', ''),
                'license_number': user_data.get('licenseNumber', ''),
                'pan_card': user_data.get('panCard', ''),
            }
            
            # Retrieve the retailer instance for the user
            retailer_instance = get_object_or_404(RetailerProfile, user=user)
            
            # Update the fields manually
            for field, value in retailer_data.items():
                setattr(retailer_instance, field, value)
            
            # Save the updated instance
            retailer_instance.save()

        return Response({"detail": "User registered successfully."}, status=status.HTTP_201_CREATED)

    # If the user data is invalid, return errors
    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
