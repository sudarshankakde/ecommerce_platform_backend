# Generated by Django 5.1.1 on 2024-10-06 15:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0012_alter_order_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="retailerprofile",
            name="license_number",
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="retailerprofile",
            name="pan_card",
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="retailerprofile",
            name="verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="api.category",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="creator",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
