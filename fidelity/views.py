from django.shortcuts import render
from django.http import HttpResponse
from .import plugin_Ecom, getOrderStatus, createOrder
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from product.models import Product, CatalogCategory, CatalogSubCategory, Order, OrderItem, ProductBrand, Wishlist, OrderItem
import requests
from accounts.models import Address, User,PrimeMemberPlan,UserSubscription,Cart
# from customer.models import NonPrime ,Prime
from order.models import OrderPaymentDetail,PrimeOrderPaymentDetail,OrderLog
from product.models import Order,ApplyCoupon
from datetime import datetime
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta
import re
from django.db.models import Max

# Create your views here.
class createorderView(GenericAPIView):
 def get(self, request, format=None):
        # Your logic to create an order using createOrder.py
        order_id = request.GET.get('order_id')
        order_details = Order.objects.filter(order_id=order_id).first()
        if order_details:

            serialized_orders = []
            # Loop through each order and append its data to the list
            # for order in order_details:
            user_address_details = Address.objects.filter(id=order_details.user_address_id_id).first()
            user_details = User.objects.filter(id=order_details.user_id).first()
            user_address123 =[]
            user_detailss =[]

            user_all_details ={
                    "mobile":user_details.mobile,
                    "full_name":user_details.full_name,
                    "email":user_details.email
            }
            user_detailss.append(user_all_details)
            user_address={
                    "user_address":user_address_details.bulding_name,
                    "city":user_address_details.city,
                    "pincode":user_address_details.pincode,
                    "street_address":user_address_details.street_address,
                    "state":user_address_details.state,
                    "house_no":user_address_details.house_no
            }
            user_address123.append(user_address)
            serialized_order = {
                    "order_id": order_details.order_id,
                    "total": order_details.total,
                    "user_address_id": order_details.user_address_id_id,
                    "user_id": order_details.user_id,
                    "user_address_details":user_address123,
                    "user_detailss":user_detailss
                    # Add more fields as needed
                }
            price_str = order_details.total
            price_float = float(price_str)
            has_decimal = price_float % 1 != 0
            if has_decimal:
                priceamt = price_float
            else:
               priceamt = "{:.2f}".format(float(price_float))
            price1 = str(priceamt)
            amt = price1.replace(".", "")
            serialized_orders.append(serialized_order)
            Create_Order = "CreateOrder"
            EN = "EN"
            merchant= "TEST_ECOM531"
            amount = amt
            description = "order created"
            currency = '978'
            approve_url = "/testshopPageReturn.jsp"
            CancelURL = "/testshopPageReturn.jsp"
            decline_url = "/testshopPageReturn.jsp"
            order_type = "Purchase"
            shipping_country = "Ghana"
            delivery_period = 32
            merchant_ext_id = "E643C1426056"
            email = serialized_orders[0]['user_detailss'][0]['email']
            phone = serialized_orders[0]['user_detailss'][0]['mobile']
            shipping_city = serialized_orders[0]['user_address_details'][0]['city']
            shipping_state = serialized_orders[0]['user_address_details'][0]['state']
            shipping_zip_code = serialized_orders[0]['user_address_details'][0]['pincode']
            shipping_address = serialized_orders[0]['user_address_details'][0]['user_address']



            result = createOrder.create_order(Create_Order, EN,  merchant ,amount , currency,  description, approve_url, CancelURL, decline_url, order_type, email, phone, shipping_country,shipping_city, delivery_period, merchant_ext_id, shipping_state,shipping_zip_code, shipping_address)


            if result:
                return Response({'status':True,'msg':'order found','data':result})
            else:
                return Response({'status':False,'msg':'order not found', 'data':[]})
        else:
            return Response ({'status':False,'msg':'order not found', 'data':[]})

class getorderstatusview(GenericAPIView):
    def get(self, request, format=None):
        # Your logic to get order status using getOrderStatus.py
        order_id  = request.GET.get('order_id')
        session_id  = request.GET.get('session_id')
        operation ="GetOrderStatus"
        language ="EN"
        merchant = "TEST_ECOM531"
        result = getOrderStatus.get_order_status(operation, language, merchant,order_id,session_id)
        # Handle the result and return an appropriate HTTP response
        if result:
            return HttpResponse(result)
        else:
            return HttpResponse("Failed to retrieve order status")

