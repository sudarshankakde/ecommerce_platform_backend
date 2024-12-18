# Generated by Django 5.1.1 on 2024-10-16 01:25

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0017_alter_brand_icon_alter_category_icon_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="brand",
            name="icon",
            field=cloudinary.models.CloudinaryField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="WholeSetail/Brand_icon",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="icon",
            field=cloudinary.models.CloudinaryField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="WholeSetail/category_images",
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=cloudinary.models.CloudinaryField(
                max_length=255, verbose_name="image"
            ),
        ),
        migrations.AlterField(
            model_name="wholesalerprofile",
            name="logo",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True, verbose_name="logo"
            ),
        ),
    ]
