# Generated by Django 5.1.1 on 2024-10-16 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0016_alter_brand_icon_alter_category_icon_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="brand",
            name="icon",
            field=models.ImageField(
                blank=True, null=True, upload_to="WholeSetail/Brand_images/"
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="icon",
            field=models.ImageField(
                blank=True, null=True, upload_to="WholeSetail/category_images/"
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=models.ImageField(upload_to="WholeSetail/product_images/"),
        ),
        migrations.AlterField(
            model_name="wholesalerprofile",
            name="logo",
            field=models.ImageField(
                blank=True, null=True, upload_to="WholeSetail/WholeSaler/"
            ),
        ),
    ]