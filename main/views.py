
import requests
from payme.views import PaymeWebHookAPIView
from payme.models import PaymeTransactions
from payme.types import response
from orders.models import Order
from payment.settings import TELEGRAM_BOT_TOKEN
from django.core.exceptions import ObjectDoesNotExist

import logging
from click_up.views import ClickWebhook
from click_up.models import ClickTransaction

logger = logging.getLogger('payment')
import html

from .engine import execute_query
from asgiref.sync import async_to_sync


# class PaymeCallBackAPIView(PaymeWebHookAPIView):
#     def copy_and_edit_message(chat_id: int, message_id: int, language: str):
#         try:
#             # 1️⃣ Eski xabarni nusxalash
#             copy_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/copyMessage"
            
#             copy_response = requests.post(copy_url, json={
#                 "chat_id": chat_id,
#                 "from_chat_id": chat_id,
#                 "message_id": message_id
#             })
#             copy_data = copy_response.json()
            
#             if not copy_data.get("ok"):
#                 print(f"Nusxalashda xatolik: {copy_data}")
#                 return
            
#             new_message_id = copy_data["result"]["message_id"]  # Yangi message_id

#             # 2️⃣ Yangi status matnini tanlash
#             new_status = "Status: ✅ To'langan" if language == 'uz' else "Статус: ✅ Оплаченный"

#             # 3️⃣ Eski matnni HTML xavfsiz formatga o'tkazish
#             old_message = copy_data["result"]["text"]  # Nusxalangan xabar matni
#             safe_old_message = html.escape(old_message)  # HTML format uchun xavfsiz qilish

#             # 4️⃣ Yangi xabarni tahrirlash
#             edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"

#             new_text = f"{safe_old_message}\n\n{html.escape(new_status)}"

#             edit_response = requests.post(edit_url, json={
#                 "chat_id": chat_id,
#                 "message_id": new_message_id,
#                 "text": new_text,
#                 "parse_mode": "HTML"
#             })

#             if edit_response.status_code == 200:
#                 print("Xabar muvaffaqiyatli tahrirlandi!")
#             else:
#                 print(f"Tahrirlashda xatolik: {edit_response.text}")

#         except Exception as e:
#             print(f"Xatolik yuz berdi: {e}")


#     def check_perform_transaction(self, params):
#         try:
#             account = self.fetch_account(params)
#             self.validate_amount(account, params.get('amount'))

#             # Fetch the order from the database
#             order_id = account.id  # Assuming account is an Order object
#             try:
#                 order = Order.objects.get(id=order_id)
#             except Order.DoesNotExist:
#                 raise ValueError("Order not found")

#             # Create a CheckPerformTransaction response
#             result = response.CheckPerformTransaction(allow=True)

#             # Loop through the items in the order and add them to the response
#             for item in order.items:
#                 result.add_item(response.Item(
#                     discount=item.get('discount', 0),
#                     title=item.get('title', 'No Title'),
#                     price=item.get('price', 0),
#                     count=item.get('count', 1),
#                     code=item.get('code', '000000'),
#                     units=item.get('units', 'pcs'),
#                     vat_percent=item.get('vat_percent', 0),
#                     package_code=item.get('package_code', '')
#                 ))

#             return result.as_resp()
#         except Exception as e:
#             logger.error("Error in check_perform_transaction: %s", str(e))
#             raise

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
#         try:
#             print("handle_created_payment", result)
#             transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])
#             try:
#                 order = Order.objects.get(id=transaction.account_id)
#                 order.status = Order.OrderStatus.PENDING
#                 order.save()

#             except ObjectDoesNotExist:
#                 print("Order not found for transaction ID", params["id"])
#         except Exception as e:
#             logger.error("Error in handle_created_payment: %s", str(e))
#             raise

    
#     def handle_successfully_payment(self, params, result, *args, **kwargs):
#         # Call the asynchronous method using async_to_sync
#         async_to_sync(self._handle_successfully_payment)(params, result, *args, **kwargs)


#     async def _handle_successfully_payment(self, params, result, *args, **kwargs):
#         try:
#             print("handle_successfully_payment", result)
#             transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])
#             try:
#                 order = Order.objects.get(id=transaction.account_id)
#                 order.status = Order.OrderStatus.PAID
#                 order.is_paid = True
#                 order.payment_method = Order.PaymentMethod.PAYME
#                 order.save()

#                 # Mavjud database'dagi order statusni yangilash
#                 try:
#                     external_order_id = order.bot_order_id  # Order ID'ni olish
#                     query = f"UPDATE order SET status = TRUE WHERE id = {external_order_id}"
#                     await execute_query(query)
#                     print(f"External order {external_order_id} status updated to 'True'")
#                 except Exception as e:
#                     logger.error("Error in handle_successfully_payment: %s", str(e))