class getorderinformation(GenericAPIView):
    def post(self, request, format=None):
        result =  OrderPaymentDetail.objects.create(

            OrderID = request.data.get('order_id', None),
            SessionId  = request.data.get('session_id',None),
            RRN=request.data.get('RRN'),
            OrderStatus=request.data.get('OrderStatus', None),
            TypeCard=request.data.get('TypeCard', None),
            PurchaseAmountScr=request.data.get('PurchaseAmountScr', None),
            OrderDescription=request.data.get('OrderDescription', None),
            TotalAmountScr=request.data.get('TotalAmountScr', None),
            TranDateTime=request.data.get('TranDateTime', None),
            PurchaseAmount=request.data.get('PurchaseAmount', None),
            TotalAmount=request.data.get('TotalAmount', None),
            OrderID_MerchandPortal=request.data.get('OrderID_MerchandPortal', None),
            TranId=request.data.get('TranId'),
        )
        get_plan_id = Order.objects.filter(order_id = request.data.get('order_id', None)).first()

        if get_plan_id:
          plan_id = get_plan_id.plan_id
          user_id = get_plan_id.user_id
        else:
           plan_id = 0
           user_id = 0
        Order_Status_Updated = result.OrderStatus
        status = ''
        if Order_Status_Updated == "paymentSuccessful":
            status=9
            UserSubscription.objects.filter(plan_id = plan_id,user_id =user_id).update(payment_status=status,status = 1)
            User.objects.filter(id = user_id).update(is_prime =1)
            Order.objects.filter(order_id = request.data.get('order_id', None)).update(order_status_merchant=status,payment_status = status,order_status_id = 16)
            user = Order.objects.filter(order_id = request.data.get('order_id', None)).first()
            updatecart = Cart.objects.filter(user_id=user.user_id).delete()
            OrderLog.objects.create(
                  order_id = user.id,
                  user_id = user.user_id,
                  role = 'customer',
                  status = 'placed',
                  store_id = user.store_id
                )
            if ApplyCoupon.objects.filter(user_id=user.user_id).exists():
              removeapplycoupon = ApplyCoupon.objects.get(user_id=user.user_id)
              removeapplycoupon.delete()

        elif Order_Status_Updated == "paymentFailed":
            status=10
            UserSubscription.objects.filter(plan_id = plan_id,status = 0,user_id =user_id).update(payment_status=status,status = 1)
            Order.objects.filter(order_id = request.data.get('order_id', None)).update(order_status_merchant=status,payment_status = status,order_status_id = 10)
        elif Order_Status_Updated == "userCancelledPayment":
            status=8
            UserSubscription.objects.filter(plan_id = plan_id,status = 0,user_id =user_id).update(payment_status=status,status = 1)
            Order.objects.filter(order_id = request.data.get('order_id', None)).update(order_status_merchant=status,payment_status = status,order_status_id = 8)

        if result:
            data = {}
            # data['payment_status'] = Order_Status_Updated
            if Order_Status_Updated == "paymentSuccessful":
                data['payment_status'] = "APPROVED"
                return Response({'status':True,'data': data,'msg':'Payment Success'})
            elif Order_Status_Updated == "paymentFailed":
                data['payment_status'] = "DECLINED"
                return Response({'status':False,'data': data,'msg':'Payment Decline'})
            elif Order_Status_Updated == "userCancelledPayment":
                data['payment_status'] = "CANCELED"
                return Response({'status':False,'data': data,'msg':'Payment Failed' })

            return Response({
                'status': True,
                'msg': 'Order Created and Saved'
            })
        else:
            return Response({
                'status': False,
                'msg': 'Order not saved'
            })

