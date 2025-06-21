from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from fulfillmentmanager.serializers import UserFullProfileSerializer
from product.serializers import GetProductSerializer,OrderRatingSerializer,UserdetailsSerializer,DeliveryRatingSerializer,PlanBenefitsSerializer,NotificationListSerializer,NewArivalProductSerializer,CouponCodeApplySerializer,UserAddressSerializer,ProductImagesSerializer, ProductDetilSerializer,CartImageSerializer,SearchKeySerializer, DeliveryDetailsSerializer,CouponSerializer, BrandProductSerializer,UserDefaultAddressSerializer, BrandProductlistSerializer, UpdateCartQuantitySerializer,OrderSerializer,StroreSerializer,CetegoryDetailSerializer, OrderItemSerializer, SearchProductSerializer, ProductListSerializer,CategoryListSerializer,ProductDetailSerializer, AddCartSerializer, CategoriesSerializer, SubCategoriesSerializer, ViewCartSerializer, DeleteCartSerializer, CouponListSerializer, CoupondiscountSerializer, DashboardSerializer, OfferSerializer, ProductBrandSerializer, AddCartSerializer, AddToWishSerializer
from product.models import Product,Images,ProductRating, OrderRating,DeliveryBoyRating, CatalogCategory,SerachProduct, ApplyCoupon,CatalogSubCategory, Order, OrderItem, ProductBrand, Wishlist, OrderItem
from setting.models import OrderStatus
from order.models import OrderLog, AssignOrderToStoreBoy, AssignOrderToDeliveryBoy
from accounts.models import Cart,Address,User,GustUser,PrimeMemberPlan,PlanBenefits,UserSubscription
from coupon_management.validations import validate_coupon
from coupon_management.models import Coupon
from CreateCoupon.models import CustomCoupon
# from customer.models import NonPrime
from stores.models import Stores,StoreInventory, AssignStoreBoy, AssignFulfillmentManager, AssignStoreManagers,DeliveryCharges,ServiceRange,StoreTiming
from banner.models import HomeBanner,OfferBanners,Notification
from datetime import datetime
from rest_framework import views
import csv,datetime
from product.forms import CSVUploadForm
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum
from accounts.views import TestNotifications,CheckDays
from django.http import HttpRequest
from datetime import date, timedelta
import re
from django.db.models import OuterRef, Subquery,F
from geopy.distance import geodesic
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.measure import Distance
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import Avg
from django.db.models import Count, Max
from datetime import datetime
from django.core.files.base import ContentFile
import requests




# Create your views here.
class CalculateDeliveryCharge(GenericAPIView):
   def deliver_charge(user_id,distance):

          getplan_id = UserSubscription.objects.filter(user_id = user_id,status =1, payment_status =9).first()
          palnbenifit = PlanBenefits.objects.filter(plan_id = getplan_id.plan_id).first()
          plan_expiredate = getplan_id.plan_expiredate
          given_date = datetime.strptime(plan_expiredate, '%Y-%m-%d').date()
          date_30_days_ago = given_date - timedelta(days=30)
          order_count = Order.objects.filter(user_id = user_id,
                created_at__date__gte=date_30_days_ago,
                created_at__date__lte=plan_expiredate
            ).count()
        #   if palnbenifit.market_discount:
        #     marketdiscount = palnbenifit.market_discount
        #     primediscount = palnbenifit.prime_discount
        #   else:
        #     marketdiscount = '0'
        #     primediscount = '0'
          if int(palnbenifit.free_delivery_order) > int(order_count):
               price = 0
          else:
             chk_deliverycharge = DeliveryCharges.objects.filter(distance__gte=distance).first()
             if chk_deliverycharge is not None:
                price = chk_deliverycharge.price
             else:
               price = 10
          response_data = {
            'status': True,
            'price': price,
            # 'prime_discount': primediscount,
            # 'market_discount': marketdiscount,

        }
          return(response_data)

class CheckSroreTime(GenericAPIView):
   def Check_Store_time(store_id):

            today = timezone.now()
            day_of_week = today.weekday()
            if day_of_week == 0:
                day_of_week = 'monday'
                getstore_time = StoreTiming.objects.filter(store_id = store_id).first()
                if getstore_time:
                    storetime = getstore_time.monday
                else:
                   return(1)
            elif day_of_week == 1:
                day_of_week = 'tuesday'
                getstore_time = StoreTiming.objects.filter(store_id = store_id).first()
                if getstore_time:
                    storetime = getstore_time.tuesday
                else:
                   return(1)
            elif day_of_week == 2:
                day_of_week = 'wednesday'
                getstore_time = StoreTiming.objects.filter(store_id = store_id).first()
                if getstore_time:
                    storetime = getstore_time.wednesday
                else:
                   return(1)
            elif day_of_week == 3:
                day_of_week = 'thursday'
                getstore_time = StoreTiming.objects.filter(store_id = store_id).first()
                if getstore_time:
                    storetime = getstore_time.thursday
                else:
                   return(1)
            elif day_of_week == 4:
                day_of_week = 'friday'
                getstore_time = StoreTiming.objects.filter(store_id = store_id).first()
                if getstore_time:
                    storetime = getstore_time.friday
                else:
                   return(1)
            elif day_of_week == 5:
                day_of_week = 'saturday'
                getstore_time = StoreTiming.objects.filter(store_id = store_id).first()
                if getstore_time:
                    storetime = getstore_time.saturday
                else:
                   return(1)
                storetime = getstore_time.saturday
            else:
                day_of_week = 'sunday'
                getstore_time = StoreTiming.objects.filter(store_id = store_id).first()
                if getstore_time:
                    storetime = getstore_time.sunday
                else:
                   return(1)

            my_datetime = datetime.now()
            formatted_time = my_datetime.strftime("%I:%M %p")
            closetime = (storetime).split(" ")
            changetime  = closetime[3]
            gettime = str(changetime).replace('.', ':')
            finalstore_time  = gettime+' '+closetime[4]
            current_time  = datetime.strptime(formatted_time, '%I:%M %p').time()
            store_time = datetime.strptime(finalstore_time, '%I:%M %p').time()
            if store_time < current_time:
                return(1)
            else:
               return(0)


# class DeliveryChargeNonProme(GenericAPIView):
#    def deliver_charge(user_id,distance):

class GetProductView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetProductSerializer

    def post(self, request, format=None):
        store_id = request.data.get('store_id')
        category_id = request.data.get('category_id')
        sub_category_id = request.data.get('sub_category_id')
        product_ids_query = StoreInventory.objects.filter(store_id=store_id,status = 1).values('product_id')

        if sub_category_id is not None and sub_category_id != '':
            total_product = Product.objects.filter(
                category_id=category_id,
                subcategory_id=sub_category_id,
                id__in=product_ids_query
            ).count()
            get_product_ids = Product.objects.filter(
                category_id=category_id,
                subcategory_id=sub_category_id,
                id__in=product_ids_query
            )
        else:
            total_product = Product.objects.filter(
                category_id=category_id,
                id__in=product_ids_query
            ).count()
            get_product_ids = Product.objects.filter(
                category_id=category_id,
                id__in=product_ids_query
            )

        items_per_page = 20  # You can adjust this value as needed
        page_number = request.data.get('page', 1)
        paginator = Paginator(get_product_ids, items_per_page)
        page = paginator.get_page(page_number)
        product_list = []
        for product_id in page:
            product = Product.objects.filter(id=product_id.id, category_id=category_id, subcategory_id=sub_category_id).first() \
             if sub_category_id is not None and sub_category_id != '' \
             else Product.objects.filter(id=product_id.id, category_id=category_id).first()
            if product:
                serializer = GetProductSerializer(product)
                is_favourite = Wishlist.objects.filter(Product_id=product_id.id, user_id=request.user.id).exists()
                in_cart = Cart.objects.filter(productId_id = product_id.id, user_id = request.user.id).exists()
                cart_quantity = Cart.objects.filter(productId_id = product_id.id, user_id = request.user.id).first()
                inventory_count = StoreInventory.objects.filter(product_id = product_id.id,store_id=store_id,status = 1).first()
                prorating = ProductRating.objects.filter(product_id=product_id.id).aggregate(Avg('rating'))['rating__avg']
                if cart_quantity:
                  quantity = cart_quantity.quantity
                else:
                 quantity = 0
                if inventory_count.price == 0 or inventory_count.price == None:
                   price = product_id.price
                else:
                  price = str(inventory_count.price)

                product_data = serializer.data
                product_data['price'] = price
                product_data['is_favourite'] = is_favourite
                product_data['in_cart'] = in_cart
                product_data['pro_quantity'] = quantity
                product_data['product_tags'] = 0
                product_data['inventory'] = inventory_count.inventory if inventory_count else 0

                product_data['rating'] = prorating if prorating else 4.5

                product_list.append(product_data)
        response_data = {
            'store_id': store_id,
            'total_product' : total_product,
            'product_list': product_list
        }
        if not product_list:
            return Response({'status': False, 'msg': 'Data not found', 'data': response_data}, status=status.HTTP_200_OK)

        return Response({'status': True, 'msg': 'Product list', 'data': response_data}, status=status.HTTP_200_OK)

class AddtoCart(GenericAPIView):
   #permission_classes = [IsAuthenticated]
   serializer_class = AddCartSerializer
   def post(self, request, format= None):
        product_id = request.data['productId']
        store_id = request.data['store']
        quantity  = int(request.data['quantity'])
        user_id = request.user.id
        closetime  = CheckSroreTime.Check_Store_time(int(store_id))
        if closetime == 1:
           return Response({'status':False, 'data':{}, 'msg':'store closed'})
        else:
            if StoreInventory.objects.filter(store_id = store_id, product_id = product_id,status = 1).exists():
        #   get_inventory = StoreInventory.objects.get(store_id = store_id, product_id = product_id,status = 1).inventory
        #   if quantity > get_inventory:
        #    return Response({'status':False, 'data':{}, 'msg':f'this product quantity not available. Only {get_inventory} item left.'})
                if Cart.objects.filter(productId_id = product_id, user_id = user_id).exists():
                  return Response({'status':False, 'data':{}, 'msg':'This product already in cart'})
                serializer = AddCartSerializer(data= request.data, context={'request': request})
                if not serializer.is_valid():
                    return Response({'status':False, 'errors':serializer.errors, 'msg':'Something went wrong'})
                serializer.save()
                return Response({'status':True, 'data':serializer.data, 'msg':'Data saved successfully'})
            else:
                return Response({'status':False, 'data':{}, 'msg':'this product is not available in store'})


class ClearCart(GenericAPIView):
   #permission_classes = [IsAuthenticated]
   serializer_class = AddCartSerializer
   def get(self, request, format= None):
        user_id = request.user.id
        clear_cart = Cart.objects.filter(user_id = user_id).delete()
        return Response({'status':True, 'data':{}, 'msg':'your cart clear successfully'})


class AddPrimeInCart(GenericAPIView):
   #permission_classes = [IsAuthenticated]
   serializer_class = AddCartSerializer
   def post(self, request, format= None):
        plan_id = request.data['plan_id']
        user_id = request.user.id
        if Cart.objects.filter(user_id=user_id,plan_id = plan_id).exists():
           return Response({'status':False, 'data':{}, 'msg':'this plan already added'})
        else:
          order_detailsPlan = PrimeMemberPlan.objects.filter(id=plan_id).first()
          timestamp = str(int(datetime.timestamp(datetime.now())))
          input_string = order_detailsPlan.plan_validity
          matches = re.search(r'\d+', input_string)
          number = int(matches.group())
          order_id = f"PRIME-{timestamp}"
          plan_amount = order_detailsPlan.plan_amount
          plan_validity = order_detailsPlan.plan_validity
          plan_expiredate = (date.today()+timedelta(days=number)).isoformat()
          plan_id = plan_id
          user_id = user_id
          addcart = Cart(user_id = user_id, amount = plan_amount,plan_id=plan_id)
          addcart.save()
          purcshe_plan = UserSubscription(
                order_id=order_id,
                plan_amount=plan_amount,
                plan_validity=plan_validity,
                plan_expiredate=plan_expiredate,
                plan_id=plan_id,
                user_id=user_id,  # Set the user instance directly
                )
          purcshe_plan.save()
        return Response({'status':True, 'data':{}, 'msg':'Data saved successfully'})