#                 # Send a message to the user notifying them about the successful payment
#                 user_chat_id = order.telegram_id  # Assuming `Order` has a `user` with `chat_id`
#                 user_lang = order.user_lang_code
#                 if user_lang == 'uz':
#                     payment_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz muvaffaqiyatli amalga oshirildi.\nJami: {order.total_cost} UZS."
#                 elif user_lang == 'ru':
#                     payment_message = f"Ваш платёж по заказу №{order.id} был успешно завершен.\nВсего: {order.total_cost} UZS."
#                 else:
#                     payment_message = f"Your payment for order #{order.id} has been successfully processed.\nTotal: {order.total_cost} UZS."

#                 # Send a message via the Telegram API
#                 self.send_telegram_message(user_chat_id, payment_message)
#                 self.copy_and_edit_message(chat_id=order.chat_id, message_id=order.message_id, language=order.user_lang_code)

#             except ObjectDoesNotExist:
#                 print("Order not found for transaction ID", params["id"])
#         except Exception as e:
#             logger.error("Error in handle_successfully_payment: %s", str(e))
#             raise

#     def handle_cancelled_payment(self, params, result, *args, **kwargs):
#         try:
#             print("handle_cancelled_payment", result)
#             transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])

#             if transaction.state == PaymeTransactions.CANCELED:
#                 order = Order.objects.get(id=transaction.account_id)
#                 order.is_paid = False
#                 order.save()

#                 try:
#                     order = Order.objects.get(id=transaction.account_id)
#                     order.is_paid = False
#                     order.status = Order.OrderStatus.CANCELLED
#                     order.save()
#                     user_chat_id = order.telegram_id
#                     user_lang = order.user_lang_code
#                     if user_lang == 'uz':
#                         cancellation_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz bekor qilindi.\nIltimos, qayta urinib ko'ring."
#                     elif user_lang == 'ru':
#                         cancellation_message = f"Ваш платёж по заказу №{order.id} был отменён.\nПожалуйста, попробуйте снова."
#                     else:
#                         cancellation_message = f"Your payment for Order #{order.id} was cancelled.\nPlease try again."

#                     # Send a message via the Telegram API
#                     self.send_telegram_message(user_chat_id, cancellation_message)

#                 except ObjectDoesNotExist:
#                     print("Order not found for transaction ID", params["id"])
#         except Exception as e:
#             logger.error("Error in handle_cancelled_payment: %s", str(e))
#             raise



# class ClickWebhookAPIView(ClickWebhook):
#     def copy_and_edit_message(chat_id: int, message_id: int, language: str):
#         try:
#             # 1️⃣ Eski xabarni nusxalash
#             copy_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/copyMessage"
            
#             copy_response = requests.post(copy_url, json={
#                 "chat_id": chat_id,
#                 "from_chat_id": chat_id,
#                 "message_id": message_id
#             })

#             copy_data = copy_response.json()
            
#             if not copy_data.get("ok"):
#                 print(f"Nusxalashda xatolik: {copy_data}")
#                 return
            
#             new_message_id = copy_data["result"]["message_id"]  # Yangi message_id

#             # 2️⃣ Yangi status matnini tanlash
#             new_status = "Status: ✅ To'langan" if language == 'uz' else "Статус: ✅ Оплаченный"

#             # 3️⃣ Eski matnni HTML xavfsiz formatga o'tkazish
#             old_message = copy_data["result"]["text"]  # Nusxalangan xabar matni
#             safe_old_message = html.escape(old_message)  # HTML format uchun xavfsiz qilish

#             # 4️⃣ Yangi xabarni tahrirlash
#             edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"

#             new_text = f"{safe_old_message}\n\n{html.escape(new_status)}"

#             edit_response = requests.post(edit_url, json={
#                 "chat_id": chat_id,
#                 "message_id": new_message_id,
#                 "text": new_text,
#                 "parse_mode": "HTML"
#             })

#             if edit_response.status_code == 200:
#                 print("Xabar muvaffaqiyatli tahrirlandi!")
#             else:
#                 print(f"Tahrirlashda xatolik: {edit_response.text}")

#         except Exception as e:
#             logger.error("Xatolik yuz berdi xabarni edit qilishda: %s", str(e))
#             print(f"Xatolik yuz berdi: {e}")

#     def send_telegram_message(self, chat_id, text):
#         url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#         params = {
#             "chat_id": chat_id,
#             "text": text,
#             "parse_mode": "HTML"
#         }
#         response = requests.post(url, data=params)
#         return response
    