class JoinPrimeView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Your logic to create an order using createOrder.py
        plan_id = request.data.get('plan_id')
        user = request.user.id # Use the request.user instance directly

        if Address.objects.filter(user=user).exists():
            if UserSubscription.objects.filter(user=user, plan_id=plan_id, status=1,payment_status=9).exists():
                return Response({'status': False, 'msg': 'This plan is already running', 'data': []})

            order_detailsPlan = PrimeMemberPlan.objects.filter(id=plan_id).first()
            timestamp = str(int(datetime.timestamp(datetime.now())))
            input_string = order_detailsPlan.plan_validity
            matches = re.search(r'\d+', input_string)
            number = int(matches.group())
            order_id = f"PRIME-{timestamp}"
            plan_amount = order_detailsPlan.plan_amount
            plan_validity = order_detailsPlan.plan_validity
            plan_expiredate = (date.today() + timedelta(days=number)).isoformat()
            plan_id = plan_id
            user_id = user
            purcshe_plan = UserSubscription(
                order_id=order_id,
                plan_amount=plan_amount,
                plan_validity=plan_validity,
                plan_expiredate=plan_expiredate,
                plan_id=plan_id,
                user_id=user_id,  # Set the user instance directly

            )
            purcshe_plan.save()



            if order_detailsPlan:

                serialized_orders = []
                # Loop through each order and append its data to the list
                # for order in order_details:
                user_address_details = Address.objects.filter(user_id=user).first()
                user_details = User.objects.filter(id=user).first()
                user_address123 =[]
                user_detailss =[]

                user_all_details ={
                        "mobile":user_details.mobile,
                        "full_name":user_details.full_name,
                        "email":user_details.email
                }
                user_detailss.append(user_all_details)
                user_address={
                        "user_address":user_address_details.bulding_name,
                        "city":user_address_details.city,
                        "pincode":user_address_details.pincode,
                        "street_address":user_address_details.street_address,
                        "state":user_address_details.state,
                        "house_no":user_address_details.house_no
                }
                user_address123.append(user_address)
                serialized_order = {
                        "order_id": order_id,
                        "total": order_detailsPlan.plan_amount,
                        "user_address_id": user_address_details.id,
                        "user_id": user,
                        "user_address_details":user_address123,
                        "user_detailss":user_detailss
                        # Add more fields as needed
                    }
                serialized_orders.append(serialized_order)
                Create_Order = "CreateOrder"
                EN = "EN"
                merchant= "TEST_ECOM531"
                amount = int(order_detailsPlan.plan_amount)
                description = "order created"
                currency = '936'
                approve_url = "/testshopPageReturn.jsp"
                CancelURL = "/testshopPageReturn.jsp"
                decline_url = "/testshopPageReturn.jsp"
                order_type = "Purchase"
                shipping_country = "Ghana"
                delivery_period = 32
                merchant_ext_id = "E643C1426056"
                email = serialized_orders[0]['user_detailss'][0]['email']
                phone = serialized_orders[0]['user_detailss'][0]['mobile']
                shipping_city = serialized_orders[0]['user_address_details'][0]['city']
                shipping_state = serialized_orders[0]['user_address_details'][0]['state']
                shipping_zip_code = serialized_orders[0]['user_address_details'][0]['pincode']
                shipping_address = serialized_orders[0]['user_address_details'][0]['user_address']

                orderID = {}
                orderID['order_id'] = order_id
                result = createOrder.create_order(Create_Order, EN,  merchant ,amount , currency,  description, approve_url, CancelURL, decline_url, order_type, email, phone, shipping_country,shipping_city, delivery_period, merchant_ext_id, shipping_state,shipping_zip_code, shipping_address)


                if result:
                    return Response({'status':True,'msg':'order found','order_id':orderID,'data':result})
                else:
                    return Response({'status':False,'msg':'order not found', 'data':[]})
            else:
                return Response ({'status':False,'msg':'order not found', 'data':[]})
        else:
            return Response ({'status':False,'msg':'please add address', 'data':[]})

