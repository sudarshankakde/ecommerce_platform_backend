# Generated by Django 5.1.1 on 2024-09-29 03:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0006_product_images_alter_productimage_product"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="productimage",
            name="product",
        ),
    ]