#     def created_payment(self, params, *args, **kwargs):
#         try:
#             transaction = ClickTransaction.objects.get(
#                 transaction_id=params.click_trans_id
#             )
#             try:
#                 order = Order.objects.get(id=transaction.account_id)
#                 order.status = Order.OrderStatus.PENDING
#                 order.payment_method = Order.PaymentMethod.CLICK
#                 order.save()
#             except ObjectDoesNotExist:
#                 print("Order not found for transaction ID", params["id"])
#         except Exception as e:
#             logger.error("Error in created_payment: %s", str(e))
#             raise

#     def successfully_payment(self, params, result, *args, **kwargs):
#         # Call the asynchronous method using async_to_sync
#         async_to_sync(self._successfully_payment)(params, result, *args, **kwargs)



#     async def _successfully_payment(self, params, *args, **kwargs):
#         try:
#             transaction = ClickTransaction.objects.get(
#                 transaction_id=params.click_trans_id
#             )
#             try:
#                 order = Order.objects.get(id=transaction.account_id)
#                 order.status = Order.OrderStatus.PAID
#                 order.is_paid = True
#                 order.payment_method = Order.PaymentMethod.CLICK
#                 order.save()
#                 try:
#                     external_order_id = order.bot_order_id  # Order ID'ni olish
#                     query = f"UPDATE order SET status = TRUE WHERE id = {external_order_id}"
#                     await execute_query(query)
#                     print(f"External order {external_order_id} status updated to 'True'")
#                 except Exception as e:
#                     logger.error("Error in handle_successfully_payment: %s", str(e))

#                 # Send a message to the user notifying them about the successful payment
#                 user_chat_id = order.telegram_id  # Assuming `Order` has a `user` with `chat_id`
#                 user_lang = order.user_lang_code
#                 if user_lang == 'uz':
#                     payment_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz muvaffaqiyatli amalga oshirildi.\nJami: {order.total_cost} UZS."
#                 elif user_lang == 'ru':
#                     payment_message = f"Ваш платёж по заказу №{order.id} был успешно завершен.\nВсего: {order.total_cost} UZS."
#                 else:
#                     payment_message = f"Your payment for order #{order.id} has been successfully processed.\nTotal: {order.total_cost} UZS."

#                 # Send a message via the Telegram API
#                 self.send_telegram_message(user_chat_id, payment_message)
#                 self.copy_and_edit_message(chat_id=order.chat_id, message_id=order.message_id, language=order.user_lang_code)

#             except ObjectDoesNotExist:
#                 print("Order not found for transaction ID", params["id"])
#         except Exception as e:
#             logger.error("Error in successfully_payment: %s", str(e))
#             raise

#     def cancelled_payment(self, params, *args, **kwargs):
#         try:
#             transaction = ClickTransaction.objects.get(
#                 transaction_id=params.click_trans_id
#             )

#             if transaction.state == ClickTransaction.CANCELLED:
#                 try:
#                     order = Order.objects.get(id=transaction.account_id)
#                     order.is_paid = False
#                     order.status = Order.OrderStatus.CANCELLED
#                     order.save()
#                     user_chat_id = order.telegram_id
#                     user_lang = order.user_lang_code
#                     if user_lang == 'uz':
#                         cancellation_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz bekor qilindi.\nIltimos, qayta urinib ko'ring."
#                     elif user_lang == 'ru':
#                         cancellation_message = f"Ваш платёж по заказу №{order.id} был отменён.\nПожалуйста, попробуйте снова."
#                     else:
#                         cancellation_message = f"Your payment for Order #{order.id} was cancelled.\nPlease try again."

#                     # Send a message via the Telegram API
#                     self.send_telegram_message(user_chat_id, cancellation_message)

#                 except ObjectDoesNotExist:
#                     print("Order not found for transaction ID", params["id"])
#         except Exception as e:
#             logger.error("Error in cancelled_payment: %s", str(e))
#             raise