class RemovePrimeInCart(GenericAPIView):
   #permission_classes = [IsAuthenticated]
   serializer_class = AddCartSerializer
   def post(self, request, format= None):
        plan_id = request.data['plan_id']
        user_id = request.user.id
        if Cart.objects.filter(user_id=user_id,plan_id = plan_id).exists():
           delete_plan = Cart.objects.filter(user_id=user_id,plan_id = plan_id).delete()
           delete_plan = UserSubscription.objects.filter(user_id=user_id,plan_id = plan_id).delete()
           return Response({'status':True, 'data':{}, 'msg':'Remove successfully'})
        else:
           return Response({'status':False, 'data':{}, 'msg':'This plan not added in cart'})

class UpdateCartQuantity(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = UpdateCartQuantitySerializer
   def post(self, request, format= None):
      serializer = UpdateCartQuantitySerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      productId = serializer.validated_data['productId']
      updatequantity = serializer.validated_data['update_quantity']
      user_id =  request.user.id
      get_store_id = Cart.objects.get(user_id = user_id, productId_id = productId).store_id
      get_inventory = StoreInventory.objects.get(store_id = get_store_id, product_id = productId,status = 1).inventory
    #   if get_inventory < updatequantity:
    #      return Response({'status':False, 'data':{}, 'msg':'Sorry, we currently do not have the requested quantity in stock.'})
      get_amount = Cart.objects.get(productId_id = productId,user_id = user_id).amount
      update_amt = (updatequantity * get_amount)

      update_cart = Cart.objects.filter(productId_id = productId, user_id = user_id).update(total_amount=update_amt,quantity=updatequantity)
      if update_cart:
         return Response({'status':True, 'data':{}, 'msg':'quantity updated'})
      else:
         return Response({'status':False, 'data':{}, 'msg':'Something went wrong'})

class AddTipIncart(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = UpdateCartQuantitySerializer
   def post(self, request, format= None):
      tip = request.data.get('tip')
      user_id = request.user.id
      get_cart = Cart.objects.filter(user_id = user_id).first()
      update_tip = Cart.objects.filter(id = get_cart.id).update(add_tip = tip)
      return Response({'status':True, 'data':{}, 'msg':'tip added'})

class DeliveryInstAdd(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = UpdateCartQuantitySerializer
   def post(self, request, format= None):
      delivery_instructions = request.data.get('delivery_instructions')
      user_id = request.user.id
      get_cart = Cart.objects.filter(user_id = user_id).first()
      delivery_inst  = Cart.objects.filter(id = get_cart.id).update(delivery_instructions = delivery_instructions)
      return Response({'status':True, 'data':{}, 'msg':'delivery instructions added'})

class RemoveTipIncart(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = UpdateCartQuantitySerializer
   def get(self, request, format= None):
      user_id = request.user.id
      get_cart = Cart.objects.filter(user_id = user_id).first()
      update_tip = Cart.objects.filter(id = get_cart.id).update(add_tip = 0)
      return Response({'status':True, 'data':{}, 'msg':'remove tip'})

class RemoveDeliveryInst(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = UpdateCartQuantitySerializer
   def get(self, request, format= None):
      user_id = request.user.id
      get_cart = Cart.objects.filter(user_id = user_id).first()
      update_tip = Cart.objects.filter(id = get_cart.id).update(delivery_instructions = None)
      return Response({'status':True, 'data':{}, 'msg':'remove delivery instructions'})


class Categories(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoriesSerializer
    def get(self, request, format=None):
     categories = CatalogCategory.objects.filter(status =1)
     serializer = CategoriesSerializer(categories, many=True)
     if serializer is not None:
      categorieslist = {}
      categorieslist['categories listing'] = serializer.data
      return Response({'status':True, 'msg':'categories list', 'data': categorieslist}, status=status.HTTP_200_OK)
     else:
      return Response({'status':False, 'msg':'data not found', 'data': {}}, status=status.HTTP_200_OK)

class SubCategories(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubCategoriesSerializer
    def post(self, request, format=None):
     subcategories = CatalogSubCategory.objects.filter(category_id = request.data['category_id'],status =1)
     serializer = SubCategoriesSerializer(subcategories, many=True)
     if serializer is not None:
      subcategories_list = {}
      subcategories_list['sub_categories_list'] = serializer.data
      return Response({'status':True, 'msg':'sub categories list', 'data': subcategories_list}, status=status.HTTP_200_OK)
     else:
      return Response({'status':False, 'msg':'data not found', 'data': {}}, status=status.HTTP_200_OK)

class ViewCart(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ViewCartSerializer, UserDefaultAddressSerializer

    def get(self, request, format=None):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        user_id = request.user.id
        current_date = datetime.now().date()  # Get the current date
        is_special_day = CheckDays.is_1st_or_3rd_wednesday(current_date)

        if authorization_header:
           if authorization_header.startswith('Bearer '):
             bearer_token = authorization_header[7:]
             if GustUser.objects.filter(id=user_id,access_token = bearer_token):
               viewcart = Cart.objects.filter(user=user_id,plan_id = None)
               prime_amount = Cart.objects.filter(user=user_id,productId_id = None).first()
               tip = Cart.objects.filter(user_id = user_id).first()
               default_address_data = {}
             else:
               viewcart = Cart.objects.filter(user=user_id,plan_id = None)
               tip = Cart.objects.filter(user_id = user_id).first()
               prime_amount = Cart.objects.filter(user=user_id,productId_id = None).first()
               default_address = Address.objects.filter(user_id=user_id, deafult=1).first()
               default_address_data = UserDefaultAddressSerializer(default_address).data
        if not viewcart.exists():
            return Response({'status': False, 'data': {}, 'msg': 'cart is empty'}, status=status.HTTP_200_OK)

        serializer = ViewCartSerializer(viewcart, many=True)
        cart_items = list(serializer.data)
        for proinventory in cart_items:
                  product_id  = proinventory['productId']                 
                  store_id = proinventory['store']
                  inventory = StoreInventory.objects.filter(product_id = product_id['id'],store_id = store_id).first()
                  if inventory.price == 0 or inventory.price==None:
                      price = Product.objects.filter(id = product_id['id']).first()                      
                      fprice = price.price
                  else: 
                      
                      fprice = str(inventory.price)
                  proinventory['price'] = fprice                    
                  proinventory['inventory'] = inventory.inventory if inventory else 0
                      

        subtotalamt = sum([float(item['total_amount']) for item in serializer.data])

        try:
            apply_coupon = ApplyCoupon.objects.get(user_id=user_id)
            coupon_code = apply_coupon.coupon_code
        except ApplyCoupon.DoesNotExist:
            coupon_code = ""

        if prime_amount is None:
           plan_amount = 0
        else:
           plan_amount = prime_amount.amount

        if default_address is None:
            distancee = "0"
        else:
            store_id = viewcart[0].store_id
            store_latlong = Stores.objects.filter(id = store_id).first()
            coords_1 = (store_latlong.latitude, store_latlong.longitude)
            coords_2 = (default_address.latitude, default_address.longitude)
            distancee = geodesic(coords_1, coords_2).kilometers
        distance = str(distancee)
        if User.objects.filter(id = user_id, is_prime =1).exists():
           user_id = request.user.id
           calprice = CalculateDeliveryCharge.deliver_charge(user_id,distance)
           price = calprice['price']
        #    makketdiscount = calprice['market_discount']
        #    primediscount = calprice['prime_discount']

        else:
          chk_deliverycharge = DeliveryCharges.objects.filter(distance__gte=distance).first()
          if chk_deliverycharge is not None:
            price = chk_deliverycharge.price
          else:
            price = 10

        totalamount = (subtotalamt)
        # if totalamount >= 400 :
        #    if User.objects.filter(id = user_id, is_prime =1).exists():
        #     # if is_special_day == True:
        #     #   prime_discount = int(makketdiscount)
        #     # else:
        #     #   prime_discount = int(primediscount)

        # #    ftotalamount = (totalamount) * prime_discount / 100
        # #    fftotalamount = totalamount-ftotalamount
        # else:

        #    fftotalamount = totalamount
        #    ftotalamount = 0

        viewcartlist = {
            'coupon_details': {},
            'coupon_discount': "",
            'discount_amount': "",
            'delivery_charge': price,
            'prime_discount': 0.0,
            'tip': tip.add_tip,
            'delivery_instructions': tip.delivery_instructions,
            'sub_total': str(subtotalamt),
            'total_amount': str(totalamount+tip.add_tip+price+plan_amount),
            'cart_listing': cart_items,
            'default_address': default_address_data,
            'missed_product': [],
        }

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                coupondiscount = coupon.get_discount()
                discount_amount = ((subtotalamt) * coupondiscount['value']) / 100

                viewcartlist.update({
                    'coupon_details': {'code': coupon_code, 'details': coupondiscount},
                    'coupon_discount': str(coupondiscount['value']),
                    'discount_amount': str(discount_amount),
                    'total_amount': str((subtotalamt+plan_amount+tip.add_tip) - discount_amount+price),
                    "prime_discount": 0,
                })
            except Coupon.DoesNotExist:
                return Response({'status': False, 'msg': 'Coupon code invalid', 'data': {}}, status=status.HTTP_200_OK)

        get_store_product = StoreInventory.objects.filter(store_id=store_id,status = 1)[:50]
        summer_productlist = []

        for store_pro in get_store_product:
            get_summer = Product.objects.filter(product_tags=24, id=store_pro.product_id)
            is_favourite = Wishlist.objects.filter(Product_id=store_pro.product_id, user_id=request.user.id).exists()
            in_cart = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).exists()
            cart_quantity = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).first()
            quantity = cart_quantity.quantity if cart_quantity else 0
            prorating = ProductRating.objects.filter(product_id=store_pro.product_id).aggregate(Avg('rating'))['rating__avg']


            summer_serializer = GetProductSerializer(get_summer, many=True)
            summer_data = summer_serializer.data

            for item in summer_data:
                stoinvent_price = StoreInventory.objects.filter(product_id=item['id'],status = 1).first()
                if stoinvent_price.price==0 or stoinvent_price.price==None:
                   price = item['price']
                else:
                    price =  str(stoinvent_price.price)
                item['price'] = price
                item['is_favourite'] = is_favourite
                item['in_cart'] = in_cart
                item['pro_quantity'] = quantity
                item['product_tags'] = 0
                item['inventory'] = store_pro.inventory
                item['rating'] = prorating if prorating else 4.5

                summer_productlist.append(item)


            viewcartlist['missed_product'] = summer_productlist

        prime_member_plans = PrimeMemberPlan.objects.filter(plan_recommanded = 1).first()
        queryset = PlanBenefits.objects.filter(plan_id=prime_member_plans.id)
        plan_benefits = PlanBenefitsSerializer(queryset, many=True).data
        if UserSubscription.objects.filter(user_id= user_id,status =1,payment_status=9).exists():
           prime_plans = {}
           prime_plans['plan_id'] = prime_member_plans.id
           prime_plans['status'] = False
           prime_plans['prime_status'] = True
           prime_plans['msg'] = "you have already purchase prime plan"
           viewcartlist['prime_plan'] = prime_plans
           return Response({'status': True, 'data': viewcartlist, 'msg': 'View Cart List'})

        if Cart.objects.filter(user_id=user_id, plan_id = prime_member_plans.id).exists():
           prime_plans = {}
           prime_plans['plan_id'] = prime_member_plans.id
           prime_plans['plan_amount'] = prime_member_plans.plan_amount
           prime_plans['status'] = False
           prime_plans['prime_status'] = False
           prime_plans['msg'] = "this plan added in cart"
           viewcartlist['prime_plan'] =prime_plans
           return Response({'status': True, 'data': viewcartlist, 'msg': 'View Cart List'})
        else:
          purchase_plan_data = {
                  'plan_id': prime_member_plans.id,
                  'plan_amount': prime_member_plans.plan_amount,
                  'plan_validity': prime_member_plans.plan_validity,
                  'plan_text': prime_member_plans.plan_text,
                  'plan_recommanded': prime_member_plans.plan_recommanded,
                  'created_at': prime_member_plans.created_at,
                  'updated_at': prime_member_plans.updated_at,
                  'status': True,
                  'prime_status': False,
                  'benefits': plan_benefits,
              }
        #   viewcartlist['prime_plan'] = purchase_plan_data

        return Response({'status': True, 'data': viewcartlist, 'msg': 'View Cart List'})

class DeleteCart(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = DeleteCartSerializer
   def post(self, request, format=None):
      serializer = DeleteCartSerializer()
      product_id = request.data.get('product_id')
      user_id = request.user.id
      if product_id is None:
            return Response({'status': False, 'msg': 'Missing product id', 'data': None}, status=status.HTTP_200_OK)
      deletecart = Cart.objects.filter(productId_id = product_id,user_id = user_id).delete()
      if Cart.objects.filter(user_id = user_id).exists():
         user_id = user_id
         if Cart.objects.filter(user_id = user_id,productId_id = None).exists():
            cartcount = Cart.objects.filter(user_id = user_id,productId_id__isnull=False).count()
            if cartcount == 0 :
              cart = Cart.objects.filter(user_id = user_id).delete()
              ApplyCoupon.objects.filter(user_id = user_id).delete()
      #serializer = DeleteCartSerializer(deletecart, many=True)
      if deletecart:

        return Response({'status':True, 'msg':'deleted successfully', 'data': {}}, status=status.HTTP_200_OK)
      else:

        return Response({'status':False, 'msg':'Allready deleted', 'data': {}}, status=status.HTTP_200_OK)

class CouponList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = CouponListSerializer
   def get(self, request, format=None):
    couponlist = Coupon.objects.filter(status =1)
    couponlisting = []
    for rec in couponlist:
            if CustomCoupon.objects.filter(coupon_ptr_id=rec.id).exists():
                copdis = CustomCoupon.objects.get(coupon_ptr_id=rec.id)  # Use get() to get a single object
                serializer = CouponListSerializer(rec)
                coupon_data = serializer.data
                coupon_data['short_description'] = copdis.short_description
                coupon_data['description'] = copdis.description
                couponlisting.append(coupon_data)

    return Response({'status': True, 'msg': 'Coupon list', 'data': couponlisting}, status=status.HTTP_200_OK)


class CheckDiscount(GenericAPIView):
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    coupon = Coupon.objects.get(status =1, code = request.data['code'])
    coupondiscount = coupon.get_discount()
    coupondiscountlist = {}
    coupondiscountlist['coupon discount'] = coupondiscount
    return Response({'status':True, 'msg':'discount', 'data': coupondiscountlist}, status=status.HTTP_200_OK)

class OrderPlace(GenericAPIView):
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
   user_id = request.user.id
   store_id = request.data['store']
   closetime  = CheckSroreTime.Check_Store_time(store_id)
   if closetime == 1:
           return Response({'status':False, 'data':{}, 'msg':'store closed'})
   get_user_addresslatlong = Address.objects.filter(id= request.data['address_id']).first()
   storelatlong = Stores.objects.filter(id = request.data['store']).filter().first()
   coords_1 = (get_user_addresslatlong.latitude, get_user_addresslatlong.longitude)
   coords_2 = (storelatlong.latitude, storelatlong.longitude)
   distance = geodesic(coords_1, coords_2).kilometers
   rangeget = ServiceRange.objects.first()
   rangef = (rangeget.range_in_km).split()
   finalrange = rangef[0]
   radius_km = int(finalrange)
   if distance >= radius_km :
    return Response({'status':False, 'msg':'your location is not in store range. Please update address', 'data': {}}, status=status.HTTP_200_OK)
   else:
      authorization_header = request.META.get('HTTP_AUTHORIZATION')
      if authorization_header:
          if authorization_header.startswith('Bearer '):
            bearer_token = authorization_header[7:]
            if GustUser.objects.filter(access_token = bearer_token):
                return Response({'status':False, 'msg':'Please login', 'data': []}, status=status.HTTP_200_OK)
      store = request.data['store']
      if AssignFulfillmentManager.objects.filter(store_id=store).exists():
       if Cart.objects.filter(user_id = request.user.id).exists():
        if Order.objects.filter(store_id = request.data['store']).exists():
            last_order_id = Order.objects.filter(store_id = request.data['store']).last()
            lastorder_id = last_order_id.order_id
            parts = lastorder_id.split('-')
            prefix = parts[0]
            getstore_code = Stores.objects.filter(id = request.data['store']).first()
            if getstore_code.Shop_code == prefix:
                    order_idcode = lastorder_id
                    numeric_part = int(order_idcode.split('-')[1])
                    numeric_part += 1
                    order_id = f"{order_idcode.split('-')[0]}-{numeric_part}"
            else:
                order_id = f"{getstore_code.Shop_code}-{100000001}"
        else:
               getstore_code = Stores.objects.filter(id = request.data['store']).first()
               order_id = f"{getstore_code.Shop_code}-{100000001}"

        product_id = request.data['product_id']
        item_quantity = request.data['quantity']
        order_quantity = sum(item_quantity)
        coupon_code = request.data['coupon_code']
        coupon_discount = request.data['coupon_discount']
        coupon_discount_amount = request.data['coupon_discount_amount']
        sub_total = request.data['sub_total']

        total_amount = request.data['total_amount']
        address_id = request.data['address_id']
        tip = request.data['tip']
        delivery_instructions = request.data['delivery_instructions']
        store = request.data['store']
        orderstatus = OrderStatus.objects.get(title = 'placed')
        plan_id = request.data['plan_id']
        payment_mode = request.data['payment_mode']
        delivery_charges = request.data['delivery_charges']
        prime_discount = request.data['prime_discount']
        if payment_mode == "3":
           ordermerchant = 0
        else:
          ordermerchant = None
        # storeboys = AssignStoreBoy.objects.filter(store_id=store, status='free')
        # if storeboys.exists():
        #       storeboy = storeboys.first()
        totalamt = round(float(total_amount))
        orders = Order(order_id = order_id, coupon_code = coupon_code, coupon_discount = coupon_discount, coupon_discount_amount= coupon_discount_amount, subtotal = sub_total, total=total_amount, user_address_id_id=address_id, order_quantity = order_quantity, user_id=request.user.id, store_id = store, order_status_id= orderstatus.id,tip= tip,delivery_instructions=delivery_instructions,plan_id=plan_id,payment_mode=payment_mode,order_status_merchant = ordermerchant,delivery_charges=delivery_charges,prime_discount=prime_discount)
        orders.save()
        if payment_mode == "1" or payment_mode == "2":
          updatecart = Cart.objects.filter(user_id=request.user.id).delete()
          if ApplyCoupon.objects.filter(user_id=request.user.id).exists():
            removeapplycoupon = ApplyCoupon.objects.get(user_id=request.user.id)
            removeapplycoupon.delete()
            OrderLog.objects.create(
                    order_id = orders.id,
                    user_id = request.user.id,
                    role = 'customer',
                    status = 'placed',
                    store_id = store
                  )
          else:
            OrderLog.objects.create(
                  order_id = orders.id,
                  user_id = request.user.id,
                  role = 'customer',
                  status = 'placed',
                  store_id = store
                )

              # if storeboy:
              #   AssignOrderToStoreBoy.objects.create(user_id= storeboy.user_id, order_id= orders.id,status = 'placed')
              #   storeboy.status = 'busy'
              #   storeboy.save()


        if len(product_id) == len(item_quantity):
                for product_id, item_quantity in zip(product_id, item_quantity):
                  order_item = OrderItem(product_id=product_id, item_quantity=item_quantity ,order_id = orders.id, store_id = store)
                  order_item.save()

                # get_quantity = StoreInventory.objects.get(product_id=product_id, store_id = store,status = 1).inventory
                # #if get_quantity >= item_quantity:
                # update_quantity = get_quantity-item_quantity
                # update_model = StoreInventory.objects.filter(product_id=product_id, store_id = store,status = 1).update(inventory=update_quantity)
                order_idss = {}
                order_idss['order_id'] = order_id
                # else:
                #   return Response({'status':False, 'msg':'Iteam quantity not available', 'data': {}}, status=status.HTTP_200_OK)

                assign_manager = AssignFulfillmentManager.objects.filter(store_id=store).first()
                manager_id = assign_manager.user_id
                title = 'New order has been assigned to you'
                body = f'{order_id} has been assigned to you'
                types = 'orders'
                order_id = order_id
                order_type = 1
                request = HttpRequest()
                test_notifications = TestNotifications()
                response = test_notifications.send_push_notification(title, body,manager_id,types,order_id,order_type)

                assign_managerst = AssignStoreManagers.objects.filter(store_id=store).first()
                manager_id = assign_managerst.user_id
                title = 'New order has been assigned'
                body = f'{order_id} has been assigned'
                types = 'orders'
                order_id = order_id
                order_type =1
                request = HttpRequest()
                test_notifications = TestNotifications()
                response = test_notifications.send_push_notification(title, body,manager_id,types,order_id,order_type)

                return Response({'status':True, 'msg':'order placed', 'data': order_idss}, status=status.HTTP_200_OK)
       else:
        return Response({'status':False, 'msg':'your cart is empty', 'data': {}}, status=status.HTTP_200_OK)
      else:
        return Response({'status':False, 'msg':'We can not provide order processing right now due to a lack of staff.', 'data': {}}, status=status.HTTP_200_OK)

class OrderPlaceNew(GenericAPIView):
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
   user_id = request.user.id
   authorization_header = request.META.get('HTTP_AUTHORIZATION')
   if authorization_header:
      if authorization_header.startswith('Bearer '):
         bearer_token = authorization_header[7:]
         if GustUser.objects.filter(access_token = bearer_token):
            return Response({'status':False, 'msg':'Please login', 'data': []}, status=status.HTTP_200_OK)
   if Cart.objects.filter(user_id = request.user.id).exists():
    timestamp = str(int(datetime.timestamp(datetime.now())))
    order_id = f"MELCOM-{timestamp}"
    product_id = request.data['product_id']
    item_quantity = request.data['quantity']
    order_quantity = sum(item_quantity)
    coupon_code = request.data['coupon_code']
    coupon_discount = request.data['coupon_discount']
    coupon_discount_amount = request.data['coupon_discount_amount']
    sub_total = request.data['sub_total']
    total_amount = request.data['total_amount']
    address_id = request.data['address_id']
    tip = request.data['tip']
    delivery_instructions = request.data['delivery_instructions']
    store = request.data['store']
    plan_id = request.data['plan_id']
    orderstatus = OrderStatus.objects.get(title = 'placed')
    # storeboys = AssignStoreBoy.objects.filter(store_id=store, status='free')
    # if storeboys.exists():
    #       storeboy = storeboys.first()
    orders = Order(order_id = order_id, coupon_code = coupon_code, coupon_discount = coupon_discount, coupon_discount_amount= coupon_discount_amount, subtotal = sub_total, total=total_amount, user_address_id_id=address_id, order_quantity = order_quantity, user_id=request.user.id, store_id = store, order_status_id= orderstatus.id,tip= tip,delivery_instructions=delivery_instructions,plan_id=plan_id)
    orders.save()
    updatecart = Cart.objects.filter(user_id=request.user.id).delete()
    if ApplyCoupon.objects.filter(user_id=request.user.id).exists():
     removeapplycoupon = ApplyCoupon.objects.get(user_id=request.user.id)
     removeapplycoupon.delete()

     OrderLog.objects.create(
            order_id = orders.id,
            user_id = request.user.id,
            role = 'customer',
            status = 'placed'
          )

          # if storeboy:
          #   AssignOrderToStoreBoy.objects.create(user_id= storeboy.user_id, order_id= orders.id,status = 'placed')
          #   storeboy.status = 'busy'
          #   storeboy.save()


    if len(product_id) == len(item_quantity):
            for product_id, item_quantity in zip(product_id, item_quantity):
              order_item = OrderItem(product_id=product_id, item_quantity=item_quantity ,order_id = orders.id, store_id = store)
              order_item.save()

            get_quantity = StoreInventory.objects.get(product_id=product_id, store_id = store,status = 1).inventory
            #if get_quantity >= item_quantity:
            update_quantity = get_quantity-item_quantity
            update_model = StoreInventory.objects.filter(product_id=product_id, store_id = store,status = 1).update(inventory=update_quantity)
            order_idss = {}
            order_idss['order_id'] = order_id
            # else:
            #   return Response({'status':False, 'msg':'Iteam quantity not available', 'data': {}}, status=status.HTTP_200_OK)

            assign_manager = AssignFulfillmentManager.objects.get(store_id=store)
            manager_id = assign_manager.user_id
            title = 'New order has been assigned to you'
            body = f'{order_id} has been assigned to you'
            types = 'orders'
            request = HttpRequest()
            test_notifications = TestNotifications()
            response = test_notifications.send_push_notification(title, body,manager_id,types)

    # else:
    #      return Response({'status':False, 'msg':'store boy is busy.. please try again after some time.', 'data': {}}, status=status.HTTP_200_OK)
    return Response({'status':True, 'msg':'order placed', 'data': order_idss}, status=status.HTTP_200_OK)
   else:
    return Response({'status':False, 'msg':'your cart is empty', 'data': {}}, status=status.HTTP_200_OK)


class UserDashboard(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardSerializer, OfferSerializer, CategoriesSerializer, ProductBrandSerializer

    def post(self, request, format=None):
        store_id = request.data.get('store')
        print(request.user.id)

        # coords_1 = (5.5878269797233315, -0.22746836224463174)
        # coords_2 = (5.668436196676484, -0.21648277024512466)
        # distance = geodesic(coords_1, coords_2).kilometers
        # print(distance)

        userd = User.objects.filter(id = request.user.id).first()
        user_details  = UserdetailsSerializer(userd).data

        lastdeliveryorder = Order.objects.filter(user_id = request.user.id,order_status_id = 6,skip_rating = 0).last()
            # if deliveryrating is None:
            # if deliveryrating is None:
        if lastdeliveryorder:
            lastdeliveryorder_id = lastdeliveryorder.id
            showlastdeliveryorder_id = lastdeliveryorder.order_id
            deliveryrating = DeliveryBoyRating.objects.filter(order_id = lastdeliveryorder_id).first()
            delivery_name = User.objects.filter(id=lastdeliveryorder.delivery_boy_id).first()

            if lastdeliveryorder.delivery_boy_id:
                delivery_name = User.objects.filter(id=lastdeliveryorder.delivery_boy_id).first()
            else:
               delivery_name =''

            userimage = UserFullProfileSerializer(delivery_name).data
            deliveryorder = {}
            # if deliveryrating is None:
            deliveryorder['order_id'] = lastdeliveryorder_id
            deliveryorder['show_order_id'] = showlastdeliveryorder_id
            deliveryorder['deliveryboy_id'] = lastdeliveryorder.delivery_boy_id
            deliveryorder['deliveryboy_profile'] = userimage['profile_image']
            if isinstance(delivery_name, User) and delivery_name.full_name:
                    deliveryorder['deliveryboy_name'] = delivery_name.full_name
            else:
                    deliveryorder['deliveryboy_name'] = ''
            # else:
            #     deliveryorder = {}
        else:
           deliveryorder = {}

        # Optimize database queries using select_related/prefetch_related
        homebanner = HomeBanner.objects.filter(status=1,default=0).order_by('priority')
        offerbanner = OfferBanners.objects.filter(status=1,default=0).order_by('priority')
        defaultofferbanner = OfferBanners.objects.filter(status=1, default=1)
        defaulthomebanner = HomeBanner.objects.filter(status=1, default=1)
        serializerhomebanner = DashboardSerializer(homebanner, many=True)

        defaulthomeimage = DashboardSerializer(defaulthomebanner, many=True)
        defaultofferimage = OfferSerializer(defaultofferbanner, many=True)

        serializeroffer = OfferSerializer(offerbanner, many=True)

        categories = CatalogCategory.objects.filter(status=1)[:12]
        categoriesserializer = CategoriesSerializer(categories, many=True)

        product_brand_ids = StoreInventory.objects.filter(store_id=store_id,status = 1).values_list('product__Brand_id', flat=True).distinct()
        product_brands = ProductBrand.objects.filter(id__in=product_brand_ids)[:5]
        productbrand = ProductBrandSerializer(product_brands, many=True)

        if Address.objects.filter(user_id=request.user.id, deafult=1).exists():
            useraddress = Address.objects.filter(user_id=request.user.id, deafult=1).first()
            userlat  = useraddress.latitude
            userlong  = useraddress.longitude
        else:
            useraddress = ""
            userlat = 0
            userlong = 0

        useraddress = UserAddressSerializer(useraddress).data if useraddress else {}
        store_detials = Stores.objects.filter(id = store_id).first()
        storelat = store_detials.latitude
        storelong = store_detials.longitude
        coords_1 = (storelat, storelong)
        coords_2 = (userlat, userlong)
        distance = geodesic(coords_1, coords_2).kilometers
        rangeget = ServiceRange.objects.first()
        rangef = (rangeget.range_in_km).split()
        finalrange = rangef[0]
        radius_km = int(finalrange)
        time = 30
        km_time = distance/time
        totaltime = int(km_time*60)+8
        if totaltime < radius_km:
           dtime = str(totaltime)+' mins'
        else:
           dtime = '15 mins'

        track_order = Order.objects.filter(user_id = request.user.id, store_id = store_id, order_status_id__in = [1,2,3,4,5]).last()
        if track_order:
            track_order_dict = {
                    'id': track_order.id,
                    'order_id': track_order.order_id,
                    'order_status': track_order.order_status_id,
                    'store_name': store_detials.name,
                     }
        else:
            track_order_dict = {}
        # Optimize database queries using select_related/prefetch_related
        order_queryset = Order.objects.filter(user_id=request.user.id, store_id=store_id).order_by('-id')[:5]
        product_set = set()
        product_list = []

        for order in order_queryset:
            order_items = OrderItem.objects.filter(order=order).select_related('product__Brand')[:10]
            for order_item in order_items:
                if StoreInventory.objects.filter(product_id = order_item.product_id,store_id=store_id).exists():
                  product_id = order_item.product_id

                  if product_id in product_set:
                      continue
                  else:
                    product_set.add(product_id)
                    product_data = GetProductSerializer(order_item.product).data
                    is_favourite = Wishlist.objects.filter(Product_id=product_id, user_id=request.user.id).exists()
                    in_cart = Cart.objects.filter(productId_id=product_id, user_id=request.user.id).exists()
                    cart_quantity = Cart.objects.filter(productId_id=product_id, user_id=request.user.id).first()
                    pro_inventory = StoreInventory.objects.filter(product_id=product_id,status = 1).first()
                    quantity = cart_quantity.quantity if cart_quantity else 0
                    prorating = ProductRating.objects.filter(product_id=product_id).aggregate(Avg('rating'))['rating__avg']
                    if pro_inventory.price == 0 or pro_inventory.price == None:
                        fprice = Product.objects.filter(product_id = product_id).first()
                        price = fprice.price
                    else:
                        price = str(pro_inventory.price)
                    # if pro_inventory.price == 0 or pro_inventory.price == None:
                    #     price = 0
                    # else:
                    #     price = str(pro_inventory.price)

                    product_data['price'] = price
                    product_data['is_favourite'] = is_favourite
                    product_data['in_cart'] = in_cart
                    product_data['pro_quantity'] = quantity
                    product_data['product_tags'] = 0
                    product_data['inventory'] = pro_inventory.inventory if pro_inventory else 0
                    product_data['rating'] = prorating if prorating else 4.5

                    product_list.append(product_data)

        get_store_product = StoreInventory.objects.filter(store_id=store_id,status = 1,product__product_tags=24)
        summer_productlist = []

        for store_pro in get_store_product:
            get_summer = Product.objects.filter(id=store_pro.product_id)
            is_favourite = Wishlist.objects.filter(Product_id=store_pro.product_id, user_id=request.user.id).exists()
            in_cart = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).exists()
            cart_quantity = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).first()
            quantity = cart_quantity.quantity if cart_quantity else 0
            prorating = ProductRating.objects.filter(product_id=store_pro.product_id).aggregate(Avg('rating'))['rating__avg']


            summer_serializer = GetProductSerializer(get_summer, many=True)
            summer_data = summer_serializer.data

            for item in summer_data:
                stoinvent_price = StoreInventory.objects.filter(product_id=item['id'],status = 1).first()
                if stoinvent_price.price==0 or stoinvent_price.price==None:
                   price = item['price']
                else:
                    price =  str(stoinvent_price.price)
                item['price'] = price
                item['is_favourite'] = is_favourite
                item['in_cart'] = in_cart
                item['pro_quantity'] = quantity
                item['product_tags'] = 0
                item['inventory'] = store_pro.inventory
                item['rating'] = prorating if prorating else 4.5

                summer_productlist.append(item)
        newarrival_product = StoreInventory.objects.filter(store_id=store_id,status = 1,product__product_tags=6)
        newarrival = []
        for store_pro in newarrival_product:
            get_summer = Product.objects.filter(id=store_pro.product_id)
            is_favourite = Wishlist.objects.filter(Product_id=store_pro.product_id, user_id=request.user.id).exists()
            in_cart = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).exists()
            cart_quantity = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).first()
            quantity = cart_quantity.quantity if cart_quantity else 0
            prorating = ProductRating.objects.filter(product_id=store_pro.product_id).aggregate(Avg('rating'))['rating__avg']


            summer_serializer = GetProductSerializer(get_summer, many=True)
            summer_data = summer_serializer.data

            for item in summer_data:
                stoinvent_price = StoreInventory.objects.filter(product_id=item['id'],status = 1).first()
                if stoinvent_price.price==0 or stoinvent_price.price==None:
                   price = item['price']
                else:
                    price =  str(stoinvent_price.price)
                item['price'] = price
                item['is_favourite'] = is_favourite
                item['in_cart'] = in_cart
                item['pro_quantity'] = quantity
                item['product_tags'] = 0
                item['inventory'] = store_pro.inventory
                item['rating'] = prorating if prorating else 4.5

                newarrival.append(item)
        premiuml_product = StoreInventory.objects.filter(store_id=store_id,status = 1,product__product_tags=4)
        premium_product = []
        for store_pro in premiuml_product:
            get_summer = Product.objects.filter(id=store_pro.product_id)
            is_favourite = Wishlist.objects.filter(Product_id=store_pro.product_id, user_id=request.user.id).exists()
            in_cart = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).exists()
            cart_quantity = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).first()
            quantity = cart_quantity.quantity if cart_quantity else 0
            prorating = ProductRating.objects.filter(product_id=store_pro.product_id).aggregate(Avg('rating'))['rating__avg']


            summer_serializer = GetProductSerializer(get_summer, many=True)
            summer_data = summer_serializer.data

            for item in summer_data:
                stoinvent_price = StoreInventory.objects.filter(product_id=item['id'],status = 1).first()
                if stoinvent_price.price==0 or stoinvent_price.price==None:
                   price = item['price']
                else:
                    price =  str(stoinvent_price.price)
                item['price'] = price
                item['is_favourite'] = is_favourite
                item['in_cart'] = in_cart
                item['pro_quantity'] = quantity
                item['product_tags'] = 0
                item['inventory'] = store_pro.inventory
                item['rating'] = prorating if prorating else 4.5
                premium_product.append(item)

        # Similar optimization can be applied to 'newarrival' and 'premium_product' sections

        dashboard = {
            'store_id': request.data['store'],
            'home_banner': serializerhomebanner.data,
            'offer_banner': serializeroffer.data,
            'categories': categoriesserializer.data,
            'product_brand': productbrand.data,
            'order_again': product_list,
            'summer_fruits': summer_productlist,
            'new_arrivals': newarrival,
            'premium_products': premium_product,
            'user_address': useraddress,
            'defaultofferbanner':defaultofferimage.data,
            'defaulthomebanner':defaulthomeimage.data,
            'delivered_order':deliveryorder,
            'delivery_time':dtime,
            'user_details':user_details,
            'track_order':track_order_dict
        }

        return Response({'status': True, 'msg': 'dashboard', 'data': dashboard}, status=status.HTTP_200_OK)


class CategoryListAPIView(GenericAPIView):
    def get(self, request, format=None):
     categories = CatalogCategory.objects.all()
     serializer = CategoryListSerializer(categories, many=True)
     return Response(
       {'status':True, 'msg':'category details', 'data':serializer.data}, status=status.HTTP_200_OK)

class CategoryDetailAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        products = CatalogCategory.objects.filter(id=pk)
        serializer = CetegoryDetailSerializer(products, many=True)
        return Response(
       {'status':True, 'msg':'category details', 'data':serializer.data}, status=status.HTTP_200_OK)

class ProductListAPIView(GenericAPIView):
 permission_classes = [IsAuthenticated]
 def get(self, request, format=None):
    queryset = Product.objects.all()
    serializer = ProductListSerializer(queryset, many=True)
    return Response(
       {'status':True, 'msg':'Product list', 'data':serializer.data}, status=status.HTTP_200_OK)


class ProductDetailAPIView(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def get(self, request,pk):
       queryset = Product.objects.filter(id=pk)
       serializer = ProductDetailSerializer(queryset,  many=True)
       return Response(serializer.data)

class PreviousOrder(GenericAPIView):
  permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
   # if Order.objects.filter(user_id = request.user.id).exists():
     orders  = Order.objects.filter(user_id = request.user.id, is_delete = 0).order_by('-created_at')
     productlist = []
     for order in orders:
            order_serializer = OrderSerializer(order)
            getstore_details = Stores.objects.get(id = order.store_id)
            strore_address = StroreSerializer(getstore_details)
            order_items = OrderItem.objects.filter(order_id=order.id)
            order_item_list = []
            for order_item in order_items:
                product = Product.objects.get(id=order_item.product_id)
                serializer = GetProductSerializer(product)
                prorating = ProductRating.objects.filter(product_id=order_item.product_id).aggregate(Avg('rating'))['rating__avg']
                product_data = serializer.data
                product_data['item_quantity'] = order_item.item_quantity
                product_data['product_tags'] = 0
                product_data['rating'] = prorating if prorating else 4.5
                order_item_list.append(product_data)

            order_details = order_serializer.data
            store_details = strore_address.data
            order_details['strore_details'] = store_details
            order_details['order_items'] = order_item_list
            productlist.append(order_details)
            previousorder = {}
            previousorder['previous_order'] = productlist

     if productlist:
          return Response({'status': True, 'msg': 'Product lists from multiple orders.', 'data': previousorder}, status=status.HTTP_200_OK)
     else:
          return Response({'status': False, 'msg': 'Data not found', 'data': {}}, status=status.HTTP_200_OK)


class RecentOrder(GenericAPIView):
  permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    if Order.objects.filter(user_id = request.user.id).exists():

     order_id = Order.objects.filter(user_id = request.user.id, is_delete = 0).order_by('-created_at').first()
     getorder_details = Order.objects.get(order_id = order_id.order_id, user_id = request.user.id)
     orderdetail_serializer = OrderSerializer(getorder_details)
     get_product_id = OrderItem.objects.filter(order_id = order_id.id)
     getstore_details = Stores.objects.get(id = order_id.store_id)
     strore_address = StroreSerializer(getstore_details)
     productlist = []
     for productid in get_product_id:
            product = Product.objects.get(id = productid.product_id)
            product_serializer  = GetProductSerializer(product)
            prorating = ProductRating.objects.filter(product_id=productid.product_id).aggregate(Avg('rating'))['rating__avg']
            product_data = product_serializer.data
            product_data['item_quantity'] = productid.item_quantity
            product_data['rating'] = prorating if prorating else 4.5
            product_data['product_tags'] = 0
            productlist.append(product_data)
            prolist = {}
            prolist['store_details'] = strore_address.data
            prolist['order_details'] = orderdetail_serializer.data
            prolist['order_item'] = productlist
     return Response({'status':True,'msg':'recent order', 'data' : prolist}, status=status.HTTP_200_OK)
    else:
       return Response({'status':False,'msg':'data not found', 'data' : {}}, status=status.HTTP_200_OK)

class UserOrderList(GenericAPIView):
  permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
     cart_value = Cart.objects.filter(user_id = request.user.id).exists()
     orders = Order.objects.filter(Q(user_id=request.user.id) & Q(is_delete=0) & Q(payment_mode__in=[1, 2, 3]) & (Q(order_status_merchant__isnull=True) | Q(order_status_merchant=9))).order_by('-created_at')
     productlist = []
     for order in orders:
            order_serializer = OrderSerializer(order)
            getstore_details = Stores.objects.get(id = order.store_id)
            strore_address = StroreSerializer(getstore_details)
            if OrderRating.objects.filter(user_id_id = request.user.id,order_id=order.id).exists():
              order_rating = OrderRating.objects.filter(user_id_id = request.user.id,order_id=order.id)
              orderrating = OrderRatingSerializer(order_rating, many= True).data[0]
            else:
               orderrating = {}
            order_items = OrderItem.objects.filter(order_id=order.id)
            order_item_list = []
            for order_item in order_items:
                try:
                  product = Product.objects.get(id=order_item.product_id)
                  serializer = GetProductSerializer(product)
                  prorating = ProductRating.objects.filter(product_id=order_item.product_id).aggregate(Avg('rating'))['rating__avg']
                  product_data = serializer.data
                  product_data['item_quantity'] = order_item.item_quantity
                  product_data['rating'] = prorating if prorating else 4.5
                  product_data['product_tags'] = 0
                  order_item_list.append(product_data)
                except Product.DoesNotExist:
                  # Handle the case when the product is not found
                  product_data = {'id': order_item.product_id, 'item_quantity': order_item.item_quantity, 'product_tags': 0}
                  order_item_list.append(product_data)

            order_details = order_serializer.data
            store_details = strore_address.data
            order_details['strore_details'] = store_details
            order_details['order_items'] = order_item_list
            order_details['order_rating'] = orderrating
            productlist.append(order_details)
            previousorder = {}
            previousorder['cart_value'] = cart_value
            previousorder['previous_order'] = productlist

     if productlist:
          return Response({'status': True, 'msg': 'User order listing', 'data': previousorder}, status=status.HTTP_200_OK)
     else:
          return Response({'status': False, 'msg': 'Data not found', 'data': None}, status=status.HTTP_200_OK)

class AddToWishProduct(GenericAPIView):
     permission_classes = [IsAuthenticated]
     serializer_class = AddToWishSerializer
     def post(self, request, format= None):
      product_id = request.data.get('product_id')
      user = request.user.id
      if Wishlist.objects.filter(Product_id=product_id, user_id=user).exists():
        return Response({'status':False, 'msg':'This product alredy added', 'data': {}}, status=status.HTTP_200_OK)
      else:
        #serializer = AddToWishSerializer(data= request.data, context={'request': request})
        product_id = request.data['product_id']
        user = request.user.id
        addtowish = Wishlist(Product_id = product_id, user_id = user)
        addtowish.save()
        return Response({'status':True, 'msg':'added successfully', 'data': {}}, status=status.HTTP_200_OK)

class SearchProduct(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchProductSerializer
    filter_backends = [SearchFilter]

    def post(self, request, format= None):
        search_fields = request.data.get('product_name')
        store_id = request.data.get('store_id')
        user_id = request.user.id
        searchproduct = SerachProduct(product_name=search_fields, user_id=user_id)
        searchproduct.save()
        # queryset = Product.objects.filter(product_name__icontains=search_fields)
        queryset_ids = Product.objects.filter(product_name__icontains=search_fields).values_list('id', flat=True)
        priduct_ids = StoreInventory.objects.filter(product_id__in=queryset_ids,store_id = store_id,status = 1).values_list('product_id', flat=True)
        queryset = Product.objects.filter(id__in=priduct_ids)
        id_list = list(queryset_ids)
        items_per_page = 20  # You can adjust this value as needed
        page_number = request.data.get('page', 1)
        paginator = Paginator(queryset, items_per_page)
        page = paginator.get_page(page_number)
        search_productlist =[]
        product_ids = []
        for new_pro in page:
            if StoreInventory.objects.filter(product_id = new_pro.id,store_id = store_id,status = 1).exists():
              product_ids.append(new_pro.id)
              is_favourite = Wishlist.objects.filter(Product_id=new_pro.id, user_id=self.request.user.id).exists()
              in_cart = Cart.objects.filter(productId_id=new_pro.id, user_id=self.request.user.id).exists()
              cart_quantity = Cart.objects.filter(productId_id=new_pro.id, user_id=self.request.user.id).first()
              pro_inventry = StoreInventory.objects.filter(product_id = new_pro.id,status = 1).first()
              prorating = ProductRating.objects.filter(product_id=new_pro.id).aggregate(Avg('rating'))['rating__avg']


              if cart_quantity:
                  quantity = cart_quantity.quantity
              else:
                  quantity = 0

              search_serializer = GetProductSerializer(new_pro)
              search_data = search_serializer.data
              search_data['is_favourite'] = is_favourite
              search_data['in_cart'] = in_cart
              search_data['pro_quantity'] = quantity
              search_data['product_tags'] = 0
              search_data['inventory'] = pro_inventry.inventory if pro_inventry else 0
              search_data['rating'] = prorating if prorating else 4.5

              search_productlist.append(search_data)

        count = StoreInventory.objects.filter(product_id__in=id_list,store_id = store_id,status = 1).count()

        return Response({'status': True, 'total_product':count, 'data': search_productlist, 'msg': 'Product list'})

class UserWishList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def get(self, request, format=None):
      user = request.user.id
      if Wishlist.objects.filter(user_id=user).exists():
        product_id = Wishlist.objects.filter(user_id=user)
        productlist = []
        for productid in product_id:
            product = Product.objects.filter(id = productid.Product_id)
            serializer = GetProductSerializer(product, many=True)
            is_favourite = Wishlist.objects.filter(Product_id=productid.Product_id, user_id=request.user.id).exists()
            in_cart = Cart.objects.filter(productId_id = productid.Product_id, user_id = request.user.id).exists()
            cart_quantity = Cart.objects.filter(productId_id = productid.Product_id, user_id = request.user.id).first()
            pro_inventry = StoreInventory.objects.filter(product_id = productid.Product_id,status = 1).first()
            prorating = ProductRating.objects.filter(product_id=productid.Product_id).aggregate(Avg('rating'))['rating__avg']

            if cart_quantity:
             quantity = cart_quantity.quantity
            else:
             quantity = 0

            product_data_list = serializer.data

            for product_data in product_data_list:
             product_data['is_favourite'] = is_favourite
             product_data['in_cart'] = in_cart
             product_data['pro_quantity'] = quantity
             product_data['product_tags'] = 0
             product_data['inventory'] = pro_inventry.inventory if pro_inventry else 0
             product_data['rating'] = prorating if prorating else 4.5
             productlist.append(product_data)


             prolist = {}
             prolist['wish_product_list'] = productlist

        return Response({'status':True, 'msg':'wish list product', 'data': prolist}, status=status.HTTP_200_OK)
      else:
         return Response({'status':False, 'msg':'wish list is empty', 'data': {}}, status=status.HTTP_200_OK)


class DeleteWishList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      productId = request.data.get('product_id')
      user = request.user.id
      if Wishlist.objects.filter(Product_id=productId, user_id=user).exists():
        deletewishlist = Wishlist.objects.filter(Product_id=productId, user_id=user).delete()
        return Response({'status':True, 'msg':'Delete successfully', 'data': {}}, status=status.HTTP_200_OK)
      else:
        return Response({'status':False, 'msg':'This product not in your wishlist', 'data': {}}, status=status.HTTP_200_OK)

class RemoveAllwishList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def get(self, request, format=None):
      user = request.user.id
      if Wishlist.objects.filter(user_id=user).exists():
        removeall = Wishlist.objects.filter(user_id=user).delete()
        return Response({'status':True, 'msg':'Delete successfully', 'data': {}}, status=status.HTTP_200_OK)
      else:
        return Response({'status':False, 'msg':'wishlist already empty', 'data': {}}, status=status.HTTP_200_OK)


class OrderDetails(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      order_id  = request.data.get('order_id')
      user = request.user.id
      if Order.objects.filter(order_id = order_id, user_id = user).exists():
         getorder_details = Order.objects.get(order_id = order_id, user_id = user)
         orderdetail_serializer = OrderSerializer(getorder_details)
         prime_amount = PrimeMemberPlan.objects.filter(id = getorder_details.plan_id).first()
         if prime_amount:
            amountprime = prime_amount.plan_amount
         else:
            amountprime = 0
         if OrderRating.objects.filter(user_id_id = request.user.id,order_id=getorder_details.id).exists():
              order_rating = OrderRating.objects.filter(user_id_id = request.user.id,order_id=getorder_details.id)
              orderrating = OrderRatingSerializer(order_rating, many= True).data[0]
         else:
               orderrating = {}
         deliveryboyrating  = DeliveryBoyRating.objects.filter(user_id_id = request.user.id, order_id = getorder_details.id).exists()
         if deliveryboyrating:
            deliveryboyratingdetails  = DeliveryBoyRating.objects.filter(user_id_id = request.user.id, order_id = getorder_details.id)
            deliveryorderrating = DeliveryRatingSerializer(deliveryboyratingdetails, many= True).data[0]
         else:
            deliveryorderrating = {}

         get_store_details = Stores.objects.filter(name=getorder_details.store).first()
         if get_store_details is not None:
              storelat = get_store_details.latitude
              storelong = get_store_details.longitude

              storedetails = StroreSerializer(get_store_details)
         else:
              storelat = 0
              storelong = 0
              # Handle the case when no matching store is found
              storedetails = {}
         get_delivery_address = Address.objects.get(id = getorder_details.user_address_id.id)
         del_lat = get_delivery_address.latitude
         del_long = get_delivery_address.longitude

         delivery_address = UserDefaultAddressSerializer(get_delivery_address)
        #  storedetails = StroreSerializer(get_store_details)
         order_items  = OrderItem.objects.filter(order_id = getorder_details.id)
         if order_items.exists():
          coords_1 = (storelat, storelong)
          coords_2 = (del_lat, del_long)
          distance = geodesic(coords_1, coords_2).kilometers
          time = 30
          km_time = distance/time
          totaltime = int(km_time*60)
          iteam_count = OrderItem.objects.filter(order_id = getorder_details.id).count()
          if iteam_count <= 5:
             durations = str(5+totaltime)+ ' mins'
          elif iteam_count <= 15:
             durations = str(10+totaltime)+ ' mins'
          elif iteam_count <= 25:
             durations = str(15+totaltime)+ ' mins'
          else:
             durations =str(20+totaltime)+ ' mins'

          order_item_list = []
          for order_item  in order_items:
            product = Product.objects.get(id = order_item.product_id)
            product_serializer  = GetProductSerializer(product)
            prorating = ProductRating.objects.filter(product_id=order_item.product_id).aggregate(Avg('rating'))['rating__avg']
            product_data = product_serializer.data
            product_data['item_quantity'] = order_item.item_quantity
            product_data['rating'] = prorating if prorating else 4.5
            product_data['product_tags'] = 0
            order_item_list.append(product_data)
         else:
             order_item_list = ""
         assignDeliveryBoy= AssignOrderToDeliveryBoy.objects.filter(order_id = getorder_details.id).count()
         if assignDeliveryBoy > 0:
            delivery_boy_id = AssignOrderToDeliveryBoy.objects.filter(order_id = getorder_details.id).first()
            delivery_boy = User.objects.get(id = delivery_boy_id.user_id)
            delivery_boy_details =  DeliveryDetailsSerializer(delivery_boy).data
         else:
            delivery_boy_details ={}
         if getorder_details.delivery_instructions:
            my_string =  getorder_details.delivery_instructions
            my_string= my_string.split(',')
         else:
            my_string = []

         prolist = {}
         prolist['order_details'] = orderdetail_serializer.data
         prolist['order_details']['primemamber_amount'] = amountprime
         prolist['order_details']['delivery_instructions'] = my_string
         prolist['order_rating'] = orderrating
         prolist['order_item'] = order_item_list
         prolist['store_address'] = storedetails.data
         prolist['delivery_address'] = delivery_address.data
         prolist['delivery_boy_details'] = delivery_boy_details
         prolist['delivery_durations'] = durations
         prolist['delivery_boyrating'] = deliveryboyrating
         prolist['delivery_boyrating_details'] = deliveryorderrating
         return Response({'status':True, 'msg':' successfully', 'data': prolist}, status=status.HTTP_200_OK)
      else:
         return Response({'status':False, 'msg':'This order Id does not exit', 'data': 'null'}, status=status.HTTP_200_OK)



class ProductBrandList(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        store_id = request.data.get('store_id')

        # Query to get a list of unique product brand IDs for the given store
        product_brand_ids = StoreInventory.objects.filter(store_id=store_id).values_list(
            'product__Brand_id', flat=True
        ).distinct()
        # product_brand_count = StoreInventory.objects.filter(store_id=store_id).values_list(
        #     'product__Brand_id', flat=True
        # ).count()
        product_brand_count = ProductBrand.objects.filter(id__in=product_brand_ids).count()

        items_per_page = 20  # You can adjust this value as needed
        page_number = request.data.get('page', 1)
        paginator = Paginator(product_brand_ids, items_per_page)
        page = paginator.get_page(page_number)

        # Query to get the product brands using the list of brand IDs
        product_brands = ProductBrand.objects.filter(id__in=page)

        # Serialize the product brands
        product_brand_serializer = ProductBrandSerializer(product_brands, many=True)

        if product_brands:
            return Response({'status': True, 'msg': 'Successfully','total_product':product_brand_count, 'data': product_brand_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'msg': 'Data not found', 'data': []}, status=status.HTTP_200_OK)

class BrandProductList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      category_id  = request.data.get('category_id')
      store_id  = request.data.get('store_id')

      serializer = BrandProductlistSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      brand_id = serializer.validated_data['brand_id']
      if category_id is not None and category_id != '':
       productlistids = StoreInventory.objects.filter(store_id=store_id,status = 1).values_list(
            'product_id', flat=True
        ).distinct()
       productlist = Product.objects.filter(Brand_id = brand_id,category_id=category_id,id__in=productlistids)
       productlist_count = Product.objects.filter(Brand_id = brand_id,category_id=category_id, id__in=productlistids).count()
      else:
       productlistids = StoreInventory.objects.filter(store_id=store_id,status = 1).values_list(
            'product_id', flat=True
        ).distinct()
       productlist = Product.objects.filter(Brand_id = brand_id,id__in=productlistids)
       productlist_count = Product.objects.filter(Brand_id = brand_id,id__in=productlistids).count()
      items_per_page = 20  # You can adjust this value as needed
      page_number = request.data.get('page', 1)
      paginator = Paginator(productlist, items_per_page)
      page = paginator.get_page(page_number)
      brandproductlist = []
      for prolist in page:
          is_favourite = Wishlist.objects.filter(Product_id=prolist.id, user_id=request.user.id).exists()
          in_cart = Cart.objects.filter(productId_id = prolist.id, user_id = request.user.id).exists()
          cart_quantity = Cart.objects.filter(productId_id = prolist.id, user_id = request.user.id).first()
          inventory_count = StoreInventory.objects.filter(product_id = prolist.id,status = 1).first()
          prorating = ProductRating.objects.filter(product_id=prolist.id).aggregate(Avg('rating'))['rating__avg']

          if cart_quantity:
            quantity = cart_quantity.quantity
          else:
            quantity = 0

          brand_product_serializer = BrandProductSerializer(prolist)
          brandpro = brand_product_serializer.data


          brandpro['is_favourite'] = is_favourite
          brandpro['in_cart'] = in_cart
          brandpro['pro_quantity'] = quantity
          brandpro['product_tags'] = 0
          brandpro['inventory'] = inventory_count.inventory if inventory_count else 0
          brandpro['rating'] = prorating if prorating else 4.5

          brandproductlist.append(brandpro)

      if brandproductlist:
       return Response({'status':True, 'msg':' successfully','total_product':productlist_count, 'data': brandproductlist}, status=status.HTTP_200_OK)
      else:
         return Response({'status':False, 'msg':' data not found', 'data': []}, status=status.HTTP_200_OK)

class OrderAgain(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if Order.objects.filter(user_id=request.user.id).exists():
            order_queryset = Order.objects.filter(user_id=request.user.id).order_by('-id')
            product_set = set()  # Use a set to store unique product IDs
            product_list = []

            for order in order_queryset:
                order_items = OrderItem.objects.filter(order=order)
                for order_item in order_items:
                    product_id = order_item.product_id  # Get the product_id from order_item

                    # Check if the product_id has already been added to the set
                    if product_id in product_set:
                        continue  # Skip this product if it's a duplicate
                    else:
                        product_set.add(product_id)  # Add the product_id to the set
                        product = Product.objects.filter(id=product_id)
                        serializer = GetProductSerializer(product, many=True)
                        product_data_list = serializer.data

                        for product_data in product_data_list:
                            is_favourite = Wishlist.objects.filter(Product_id=product_id, user_id=request.user.id).exists()
                            in_cart = Cart.objects.filter(productId_id=product_id, user_id=request.user.id).exists()
                            cart_quantity = Cart.objects.filter(productId_id=product_id, user_id=request.user.id).first()
                            inventory_count = StoreInventory.objects.filter(product_id = product_id,status = 1).first()
                            prorating = ProductRating.objects.filter(product_id=product_id).aggregate(Avg('rating'))['rating__avg']


                            if cart_quantity:
                                quantity = cart_quantity.quantity
                            else:
                                quantity = 0

                            product_data['is_favourite'] = is_favourite
                            product_data['in_cart'] = in_cart
                            product_data['pro_quantity'] = quantity
                            product_data['product_tags'] = 0
                            product_data['inventory'] = inventory_count.inventory if inventory_count else 0
                            product_data['rating'] = prorating if prorating else 4.5

                            product_list.append(product_data)

            return Response({'status': True, 'msg': 'Successfully', 'data': product_list}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'msg': 'Data not found', 'data': []}, status=status.HTTP_200_OK)


class NewArivalProductList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      category_id  = request.data.get('category_id')
      store_id = request.data.get('store_id')

      product_ids_query = StoreInventory.objects.filter(store_id=store_id,status = 1).values('product_id')

      if category_id is not None and category_id != '':
            total_product = Product.objects.filter(
                product_tags = 6,
                category_id=category_id,
                id__in=product_ids_query
            ).count()
            get_product_ids = Product.objects.filter(
                category_id=category_id,
                product_tags = 6,
                id__in=product_ids_query
            )
      else:
            total_product = Product.objects.filter(
                product_tags = 6,
                id__in=product_ids_query
            ).count()
            get_product_ids = Product.objects.filter(
                product_tags = 6,
                id__in=product_ids_query
            )

      items_per_page = 20  # You can adjust this value as needed
      page_number = request.data.get('page', 1)
      paginator = Paginator(get_product_ids, items_per_page)
      page = paginator.get_page(page_number)

      newarival_productlist = []
      for store_pro in page:
        if not category_id:
          productlist = Product.objects.filter(product_tags = 6, id=store_pro.id)

        else:
          productlist = Product.objects.filter(category_id=category_id,product_tags = 6, id=store_pro.id)

        is_favourite = Wishlist.objects.filter(Product_id=store_pro.id, user_id=request.user.id).exists()
        in_cart = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).exists()
        cart_quantity = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).first()
        inventory_count = StoreInventory.objects.filter(product_id = store_pro.id,status = 1).first()
        prorating = ProductRating.objects.filter(product_id=store_pro.id).aggregate(Avg('rating'))['rating__avg']

        if cart_quantity:
               quantity = cart_quantity.quantity
        else:
                quantity = 0

        brand_product_serializer = NewArivalProductSerializer(productlist, many=True)
        brandpro = brand_product_serializer.data
        for item in brandpro:
            item['is_favourite'] = is_favourite
            item['in_cart'] = in_cart
            item['pro_quantity'] = quantity
            item['product_tags'] = 0
            item['inventory'] = inventory_count.inventory if inventory_count else 0
            item['rating'] = prorating if prorating else 4.5

            newarival_productlist.append(item)

      if newarival_productlist:
          return Response({'status':True, 'msg':' successfully','total_product':total_product, 'data': newarival_productlist}, status=status.HTTP_200_OK)
      else:
            return Response({'status':False, 'msg':' data not found', 'data': []}, status=status.HTTP_200_OK)

class PremiumProductList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      category_id  = request.data.get('category_id')
      store_id = request.data.get('store_id')
      product_ids_query = StoreInventory.objects.filter(store_id=store_id,status = 1).values('product_id')

      if category_id is not None and category_id != '':
            total_product = Product.objects.filter(
                product_tags = 4,
                category_id=category_id,
                id__in=product_ids_query
            ).count()
            get_product_ids = Product.objects.filter(
                category_id=category_id,
                product_tags = 4,
                id__in=product_ids_query
            )
      else:
            total_product = Product.objects.filter(
                product_tags = 4,
                id__in=product_ids_query
            ).count()
            get_product_ids = Product.objects.filter(
                product_tags = 4,
                id__in=product_ids_query
            )

      # get_store_product = StoreInventory.objects.filter(store_id=store_id)
      items_per_page = 20  # You can adjust this value as needed
      page_number = request.data.get('page', 1)
      paginator = Paginator(get_product_ids, items_per_page)
      page = paginator.get_page(page_number)

      newarival_productlist = []
      for store_pro in page:
        if not category_id:
          productlist = Product.objects.filter(product_tags = 4, id=store_pro.id)

        else:
          productlist = Product.objects.filter(category_id=category_id,product_tags = 4, id=store_pro.id)

        is_favourite = Wishlist.objects.filter(Product_id=store_pro.id, user_id=request.user.id).exists()
        in_cart = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).exists()
        cart_quantity = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).first()
        inventory_count = StoreInventory.objects.filter(product_id = store_pro.id,status = 1).first()
        prorating = ProductRating.objects.filter(product_id=store_pro.id).aggregate(Avg('rating'))['rating__avg']

        if cart_quantity:
               quantity = cart_quantity.quantity
        else:
                quantity = 0

        brand_product_serializer = NewArivalProductSerializer(productlist, many=True)
        brandpro = brand_product_serializer.data
        for item in brandpro:
            item['is_favourite'] = is_favourite
            item['in_cart'] = in_cart
            item['pro_quantity'] = quantity
            item['product_tags'] = 0
            item['inventory'] = inventory_count.inventory if inventory_count else 0
            item['rating'] = prorating if prorating else 4.5

            newarival_productlist.append(item)

      if newarival_productlist:
          return Response({'status':True, 'msg':' successfully','total_product':total_product, 'data': newarival_productlist}, status=status.HTTP_200_OK)
      else:
            return Response({'status':False, 'msg':' data not found', 'data': []}, status=status.HTTP_200_OK)

class SummerProductList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      category_id  = request.data.get('category_id')
      store_id = request.data.get('store_id')

      product_ids_query = StoreInventory.objects.filter(store_id=store_id,status = 1).values('product_id')

      if category_id is not None:
            total_product = Product.objects.filter(
                product_tags = 5,
                category_id=category_id,
                id__in=product_ids_query
            ).count()
            get_product_ids = Product.objects.filter(
                category_id=category_id,
                product_tags = 5,
                id__in=product_ids_query
            )
      else:
            total_product = Product.objects.filter(
                product_tags = 5,
                id__in=product_ids_query
            ).count()
            get_product_ids = Product.objects.filter(
                product_tags = 5,
                id__in=product_ids_query
            )

      get_store_product = StoreInventory.objects.filter(store_id=store_id,status = 1)
      items_per_page = 20  # You can adjust this value as needed
      page_number = request.data.get('page', 1)
      paginator = Paginator(get_product_ids, items_per_page)
      page = paginator.get_page(page_number)

      newarival_productlist = []
      for store_pro in page:
        if not category_id:
          productlist = Product.objects.filter(product_tags = 5, id=store_pro.id)

        else:
          productlist = Product.objects.filter(category_id=category_id,product_tags = 5, id=store_pro.id)

        is_favourite = Wishlist.objects.filter(Product_id=store_pro.id, user_id=request.user.id).exists()
        in_cart = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).exists()
        cart_quantity = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).first()
        inventory_count = StoreInventory.objects.filter(product_id = store_pro.id,status = 1).first()
        prorating = ProductRating.objects.filter(product_id=store_pro.id).aggregate(Avg('rating'))['rating__avg']

        if cart_quantity:
               quantity = cart_quantity.quantity
        else:
                quantity = 0

        brand_product_serializer = NewArivalProductSerializer(productlist, many=True)
        brandpro = brand_product_serializer.data
        for item in brandpro:
            item['is_favourite'] = is_favourite
            item['in_cart'] = in_cart
            item['pro_quantity'] = quantity
            item['product_tags'] = 0
            item['inventory'] = inventory_count.inventory if inventory_count else 0
            item['rating'] = prorating if prorating else 4.5

            newarival_productlist.append(item)

      if newarival_productlist:
          return Response({'status':True, 'msg':' successfully', 'data': newarival_productlist}, status=status.HTTP_200_OK)
      else:
            return Response({'status':False, 'msg':' data not found', 'data': []}, status=status.HTTP_200_OK)

