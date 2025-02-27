from .serializers import OrderSerializer

from rest_framework import views, response
from payme import Payme
from payment.settings import PAYME_ID
from rest_framework import status

payme = Payme(payme_id=PAYME_ID)

class OrderCreate(views.APIView):

    serializer_class = OrderSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save order with items
        order = serializer.save()

        result = {
            "order": serializer.data
        }
        payment_method = serializer.validated_data["payment_method"].lower()

        # if payment_method == 'payme':
        #     payment_link = payme.initializer.generate_pay_link(
        #         id=order.id,
        #         amount=order.total_cost,
        #         return_url="https://t.me/JononChickenBot"
        #     )
        #     result["payment_link"] = payment_link
        
        # return response.Response(result)
    
        if payment_method == 'payme':
            try:
                # Payme API orqali to'lov havolasini yaratish
                payment_link = payme.initializer.generate_pay_link(
                    id=order.id,
                    amount=order.total_cost,
                    return_url="https://t.me/JononChickenBot"
                )
                result["payment_link"] = payment_link
            except Exception as e:
                # Payme API bilan bog'liq xatoliklarni ushlash
                return response.Response(
                    {"error": f"Failed to generate payment link: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return response.Response(result, status=status.HTTP_201_CREATED)


# class OrderCreate(views.APIView):

#     serializer_class = OrderSerializer
    
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         serializer.save()

#         result = {
#             "order":serializer.data
#         }

#         if serializer.data["payment_method"] == 'payme':
#             payment_link = payme.initializer.generate_pay_link(
#                 id=serializer.data["id"],
#                 amount=serializer.data["total_cost"],
#                 return_url="https://t.me/JononChickenBot"
#             )
#             result["payment_link"] = payment_link
        
#         return response.Response(result)