class UpgradePrimePlanView(GenericAPIView):
 permission_classes = [IsAuthenticated]

 def post(self, request, format=None):
        # Your logic to create an order using createOrder.py
        plan_id = request.data.get('plan_id')
        user = request.user.id

        if Address.objects.filter(user_id=user).exists():
            if UserSubscription.objects.filter(user_id = user,plan_id=plan_id,status=1,payment_status=9):
                return Response ({'status':False,'msg':'this plan already runing', 'data':[]})
            order_detailsPlan = PrimeMemberPlan.objects.filter(id=plan_id).first()
            timestamp = str(int(datetime.timestamp(datetime.now())))
            input_string = order_detailsPlan.plan_validity
            matches = re.search(r'\d+', input_string)
            number = int(matches.group())
            order_id = f"PRIMEUP-{timestamp}"
            plan_amount = order_detailsPlan.plan_amount
            plan_validity = order_detailsPlan.plan_validity
            plan_expiredate = (date.today()+timedelta(days=number)).isoformat()
            plan_id = plan_id
            user_id = user
            purcshe_plan = UserSubscription(order_id=order_id,plan_amount=plan_amount,plan_validity=plan_validity,plan_expiredate=plan_expiredate,plan_id=plan_id,user_id=user_id)
            purcshe_plan.save()
            if order_detailsPlan:

                serialized_orders = []
                # Loop through each order and append its data to the list
                # for order in order_details:
                user_address_details = Address.objects.filter(user_id=user).first()
                user_details = User.objects.filter(id=user).first()
                user_address123 =[]
                user_detailss =[]

                user_all_details ={
                        "mobile":user_details.mobile,
                        "full_name":user_details.full_name,
                        "email":user_details.email
                }
                user_detailss.append(user_all_details)
                user_address={
                        "user_address":user_address_details.bulding_name,
                        "city":user_address_details.city,
                        "pincode":user_address_details.pincode,
                        "street_address":user_address_details.street_address,
                        "state":user_address_details.state,
                        "house_no":user_address_details.house_no
                }
                user_address123.append(user_address)
                serialized_order = {
                        "order_id": order_id,
                        "total": order_detailsPlan.plan_amount,
                        "user_address_id": user_address_details.id,
                        "user_id": user,
                        "user_address_details":user_address123,
                        "user_detailss":user_detailss
                        # Add more fields as needed
                    }
                serialized_orders.append(serialized_order)
                Create_Order = "CreateOrder"
                EN = "EN"
                merchant= "TEST_ECOM531"
                amount = int(order_detailsPlan.plan_amount)
                description = "order created"
                currency = '978'
                approve_url = "/testshopPageReturn.jsp"
                CancelURL = "/testshopPageReturn.jsp"
                decline_url = "/testshopPageReturn.jsp"
                order_type = "Purchase"
                shipping_country = "Ghana"
                delivery_period = 32
                merchant_ext_id = "E643C1426056"
                email = serialized_orders[0]['user_detailss'][0]['email']
                phone = serialized_orders[0]['user_detailss'][0]['mobile']
                shipping_city = serialized_orders[0]['user_address_details'][0]['city']
                shipping_state = serialized_orders[0]['user_address_details'][0]['state']
                shipping_zip_code = serialized_orders[0]['user_address_details'][0]['pincode']
                shipping_address = serialized_orders[0]['user_address_details'][0]['user_address']

                orderID = {}
                orderID['order_id'] = order_id
                result = createOrder.create_order(Create_Order, EN,  merchant ,amount , currency,  description, approve_url, CancelURL, decline_url, order_type, email, phone, shipping_country,shipping_city, delivery_period, merchant_ext_id, shipping_state,shipping_zip_code, shipping_address)


                if result:
                    return Response({'status':True,'msg':'order found','order_id':orderID,'data':result})
                else:
                    return Response({'status':False,'msg':'order not found', 'data':[]})
            else:
                return Response ({'status':False,'msg':'order not found', 'data':[]})
        else:
            return Response ({'status':False,'msg':'please add aaddress', 'data':[]})

