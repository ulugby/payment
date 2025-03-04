from django.db import models



class Order(models.Model):

    class PaymentMethod(models.TextChoices):
        CLICK = "click", "Click"
        PAYME = "payme", "Payme"


    class OrderStatus(models.TextChoices):
        CREATED = "created", "Created"
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"


    customer_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    # total_cost = models.BigIntegerField()

    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="amount")

    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, verbose_name="payment method", null=True, blank=True
    )
    # payment_method = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING, verbose_name='status'
    )
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chat_id = models.PositiveBigIntegerField(default='2083239343')
    items = models.JSONField(default=list)  # Added items field to store order items
    user_lang_code = models.CharField(max_length=10, default='uz')

    def __str__(self):
        return f"Order #{self.id} - {self.total_cost} - {self.status}"