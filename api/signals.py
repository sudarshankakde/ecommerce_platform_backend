from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import RetailerProfile, WholesalerProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if instance.is_wholesaler:
        # Create or update wholesaler profile
        WholesalerProfile.objects.update_or_create(
            user=instance,
            defaults={
                'company_name': '',  # Initialize with default data or leave empty
                'gst_number': '',
                'address': '',
                'company_description': '',
                'years_in_business': None,
                'total_sales': 0,
                'rating': 0.0,
                'verified': False,
            }
        )
    elif instance.is_retailer:
        # Create or update retailer profile
        RetailerProfile.objects.update_or_create(
            user=instance,
            defaults={
                'shop_name': '',  # Initialize with default data or leave empty
                'contact_number': '',
                'address': '',
                'gst_number': '',
            }
        )