class getprimeorderinformation(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        result =  PrimeOrderPaymentDetail.objects.create(

            OrderID = request.data.get('order_id', None),
            SessionId  = request.data.get('session_id',None),
            RRN=request.data.get('RRN', None),
            OrderStatus=request.data.get('OrderStatus', None),
            TypeCard=request.data.get('TypeCard', None),
            PurchaseAmountScr=request.data.get('PurchaseAmountScr', None),
            OrderDescription=request.data.get('OrderDescription', None),
            TotalAmountScr=request.data.get('TotalAmountScr', None),
            TranDateTime=request.data.get('TranDateTime', None),
            PurchaseAmount=request.data.get('PurchaseAmount', None),
            TotalAmount=request.data.get('TotalAmount', None),
            OrderID_MerchandPortal=request.data.get('OrderID_MerchandPortal', None),
            TranId=request.data.get('TranId', None),
        )

        Order_Status_Updated = result.OrderStatus
        status = ''
        if Order_Status_Updated == "paymentSuccessful":
            user = request.user.id
            status=9
            User.objects.filter(id = user).update(is_prime =1)
            UserSubscription.objects.filter(order_id =  request.data.get('order_id', None)).update(payment_status=status,status = 1)

        elif Order_Status_Updated == "paymentFailed":
            status=10
            UserSubscription.objects.filter(order_id =   request.data.get('order_id', None)).update(payment_status=status)
        elif Order_Status_Updated == "userCancelledPayment":
            status=8
            UserSubscription.objects.filter(order_id =   request.data.get('order_id', None)).update(payment_status=status)

        if result:
            data = {}
            data['payment_status'] = Order_Status_Updated
            if Order_Status_Updated == "paymentSuccessful":
             return Response({'status':True,'data': data,'msg':'Payment success'})
            elif Order_Status_Updated == "paymentFailed":
             return Response({'status':False,'data': data,'msg':'Payment decline'})
            elif Order_Status_Updated == "userCancelledPayment":
             return Response({'status':False,'data': data,'msg':'Payment canceled'})
        else:
            return Response({'status':False,'msg':'Order  not saved'})

class getupgradeprimeorderinformation(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        result =  PrimeOrderPaymentDetail.objects.create(
            OrderID = request.data.get('order_id', None),
            SessionId  = request.data.get('session_id',None),
            RRN=request.data.get('RRN', None),
            OrderStatus=request.data.get('OrderStatus', None),
            TypeCard=request.data.get('TypeCard', None),
            PurchaseAmountScr=request.data.get('PurchaseAmountScr', None),
            OrderDescription=request.data.get('OrderDescription', None),
            TotalAmountScr=request.data.get('TotalAmountScr', None),
            TranDateTime=request.data.get('TranDateTime', None),
            PurchaseAmount=request.data.get('PurchaseAmount', None),
            TotalAmount=request.data.get('TotalAmount', None),
            OrderID_MerchandPortal=request.data.get('OrderID_MerchandPortal', None),
            TranId=request.data.get('TranId', None),
        )

        Order_Status_Updated = result.OrderStatus
        status = ''
        if Order_Status_Updated == "paymentSuccessful":
            user_id = request.user.id
            status=9
            UserSubscription.objects.filter(user_id =  user_id,status=1,payment_status =9).update(payment_status=0,status = 0)
            UserSubscription.objects.filter(order_id =  request.data.get('order_id', None)).update(payment_status=status,status = 1)
            User.objects.filter(id = user_id).update(is_prime=1)
        elif Order_Status_Updated == "paymentFailed":
            status=10
            UserSubscription.objects.filter(order_id =   request.data.get('order_id', None)).update(payment_status=status)
        elif Order_Status_Updated == "userCancelledPayment":
            status=8
            UserSubscription.objects.filter(order_id =   request.data.get('order_id', None)).update(payment_status=status)



        if result:
            data = {}
            data['payment_status'] = Order_Status_Updated
            if Order_Status_Updated == "paymentSuccessful":
                return Response({'status':True,'data': data,'msg':'Payment success'})
            elif Order_Status_Updated == "paymentFailed":
                return Response({'status':False,'data': data,'msg':'Payment decline'})
            elif Order_Status_Updated == "userCancelledPayment":
                return Response({'status':False,'data': data,'msg':'Payment canceled'})

            return Response({
                'status': True,
                'msg': 'Order Created and Saved'
            })

        else:

            return Response({'status':False,'msg':'Order  not saved'})














