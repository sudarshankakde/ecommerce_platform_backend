# Generated by Django 5.1.1 on 2024-09-29 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0007_remove_productimage_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="wholesalerprofile",
            name="logo",
            field=models.ImageField(blank=True, null=True, upload_to="WholeSaler/"),
        ),
    ]