class ApplyCoupn(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      serializer = CouponCodeApplySerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      coupon_code = serializer.validated_data['coupon_code']
      user_id =  request.user.id
      try:
        coupon = Coupon.objects.get(code=coupon_code)

        if ApplyCoupon.objects.filter(user_id=user_id).exists():
         return Response({'status':False, 'msg':'alredy apply coupon', 'data': {}}, status=status.HTTP_200_OK)
        applycoupon = ApplyCoupon(coupon_code= coupon_code, user_id= user_id)
        applycoupon.save()
        if applycoupon:
         return Response({'status':True, 'msg':'coupon apply successfully', 'data': {}}, status=status.HTTP_200_OK)

      except Coupon.DoesNotExist:
                return Response({'status': False, 'msg': 'Coupon code invalid', 'data': {}}, status=status.HTTP_200_OK)


class RemoveApplyCoupn(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def get(self, request, format=None):
      user_id =  request.user.id
      try:
        applycoupon = ApplyCoupon.objects.get(user_id=user_id)
        applycoupon.delete()
        return Response({'status': True, 'msg': 'Coupon deleted successfully', 'data': {}}, status=status.HTTP_200_OK)
      except ApplyCoupon.DoesNotExist:
          return Response({'status': False, 'msg': 'No coupon applied', 'data': {}}, status=status.HTTP_200_OK)

class RecentSearch(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def get(self, request, format=None):
      user_id =  request.user.id

      search_keyp = SerachProduct.objects.filter(user_id=user_id) \
                    .values('product_name') \
                    .annotate(max_id=Max('id')) \
                    .order_by('-max_id') \
                    [:5]
      search_key = SearchKeySerializer(search_keyp, many=True)
      return Response({'status': True, 'msg': 'recent search', 'data': search_keyp}, status=status.HTTP_200_OK)


class ClearOrderHistory(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      user_id =  request.user.id
      order_id = request.data.get('order_id')
      if order_id is not None and order_id != '':
         delete_order = Order.objects.filter(user_id = user_id,order_id = order_id, order_status_id__in = [6,7,8]).update(is_delete=1)
         return Response({'status': True, 'msg': 'This order deleted successfully', 'data': {}}, status=status.HTTP_200_OK)
      else:
         delete_order = Order.objects.filter(user_id = user_id,order_status_id__in = [6,7,8]).update(is_delete=1)
         return Response({'status': True, 'msg': 'All orders deleted successfully', 'data': {}}, status=status.HTTP_200_OK)

class CartQuantity(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def get(self, request, format=None):
      user_id = request.user.id
      if Cart.objects.filter(user_id = user_id).exists():
        cartiteam_quantity = Cart.objects.filter(user_id = user_id,plan_id = None).count()
        product_id = Cart.objects.filter(user_id = user_id).first()
        get_productimage =  Product.objects.filter(id=product_id.productId_id).first()
        cartimg = CartImageSerializer(get_productimage).data
        subtotal_amount = Cart.objects.filter(user_id=user_id).aggregate(total=Sum('total_amount'))['total']
        cartdata = {
                'iteam_quantity': cartiteam_quantity,
                'total_amount': str(subtotal_amount),
                'image' : cartimg
            }
        return Response({'status': True, 'msg': 'successfully', 'data': cartdata}, status=status.HTTP_200_OK)
      else:
         return Response({'status': False, 'msg': 'your cart is empty', 'data': {}}, status=status.HTTP_200_OK)

class ProductDetail(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        product_id = request.data.get('product_id')
        category_id = request.data.get('category_id')
        store_id = request.data.get('store_id')
        get_product_details = Product.objects.filter(id=product_id).first()
        is_favourites = Wishlist.objects.filter(Product_id=product_id, user_id=request.user.id).exists()
        in_carts = Cart.objects.filter(productId_id=product_id, user_id=request.user.id).exists()
        cart_quantity = Cart.objects.filter(productId_id=product_id, user_id=request.user.id).first()
        inventory_count = StoreInventory.objects.filter(product_id=product_id,status = 1).first()
        prorating = ProductRating.objects.filter(product_id=product_id).aggregate(Avg('rating'))['rating__avg']
        if inventory_count.price == 0 or inventory_count.price == None:
            price_details = get_product_details.price
        else:
           price_details = str(inventory_count.price)


        if cart_quantity:
            quantitys = cart_quantity.quantity
            total_amounts = (quantitys * float(get_product_details.price))
        else:
            quantitys = 0
            total_amounts = 0

        product_images = Images.objects.filter(product_id=product_id)
        productimages = ProductImagesSerializer(product_images, many=True).data
        product_details = ProductDetilSerializer(get_product_details).data

        if category_id is not None and category_id != '' and category_id == '0':

            similar_product = Product.objects.filter(category_id=get_product_details.category_id).exclude(id=product_id)[:15]
        else:

            similar_product = Product.objects.filter(category_id=category_id).exclude(id=product_id)[:15]
        similer_product_list = []

        for prolist in similar_product:
                store_inventory_exists = StoreInventory.objects.filter(store_id=store_id, product_id=prolist.id, status=1).exists()
                if store_inventory_exists:
                    is_favourite = Wishlist.objects.filter(Product_id=prolist.id, user_id=request.user.id).exists()
                    in_cart = Cart.objects.filter(productId_id=prolist.id, user_id=request.user.id).exists()
                    cart_quantity = Cart.objects.filter(productId_id=prolist.id, user_id=request.user.id).first()
                    inventory_countsimiler = StoreInventory.objects.filter(product_id=prolist.id,status = 1,store_id = store_id).first()  # Fixed variable name here
                    prorating = ProductRating.objects.filter(product_id=prolist.id).aggregate(Avg('rating'))['rating__avg']
                    if inventory_countsimiler.price == 0 or inventory_countsimiler.price == None:
                        price = prolist.price
                    else:
                         price = str(inventory_countsimiler.price)

                    if cart_quantity:
                        quantity = cart_quantity.quantity
                        total_amount = (quantity * float(get_product_details.price))
                    else:
                        quantity = 0
                        total_amount = 0

                    similar_product_details = ProductDetilSerializer(prolist).data
                    similar_product_details['price'] = price
                    similar_product_details['product_tags'] = 0
                    similar_product_details['is_favourite'] = is_favourite
                    similar_product_details['in_cart'] = in_cart
                    similar_product_details['pro_quantity'] = quantity
                    similar_product_details['tota_amount'] = total_amount
                    similar_product_details['inventory'] = inventory_countsimiler.inventory if inventory_countsimiler else 0
                    similar_product_details['rating'] = prorating if prorating else 4.5


                    similer_product_list.append(similar_product_details)



        must_like_product = Product.objects.filter(subcategory_id=get_product_details.subcategory_id).exclude(id=product_id)[:15]
        must_like_product_list = []

        for prolistmust in must_like_product:
                store_inventory_exists = StoreInventory.objects.filter(store_id=store_id, product_id=prolistmust.id, status=1).exists()
                if store_inventory_exists:
                    is_favourite = Wishlist.objects.filter(Product_id=prolistmust.id, user_id=request.user.id).exists()
                    in_cart = Cart.objects.filter(productId_id=prolistmust.id, user_id=request.user.id).exists()
                    cart_quantity = Cart.objects.filter(productId_id=prolistmust.id, user_id=request.user.id).first()
                    inventory_countlike = StoreInventory.objects.filter(product_id=prolistmust.id,status = 1,store_id=store_id).first()  # Fixed variable name here
                    prorating = ProductRating.objects.filter(product_id=prolistmust.id).aggregate(Avg('rating'))['rating__avg']
                    if inventory_countlike.price == 0 or inventory_countlike.price == None:
                        price = prolist.price
                    else:
                         price = str(inventory_countlike.price)

                    if cart_quantity:
                        quantity = cart_quantity.quantity
                        total_amount = (quantity * float(get_product_details.price))
                    else:
                        quantity = 0
                        total_amount = 0

                    mustlike_product_details = ProductDetilSerializer(prolistmust).data
                    mustlike_product_details['price'] = price
                    mustlike_product_details['product_tags'] = 0
                    mustlike_product_details['is_favourite'] = is_favourite
                    mustlike_product_details['in_cart'] = in_cart
                    mustlike_product_details['pro_quantity'] = quantity
                    mustlike_product_details['tota_amount'] = total_amount
                    mustlike_product_details['inventory'] = inventory_countlike.inventory if inventory_countlike else 0
                    mustlike_product_details['rating'] = prorating if prorating else 4.5


                    must_like_product_list.append(mustlike_product_details)

        product_details['price'] = price_details
        product_details['product_tags'] = 0
        product_details['is_favourite'] = is_favourites
        product_details['in_cart'] = in_carts
        product_details['pro_quantity'] = quantitys
        product_details['tota_amount'] = total_amounts
        product_details['product_all_images'] = productimages
        product_details['inventory'] = inventory_count.inventory if inventory_count else 0
        product_details['rating'] = prorating if prorating else 4.5

        product_details['similar_product'] = must_like_product_list
        product_details['you_may_like'] = similer_product_list

        return Response({'status': True, 'msg': 'successfully', 'data': product_details}, status=status.HTTP_200_OK)

class Notifications(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        user_id = request.user.id
        if Notification.objects.filter(user_id = user_id).exists():
            notification_list = Notification.objects.filter(user_id = user_id).order_by('-timestamp')
            listnotification = NotificationListSerializer(notification_list,many =True).data
            return Response({'status':True, 'data': listnotification,'msg': 'Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False, 'data': [],'msg': 'data not found'}, status=status.HTTP_200_OK)

class ReorderView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user_id = request.user.id
        order_id = request.data.get('order_id')
        store_id = request.data.get('store_id')
        if not order_id:
            return Response({'status':False, 'data': {},'msg': 'order_id is required.'}, status=status.HTTP_200_OK)
        elif not store_id:
            return Response({'status':False, 'data': {},'msg': 'store_id is required.'}, status=status.HTTP_200_OK)
        else:
            if Order.objects.filter(order_id = order_id,store_id=store_id).exists():
              removecart = Cart.objects.filter(user_id=user_id).delete()
              getorder_id = Order.objects.filter(order_id = order_id).first()
              order_iteam = OrderItem.objects.filter(order_id = getorder_id.id)
              for item in order_iteam:
                  priceinventory = StoreInventory.objects.filter(product_id = item.product_id).first()
                  if priceinventory.price == 0 or priceinventory.price==None:
                      priamt = getpro_detail.price
                  else:
                      priamt = str(priceinventory.price)
                  getpro_detail = Product.objects.filter(id = item.product_id).first()
                  quantity = int(item.item_quantity)
                  weight = getpro_detail.product_weight
                  amount = float(priamt)
                  total_amount = int(quantity*amount)
                  productId_id = item.product_id
                  user_id = user_id
                  store_id = item.store_id
                  addincart = Cart(quantity=quantity,weight=weight,amount=amount,total_amount=total_amount,productId_id=productId_id,user_id=user_id,store_id=store_id)
                  addincart.save()
              return Response({'status':True, 'data': {},'msg': 'success.'}, status=status.HTTP_200_OK)
            else:
              return Response({'status':False, 'data': {},'msg': 'Please change store.'}, status=status.HTTP_200_OK)

class AddOrderRatingView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user_id = request.user.id
        message = request.data.get('message')
        order_id = request.data.get('order_id')
        rating = request.data.get('rating')
        if not order_id:
            return Response({'status':False, 'data': {},'msg': 'order_id is required.'}, status=status.HTTP_200_OK)
        elif not rating:
            return Response({'status':False, 'data': {},'msg': 'rating is required.'}, status=status.HTTP_200_OK)
        else:
            if OrderRating.objects.filter(user_id_id=user_id,order_id=order_id).exists():
               return Response({'status':False, 'data': {},'msg': 'already added.'}, status=status.HTTP_200_OK)
            else:
              getorderiteam = OrderItem.objects.filter(order_id = order_id)
              for orderiteam in getorderiteam:
                 addratingpro = ProductRating(rating = rating,product_id = orderiteam.product_id)
                 addratingpro.save()

              order_id = order_id
              user_id = user_id
              message = message
              rating = rating
              addincart = OrderRating(order_id=order_id,user_id_id=user_id,messages=message,rating=rating)
              addincart.save()
              return Response({'status':True, 'data': {},'msg': 'success.'}, status=status.HTTP_200_OK)


class AddDelivryboyRatingView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user_id = request.user.id
        message = request.data.get('message')
        order_id = request.data.get('order_id')
        rating = str(request.data.get('rating'))
        order_rating = str(request.data.get('order_rating'))
        order_message = request.data.get('order_message')
        deliveryboy_id = request.data.get('deliveryboy_id')
        if not order_id:
            return Response({'status':False, 'data': {},'msg': 'order_id is required.'}, status=status.HTTP_200_OK)
        elif not deliveryboy_id:
            return Response({'status':False, 'data': {},'msg': 'deliveryboy_id is required.'}, status=status.HTTP_200_OK)
        else:
            if DeliveryBoyRating.objects.filter(user_id_id=user_id,order_id=order_id).exists():
               return Response({'status':False, 'data': {},'msg': 'already added.'}, status=status.HTTP_200_OK)
            else:

              if rating == "0" and order_rating == "0":
                    updaterating = Order.objects.filter(id = order_id).update(skip_rating = 1)
                    return Response({'status':True, 'data': {},'msg': ''}, status=status.HTTP_200_OK)
              else:
                    order_id = order_id
                    user_id = user_id
                    message = message
                    rating = rating
                    deliveryboy_id = deliveryboy_id
                    addincart = DeliveryBoyRating(order_id=order_id,user_id_id=user_id,messages=message,rating=rating,deliveryboy_id = deliveryboy_id)
                    addincart.save()

                    getorderiteam = OrderItem.objects.filter(order_id = order_id)
                    for orderiteam in getorderiteam:
                        addratingpro = ProductRating(rating = rating,product_id = orderiteam.product_id)
                        addratingpro.save()

                    order_id = order_id
                    user_id = user_id
                    order_message = order_message
                    order_rating = order_rating
                    addincart = OrderRating(order_id=order_id,user_id_id=user_id,messages=order_message,rating=order_rating)
                    addincart.save()
                    updaterating = Order.objects.filter(id = order_id).update(skip_rating = 1)

                    return Response({'status':True, 'data': {},'msg': 'your rating has been submited.'}, status=status.HTTP_200_OK)

class DownloadProductImage(GenericAPIView):
    def get(self, request, format=None):
        product_data = Product.objects.exclude(product_url__exact='', product_url__isnull=False)
        # product_data=GetProductSerializer(product_data,many =True).data
        if product_data:
            for productData in product_data:
                image_url = productData.product_url
                # Make a request to the image URL
                image_response = requests.get(image_url)
                # Extract the filename from the URL
                image_filename = image_url.split('/')[-1]
                image_content = ContentFile(image_response.content)
                productData.product_url=''
                # Update the product_image field for the current productData
                productData.product_image.save(image_filename, image_content)

        return Response({'message':product_data})



        # print(product_data)

