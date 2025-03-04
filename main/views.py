
import requests
from payme.views import PaymeWebHookAPIView
from payme.models import PaymeTransactions
from payme.types import response
from orders.models import Order
from payment.settings import TELEGRAM_BOT_TOKEN
from django.core.exceptions import ObjectDoesNotExist

import logging
from clickuz import ClickUz
from clickuz.views import ClickUzMerchantAPIView


logger = logging.getLogger('payment')

# class PaymeCallBackAPIView(PaymeWebHookAPIView):

#     def check_perform_transaction(self, params):
#         account = self.fetch_account(params)
#         self.validate_amount(account, params.get('amount'))

#         # Fetch the order from the database
#         order_id = account.id  # Assuming account is an Order object
#         try:
#             order = Order.objects.get(id=order_id)
#         except Order.DoesNotExist:
#             raise ValueError("Order not found")

#         # Create a CheckPerformTransaction response
#         result = response.CheckPerformTransaction(allow=True)

#         # Loop through the items in the order and add them to the response
#         for item_data in order.items:
#             item = response.Item(
#                 discount=item_data.get('discount', 0),  # Default to 0 if discount is not provided
#                 title=item_data.get('title', 'No Title'),  # Default title if not provided
#                 price=item_data.get('price', 0),  # Default to 0 if price is not provided
#                 count=item_data.get('count', 1),  # Default to 1 if count is not provided
#                 code=item_data.get('code', '000000'),  # Default code if not provided
#                 units=item_data.get('units', 'pcs'),  # Default units if not provided
#                 vat_percent=item_data.get('vat_percent', 0),  # Default to 0 if VAT is not provided
#                 package_code=item_data.get('package_code', '')  # Optional, default to empty string
#             )
#             result.add_item(item)

#         return result.as_resp()
    
#     def send_telegram_message(self, chat_id, text):
#         url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#         params = {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": "HTML"
#         }
#         response = requests.post(url, data=params)
#         return response
    
#     def handle_created_payment(self, params, result, *args, **kwargs):
#         print("handle_created_payment", result)

#         transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])
#         try:
#             order = Order.objects.get(id=transaction.account_id)
#             order.status = Order.OrderStatus.PENDING
#             order.save()

#         except ObjectDoesNotExist:
#             print("Order not found for transaction ID", params["id"])

#     def handle_successfully_payment(self, params, result, *args, **kwargs):
#         print("handle_successfully_payment",result)

#         transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])
#         try:
#             order = Order.objects.get(id=transaction.account_id)
#             order.status = Order.OrderStatus.PAID
#             order.is_paid = True
#             order.payment_method = Order.PaymentMethod.PAYME
#             order.save()
#             # Send a message to the user notifying them about the successful payment
#             user_chat_id = order.chat_id  # Assuming `Order` has a `user` with `chat_id`
#             user_lang = order.user_lang_code
#             if user_lang == 'uz':
#                 payment_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz muvaffaqiyatli amalga oshirildi.\nJami: {order.total_cost} UZS."
#             if user_lang == 'ru':
#                 payment_message = f"Ваш платёж по заказу №{order.id} был успешно завершен.\nВсего: {order.total_cost} UZS."

#             # Send a message via the Telegram API
#             self.send_telegram_message(user_chat_id, payment_message)

#         except ObjectDoesNotExist:
#             print("Order not found for transaction ID", params["id"])

#     def handle_cancelled_payment(self, params, result, *args, **kwargs):
#         print("handle_cancelled_payment", result)
#         transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])

#         if transaction.state == PaymeTransactions.CANCELED:
#             order = Order.objects.get(id=transaction.account_id)
#             order.is_paid = False
#             order.save()

#             try:
#                 order = Order.objects.get(id=transaction.account_id)
#                 order.is_paid = False
#                 order.status = Order.OrderStatus.CANCELLED
#                 order.save()

#                 # Send a cancellation message to the user
#                 user_chat_id = order.chat_id  # Assuming `Order` has a `user` with `chat_id`
#                 cancellation_message = f"Your payment for Order #{order.id} was cancelled.\nPlease try again."

#                 # Send a message via the Telegram API
#                 self.send_telegram_message(user_chat_id, cancellation_message)

#             except ObjectDoesNotExist:
#                 print("Order not found for transaction ID", params["id"])



# class OrderCheckAndPayment(ClickUz):

#     def send_telegram_message(self, chat_id, text):
#         url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#         params = {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": "HTML"
#         }
#         response = requests.post(url, data=params)
#         return response

#     def check_order(self, order_id: str, amount: str):
#         orders = Order.objects.filter(id=order_id)
#         if orders.exists():
#             order = orders.first()
#             if float(order.total_cost) == float(amount):
#                 return self.ORDER_FOUND
#             else:
#                 return self.INVALID_AMOUNT
#         else:
#             return self.ORDER_NOT_FOUND

#     def successfully_payment(self, order_id: str, transaction: object):
#         orders = Order.objects.filter(id=order_id)
#         if orders.exists():
#             order = orders.first()
#             order.status = Order.OrderStatus.PAID
#             order.is_paid = True
#             order.payment_method = Order.PaymentMethod.CLICK
#             order.save()

#             user_chat_id = order.chat_id
#             user_lang = order.user_lang_code
#             if user_lang == 'uz':
#                 payment_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz muvaffaqiyatli amalga oshirildi.\nJami: {order.total_cost} UZS."
#             if user_lang == 'ru':
#                 payment_message = f"Ваш платёж по заказу №{order.id} был успешно завершен.\nВсего: {order.total_cost} UZS."
            