class PaymeCallBackAPIView(PaymeWebHookAPIView):
    def copy_and_edit_message(self, chat_id: int, message_id: int, language: str):
        try:
            # 1️⃣ Eski xabarni nusxalash
            copy_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/copyMessage"
            
            copy_response = requests.post(copy_url, json={
                "chat_id": chat_id,
                "from_chat_id": chat_id,
                "message_id": message_id
            })
            copy_data = copy_response.json()
            
            if not copy_data.get("ok"):
                print(f"Nusxalashda xatolik: {copy_data}")
                return
            
            new_message_id = copy_data["result"]["message_id"]  # Yangi message_id

            # 2️⃣ Yangi status matnini tanlash
            new_status = "Status: ✅ To'langan" if language == 'uz' else "Статус: ✅ Оплаченный"

            # 3️⃣ Eski matnni HTML xavfsiz formatga o'tkazish
            old_message = copy_data["result"]["text"]  # Nusxalangan xabar matni
            safe_old_message = html.escape(old_message)  # HTML format uchun xavfsiz qilish

            # 4️⃣ Yangi xabarni tahrirlash
            edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"

            new_text = f"{safe_old_message}\n\n{html.escape(new_status)}"

            edit_response = requests.post(edit_url, json={
                "chat_id": chat_id,
                "message_id": new_message_id,
                "text": new_text,
                "parse_mode": "HTML"
            })

            if edit_response.status_code == 200:
                print("Xabar muvaffaqiyatli tahrirlandi!")
            else:
                print(f"Tahrirlashda xatolik: {edit_response.text}")

        except Exception as e:
            logger.error("Xatolik yuz berdi xabarni edit qilishda: %s", str(e))
            print(f"Xatolik yuz berdi: {e}")

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
        # Call the asynchronous method using async_to_sync
        async_to_sync(self._handle_successfully_payment)(params, result, *args, **kwargs)

    async def _handle_successfully_payment(self, params, result, *args, **kwargs):
        try:
            print("handle_successfully_payment", result)
            transaction = PaymeTransactions.get_by_transaction_id(transaction_id=params["id"])
            try:
                order = Order.objects.get(id=transaction.account_id)
                order.status = Order.OrderStatus.PAID
                order.is_paid = True
                order.payment_method = Order.PaymentMethod.PAYME
                order.save()

                # Mavjud database'dagi order statusni yangilash
                try:
                    external_order_id = order.bot_order_id  # Order ID'ni olish
                    query = f"UPDATE order SET status = TRUE WHERE id = {external_order_id}"
                    await execute_query(query)
                    print(f"External order {external_order_id} status updated to 'True'")
                except Exception as e:
                    logger.error("Error in handle_successfully_payment: %s", str(e))

                # Send a message to the user notifying them about the successful payment
                user_chat_id = order.telegram_id  # Assuming `Order` has a `user` with `chat_id`
                user_lang = order.user_lang_code
                if user_lang == 'uz':
                    payment_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz muvaffaqiyatli amalga oshirildi.\nJami: {order.total_cost} UZS."
                elif user_lang == 'ru':
                    payment_message = f"Ваш платёж по заказу №{order.id} был успешно завершен.\nВсего: {order.total_cost} UZS."
                else:
                    payment_message = f"Your payment for order #{order.id} has been successfully processed.\nTotal: {order.total_cost} UZS."

                # Send a message via the Telegram API
                self.send_telegram_message(user_chat_id, payment_message)
                self.copy_and_edit_message(chat_id=order.chat_id, message_id=order.message_id, language=order.user_lang_code)

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
                    user_chat_id = order.telegram_id
                    user_lang = order.user_lang_code
                    if user_lang == 'uz':
                        cancellation_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz bekor qilindi.\nIltimos, qayta urinib ko'ring."
                    elif user_lang == 'ru':
                        cancellation_message = f"Ваш платёж по заказу №{order.id} был отменён.\nПожалуйста, попробуйте снова."
                    else:
                        cancellation_message = f"Your payment for Order #{order.id} was cancelled.\nPlease try again."

                    # Send a message via the Telegram API
                    self.send_telegram_message(user_chat_id, cancellation_message)

                except ObjectDoesNotExist:
                    print("Order not found for transaction ID", params["id"])
        except Exception as e:
            logger.error("Error in handle_cancelled_payment: %s", str(e))
            raise


