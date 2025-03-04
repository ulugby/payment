# Generated by Django 5.1.6 on 2025-02-13 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_remove_orders_pay_link_orders_address_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("customer_name", models.CharField(max_length=255)),
                ("address", models.CharField(max_length=255)),
                ("total_cost", models.BigIntegerField()),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_method", models.CharField(max_length=255)),
                ("is_paid", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(default="Pending", max_length=20)),
            ],
        ),
        migrations.DeleteModel(
            name="Orders",
        ),
    ]