#             # Send a message via the Telegram API
#             self.send_telegram_message(user_chat_id, payment_message)

#             return self.ORDER_FOUND
#         else:
#             return self.ORDER_NOT_FOUND

class PaymeCallBackAPIView(PaymeWebHookAPIView):

    def check_perform_transaction(self, params):
        try:
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
            for item in order.items:
                result.add_item(response.Item(
                    discount=item.get('discount', 0),
                    title=item.get('title', 'No Title'),
                    price=item.get('price', 0),
                    count=item.get('count', 1),
                    code=item.get('code', '000000'),
                    units=item.get('units', 'pcs'),
                    vat_percent=item.get('vat_percent', 0),
                    package_code=item.get('package_code', '')
                ))

            return result.as_resp()
        except Exception as e:
            logger.error("Error in check_perform_transaction: %s", str(e))
            raise

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
        try:
            print("handle_created_payment", result)
            transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])
            try:
                order = Order.objects.get(id=transaction.account_id)
                order.status = Order.OrderStatus.PENDING
                order.save()

            except ObjectDoesNotExist:
                print("Order not found for transaction ID", params["id"])
        except Exception as e:
            logger.error("Error in handle_created_payment: %s", str(e))
            raise

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        try:
            print("handle_successfully_payment", result)
            transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])
            try:
                order = Order.objects.get(id=transaction.account_id)
                order.status = Order.OrderStatus.PAID
                order.is_paid = True
                order.payment_method = Order.PaymentMethod.PAYME
                order.save()
                # Send a message to the user notifying them about the successful payment
                user_chat_id = order.chat_id  # Assuming `Order` has a `user` with `chat_id`
                user_lang = order.user_lang_code
                if user_lang == 'uz':
                    payment_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz muvaffaqiyatli amalga oshirildi.\nJami: {order.total_cost} UZS."
                if user_lang == 'ru':
                    payment_message = f"Ваш платёж по заказу №{order.id} был успешно завершен.\nВсего: {order.total_cost} UZS."

                # Send a message via the Telegram API
                self.send_telegram_message(user_chat_id, payment_message)

            except ObjectDoesNotExist:
                print("Order not found for transaction ID", params["id"])
        except Exception as e:
            logger.error("Error in handle_successfully_payment: %s", str(e))
            raise

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        try:
            print("handle_cancelled_payment", result)
            transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])

            if transaction.state == PaymeTransactions.CANCELED:
                order = Order.objects.get(id=transaction.account_id)
                order.is_paid = False
                order.save()

                try:
                    order = Order.objects.get(id=transaction.account_id)
                    order.is_paid = False
                    order.status = Order.OrderStatus.CANCELLED
                    order.save()

                    # Send a cancellation message to the user
                    user_chat_id = order.chat_id  # Assuming `Order` has a `user` with `chat_id`
                    cancellation_message = f"Your payment for Order #{order.id} was cancelled.\nPlease try again."

                    # Send a message via the Telegram API
                    self.send_telegram_message(user_chat_id, cancellation_message)

                except ObjectDoesNotExist:
                    print("Order not found for transaction ID", params["id"])
        except Exception as e:
            logger.error("Error in handle_cancelled_payment: %s", str(e))
            raise

class OrderCheckAndPayment(ClickUz):

    def send_telegram_message(self, chat_id, text):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=params)
        logger.info("Telegram message sent: %s", response.json())
        return response

    def check_order(self, order_id: str, amount: str):
        try:
            logger.debug("Checking order with ID: %s and amount: %s", order_id, amount)
            orders = Order.objects.filter(id=order_id)
            if orders.exists():
                order = orders.first()
                if float(order.total_cost) == float(amount):
                    logger.debug("Order found and amount is valid")
                    return self.ORDER_FOUND
                else:
                    logger.debug("Invalid amount")
                    return self.INVALID_AMOUNT
            else:
                logger.debug("Order not found")
                return self.ORDER_NOT_FOUND
        except Exception as e:
            logger.error("Error in check_order: %s", str(e))
            raise

    def successfully_payment(self, order_id: str, transaction: object):
        try:
            logger.debug("Processing successful payment for order ID: %s", order_id)
            orders = Order.objects.filter(id=order_id)
            if orders.exists():
                order = orders.first()
                order.status = Order.OrderStatus.PAID
                order.is_paid = True
                order.payment_method = Order.PaymentMethod.CLICK
                order.save()

                user_chat_id = order.chat_id  # Assuming `Order` has a `user` with `chat_id`
                user_lang = order.user_lang_code
                if user_lang == 'uz':
                    payment_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz muvaffaqiyatli amalga oshirildi.\nJami: {order.total_cost} UZS."
                elif user_lang == 'ru':
                    payment_message = f"Ваш платёж по заказу №{order.id} был успешно завершен.\nВсего: {order.total_cost} UZS."
                else:
                    payment_message = f"Your payment for order #{order.id} has been successfully processed.\nTotal: {order.total_cost} UZS."

                # Send a message via the Telegram API
                self.send_telegram_message(user_chat_id, payment_message)

                logger.debug("Payment processed and Telegram message sent")
                return self.ORDER_FOUND
            else:
                logger.debug("Order not found")
                return self.ORDER_NOT_FOUND
        except Exception as e:
            logger.error("Error in successfully_payment: %s", str(e))
            raise

class ClickCallBackAPIView(ClickUzMerchantAPIView):
    VALIDATE_CLASS = OrderCheckAndPayment