class ClickWebhookAPIView(ClickWebhook):
    def copy_and_edit_message(self, chat_id: int, message_id: int, language: str):
        try:
            # 1️⃣ Eski xabarni nusxalash
            copy_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/copyMessage"
            
            copy_response = requests.post(copy_url, json={
                "chat_id": chat_id,
                "from_chat_id": chat_id,
                "message_id": message_id
            })

            copy_data = copy_response.json()
            
            if not copy_data.get("ok"):
                print(f"Nusxalashda xatolik: {copy_data}")
                return
            
            new_message_id = copy_data["result"]["message_id"]  # Yangi message_id

            # 2️⃣ Yangi status matnini tanlash
            new_status = "Status: ✅ To'langan" if language == 'uz' else "Статус: ✅ Оплаченный"

            # 3️⃣ Eski matnni HTML xavfsiz formatga o'tkazish
            old_message = copy_data["result"]["text"]  # Nusxalangan xabar matni
            safe_old_message = html.escape(old_message)  # HTML format uchun xavfsiz qilish

            # 4️⃣ Yangi xabarni tahrirlash
            edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"

            new_text = f"{safe_old_message}\n\n{html.escape(new_status)}"

            edit_response = requests.post(edit_url, json={
                "chat_id": chat_id,
                "message_id": new_message_id,
                "text": new_text,
                "parse_mode": "HTML"
            })

            if edit_response.status_code == 200:
                print("Xabar muvaffaqiyatli tahrirlandi!")
            else:
                print(f"Tahrirlashda xatolik: {edit_response.text}")

        except Exception as e:
            logger.error("Xatolik yuz berdi xabarni edit qilishda: %s", str(e))
            print(f"Xatolik yuz berdi: {e}")

    def send_telegram_message(self, chat_id, text):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=params)
        return response
    
    def created_payment(self, params, *args, **kwargs):
        try:
            transaction = ClickTransaction.objects.get(
                transaction_id=params.click_trans_id
            )
            try:
                order = Order.objects.get(id=transaction.account_id)
                order.status = Order.OrderStatus.PENDING
                order.payment_method = Order.PaymentMethod.CLICK
                order.save()
            except ObjectDoesNotExist:
                print("Order not found for transaction ID", params["id"])
        except Exception as e:
            logger.error("Error in created_payment: %s", str(e))
            raise

    def successfully_payment(self, params, result, *args, **kwargs):
        # Call the asynchronous method using async_to_sync
        async_to_sync(self._successfully_payment)(params, result, *args, **kwargs)

    async def _successfully_payment(self, params, *args, **kwargs):
        try:
            transaction = ClickTransaction.objects.get(
                transaction_id=params.click_trans_id
            )
            try:
                order = Order.objects.get(id=transaction.account_id)
                order.status = Order.OrderStatus.PAID
                order.is_paid = True
                order.payment_method = Order.PaymentMethod.CLICK
                order.save()
                try:
                    external_order_id = order.bot_order_id  # Order ID'ni olish
                    query = f"UPDATE order SET status = TRUE WHERE id = {external_order_id}"
                    await execute_query(query)
                    print(f"External order {external_order_id} status updated to 'True'")
                except Exception as e:
                    logger.error("Error in handle_successfully_payment: %s", str(e))

                # Send a message to the user notifying them about the successful payment
                user_chat_id = order.telegram_id  # Assuming `Order` has a `user` with `chat_id`
                user_lang = order.user_lang_code
                if user_lang == 'uz':
                    payment_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz muvaffaqiyatli amalga oshirildi.\nJami: {order.total_cost} UZS."
                elif user_lang == 'ru':
                    payment_message = f"Ваш платёж по заказу №{order.id} был успешно завершен.\nВсего: {order.total_cost} UZS."
                else:
                    payment_message = f"Your payment for order #{order.id} has been successfully processed.\nTotal: {order.total_cost} UZS."

                # Send a message via the Telegram API
                self.send_telegram_message(user_chat_id, payment_message)
                self.copy_and_edit_message(chat_id=order.chat_id, message_id=order.message_id, language=order.user_lang_code)

            except ObjectDoesNotExist:
                print("Order not found for transaction ID", params["id"])
        except Exception as e:
            logger.error("Error in successfully_payment: %s", str(e))
            raise

    def cancelled_payment(self, params, *args, **kwargs):
        try:
            transaction = ClickTransaction.objects.get(
                transaction_id=params.click_trans_id
            )

            if transaction.state == ClickTransaction.CANCELLED:
                try:
                    order = Order.objects.get(id=transaction.account_id)
                    order.is_paid = False
                    order.status = Order.OrderStatus.CANCELLED
                    order.save()
                    user_chat_id = order.telegram_id
                    user_lang = order.user_lang_code
                    if user_lang == 'uz':
                        cancellation_message = f"Buyurtma raqami #{order.id} uchun to'lovingiz bekor qilindi.\nIltimos, qayta urinib ko'ring."
                    elif user_lang == 'ru':
                        cancellation_message = f"Ваш платёж по заказу №{order.id} был отменён.\nПожалуйста, попробуйте снова."
                    else:
                        cancellation_message = f"Your payment for Order #{order.id} was cancelled.\nPlease try again."

                    # Send a message via the Telegram API
                    self.send_telegram_message(user_chat_id, cancellation_message)

                except ObjectDoesNotExist:
                    print("Order not found for transaction ID", params["id"])
        except Exception as e:
            logger.error("Error in cancelled_payment: %s", str(e))
            raise