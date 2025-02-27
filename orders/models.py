from django.db import models



class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    total_cost = models.BigIntegerField()
    payment_method = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chat_id = models.PositiveBigIntegerField(default='2083239343')
    items = models.JSONField(default=list)  # Added items field to store order items

    def __str__(self):
        return f"Order #{self.id} - {self.total_cost}"