# Generated by Django 5.1.1 on 2024-10-01 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0008_wholesalerprofile_logo"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="address",
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="city",
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="order",
            name="name",
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="order_notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="portal_code",
            field=models.DecimalField(decimal_places=0, default=1, max_digits=6),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="state",
            field=models.CharField(default=1, max_length=25),
            preserve_default=False,
        ),
    ]
