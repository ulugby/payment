# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from payme import Payme
# from payme.views import PaymeWebHookAPIView
# from aiogram import Bot
# import os
# import asyncio
# import json
# import redis
# from orders.models import Order
# from orders.serializers import OrderSerializer

# import redis.asyncio as aioredis 


# redis = aioredis.from_url("redis://localhost", decode_responses=True)  

# # Initialize Telegram bot
# bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

# def generate_payment_link(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     payme = Payme(
#         payme_id="67a99c39320c36e44ded214a",
#         payme_key="3Nt7#grfrvT4ZuEY3e314qzSd7pbo3@hzPzS",
#         is_test_mode=True  # Set to False for production mode
#     )
#     # Convert amount to cents
#     amount_in_cents = order.total_cost
#     pay_link = payme.initializer.generate_pay_link(
#         id=order.id,
#         amount=amount_in_cents,
#         return_url="https://2d98-95-214-211-146.ngrok-free.app/payment/update/"
#     )
#     order.pay_link = pay_link
#     order.save()
#     return JsonResponse({"pay_link": pay_link})

# class PaymeCallBackAPIView(PaymeWebHookAPIView):
#     def handle_created_payment(self, params, result, *args, **kwargs):
#         pass

#     async def handle_successfully_payment(self, params, result, *args, **kwargs):
#         try:
#             order_id = params.get("account").get("order_id")
#             order = get_object_or_404(Order, id=order_id)

#             # Update order status
#             order.status = "Paid"
#             order.is_paid = True
#             order.save()

#             user_id = order_id  # Assuming user ID is the same as order ID for simplicity
#             await notify_user(user_id, "To'lov muvaffaqiyatli amalga oshirildi ✅")
#         except Order.DoesNotExist:
#             return JsonResponse({"error": "Order does not exist"}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     async def handle_cancelled_payment(self, params, result, *args, **kwargs):
#         try:
#             order_id = params.get("account").get("order_id")
#             order = get_object_or_404(Order, id=order_id)

#             # Update order status
#             order.status = "Cancelled"
#             order.save()

#             user_id = order_id  # Assuming user ID is the same as order ID for simplicity
#             await notify_user(user_id, "To'lov bekor qilindi ❌")
#         except Order.DoesNotExist:
#             return JsonResponse({"error": "Order does not exist"}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)

# def get_message_id_from_redis(user_id):
#     key = f"user_message_id:{user_id}"
#     order_data = redis.get(key)
#     if order_data:
#         return json.loads(order_data)
#     return None


import requests
from payme.views import PaymeWebHookAPIView
from payme.models import PaymeTransactions
from payme.types import response
from orders.models import Order
from payment.settings import TELEGRAM_BOT_TOKEN, PAYME_ID, PAYME_KEY, PAYME_ACCOUNT_MODEL, PAYME_ACCOUNT_FIELD, PAYME_AMOUNT_FIELD, PAYME_ONE_TIME_PAYMENT
from django.core.exceptions import ObjectDoesNotExist

class PaymeCallBackAPIView(PaymeWebHookAPIView):

    def check_perform_transaction(self, params):
        account = self.fetch_account(params)
        self.validate_amount(account, params.get('amount'))

        # Fetch the order from the database
        order_id = account.id  # Assuming account is an Order object
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order not found")

        # Create a CheckPerformTransaction response
        result = response.CheckPerformTransaction(allow=True)

        # Loop through the items in the order and add them to the response
        for item_data in order.items:
            item = response.Item(
                discount=item_data.get('discount', 0),  # Default to 0 if discount is not provided
                title=item_data.get('title', 'No Title'),  # Default title if not provided
                price=item_data.get('price', 0),  # Default to 0 if price is not provided
                count=item_data.get('count', 1),  # Default to 1 if count is not provided
                code=item_data.get('code', '000000'),  # Default code if not provided
                units=item_data.get('units', 'pcs'),  # Default units if not provided
                vat_percent=item_data.get('vat_percent', 0),  # Default to 0 if VAT is not provided
                package_code=item_data.get('package_code', '')  # Optional, default to empty string
            )
            result.add_item(item)

        return result.as_resp()
    
    def send_telegram_message(self, chat_id, text):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=params)
        return response
    def handle_created_payment(self, params, result, *args, **kwargs):
        print("handle_created_payment", result)


    def handle_successfully_payment(self, params, result, *args, **kwargs):
        print("handle_successfully_payment",result)

        transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])
        try:
            order = Order.objects.get(id=transaction.account_id)
            order.is_paid = True
            order.save()

            # Send a message to the user notifying them about the successful payment
            user_chat_id = order.chat_id  # Assuming `Order` has a `user` with `chat_id`
            payment_message = f"Your payment for Order #{order.id} has been successfully completed.\nTotal: {order.total_cost} UZS."

            # Send a message via the Telegram API
            self.send_telegram_message(user_chat_id, payment_message)

        except ObjectDoesNotExist:
            print("Order not found for transaction ID", params["id"])

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        print("handle_cancelled_payment", result)
        transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])

        if transaction.state == PaymeTransactions.CANCELED:
            order = Order.objects.get(id=transaction.account_id)
            order.is_paid = False
            order.save()

            try:
                order = Order.objects.get(id=transaction.account_id)
                order.is_paid = False
                order.save()

                # Send a cancellation message to the user
                user_chat_id = order.chat_id  # Assuming `Order` has a `user` with `chat_id`
                cancellation_message = f"Your payment for Order #{order.id} was cancelled.\nPlease try again."

                # Send a message via the Telegram API
                self.send_telegram_message(user_chat_id, cancellation_message)

            except ObjectDoesNotExist:
                print("Order not found for transaction ID", params["id"])

# async def notify_user(user_id, message):
#     await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
