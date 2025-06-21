from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from fulfillmentmanager.serializers import UserFullProfileSerializer
from product.serializers import GetProductSerializer,TagSerializer,OrderRatingSerializer,UserdetailsSerializer,DeliveryRatingSerializer,PlanBenefitsSerializer,NotificationListSerializer,NewArivalProductSerializer,CouponCodeApplySerializer,UserorderAddressSerializer,UserAddressSerializer,ProductImagesSerializer, ProductDetilSerializer,CartImageSerializer,SearchKeySerializer, DeliveryDetailsSerializer,CouponSerializer, BrandProductSerializer,UserDefaultAddressSerializer, BrandProductlistSerializer, UpdateCartQuantitySerializer,OrderSerializer,StroreSerializer,CetegoryDetailSerializer, OrderItemSerializer, SearchProductSerializer, ProductListSerializer,CategoryListSerializer,ProductDetailSerializer, AddCartSerializer, CategoriesSerializer, SubCategoriesSerializer, ViewCartSerializer, DeleteCartSerializer, CouponListSerializer, CoupondiscountSerializer, DashboardSerializer, OfferSerializer, ProductBrandSerializer, AddCartSerializer, AddToWishSerializer
from product.models import ProductTag, Product,Images,Tag,ProductRating, OrderRating,DeliveryBoyRating, CatalogCategory,SerachProduct, ApplyCoupon,CatalogSubCategory, Order, OrderItem, ProductBrand, Wishlist, OrderItem, ProductDiscountm
from setting.models import OrderStatus
from order.models import OrderLog, AssignOrderToStoreBoy, AssignOrderToDeliveryBoy
from accounts.models import Cart,Address,User,GustUser,PrimeMemberPlan,PlanBenefits,UserSubscription ,OrderAddress, FcmToken
from coupon_management.validations import validate_coupon
from coupon_management.models import Coupon
from CreateCoupon.models import CustomCoupon
# from customer.models import NonPrime
from stores.models import Stores,StoreInventory,ProductDiscount, AssignStoreBoy, AssignFulfillmentManager, AssignStoreManagers,DeliveryCharges,ServiceRange,StoreTiming
from banner.models import HomeBanner,OfferBanners,Notification
from datetime import datetime,date
from rest_framework import views
from decimal import Decimal
from decimal import Decimal, getcontext
from django.db.models.functions import Lower
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

import csv,datetime
from product.forms import CSVUploadForm
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum
from accounts.views import TestNotifications,CheckDays
from django.http import HttpRequest
import re
from django.db.models import OuterRef, Subquery,F
from geopy.distance import geodesic
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.measure import Distance
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import Avg
from django.db.models import Count, Max, Min
from datetime import datetime
from django.core.files.base import ContentFile
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
from datetime import timedelta
from django.core.cache import cache
import logging
from django.db.models import Case, When
import concurrent.futures

# Create your views here.
class CalculateDeliveryCharge(GenericAPIView):
   def deliver_charge(user_id,distance):

            getplan_id = UserSubscription.objects.filter(user_id = user_id,status =1, payment_status =9).first()

            if getplan_id is not None:

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

            else:
                response_data = {
                    'status': False,
                    'price': 0,
                    'msg': 'No plan id found ',
                    # 'prime_discount': primediscount,
                    # 'market_discount': marketdiscount,

                }
                return (response_data)

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

            opentimee = (storetime).split(" ")
            opentime  = opentimee[0]
            opntime = str(opentime).replace('.', ':')
            finalopenstore_time  = opntime+' '+opentimee[1]
            opentime_time = datetime.strptime(finalopenstore_time, '%I:%M %p').time()

            if store_time < current_time or opentime_time > current_time:
                return(1)
            else:
               return(0)


# class DeliveryChargeNonProme(GenericAPIView):
#    def deliver_charge(user_id,distance):
from django.core.exceptions import ObjectDoesNotExist


class GetProductView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetProductSerializer

    def post(self, request, format=None):
        try:
            # Step 1: Read request parameters
            user = request.user
            data = request.data
            store_id = data.get('store_id')
            category_id = data.get('category_id')
            sub_category_id = data.get('sub_category_id')
            looking_for = data.get('looking_for')
            product_tags = data.get('product_tags', [])
            brand_ids = data.get('brand_ids', [])
            price_low = data.get('price_low')
            price_high = data.get('price_high')
            search_text = data.get('search_text', '').strip()
            price_min = data.get('min')
            price_max = data.get('max')
            product_sort = data.get('product_sort')
            page_number = data.get('page', 1)

            # Step 2: Initial product filtering by store
            store_products = StoreInventory.objects.filter(store_id=store_id, status=1).values_list('product_id', flat=True)
            products = Product.objects.filter(id__in=store_products, status=1)

            if category_id:
                products = products.filter(category_id=category_id)
            if sub_category_id:
                products = products.filter(subcategory_id=sub_category_id)
            if looking_for:
                products = products.filter(product_for=looking_for)
            if product_tags:
                products = products.filter(product_tags__id__in=product_tags).distinct()
            if brand_ids:
                products = products.filter(Brand__id__in=brand_ids)
            if price_low is not None and price_high is not None:
                products = products.filter(price__gte=price_low, price__lte=price_high)
            if search_text:
                products = products.filter(
                    Q(product_name__icontains=search_text) |
                    Q(Brand__name__icontains=search_text) |
                    Q(product_weight__icontains=search_text) |
                    Q(category__name__icontains=search_text)
                )

            # Step 3: Price range computation
            price_range = products.aggregate(min_price=Min('price'), max_price=Max('price'))
            fallback_min = price_range['min_price'] or 0.0
            fallback_max = price_range['max_price'] or 0.0

            price_min_final = float(price_min) if price_min not in [None, ""] else fallback_min
            price_max_final = float(price_max) if price_max not in [None, ""] else fallback_max

            products = products.filter(price__gte=price_min_final, price__lte=price_max_final)

            # Step 4: Sorting
            if product_sort == "A_to_Z":
                products = products.order_by(Lower('product_name'))
            elif product_sort == "Z_to_A":
                products = products.order_by(Lower('product_name').desc())
            elif product_sort == "low_to_high":
                products = products.order_by('price')
            elif product_sort == "high_to_low":
                products = products.order_by('-price')
            elif product_sort == "most_popular_product":
                popular_map = {
                    p['product_id']: p['total_ordered']
                    for p in OrderItem.objects.values('product_id').annotate(total_ordered=Sum('item_quantity'))
                }
                sorted_ids = sorted(products.values_list('id', flat=True), key=lambda x: popular_map.get(x, 0), reverse=True)
                preserved_order = Case(*[When(id=pid, then=pos) for pos, pid in enumerate(sorted_ids)])
                products = products.filter(id__in=sorted_ids).order_by(preserved_order)

            total_product = products.exclude(price=0.00).count()

            # Step 5: Pagination
            paginator = Paginator(products, 20)
            try:
                page = paginator.page(page_number)
            except (EmptyPage, PageNotAnInteger):
                return Response({
                    'status': False,
                    'msg': 'Invalid page number',
                    'data': {
                        'store_id': store_id,
                        'total_product': total_product,
                        'product_list': [],
                        'min': fallback_min,
                        'max': fallback_max,
                    }
                }, status=status.HTTP_200_OK)

            # Step 6: Preload related data
            page_ids = list(page.object_list.values_list('id', flat=True))
            inventories = {inv.product_id: inv for inv in StoreInventory.objects.filter(product_id__in=page_ids, store_id=store_id, status=1)}
            discounts = {d.product_id: d for d in ProductDiscount.objects.filter(product_id__in=page_ids)}
            wishlisted = set(Wishlist.objects.filter(Product_id__in=page_ids, user_id=user.id).values_list('Product_id', flat=True))
            cart_map = {c.productId_id: c for c in Cart.objects.filter(productId_id__in=page_ids, user_id=user.id)}
            ratings = {r['product_id']: r['rating__avg'] for r in ProductRating.objects.filter(product_id__in=page_ids).values('product_id').annotate(Avg('rating'))}

            # Step 7: Construct response
            product_list = []
            for product in page:
                inv = inventories.get(product.id)
                if not inv or product.price == 0.0 or product.status != 1 or inv.status != 1:
                    continue

                discount_obj = discounts.get(product.id)
                prod_discount = discount_obj.discount if discount_obj else 0
                final_price = product.price - (product.price * prod_discount / 100) if discount_obj else product.price

                serializer = self.serializer_class(product)
                product_data = serializer.data
                product_data.update({
                    'product_name': product_data['product_name'].title(),
                    'is_favourite': product.id in wishlisted,
                    'in_cart': product.id in cart_map,
                    'pro_quantity': cart_map.get(product.id).quantity if product.id in cart_map else 0,
                    'product_tags': 0,
                    'inventory': inv.inventory,
                    'rating': ratings.get(product.id, 4.5),
                    'status': 1,
                    'price': f"{final_price:.2f}",
                    'product_discount': prod_discount,
                })
                product_list.append(product_data)

            response_data = {
                'store_id': store_id,
                'total_product': total_product,
                'product_list': product_list,
                'min': fallback_min,
                'max': fallback_max,
            }

            msg = 'Product list' if product_list else 'Data not found'
            return Response({'status': bool(product_list), 'msg': msg, 'data': response_data}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'status': False, 'msg': 'Object does not exist'}, status=status.HTTP_404_NOT_FOUND)


class AddtoCart(GenericAPIView):
   #permission_classes = [IsAuthenticated]
   serializer_class = AddCartSerializer
   def post(self, request, format= None):
        product_id = request.data['productId']
        store_id = request.data['store']
        looking_for = request.data['looking_for']
        quantity  = int(request.data['quantity'])
        user_id = request.user.id
        dashboard_cache_key = f"dashboard_{looking_for}_{store_id}_{user_id}"
        cache.delete(dashboard_cache_key)
        closetime  = CheckSroreTime.Check_Store_time(int(store_id))
        if closetime == 1:
           return Response({'status':False, 'data':{}, 'msg':'Store closed'})
        else:
            if StoreInventory.objects.filter(store_id = store_id, product_id = product_id,status = 1).exists():
        #   get_inventory = StoreInventory.objects.get(store_id = store_id, product_id = product_id,status = 1).inventory
        #   if quantity > get_inventory:
        #    return Response({'status':False, 'data':{}, 'msg':f'this product quantity not available. Only {get_inventory} item left.'})
                if Cart.objects.filter(productId_id = product_id, user_id = user_id,looking_for=looking_for).exists():
                  return Response({'status':False, 'data':{}, 'msg':'This product already in cart'})
                serializer = AddCartSerializer(data= request.data, context={'request': request})
                if not serializer.is_valid():
                    return Response({'status':False, 'errors':serializer.errors, 'msg':'Something went wrong'})
                serializer.save()
                return Response({'status':True, 'data':serializer.data, 'msg':'Data saved successfully'})
            else:
                return Response({'status':False, 'data':{}, 'msg':'This product is not available in store'})


class ClearCart(GenericAPIView):
   #permission_classes = [IsAuthenticated]
   serializer_class = AddCartSerializer
   def post(self, request, format= None):
        user_id = request.user.id
        looking_for = request.data['looking_for']
        cart_items = Cart.objects.filter(user_id=user_id, looking_for=looking_for)
        store_id = cart_items.values_list('store_id', flat=True).distinct()
        # clear_cart = Cart.objects.filter(user_id = user_id,looking_for=looking_for).delete()
        cart_items.delete()
        dashboard_cache_key = f"dashboard_{looking_for}_{store_id}_{user_id}"
        cache.delete(dashboard_cache_key)
        return Response({'status':True, 'data':{}, 'msg':'Your cart cleared successfully'})


class AddPrimeInCart(GenericAPIView):
   #permission_classes = [IsAuthenticated]
   serializer_class = AddCartSerializer
   def post(self, request, format= None):
        plan_id = request.data['plan_id']
        user_id = request.user.id
        if Cart.objects.filter(user_id=user_id,plan_id = plan_id).exists():
           return Response({'status':False, 'data':{}, 'msg':'This plan is already added'})
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
           return Response({'status':True, 'data':{}, 'msg':'Removed successfully'})
        else:
           return Response({'status':False, 'data':{}, 'msg':'This plan is not added into the cart'})

class UpdateCartQuantity(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateCartQuantitySerializer

    def post(self, request, format=None):
        serializer = UpdateCartQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        productId = serializer.validated_data['productId']
        updatequantity = serializer.validated_data['update_quantity']
        looking_for = serializer.validated_data['looking_for']
        user_id = request.user.id

        try:
            get_cart = Cart.objects.get(user_id=user_id, productId_id=productId,looking_for=looking_for)
            get_store_id = get_cart.store_id
            get_inventory = StoreInventory.objects.get(store_id=get_store_id, product_id=productId, status=1).inventory

            # if get_inventory < updatequantity:
            #     return Response({'status': False, 'data': {}, 'msg': 'Insufficient stock'})

            get_amount = get_cart.amount
            update_amt = updatequantity * get_amount

            update_cart = Cart.objects.filter(productId_id=productId, user_id=user_id,looking_for=looking_for).update(total_amount=update_amt, quantity=updatequantity)

            if update_cart:
                return Response({'status': True, 'data': {}, 'msg': 'Quantity updated'})
            else:
                return Response({'status': False, 'data': {}, 'msg': 'Update failed. Please try again'})

        except Cart.DoesNotExist:
            return Response({'status': False, 'data': {}, 'msg': 'Cart item not found. Check product ID or cart contents.'})

        except Exception as e:
            return Response({'status': False, 'data': {}, 'msg': 'An error occurred. Please try again later.'})

class AddTipIncart(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = UpdateCartQuantitySerializer
   def post(self, request, format= None):
      tip = request.data.get('tip')
      looking_for = request.data.get('looking_for')
      user_id = request.user.id
      get_cart = Cart.objects.filter(user_id = user_id,looking_for=looking_for).first()
      update_tip = Cart.objects.filter(id = get_cart.id,looking_for=looking_for).update(add_tip = tip)
      return Response({'status':True, 'data':{}, 'msg':'Tip added'})

class DeliveryInstAdd(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = UpdateCartQuantitySerializer
   def post(self, request, format= None):
      delivery_instructions = request.data.get('delivery_instructions')
      user_id = request.user.id
      get_cart = Cart.objects.filter(user_id = user_id).first()
      delivery_inst  = Cart.objects.filter(id = get_cart.id).update(delivery_instructions = delivery_instructions)
      return Response({'status':True, 'data':{}, 'msg':'Delivery instructions added'})

class RemoveTipIncart(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = UpdateCartQuantitySerializer
   def post(self, request, format= None):
      user_id = request.user.id
      looking_for = request.data['looking_for']
      get_cart = Cart.objects.filter(user_id = user_id,looking_for=looking_for).first()
      update_tip = Cart.objects.filter(id = get_cart.id,looking_for=looking_for).update(add_tip = 0)
      return Response({'status':True, 'data':{}, 'msg':'Tip removed successfully'})

class RemoveDeliveryInst(GenericAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = UpdateCartQuantitySerializer
   def get(self, request, format= None):
      user_id = request.user.id
      get_cart = Cart.objects.filter(user_id = user_id).first()
      update_tip = Cart.objects.filter(id = get_cart.id).update(delivery_instructions = None)
      return Response({'status':True, 'data':{}, 'msg':'Delivery instructions removed successfully'})


class Categories(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoriesSerializer
    def post(self, request, format=None):
     looking_for = request.data['looking_for']
     store_id = request.data.get('store')
     product_ids_query = StoreInventory.objects.filter(store_id=store_id, status=1).values('product_id')
     cat_ids_query = Product.objects.filter(product_for=looking_for,id__in=product_ids_query).values('category_id')
     categories = CatalogCategory.objects.filter(status =1,cat_for=looking_for,id__in=cat_ids_query)
     serializer = CategoriesSerializer(categories, many=True)
     categories_with_products = []
     for category in serializer.data:
            if Product.objects.filter(category_id=category['id']).exists():
                categories_with_products.append(category)

     if serializer is not None:
      categorieslist = {}
      categorieslist['categories listing'] = categories_with_products
      return Response({'status':True, 'msg':'Categories list', 'data': categorieslist}, status=status.HTTP_200_OK)
     else:
      return Response({'status':False, 'msg':'Data not found', 'data': {}}, status=status.HTTP_200_OK)

class SubCategories(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubCategoriesSerializer
    def post(self, request, format=None):
     looking_for = request.data['looking_for']
     subcategories = CatalogSubCategory.objects.filter(category_id = request.data['category_id'],status =1,subcat_for=looking_for)
     serializer = SubCategoriesSerializer(subcategories, many=True)
     if serializer is not None:
      subcategories_list = {}
      subcategories_list['sub_categories_list'] = serializer.data
      return Response({'status':True, 'msg':'Sub categories list', 'data': subcategories_list}, status=status.HTTP_200_OK)
     else:
      return Response({'status':False, 'msg':'Data not found', 'data': {}}, status=status.HTTP_200_OK)

class ViewCart(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ViewCartSerializer, UserDefaultAddressSerializer

    def post(self, request, format=None):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')
        user_id = request.user.id
        looking_for = request.data['looking_for']
        store_id = request.data.get('store')
        current_date = datetime.now().date()  # Get the current date
        is_special_day = CheckDays.is_1st_or_3rd_wednesday(current_date)

        
        
        # dtime = '25-30 mins'

        if authorization_header:
           if authorization_header.startswith('Bearer '):
             bearer_token = authorization_header[7:]
             if GustUser.objects.filter(id=user_id,access_token = bearer_token):
               viewcart = Cart.objects.filter(user=user_id,plan_id = None,looking_for=looking_for)
               prime_amount = Cart.objects.filter(user=user_id,productId_id = None,looking_for=looking_for).first()
               tip = Cart.objects.filter(user_id = user_id,looking_for=looking_for).first()
               default_address_data = {}
             else:
               viewcart = Cart.objects.filter(user=user_id,plan_id = None,looking_for=looking_for)
               tip = Cart.objects.filter(user_id = user_id,looking_for=looking_for).first()
               prime_amount = Cart.objects.filter(user=user_id,productId_id = None,looking_for=looking_for).first()
               default_address = Address.objects.filter(user_id=user_id, deafult=1).first()
               default_address_data = UserDefaultAddressSerializer(default_address).data
        if not viewcart.exists():
            return Response({'status': False, 'data': {}, 'msg': 'Cart is empty'}, status=status.HTTP_200_OK)

        serializer = ViewCartSerializer(viewcart, many=True)
        cart_items = list(serializer.data)
        overall_max_eta = None
        for proinventory in cart_items:
                  
                  product_id  = proinventory['productId']
                  product_id['product_name'] = product_id['product_name'].title()
                  result = CatalogCategory.objects.filter(id=product_id['category_id']).aggregate(Max('extra_eta'))
                  max_extra_eta = result['extra_eta__max']
                  if max_extra_eta is not None:
                    if overall_max_eta is None or max_extra_eta > overall_max_eta:
                        overall_max_eta = max_extra_eta
                            
                  today_date = date.today()
                  fprice = str(product_id['price'])
                  prod_discount = 0
                  discount_pro = ProductDiscount.objects.filter(product_id=product_id['id']).first()
                  if discount_pro:
                        start_date = discount_pro.startdate
                        end_date = discount_pro.enddate
                        if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = float(product_id['price'])
                            dis_price = (discount * pro_price) / 100
                            fprice = f"{pro_price - dis_price:.2f}" 
                            prod_discount = discount 
                  product_id['price'] = fprice
                  product_id['product_discount'] = prod_discount             


                  store_id = proinventory['store']
                  inventory = StoreInventory.objects.filter(product_id = product_id['id'],store_id = store_id,status=1).first()                
                  proinventory['inventory'] = inventory.inventory if inventory else 0 

                  if not inventory or inventory.inventory == 0:
                        proinventory['message'] = "kindly remove the item."

        
        print("Overall maximum ETA:", overall_max_eta)
                    
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
        distance = round(distance)
       
        if distance <= 2:
            time = 0
        elif distance <= 3:
            time = 5 
        elif distance <= 4:
            time = 10 
        elif distance <= 5:
            time = 15 
        elif distance <= 6:
            time = 20
        elif distance <= 7:
            time = 25 
        elif distance <= 8:
            time = 30         
        else:
            time= 35     
        iteam_count = Cart.objects.filter(user_id = user_id,looking_for=looking_for).count()  
        overall_max_eta = overall_max_eta if overall_max_eta is not None else 0
        time = time if time is not None else 0      
      
        if iteam_count <= 5:
              dtime = f"{30 + time+overall_max_eta} mins"
        elif iteam_count <= 15:
              dtime = f"{35 + time+overall_max_eta} mins"      
        elif iteam_count <= 25:
              dtime = f"{45 + time+overall_max_eta} mins"
        else:
              dtime =f"{50 + time+overall_max_eta} mins"

        subtotalamt = sum([float(item['total_amount']) for item in serializer.data  if item.get('inventory') == 1])

        print(subtotalamt  , serializer.data ,"0000000000000000pppppppppppppppppp")

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

        chk_deliverycharge = DeliveryCharges.objects.filter(distance__gte=distance).first()

        if chk_deliverycharge is not None:
            price = chk_deliverycharge.price
        else:
            price = 10

        # if User.objects.filter(id = user_id, is_prime =1).exists():
        #    user_id = request.user.id
        #    calprice = CalculateDeliveryCharge.deliver_charge(user_id,distance)

        #    price = calprice['price']


        # else:

        #   chk_deliverycharge = DeliveryCharges.objects.filter(distance__gte=distance).first()
        #   if chk_deliverycharge is not None:
        #     price = chk_deliverycharge.price
        #   else:
        #     price = 10

        # delivery free
        # price =0
        
        subtotal= "{:.2f}".format(float(subtotalamt))
        totalamount = (subtotalamt)
        totalamount = "{:.2f}".format(float(totalamount+tip.add_tip+price+plan_amount))
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
            'sub_total': str(subtotal),
            'total_amount': str(totalamount),
            'cart_listing': cart_items,
            'default_address': default_address_data,
            'delivery_time':dtime,
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

        get_store_product = StoreInventory.objects.filter(store_id=store_id,status = 1,product__product_tags=24)
        summer_productlist = []

        for store_pro in get_store_product:
            store_id_instance = StoreInventory.objects.get(product_id=store_pro.product_id, store_id=store_id,status=1)

            product_data = Product.objects.get(id=store_pro.product_id,product_for=looking_for)
            if product_data.price > 0:
                    today_date = date.today()
                    fprice = str(product_data.price)
                    prod_discount = 0
                    discount_pro = ProductDiscount.objects.filter(product_id=store_pro.product_id).first()
                    if discount_pro:
                            start_date = discount_pro.startdate
                            end_date = discount_pro.enddate
                            if start_date <= today_date <= end_date:
                                discount = discount_pro.discount
                                pro_price = product_data.price
                                dis_price =((discount*pro_price)/100)
                                fprice = f"{pro_price - dis_price:.2f}"   
                                prod_discount = discount
        # Check the status conditions
                    if product_data.status == 1 and store_id_instance.status == 1:
                       storestatus = 1
                    elif product_data.status == 0 and store_id_instance.status == 1:
                        storestatus = 0
                    elif product_data.status == 1 and store_id_instance.status == 0:
                        storestatus = 0
                    else:
                        storestatus = 1
                    get_summer = Product.objects.filter(id=store_pro.product_id,product_for=looking_for)
                    is_favourite = Wishlist.objects.filter(Product_id=store_pro.product_id, user_id=request.user.id).exists()
                    in_cart = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).exists()
                    cart_quantity = Cart.objects.filter(productId_id=store_pro.product_id, user_id=request.user.id).first()
                    quantity = cart_quantity.quantity if cart_quantity else 0
                    prorating = ProductRating.objects.filter(product_id=store_pro.product_id).aggregate(Avg('rating'))['rating__avg']


                    summer_serializer = GetProductSerializer(get_summer, many=True)
                    summer_data = summer_serializer.data

                    for item in summer_data:
                        # stoinvent_price = StoreInventory.objects.filter(product_id=item['id'],status = 1).first()
                        # if stoinvent_price.price==0 or stoinvent_price.price==None:
                        #    price = item['price']
                        # else:
                        #     price =  str(stoinvent_price.price)
                        # item['price'] = price
                        item['product_name'] = item['product_name'].title()
                        item['is_favourite'] = is_favourite
                        item['in_cart'] = in_cart
                        item['pro_quantity'] = quantity
                        item['product_tags'] = 0
                        item['inventory'] = store_pro.inventory
                        item['status'] = storestatus
                        item['rating'] = prorating if prorating else 4.5
                        item['price'] = fprice
                        item['product_discount'] = prod_discount

                        if storestatus == 1:

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
           prime_plans['msg'] = "You have already purchased prime plan"
           viewcartlist['prime_plan'] = prime_plans
           return Response({'status': True, 'data': viewcartlist, 'msg': 'View Cart List'})

        if Cart.objects.filter(user_id=user_id, plan_id = prime_member_plans.id,looking_for=looking_for).exists():
           prime_plans = {}
           prime_plans['plan_id'] = prime_member_plans.id
           prime_plans['plan_amount'] = prime_member_plans.plan_amount
           prime_plans['status'] = False
           prime_plans['prime_status'] = False
           prime_plans['msg'] = "This plan has been added into cart"
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
      looking_for = request.data['looking_for']
      if product_id is None:
            return Response({'status': False, 'msg': 'Missing product id', 'data': None}, status=status.HTTP_200_OK)
      
      cart_instance = Cart.objects.filter(productId_id=product_id, user_id=user_id, looking_for=looking_for).first()
      store_id = cart_instance.store_id
      
      deletecart = Cart.objects.filter(productId_id = product_id,user_id = user_id,looking_for=looking_for).delete()
      if Cart.objects.filter(user_id = user_id).exists():
         user_id = user_id
         if Cart.objects.filter(user_id = user_id,productId_id = None,looking_for=looking_for).exists():
            cartcount = Cart.objects.filter(user_id = user_id,productId_id__isnull=False,looking_for=looking_for).count()
            if cartcount == 0 :
              cart = Cart.objects.filter(user_id = user_id).delete()
              ApplyCoupon.objects.filter(user_id = user_id).delete()
      #serializer = DeleteCartSerializer(deletecart, many=True)
      if deletecart:

        dashboard_cache_key = f"dashboard_{looking_for}_{store_id}_{user_id}"
        cache.delete(dashboard_cache_key)
        return Response({'status':True, 'msg':'Deleted successfully', 'data': {}}, status=status.HTTP_200_OK)
      else:

        return Response({'status':False, 'msg':'Already deleted', 'data': {}}, status=status.HTTP_200_OK)

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
    return Response({'status':True, 'msg':'Discount', 'data': coupondiscountlist}, status=status.HTTP_200_OK)

# class OrderPlace(GenericAPIView):
#   permission_classes = [IsAuthenticated]
#   def post(self, request, format=None):
#    user_id = request.user.id
#    store_id = request.data['store']
#    closetime  = CheckSroreTime.Check_Store_time(store_id)
#    assign_manager = AssignFulfillmentManager.objects.filter(store_id=store_id , status = 1).first()
#    assign_managerst = AssignStoreManagers.objects.filter(store_id=store_id, status = 1).first()
#    viewcart = Cart.objects.filter(user=user_id, plan_id=None, looking_for=1, store_id=store_id)
#    out_of_stock_items = []
#    for cart_item in viewcart:
#         inventory = StoreInventory.objects.filter(
#             store_id=store_id,
#             product_id=cart_item.productId_id
#         ).first()

#         if inventory and inventory.inventory == 0:
#             out_of_stock_items.append(cart_item.productId.product_name)  # or cart_item.productId.id

#    if out_of_stock_items:
#         return Response({
#             'status': False,
#             'msg': "Kindly remove out-of-stock item(s) from your cart.",
#             'out_of_stock_items': out_of_stock_items
#         })

    
#    if closetime == 1:
#            return Response({'status':False, 'data':{}, 'msg':'Store Closed'})
#    if assign_managerst is None:
#        return Response({'status':False, 'data':{}, 'msg':"Sorry, we can't process your order right now due to lack of Store Manager staff."})
#    if assign_manager is None:
#        return Response({'status':False, 'data':{}, 'msg':"Sorry, we can't process your order right now due to lack of Fulfilment Manager staff."})
#    get_user_addresslatlong = Address.objects.filter(id= request.data['address_id']).first()

#    storelatlong = Stores.objects.filter(id = request.data['store']).filter().first()
#    coords_1 = (get_user_addresslatlong.latitude, get_user_addresslatlong.longitude)
#    coords_2 = (storelatlong.latitude, storelatlong.longitude)
#    distance = geodesic(coords_1, coords_2).kilometers
# #    rangeget = ServiceRange.objects.first()
# #    rangef = (rangeget.range_in_km).split()
# #    finalrange = rangef[0]
# #    radius_km = int(finalrange)

#    finalrange = storelatlong.range
#    radius_km = int(finalrange) 

#    if distance >= radius_km :
#     return Response({'status':False, 'msg':'Your location is not in the stores service range. Please update your address', 'data': {}}, status=status.HTTP_200_OK)
#    else:
#       authorization_header = request.META.get('HTTP_AUTHORIZATION')
#       if authorization_header:
#           if authorization_header.startswith('Bearer '):
#             bearer_token = authorization_header[7:]
#             if GustUser.objects.filter(access_token = bearer_token):
#                 return Response({'status':False, 'msg':'Please login', 'data': []}, status=status.HTTP_200_OK)
#       store = request.data['store']
#       if AssignFulfillmentManager.objects.filter(store_id=store).exists():
#        if Cart.objects.filter(user_id = request.user.id).exists():
#         if Order.objects.filter(store_id = request.data['store']).exists():
#             last_order_id = Order.objects.filter(store_id = request.data['store']).last()
#             lastorder_id = last_order_id.order_id
#             parts = lastorder_id.split('-')
#             prefix = parts[0]
#             getstore_code = Stores.objects.filter(id = request.data['store']).first()
#             if getstore_code.Shop_code == prefix:
#                     order_idcode = lastorder_id
#                     numeric_part = int(order_idcode.split('-')[1])
#                     numeric_part += 1
#                     order_id = f"{order_idcode.split('-')[0]}-{numeric_part}"
#             else:
#                 order_id = f"{getstore_code.Shop_code}-{100000001}"
#         else:
#                getstore_code = Stores.objects.filter(id = request.data['store']).first()
#                order_id = f"{getstore_code.Shop_code}-{100000001}"

#         product_id = request.data['product_id']
#         item_quantity = request.data['quantity']
#         order_quantity = sum(item_quantity)
#         coupon_code = request.data['coupon_code']
#         coupon_discount = request.data['coupon_discount']
#         coupon_discount_amount = request.data['coupon_discount_amount']
#         sub_total = request.data['sub_total']

#         total_amount = request.data['total_amount']
#         address_id = request.data['address_id']
#         tip = request.data['tip']
#         delivery_instructions = request.data['delivery_instructions']
#         delivery_instruction_name = request.data['delivery_instruction_name']
#         store = request.data['store']
#         orderstatus = OrderStatus.objects.get(title = 'placed')
#         plan_id = request.data['plan_id']
#         payment_mode = request.data['payment_mode']
#         delivery_charges = request.data['delivery_charges']
#         prime_discount = request.data['prime_discount']
#         order_for = request.data['looking_for']
#         iteam_unavailable = request.data['iteam_unavailable']
#         if payment_mode == "3":
#            ordermerchant = 0
#         else:
#           ordermerchant = None
#         # storeboys = AssignStoreBoy.objects.filter(store_id=store, status='free')
#         # if storeboys.exists():
#         #       storeboy = storeboys.first()
#         totalamt = round(float(total_amount))
#         orders = Order(order_id = order_id, coupon_code = coupon_code, coupon_discount = coupon_discount, coupon_discount_amount= coupon_discount_amount,
#                         subtotal = sub_total, total=total_amount, user_address_id_id=address_id,
#                         order_quantity = order_quantity, user_id=request.user.id, store_id = store,
#                         order_status_id= orderstatus.id,
#                         tip= tip,delivery_instructions=delivery_instructions,
#                         plan_id=plan_id,payment_mode=payment_mode,
#                         order_status_merchant = ordermerchant,delivery_charges=delivery_charges,prime_discount=prime_discount,order_for=order_for,iteam_unavailable=iteam_unavailable,delivery_instruction_name=delivery_instruction_name

# )
#         orders.save()

#         orderAddress = OrderAddress( user_id_id = request.user.id,
#                                      order_id_id = orders.id,
#                                      bulding_name =get_user_addresslatlong.bulding_name,
#                                      city= get_user_addresslatlong.city,
#                                      state = get_user_addresslatlong.state,
#                                      house_no= get_user_addresslatlong.house_no, street_address = get_user_addresslatlong.street_address,
#                                      pincode= get_user_addresslatlong.pincode,contact_number =get_user_addresslatlong.contact_number,
#                                      latitude = get_user_addresslatlong.latitude ,longitude = get_user_addresslatlong.longitude,
#                                      deafult= get_user_addresslatlong.deafult
#                                      )
#         orderAddress.save()
#         if payment_mode == "1" or payment_mode == "2":
#           updatecart = Cart.objects.filter(user_id=request.user.id).delete()
#           if ApplyCoupon.objects.filter(user_id=request.user.id).exists():
#             removeapplycoupon = ApplyCoupon.objects.get(user_id=request.user.id)
#             removeapplycoupon.delete()
#             OrderLog.objects.create(
#                     order_id = orders.id,
#                     user_id = request.user.id,
#                     role = 'customer',
#                     status = 'placed',
#                     store_id = store
#                   )
#           else:
#             OrderLog.objects.create(
#                   order_id = orders.id,
#                   user_id = request.user.id,
#                   role = 'customer',
#                   status = 'placed',
#                   store_id = store
#                 )

#               # if storeboy:
#               #   AssignOrderToStoreBoy.objects.create(user_id= storeboy.user_id, order_id= orders.id,status = 'placed')
#               #   storeboy.status = 'busy'
#               #   storeboy.save()


#         if len(product_id) == len(item_quantity):
#                 for product_id, item_quantity in zip(product_id, item_quantity):
#                   # Create OrderItem instance with the calculated price
#                     today_date = date.today()    
#                     discount = 0               
#                     discount_pro = ProductDiscount.objects.filter(product_id=product_id).first()
#                     if discount_pro:
#                         start_date = discount_pro.startdate
#                         end_date = discount_pro.enddate
#                         if start_date <= today_date <= end_date:
#                             discount = discount_pro.discount
                    
#                     product = Product.objects.get(id=product_id)
#                     item_price = product.price
#                     order_item = OrderItem(product_id=product_id,item_quantity=item_quantity,order_id=orders.id,store_id=store,removeItem=0,price=item_price,discount_offer=discount
#                     )
#                     order_item.save()
#                 # get_quantity = StoreInventory.objects.get(product_id=product_id, store_id = store,status = 1).inventory
#                 # #if get_quantity >= item_quantity:
#                 # update_quantity = get_quantity-item_quantity
#                 # update_model = StoreInventory.objects.filter(product_id=product_id, store_id = store,status = 1).update(inventory=update_quantity)
#                 order_idss = {}
#                 order_idss['order_id'] = order_id
#                 # else:
#                 #   return Response({'status':False, 'msg':'Iteam quantity not available', 'data': {}}, status=status.HTTP_200_OK)

#                 assign_manager = AssignFulfillmentManager.objects.filter(store_id=store , status = 1).first()
#                 manager_id = assign_manager.user_id
#                 # fcm_token_instance = FcmToken.objects.filter(user_id=manager_id).latest('id')
#                 # fcm_token = fcm_token_instance.fcm_token

#                 title = 'New order has been assigned to you'
#                 body = f'{order_id} has been assigned to you'
#                 types = 'orders'
#                 order_id = order_id
#                 order_type = 1
#                 request = HttpRequest()
#                 test_notifications = TestNotifications()
#                 response = test_notifications.send_push_notification(title, body,manager_id,types,order_id,order_type)

#                 assign_managerst = AssignStoreManagers.objects.filter(store_id=store, status = 1).first()
#                 manager_id = assign_managerst.user_id
#                 # fcm_token_instance = FcmToken.objects.filter(user_id=manager_id).latest('id')
#                 # fcm_token = fcm_token_instance.fcm_token
#                 title = 'New order has been assigned'
#                 body = f'{order_id} has been assigned'

#                 types = 'orders'
#                 order_id = order_id
#                 order_type =1
#                 request = HttpRequest()
#                 test_notifications = TestNotifications()
#                 response = test_notifications.send_push_notification(title, body,manager_id ,types,order_id,order_type)

#                 return Response({'status':True, 'msg':'Order placed', 'data': order_idss}, status=status.HTTP_200_OK)
#        else:
#         return Response({'status':False, 'msg':'Your cart is empty', 'data': {}}, status=status.HTTP_200_OK)
#       else:
#         return Response({'status':False, 'msg':"Sorry, we can't process your order right now due to lack of Fulfilment Manager staff.", 'data': {}}, status=status.HTTP_200_OK)

class OrderPlace(GenericAPIView):
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
   user_id = request.user.id
   store_id = request.data['store']
   closetime  = CheckSroreTime.Check_Store_time(store_id)
   assign_manager = AssignFulfillmentManager.objects.filter(store_id=store_id , status = 1).first()
   assign_managerst = AssignStoreManagers.objects.filter(store_id=store_id, status = 1).first()

   viewcart = Cart.objects.filter(
            user=user_id, plan_id=None, looking_for=1, store_id=store_id
        )
   out_of_stock_items = []
   for cart_item in viewcart:
            inventory = StoreInventory.objects.filter(
                store_id=store_id, product_id=cart_item.productId_id
            ).first()

            if inventory and inventory.inventory == 0:
                out_of_stock_items.append(
                    cart_item.productId.product_name
                )  # or cart_item.productId.id

   if out_of_stock_items:
            return Response(
                {
                    "status": False,
                    "msg": "Kindly remove out-of-stock item(s) from your cart.",
                    "out_of_stock_items": out_of_stock_items,
                }
            )
   if closetime == 1:
           return Response({'status':False, 'data':{}, 'msg':'Store Closed'})
   if assign_managerst is None:
       return Response({'status':False, 'data':{}, 'msg':"Sorry, we can't process your order right now due to lack of Store Manager staff."})
   if assign_manager is None:
       return Response({'status':False, 'data':{}, 'msg':"Sorry, we can't process your order right now due to lack of Fulfilment Manager staff."})
   get_user_addresslatlong = Address.objects.filter(id= request.data['address_id']).first()

   storelatlong = Stores.objects.filter(id = request.data['store']).filter().first()
   coords_1 = (get_user_addresslatlong.latitude, get_user_addresslatlong.longitude)
   coords_2 = (storelatlong.latitude, storelatlong.longitude)
   distance = geodesic(coords_1, coords_2).kilometers
#    rangeget = ServiceRange.objects.first()
#    rangef = (rangeget.range_in_km).split()
#    finalrange = rangef[0]
#    radius_km = int(finalrange)

   finalrange = storelatlong.range
   radius_km = int(finalrange) 

   if distance >= radius_km :
    return Response({'status':False, 'msg':'Your location is not in the stores service range. Please update your address', 'data': {}}, status=status.HTTP_200_OK)
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
        delivery_instruction_name = request.data['delivery_instruction_name']
        store = request.data['store']
        orderstatus = OrderStatus.objects.get(title='pending payment')
        # orderstatus_placed = OrderStatus.objects.get(title='placed')
        plan_id = request.data['plan_id']
        payment_mode = request.data['payment_mode']
        delivery_charges = request.data['delivery_charges']
        prime_discount = request.data['prime_discount']
        order_for = request.data['looking_for']
        iteam_unavailable = request.data['iteam_unavailable']
        if payment_mode == "3":
           ordermerchant = 0
           
        #    orderstatus = orderstatus_pending
        else:
          ordermerchant = None
        #   orderstatus = orderstatus_placed


        # storeboys = AssignStoreBoy.objects.filter(store_id=store, status='free')
        # if storeboys.exists():
        #       storeboy = storeboys.first()
        totalamt = round(float(total_amount))
        orders = Order(order_id = order_id, coupon_code = coupon_code, coupon_discount = coupon_discount, coupon_discount_amount= coupon_discount_amount,
                        subtotal = sub_total, total=total_amount, user_address_id_id=address_id,
                        order_quantity = order_quantity, user_id=request.user.id, store_id = store,
                        order_status_id= orderstatus.id,
                        tip= tip,delivery_instructions=delivery_instructions,
                        plan_id=plan_id,payment_mode=payment_mode,
                        order_status_merchant = ordermerchant,delivery_charges=delivery_charges,prime_discount=prime_discount,order_for=order_for,iteam_unavailable=iteam_unavailable,delivery_instruction_name=delivery_instruction_name

)
        orders.save()

        orderAddress = OrderAddress( user_id_id = request.user.id,
                                     order_id_id = orders.id,
                                     bulding_name =get_user_addresslatlong.bulding_name,
                                     city= get_user_addresslatlong.city,
                                     state = get_user_addresslatlong.state,
                                     house_no= get_user_addresslatlong.house_no, street_address = get_user_addresslatlong.street_address,
                                     pincode= get_user_addresslatlong.pincode,contact_number =get_user_addresslatlong.contact_number,
                                     latitude = get_user_addresslatlong.latitude ,longitude = get_user_addresslatlong.longitude,
                                     deafult= get_user_addresslatlong.deafult
                                     )
        orderAddress.save()
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
                  # Create OrderItem instance with the calculated price
                    today_date = date.today()    
                    discount = 0               
                    discount_pro = ProductDiscount.objects.filter(product_id=product_id).first()
                    if discount_pro:
                        start_date = discount_pro.startdate
                        end_date = discount_pro.enddate
                        if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                    
                    product = Product.objects.get(id=product_id)
                    item_price = product.price
                    order_item = OrderItem(product_id=product_id,item_quantity=item_quantity,order_id=orders.id,store_id=store,removeItem=0,price=item_price,discount_offer=discount
                    )
                    order_item.save()
                # get_quantity = StoreInventory.objects.get(product_id=product_id, store_id = store,status = 1).inventory
                # #if get_quantity >= item_quantity:
                # update_quantity = get_quantity-item_quantity
                # update_model = StoreInventory.objects.filter(product_id=product_id, store_id = store,status = 1).update(inventory=update_quantity)
                order_idss = {}
                order_idss['order_id'] = order_id
                # else:
                #   return Response({'status':False, 'msg':'Iteam quantity not available', 'data': {}}, status=status.HTTP_200_OK)

                assign_manager = AssignFulfillmentManager.objects.filter(store_id=store , status = 1).first()
                manager_id = assign_manager.user_id
                # fcm_token_instance = FcmToken.objects.filter(user_id=manager_id).latest('id')
                # fcm_token = fcm_token_instance.fcm_token

                title = 'New order has been assigned to you'
                body = f'{order_id} has been assigned to you'
                types = 'orders'
                order_id = order_id
                order_type = 1
                request = HttpRequest()
                test_notifications = TestNotifications()
                response = test_notifications.send_push_notification(title, body,manager_id,types,order_id,order_type)

                assign_managerst = AssignStoreManagers.objects.filter(store_id=store, status = 1).first()
                manager_id = assign_managerst.user_id
                # fcm_token_instance = FcmToken.objects.filter(user_id=manager_id).latest('id')
                # fcm_token = fcm_token_instance.fcm_token
                title = 'New order has been assigned'
                body = f'{order_id} has been assigned'

                types = 'orders'
                order_id = order_id
                order_type =1
                request = HttpRequest()
                test_notifications = TestNotifications()
                response = test_notifications.send_push_notification(title, body,manager_id ,types,order_id,order_type)

                return Response({'status':True, 'msg':'Order placed', 'data': order_idss}, status=status.HTTP_200_OK)
       else:
        return Response({'status':False, 'msg':'Your cart is empty', 'data': {}}, status=status.HTTP_200_OK)
      else:
        return Response({'status':False, 'msg':"Sorry, we can't process your order right now due to lack of Fulfilment Manager staff.", 'data': {}}, status=status.HTTP_200_OK)
  

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
            order_type = 1
            request = HttpRequest()
            test_notifications = TestNotifications()
            response = test_notifications.send_push_notification(title, body, manager_id, types, order_id, order_type)

    # else:
    #      return Response({'status':False, 'msg':'store boy is busy.. please try again after some time.', 'data': {}}, status=status.HTTP_200_OK)
    return Response({'status':True, 'msg':'Order placed', 'data': order_idss}, status=status.HTTP_200_OK)
   else:
    return Response({'status':False, 'msg':'Your cart is empty', 'data': {}}, status=status.HTTP_200_OK)


logger = logging.getLogger(__name__)


 

logger = logging.getLogger(__name__)
class UserDashboard(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardSerializer, OfferSerializer, CategoriesSerializer, ProductBrandSerializer

    def _fetch_user_details(self, user_id):
        userd = User.objects.filter(id=user_id).first()
        return UserdetailsSerializer(userd).data

    def _fetch_last_delivery_order(self, user_id, looking_for):
        # Fetch last delivery order data
        lastdeliveryorder = Order.objects.filter(user_id=user_id, order_status_id=6, skip_rating=0, order_for=looking_for).last()
        deliveryorder = {}
        
        if lastdeliveryorder:
            lastdeliveryorder_id = lastdeliveryorder.id
            showlastdeliveryorder_id = lastdeliveryorder.order_id
            deliveryrating = DeliveryBoyRating.objects.filter(order_id=lastdeliveryorder_id).first()
            delivery_name = User.objects.filter(id=lastdeliveryorder.delivery_boy_id).first() if lastdeliveryorder.delivery_boy_id else ''
            
            userimage = UserFullProfileSerializer(delivery_name).data if delivery_name else {}
            
            deliveryorder['order_id'] = lastdeliveryorder_id
            deliveryorder['show_order_id'] = showlastdeliveryorder_id
            deliveryorder['deliveryboy_id'] = lastdeliveryorder.delivery_boy_id
            deliveryorder['deliveryboy_profile'] = userimage.get('profile_image', '') if userimage else ''
            deliveryorder['deliveryboy_name'] = delivery_name.full_name if isinstance(delivery_name, User) and delivery_name.full_name else ''
        
        return deliveryorder

    def _fetch_banners(self, looking_for):
        # Fetch all banner data in parallel
        homebanner = HomeBanner.objects.filter(status=1, default=0, banner_for=looking_for).order_by('priority')
        offerbanner = OfferBanners.objects.filter(status=1, default=0, banner_for=looking_for).order_by('priority')
        defaultofferbanner = OfferBanners.objects.filter(status=1, default=1, banner_for=looking_for)
        defaulthomebanner = HomeBanner.objects.filter(status=1, default=1, banner_for=looking_for)
        
        return {
            'home_banner': DashboardSerializer(homebanner, many=True).data,
            'offer_banner': OfferSerializer(offerbanner, many=True).data,
            'defaultofferbanner': OfferSerializer(defaultofferbanner, many=True).data,
            'defaulthomebanner': DashboardSerializer(defaulthomebanner, many=True).data
        }

    def _fetch_categories_and_tags(self, store_id, looking_for):
        # Fetch categories and tags
        product_ids_query = StoreInventory.objects.filter(store_id=store_id, status=1).values('product_id')
        cat_ids_query = Product.objects.filter(product_for=looking_for, id__in=product_ids_query).values('category_id')
        categories = CatalogCategory.objects.filter(status=1, cat_for=looking_for, id__in=cat_ids_query)
        tags = Tag.objects.filter(status=1, tag_for=looking_for)
        
        categories_serializer = CategoriesSerializer(categories, many=True).data
        categories_with_products = []
        for category in categories_serializer:
            if Product.objects.filter(category_id=category['id']).exists():
                categories_with_products.append(category)    
        return {
            'categories': categories_with_products,
            'tags': TagSerializer(tags, many=True).data
        }

    
    def _fetch_product_brands(self, store_id):
        product_brand_ids = StoreInventory.objects.filter(
            store_id=store_id,
            status=1,
            product__status=1,
            product__price__gt=0
        ).values_list('product__Brand_id', flat=True).distinct()
        
        product_brands = ProductBrand.objects.filter(
            id__in=product_brand_ids,
            product__status=1,
            status=1,
            product__storeinventory__status=1
        ).annotate(product_count=Count('product')).filter(product_count__gt=0)[:5]

        return ProductBrandSerializer(product_brands, many=True).data

    def _fetch_order_again_products(self, user_id, store_id, looking_for):
        order_queryset = Order.objects.filter(
            user_id=user_id,
            store_id=store_id,
            order_for=looking_for,
            order_status_id=6
        ).order_by('-id')[:5]

        product_set = set()
        product_list = []

        for order in order_queryset:
            order_items = OrderItem.objects.filter(
                order=order
            ).select_related('product__Brand')[:10]

            for order_item in order_items:
                if StoreInventory.objects.filter(
                    product_id=order_item.product_id,
                    store_id=store_id,
                    status=1
                ).exists():
                    self._process_order_product(
                        order_item, store_id, product_set, product_list, looking_for
                    )

        return product_list

        
    def _process_order_product(self, order_item, store_id, product_set, product_list, looking_for):
        product_id = order_item.product_id
        if product_id in product_set:
            return

        try:
            store_id_instance = StoreInventory.objects.get(product_id=product_id, store_id=store_id, status=1)
            product_data = Product.objects.get(id=product_id, product_for=looking_for)
            
            if product_data.price <= 0:
                return
                
            today_date = date.today()
            fprice = str(product_data.price)
            prod_discount = 0
            discount_pro = ProductDiscount.objects.filter(product_id=product_id).first()
            
            if discount_pro:
                start_date = discount_pro.startdate
                end_date = discount_pro.enddate
                if start_date <= today_date <= end_date:
                    discount = discount_pro.discount
                    pro_price = product_data.price
                    dis_price = ((discount*pro_price)/100)
                    fprice = f"{pro_price - dis_price:.2f}"
                    prod_discount = discount

            # Check the status conditions
            if product_data.status == 1 and store_id_instance.status == 1:
                storestatus = 1
            elif product_data.status == 0 and store_id_instance.status == 1:
                storestatus = 0
            elif product_data.status == 1 and store_id_instance.status == 0:
                storestatus = 0
            else:
                storestatus = 1
                
            product_set.add(product_id)
            is_favourite = Wishlist.objects.filter(Product_id=product_id, user_id=self.request.user.id).exists()
            in_cart = Cart.objects.filter(productId_id=product_id, user_id=self.request.user.id).exists()
            cart_quantity = Cart.objects.filter(productId_id=product_id, user_id=self.request.user.id).first()
            pro_inventory = StoreInventory.objects.filter(product_id=product_id, status=1, store_id=store_id).first()
            prorating = ProductRating.objects.filter(product_id=product_id).aggregate(Avg('rating'))['rating__avg']
            
            product_data = GetProductSerializer(product_data).data
            product_data['product_name'] = product_data['product_name'].title()
            product_data['is_favourite'] = is_favourite
            product_data['in_cart'] = in_cart
            product_data['pro_quantity'] = cart_quantity.quantity if cart_quantity else 0
            product_data['product_tags'] = 0
            product_data['inventory'] = pro_inventory.inventory if pro_inventory else 0
            product_data['rating'] = prorating if prorating else 4.5
            product_data['status'] = storestatus
            product_data['price'] = fprice
            product_data['product_discount'] = prod_discount
            
            product_list.append(product_data)
        except (StoreInventory.DoesNotExist, Product.DoesNotExist):
            pass

    def _fetch_product_section(self, store_id, product_tag, looking_for, limit=20):
        get_store_product = StoreInventory.objects.filter(store_id=store_id, status=1, product__product_tags=product_tag)[:limit]
        product_list = []
        
        for store_pro in get_store_product:
            try:
                store_id_instance = StoreInventory.objects.get(product_id=store_pro.product_id, store_id=store_id, status=1)
                product_data = Product.objects.get(id=store_pro.product_id, product_for=looking_for)
                
                if product_data.price <= 0:
                    continue
                    
                today_date = date.today()
                fprice = str(product_data.price)
                prod_discount = 0
                discount_pro = ProductDiscount.objects.filter(product_id=store_pro.product_id).first()
                
                if discount_pro:
                    start_date = discount_pro.startdate
                    end_date = discount_pro.enddate
                    if start_date <= today_date <= end_date:
                        discount = discount_pro.discount
                        pro_price = product_data.price
                        dis_price = ((discount*pro_price)/100)
                        fprice = f"{pro_price - dis_price:.2f}"
                        prod_discount = discount
                
                # Check the status conditions
                if product_data.status == 1 and store_id_instance.status == 1:
                    storestatus = 1
                elif product_data.status == 0 and store_id_instance.status == 1:
                    storestatus = 0
                elif product_data.status == 1 and store_id_instance.status == 0:
                    storestatus = 0
                else:
                    storestatus = 1
                    
                get_product = Product.objects.filter(id=store_pro.product_id, product_for=looking_for)
                is_favourite = Wishlist.objects.filter(Product_id=store_pro.product_id, user_id=self.request.user.id).exists()
                in_cart = Cart.objects.filter(productId_id=store_pro.product_id, user_id=self.request.user.id).exists()
                cart_quantity = Cart.objects.filter(productId_id=store_pro.product_id, user_id=self.request.user.id).first()
                prorating = ProductRating.objects.filter(product_id=store_pro.product_id).aggregate(Avg('rating'))['rating__avg']
                
                product_serializer = GetProductSerializer(get_product, many=True)
                product_data = product_serializer.data
                
                for item in product_data:
                    item['product_name'] = item['product_name'].title()
                    item['is_favourite'] = is_favourite
                    item['in_cart'] = in_cart
                    item['pro_quantity'] = cart_quantity.quantity if cart_quantity else 0
                    item['product_tags'] = 0
                    item['inventory'] = store_pro.inventory
                    item['status'] = storestatus
                    item['rating'] = prorating if prorating else 4.5
                    item['price'] = fprice
                    item['product_discount'] = prod_discount
                    product_list.append(item)
            except (StoreInventory.DoesNotExist, Product.DoesNotExist):
                pass
                
        return product_list

    def _fetch_user_address_and_cart_info(self, user_id, store_id, looking_for):
        if Address.objects.filter(user_id=user_id, deafult=1).exists():
            useraddress = Address.objects.filter(user_id=user_id, deafult=1).first()
            userlat = useraddress.latitude
            userlong = useraddress.longitude
            useraddress = UserAddressSerializer(useraddress).data
        else:
            useraddress = {}
            userlat = 0
            userlong = 0
            
        # Calculate delivery time
        viewcart = Cart.objects.filter(user=user_id, looking_for=looking_for)
        serializer = ViewCartSerializer(viewcart, many=True)
        cart_items = list(serializer.data)
        overall_max_eta = None
        
        for proinventory in cart_items:
            product_id = proinventory['productId']
            product_id['product_name'] = product_id['product_name'].title()
            result = CatalogCategory.objects.filter(id=product_id['category_id']).aggregate(Max('extra_eta'))
            max_extra_eta = result['extra_eta__max']
            if max_extra_eta is not None:
                if overall_max_eta is None or max_extra_eta > overall_max_eta:
                    pass
                            
        store_detials = Stores.objects.filter(id=store_id).first()
        storelat = store_detials.latitude
        storelong = store_detials.longitude
        coords_1 = (storelat, storelong)
        coords_2 = (userlat, userlong)
        distance = geodesic(coords_1, coords_2).kilometers
        distance = round(distance)
       
        if distance <= 2:
            time = 0
        elif distance <= 3:
            time = 5 
        elif distance <= 4:
            time = 10 
        elif distance <= 5:
            time = 15 
        elif distance <= 6:
            time = 20
        elif distance <= 7:
            time = 25 
        elif distance <= 8:
            time = 30         
        else:
            time= 35
            
        iteam_count = Cart.objects.filter(user_id=user_id, looking_for=looking_for).count()        
        overall_max_eta = overall_max_eta if overall_max_eta is not None else 0
        time = time if time is not None else 0
        
        if iteam_count <= 5:
            dtime = f"{30 + time + overall_max_eta} mins"
        elif iteam_count <= 15:
            dtime = f"{35 + time + overall_max_eta} mins"      
        elif iteam_count <= 25:
            dtime = f"{45 + time + overall_max_eta} mins"
        else:
            dtime = f"{50 + time + overall_max_eta} mins"
            
        return {
            'user_address': useraddress,
            'delivery_time': dtime
        }

    def _fetch_track_order(self, user_id, looking_for):
        track_order = Order.objects.filter(
            Q(user_id=user_id) & 
            Q(is_delete=0) & 
            Q(payment_mode__in=[1, 2, 3]) & 
            Q(order_status_id__in=[1,2,3,4,5]) & 
            Q(order_for=looking_for) & 
            (Q(order_status_merchant__isnull=True) | Q(order_status_merchant=9))
        ).first()
        
        if track_order:
            return {
                'id': track_order.id,
                'order_id': track_order.order_id,
                'order_status': track_order.order_status_id,
                'store_name': track_order.store.name,
            }
        return {}

    def post(self, request, format=None):
        store_id = request.data.get('store')
        looking_for = request.data.get('looking_for')
        closetime = CheckSroreTime.Check_Store_time(int(store_id)) 
        user_id = request.user.id
        
        # Implement shorter cache key to reduce memory overhead
        dashboard_cache_key = f"dashboard_{looking_for}_{store_id}_{user_id}"
        dashboard_response = cache.get(dashboard_cache_key)
        if dashboard_response:
            logger.info(f"Cache hit: {dashboard_cache_key}")     
            return Response({'status': True, 'msg': 'Dashboard', 'data': dashboard_response}, status=status.HTTP_200_OK)
               
        # Pre-fetch store data to avoid repeated lookups
        store_obj = Stores.objects.select_related().get(id=store_id)
        store_name = store_obj.name
        
        # Further optimize by grouping related queries
        # Create master futures dict to track all parallel operations
        futures = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            # Submit high-priority data fetching tasks first
            futures['user_details'] = executor.submit(self._fetch_user_details, user_id)
            futures['address_cart'] = executor.submit(self._fetch_user_address_and_cart_info, user_id, store_id, looking_for)
            futures['track_order'] = executor.submit(self._fetch_track_order, user_id, looking_for)
            futures['categories_tags'] = executor.submit(self._fetch_categories_and_tags, store_id, looking_for)
            
            # Submit medium-priority tasks
            futures['banners'] = executor.submit(self._fetch_banners, looking_for)
            futures['product_brands'] = executor.submit(self._fetch_product_brands, store_id)
            futures['last_delivery'] = executor.submit(self._fetch_last_delivery_order, user_id, looking_for)
            
            # Submit remaining tasks in order of display importance
            futures['order_again'] = executor.submit(self._fetch_order_again_products, user_id, store_id, looking_for)
            futures['summer_fruits'] = executor.submit(self._fetch_product_section, store_id, 24, looking_for)
            futures['new_arrivals'] = executor.submit(self._fetch_product_section, store_id, 6, looking_for)
            futures['premium_products'] = executor.submit(self._fetch_product_section, store_id, 4, looking_for)
            
            # Process results as they complete to maximize CPU utilization
            completed_futures = []
            for future in concurrent.futures.as_completed(futures.values()):
                completed_futures.append(future)
            
            # Get all results after all futures are complete
            user_details = futures['user_details'].result()
            address_cart = futures['address_cart'].result()
            track_order = futures['track_order'].result()
            categories_tags = futures['categories_tags'].result()
            banners = futures['banners'].result()
            product_brands = futures['product_brands'].result()
            delivered_order = futures['last_delivery'].result()
            order_again = futures['order_again'].result()
            summer_fruits = futures['summer_fruits'].result()
            new_arrivals = futures['new_arrivals'].result() 
            premium_products = futures['premium_products'].result()
            
        # Combine all data - do this outside the executor to free up threads
        dashboard = {
            'store_id': store_id,
            'store_name': store_name,
            'home_banner': banners['home_banner'],
            'offer_banner': banners['offer_banner'],
            'defaultofferbanner': banners['defaultofferbanner'],
            'defaulthomebanner': banners['defaulthomebanner'],
            'categories': categories_tags['categories'],
            'tags': categories_tags['tags'],
            'product_brand': product_brands,
            'order_again': order_again,
            'summer_fruits': summer_fruits,
            'new_arrivals': new_arrivals,
            'premium_products': premium_products,
            'user_address': address_cart['user_address'],
            'delivery_time': address_cart['delivery_time'],
            'delivered_order': delivered_order,
            'user_details': user_details,
            'track_order': track_order,
            'store_close': closetime
        }
        
        # Cache with compression for large responses
        cache.set(dashboard_cache_key, dashboard, timeout=300)
        logger.debug(f"Dashboard cached for key: {dashboard_cache_key}")
        
        return Response({'status': True, 'msg': 'Dashboard', 'data': dashboard}, status=status.HTTP_200_OK)



class CategoryListAPIView(GenericAPIView):
    def post(self, request, format=None):
     looking_for = request.data.get('looking_for')
     categories = CatalogCategory.objects.filter(cat_for=looking_for)
     serializer = CategoryListSerializer(categories, many=True)
     categories_with_products = []
     for category in serializer.data:
            # Check if there are products related to this category
            if Product.objects.filter(category_id=category['id'],product_for=looking_for).exists():
                categories_with_products.append(category)
     return Response(
       {'status':True, 'msg':'Category Details', 'data':categories_with_products}, status=status.HTTP_200_OK)

class CategoryDetailAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        products = CatalogCategory.objects.filter(id=pk)
        serializer = CetegoryDetailSerializer(products, many=True)
        return Response(
       {'status':True, 'msg':'Category details', 'data':serializer.data}, status=status.HTTP_200_OK)

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
  def post(self, request, format=None):
    looking_for = request.data.get('looking_for')
    if Order.objects.filter(user_id = request.user.id,order_for=looking_for).exists():

     order_id = Order.objects.filter(user_id = request.user.id, is_delete = 0,order_for=looking_for).order_by('-created_at').first()
     getorder_details = Order.objects.get(order_id = order_id.order_id, user_id = request.user.id,order_for=looking_for)
     orderdetail_serializer = OrderSerializer(getorder_details)
     get_product_id = OrderItem.objects.filter(order_id = order_id.id)
     getstore_details = Stores.objects.get(id = order_id.store_id)
     strore_address = StroreSerializer(getstore_details)
     productlist = []
     for productid in get_product_id:
            product = Product.objects.get(id = productid.product_id,product_for=looking_for)
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
     return Response({'status':True,'msg':'Recent order', 'data' : prolist}, status=status.HTTP_200_OK)
    else:
       return Response({'status':False,'msg':'Data not found', 'data' : {}}, status=status.HTTP_200_OK)

class UserOrderList(GenericAPIView):
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
     looking_for = request.data.get('looking_for')
     cart_value = Cart.objects.filter(user_id = request.user.id,looking_for=looking_for).exists()
     orders = Order.objects.filter(Q(user_id=request.user.id) & Q(is_delete=0) & Q(order_for=looking_for) & Q(payment_mode__in=[1, 2, 3]) & (Q(order_status_merchant__isnull=True) | Q(order_status_merchant=9))).order_by('-created_at')
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
                  
                  
                  item_price = order_item.price
                  product = Product.objects.get(id=order_item.product_id,product_for=looking_for)
                  serializer = GetProductSerializer(product)
                  prorating = ProductRating.objects.filter(product_id=order_item.product_id).aggregate(Avg('rating'))['rating__avg']
                  product_data = serializer.data

                  today_date = date.today()
                  fprice = str(order_item.price)
                  prod_discount = 0
                  discount_pro = ProductDiscount.objects.filter(product_id=order_item.product_id).first()
                  if discount_pro:
                        start_date = discount_pro.startdate
                        end_date = discount_pro.enddate
                        if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = order_item.price
                            dis_price =((discount*pro_price)/100)
                            fprice = f"{pro_price - dis_price:.2f}"   
                            prod_discount = discount 

                  product_data['item_quantity'] = order_item.item_quantity
                  product_data['rating'] = prorating if prorating else 4.5
                  product_data['product_tags'] = 0
                  product_data['price'] = fprice
                  product_data['product_discount'] = prod_discount
                  product_data['product_name'] = product_data['product_name'].title()
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
      storeId = request.data.get('store_id')
      looking_for = request.data.get('looking_for')
      user = request.user.id
      if Wishlist.objects.filter(Product_id=product_id, user_id=user, store_id=storeId,looking_for=looking_for).exists():
        return Response({'status':False, 'msg':'This product is already added', 'data': {}}, status=status.HTTP_200_OK)
      else:
        #serializer = AddToWishSerializer(data= request.data, context={'request': request})
        product_id = request.data['product_id']
        user = request.user.id
        addtowish = Wishlist(Product_id = product_id, user_id = user, store_id=storeId,looking_for=looking_for)
        addtowish.save()

        dashboard_cache_key = f"dashboard_{looking_for}_{storeId}_{user}"
        cache.delete(dashboard_cache_key)
        return Response({'status':True, 'msg':'Added successfully', 'data': {}}, status=status.HTTP_200_OK)


class SearchProduct(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchProductSerializer
    filter_backends = [SearchFilter]

    def post(self, request, format= None):
        search_fields = request.data.get('product_name')
        store_id = request.data.get('store_id')
        looking_for = request.data.get('looking_for')
        user_id = request.user.id
        searchproduct = SerachProduct(product_name=search_fields, user_id=user_id)
        searchproduct.save()
        # queryset = Product.objects.filter(product_name__icontains=search_fields)
        queryset_ids = Product.objects.filter(product_name__icontains=search_fields, price__gt=0.00,product_for=looking_for).values_list('id', flat=True)
        priduct_ids = StoreInventory.objects.filter(product_id__in=queryset_ids,store_id = store_id,status = 1).values_list('product_id', flat=True)
        queryset = Product.objects.filter(id__in=priduct_ids,product_for=looking_for)
        id_list = list(queryset_ids)
        items_per_page = 20  # You can adjust this value as needed
        page_number = request.data.get('page', 1)
        paginator = Paginator(queryset, items_per_page)
        try:
            page = paginator.page(page_number)
        except EmptyPage:
            # If the requested page is out of range, return an empty list
            return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})

        page = paginator.get_page(page_number)
        search_productlist =[]
        product_ids = []
        for new_pro in page:
            today_date = date.today()
            fprice = str(new_pro.price)
            prod_discount = 0
            discount_pro = ProductDiscount.objects.filter(product_id=new_pro.id).first()
            if discount_pro:
                    start_date = discount_pro.startdate
                    end_date = discount_pro.enddate
                    if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = new_pro.price
                            dis_price =((discount*pro_price)/100)
                            fprice = f"{pro_price - dis_price:.2f}"   
                            prod_discount = discount
            if StoreInventory.objects.filter(product_id = new_pro.id,store_id = store_id,status = 1).exists():
              product_ids.append(new_pro.id)
              is_favourite = Wishlist.objects.filter(Product_id=new_pro.id, user_id=self.request.user.id).exists()
              in_cart = Cart.objects.filter(productId_id=new_pro.id, user_id=self.request.user.id).exists()
              cart_quantity = Cart.objects.filter(productId_id=new_pro.id, user_id=self.request.user.id).first()
              pro_inventry = StoreInventory.objects.filter(product_id = new_pro.id,status = 1, store_id = store_id).first()
              prorating = ProductRating.objects.filter(product_id=new_pro.id).aggregate(Avg('rating'))['rating__avg']


              if cart_quantity:
                  quantity = cart_quantity.quantity
              else:
                  quantity = 0
              if pro_inventry is not None and new_pro is not None:
                    if new_pro.status == 1 and pro_inventry.status == 1:
                        storestatus = 1
                    elif new_pro.status == 0 and pro_inventry.status == 1:
                        storestatus = 0
                    elif new_pro.status == 1 and pro_inventry.status == 0:
                        storestatus = 0
                    else:
                        storestatus = 1


                    search_serializer = GetProductSerializer(new_pro)
                    search_data = search_serializer.data
                    search_data['product_name'] = search_data['product_name'].title()
                    search_data['is_favourite'] = is_favourite
                    search_data['in_cart'] = in_cart
                    search_data['pro_quantity'] = quantity
                    search_data['product_tags'] = 0
                    search_data['inventory'] = pro_inventry.inventory if pro_inventry else 0
                    search_data['rating'] = prorating if prorating else 4.5
                    search_data['price'] = fprice
                    search_data['product_discount'] = prod_discount

                    if storestatus == 1:

                       search_productlist.append(search_data)

        count = StoreInventory.objects.filter(product_id__in=id_list,store_id = store_id,status = 1).count()

        return Response({'status': True, 'total_product':count, 'data': search_productlist[:items_per_page], 'msg': 'Product list'})


class UserWishList(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user.id
        storeId= request.data.get('store_id')
        looking_for= request.data.get('looking_for')
        if Wishlist.objects.filter(user_id=user, store_id=storeId,looking_for=looking_for).exists():
            product_ids = Wishlist.objects.filter(user_id=user, store_id=storeId,looking_for=looking_for).values_list('Product_id', flat=True)
            productlist = []

            for product_id in product_ids:
                product = Product.objects.filter(id=product_id, status=1,product_for=looking_for).first()

                if product:
                    today_date = date.today()
                    fprice = str(product.price)
                    prod_discount = 0
                    discount_pro = ProductDiscount.objects.filter(product_id=product.id).first()
                    if discount_pro:
                        start_date = discount_pro.startdate
                        end_date = discount_pro.enddate
                        if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = product.price
                            dis_price =((discount*pro_price)/100)
                            fprice = f"{pro_price - dis_price:.2f}"   
                            prod_discount = discount     

                    serializer = GetProductSerializer(product)
                    is_favourite = Wishlist.objects.filter(Product_id=product_id, store_id=storeId, user_id=request.user.id,looking_for=looking_for).exists()
                    in_cart = Cart.objects.filter(productId_id=product_id, user_id=request.user.id,looking_for=looking_for).exists()
                    cart_quantity = Cart.objects.filter(productId_id=product_id, user_id=request.user.id,looking_for=looking_for).first()
                    pro_inventory = StoreInventory.objects.filter(product_id=product_id, store_id=storeId, status=1).first()
                    prorating = ProductRating.objects.filter(product_id=product_id).aggregate(Avg('rating'))['rating__avg']

                    if cart_quantity:
                        quantity = cart_quantity.quantity
                    else:
                        quantity = 0

                    storestatus = 0
                    if pro_inventory is not None and product is not None:
                        if product.status == 1 and pro_inventory.status == 1:
                            storestatus = 1
                        elif product.status == 0 and pro_inventory.status == 1:
                            storestatus = 0
                        elif product.status == 1 and pro_inventory.status == 0:
                            storestatus = 0
                        elif product.status == 0 and pro_inventory.status == 0:
                            storestatus = 0
                        else:
                            storestatus = 0

                    product_data = serializer.data
                    product_data['product_name'] = product_data['product_name'].title()
                    product_data['is_favourite'] = is_favourite
                    product_data['in_cart'] = in_cart
                    product_data['pro_quantity'] = quantity
                    product_data['product_tags'] = 0
                    product_data['inventory'] = pro_inventory.inventory if pro_inventory else 0
                    product_data['rating'] = prorating if prorating else 4.5
                    product_data['price'] = fprice
                    product_data['product_discount'] = prod_discount


                    if storestatus == 1 and product.price != 0.00:
                        productlist.append(product_data)

            response_data = {'status': True, 'msg': 'Wish list product', 'data': {'wish_product_list': productlist}}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'msg': 'Wish list is empty', 'data': {}}, status=status.HTTP_200_OK)


class DeleteWishList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      productId = request.data.get('product_id')
      storeId = request.data.get('store_id')
      looking_for = request.data.get('looking_for')
      user = request.user.id
      if Wishlist.objects.filter(Product_id=productId, user_id=user,looking_for=looking_for).exists():
        deletewishlist = Wishlist.objects.filter(Product_id=productId, user_id=user, store_id=storeId,looking_for=looking_for).delete()

        dashboard_cache_key = f"dashboard_{looking_for}_{storeId}_{user}"
        cache.delete(dashboard_cache_key)
        
        return Response({'status':True, 'msg':'Deleted successfully', 'data': {}}, status=status.HTTP_200_OK)
      else:
        return Response({'status':False, 'msg':'This product not in your wishlist', 'data': {}}, status=status.HTTP_200_OK)

class RemoveAllwishList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      user = request.user.id
      looking_for = request.data.get('looking_for')
      if Wishlist.objects.filter(user_id=user,looking_for=looking_for).exists():
        removeall = Wishlist.objects.filter(user_id=user,looking_for=looking_for).delete()
        return Response({'status':True, 'msg':'Deleted successfully', 'data': {}}, status=status.HTTP_200_OK)
      else:
        return Response({'status':False, 'msg':'Wishlist is already empty', 'data': {}}, status=status.HTTP_200_OK)


class OrderDetails(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      order_id  = request.data.get('order_id')
      looking_for  = request.data.get('looking_for')
      user = request.user.id
      if Order.objects.filter(order_id = order_id, user_id = user,order_for=looking_for).exists():
         getorder_details = Order.objects.get(order_id = order_id, user_id = user,order_for=looking_for)
         orderdetail_serializer = OrderSerializer(getorder_details)
         prime_amount = PrimeMemberPlan.objects.filter(id = getorder_details.plan_id).first()
         if prime_amount:
            amountprime = prime_amount.plan_amount
         else:
            amountprime = 0
         if OrderRating.objects.filter(user_id_id = request.user.id,order_id=getorder_details.id,rating_for=looking_for).exists():
              order_rating = OrderRating.objects.filter(user_id_id = request.user.id,order_id=getorder_details.id,rating_for=looking_for)
              orderrating = OrderRatingSerializer(order_rating, many= True).data[0]
         else:
               orderrating = {}
         deliver_ratings = DeliveryBoyRating.objects.filter(deliveryboy_id = getorder_details.delivery_boy_id,rating_for=looking_for).aggregate(Avg('rating'))[
                                'rating__avg']
         deliveryboyrating  = DeliveryBoyRating.objects.filter(user_id_id = request.user.id, order_id = getorder_details.id,rating_for=looking_for).exists()
         if deliveryboyrating:
            deliveryboyratingdetails  = DeliveryBoyRating.objects.filter(user_id_id = request.user.id, order_id = getorder_details.id,rating_for=looking_for)
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

         if OrderAddress.objects.filter(order_id_id = getorder_details.id).exists():
                get_delivery_address = OrderAddress.objects.get(order_id_id = getorder_details.id)
                del_lat = get_delivery_address.latitude
                del_long = get_delivery_address.longitude
                delivery_address = UserorderAddressSerializer(get_delivery_address).data

         else:
                get_delivery_address = Address.objects.get(id = getorder_details.user_address_id_id)
                del_lat = get_delivery_address.latitude
                del_long = get_delivery_address.longitude

                delivery_address = UserDefaultAddressSerializer(get_delivery_address).data

        #  storedetails = StroreSerializer(get_store_details)
         order_items  = OrderItem.objects.filter(order_id = getorder_details.id)
         durations =''
         if order_items.exists():
          coords_1 = (storelat, storelong)
          coords_2 = (del_lat, del_long)
          distance = geodesic(coords_1, coords_2).kilometers
          time = 15
          km_time = distance/time
          totaltime = int(km_time*60)
          iteam_count = OrderItem.objects.filter(order_id = getorder_details.id).count()
        #   if iteam_count <= 5:
        #      durations = str(30)+ ' mins'
        #   elif iteam_count <= 15:
        #      durations = str(35)+ ' mins'
        #   elif iteam_count <= 25:
        #      durations = str(45)+ ' mins'
        #   else:
        #      durations =str(50)+ ' mins'

          if iteam_count <= 5:
             durations = 30
          elif iteam_count <= 15:
             durations = 35
          elif iteam_count <= 25:
             durations = 45
          else:
             durations =50

          order_item_list = []
          for order_item  in order_items:
            item_price = order_item.price
            product = Product.objects.get(id = order_item.product_id)
            product_serializer  = GetProductSerializer(product)
            prorating = ProductRating.objects.filter(product_id=order_item.product_id).aggregate(Avg('rating'))['rating__avg']
            product_data = product_serializer.data

            today_date = date.today()
            fprice = str(product.price)
            prod_discount = 0
            discount_pro = ProductDiscount.objects.filter(product_id=product.id).first()
            if discount_pro:
                start_date = discount_pro.startdate
                end_date = discount_pro.enddate
                if start_date <= today_date <= end_date:
                    discount = discount_pro.discount
                    pro_price = product.price
                    dis_price =((discount*pro_price)/100)
                    fprice = f"{pro_price - dis_price:.2f}"   
                    prod_discount = discount 

            product_data['item_quantity'] = order_item.item_quantity
            product_data['rating'] = prorating if prorating else 4.5
            product_data['product_tags'] = 0
            # product_data['price'] = str(item_price)
            product_data['price'] = fprice
            product_data['product_discount'] = prod_discount
            product_data['product_name'] = product_data['product_name'].title()
            order_item_list.append(product_data)
         else:
             order_item_list = []
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


         order_accept_time = OrderLog.objects.filter(order_id =getorder_details.id,status = "Accepted").first()
         order_picktime_time = OrderLog.objects.filter(order_id =getorder_details.id,status = "process order").first()
         order_delivery_time = OrderLog.objects.filter(order_id =getorder_details.id,status = "delivered").first()

         if order_accept_time:
            #  expected_delivery = (order_accept_time.created_at + timedelta(minutes=durations)).strftime('%I:%M %p')
             expected_delivery = order_accept_time.created_at
         else:
                expected_delivery =  getorder_details.created_at
                # expected_delivery =  (getorder_details.created_at + timedelta(minutes=durations)).strftime('%I:%M %p')

         if order_delivery_time:
                deliverytime = order_delivery_time.created_at
         else:
                deliverytime = expected_delivery

         delivery_timestr = orderdetail_serializer.data['created_at']
         created_at_datetime = datetime.strptime(delivery_timestr, '%Y-%m-%dT%H:%M:%S.%fZ')
         delivery_time = created_at_datetime + timedelta(minutes=durations)
         formatted_delivery_time = delivery_time.strftime('%I:%M %p')
         prolist['order_details'] = orderdetail_serializer.data
         prolist['order_details']['primemamber_amount'] = amountprime
         prolist['order_details']['delivery_instructions'] = my_string
         prolist['order_details']['updated_at'] = deliverytime
         prolist['order_rating'] = orderrating
         prolist['order_item'] = order_item_list
         prolist['store_address'] = storedetails.data
         prolist['delivery_address'] = delivery_address
         prolist['delivery_boy_details'] = delivery_boy_details
         prolist['delivery_durations'] = formatted_delivery_time
         prolist['delivery_durationsss'] = durations
         prolist['delivery_boyrating'] = deliveryboyrating
         prolist['delivery_boyrating_details'] = deliveryorderrating
         prolist['deliveryboy_rating'] = deliver_ratings if deliver_ratings else 0.0
         return Response({'status':True, 'msg':'Successfully', 'data': prolist}, status=status.HTTP_200_OK)
      else:
         return Response({'status':False, 'msg':'This order Id does not exists', 'data': {}}, status=status.HTTP_200_OK)


class ProductBrandList(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        store_id = request.data.get('store_id')
        search = request.data.get('search')

        # Query to get a list of unique product brand IDs for the given store
        product_ids = StoreInventory.objects.filter(
            store_id=store_id,
            status=1,
            product__status=1,  # Filter based on the status of the product
            product__price__gt=0,  # Ensure the price is not 0.00
        ).values_list('product_id', flat=True).distinct()

        # Fetch the product brands associated with the filtered product IDs
        if search:
            product_brands = ProductBrand.objects.filter(product__id__in=product_ids, product__isnull=False, name__icontains=search, status=1).distinct()
        else:
            product_brands = ProductBrand.objects.filter(product__id__in=product_ids, product__isnull=False,status=1).distinct()


        # Count the filtered product brands
        product_brand_count = product_brands.count()

        items_per_page = 20  # You can adjust this value as needed
        page_number = request.data.get('page', 1)
        paginator = Paginator(product_brands, items_per_page)

        try:
            page = paginator.page(page_number)
        except EmptyPage:
            # If the requested page is out of range, return an empty list
            return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})

        page = paginator.get_page(page_number)

        # Serialize the product brands
        product_brand_serializer = ProductBrandSerializer(page, many=True)

        if product_brands:
            return Response({'status': True, 'msg': 'Successfully', 'total_product': product_brand_count, 'data': product_brand_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'msg': 'Data not found', 'data': []}, status=status.HTTP_200_OK)
        
class BrandProductList(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        category_id = request.data.get('category_id')
        store_id = request.data.get('store_id')
        page_number = request.data.get('page', 1)
        items_per_page = 20

        serializer = BrandProductlistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        brand_id = serializer.validated_data['brand_id']

        productlistids = StoreInventory.objects.filter(
            store_id=store_id, status=1
        ).values_list('product_id', flat=True).distinct()

        product_filter = {
            'Brand_id': brand_id,
            'id__in': productlistids,
            'status': 1
        }
        if category_id:
            product_filter['category_id'] = category_id

        productlist = Product.objects.filter(**product_filter).exclude(price=0.00)
        paginator = Paginator(productlist, items_per_page)

        try:
            page = paginator.page(page_number)
        except EmptyPage:
            return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})

        # Preload related data in fewer queries
        product_ids = [prod.id for prod in page]
        store_inventories = {
            inv.product_id: inv for inv in StoreInventory.objects.filter(
                product_id__in=product_ids,
                store_id=store_id,
                status=1
            )
        }
        discounts = {
            dis.product_id: dis for dis in ProductDiscount.objects.filter(
                product_id__in=product_ids
            )
        }
        wishlisted = set(Wishlist.objects.filter(
            Product_id__in=product_ids,
            user_id=request.user.id
        ).values_list('Product_id', flat=True))
        carts = {
            c.productId_id: c for c in Cart.objects.filter(
                productId_id__in=product_ids,
                user_id=request.user.id
            )
        }
        ratings = ProductRating.objects.filter(
            product_id__in=product_ids
        ).values('product_id').annotate(avg_rating=Avg('rating'))
        ratings_dict = {r['product_id']: r['avg_rating'] for r in ratings}

        brandproductlist = []
        today_date = date.today()

        for product in page:
            product_id = product.id
            inventory = store_inventories.get(product_id)
            discount_obj = discounts.get(product_id)

            if inventory is None:
                continue

            fprice = str(product.price)
            prod_discount = 0

            if discount_obj:
                if discount_obj.startdate <= today_date <= discount_obj.enddate:
                    discount = discount_obj.discount
                    discounted_price = product.price - ((discount * product.price) / 100)
                    fprice = f"{discounted_price:.2f}"
                    prod_discount = discount

            storestatus = 1 if product.status == 1 and inventory.status == 1 else 0
            is_favourite = product_id in wishlisted
            cart_obj = carts.get(product_id)
            quantity = cart_obj.quantity if cart_obj else 0
            prorating = ratings_dict.get(product_id, 4.5)

            product_data = BrandProductSerializer(product).data
            product_data.update({
                'product_name': product_data['product_name'].title(),
                'is_favourite': is_favourite,
                'in_cart': cart_obj is not None,
                'pro_quantity': quantity,
                'product_tags': 0,
                'inventory': inventory.inventory,
                'rating': prorating,
                'status': storestatus,
                'price': fprice,
                'product_discount': prod_discount
            })

            if storestatus == 1:
                brandproductlist.append(product_data)

        total_product = productlist.count()
        if brandproductlist:
            return Response({
                'status': True,
                'msg': 'Successfully',
                'total_product': total_product,
                'data': brandproductlist[:items_per_page]
            }, status=status.HTTP_200_OK)

        return Response({
            'status': False,
            'msg': 'Data not found',
            'data': []
        }, status=status.HTTP_200_OK)

class OrderAgain(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        store_id = request.data['store_id']
        looking_for = request.data['looking_for']
        if Order.objects.filter(user_id=request.user.id,store_id=store_id,order_for=looking_for).exists():

            order_queryset = Order.objects.filter(user_id=request.user.id ,store_id=store_id,order_for=looking_for).order_by('-id')
            product_set = set()  # Use a set to store unique product IDs
            product_list = []
            closetime  = CheckSroreTime.Check_Store_time(store_id)
            if closetime == 1:
                    return Response({'status':True, 'data':[], 'msg':'Store closed'})

            for order in order_queryset:
                order_items = OrderItem.objects.filter(order=order)
                for order_item in order_items:
                    if StoreInventory.objects.filter(product_id = order_item.product_id,store_id=store_id).exists():

                        store_id_instance = StoreInventory.objects.get(product_id=order_item.product_id, store_id=store_id)

                        product_data = Product.objects.get(id=order_item.product_id)
                        today_date = date.today()
                        fprice = str(product_data.price)
                        prod_discount = 0
                        discount_pro = ProductDiscount.objects.filter(product_id=product_data.id).first()
                        if discount_pro:
                            start_date = discount_pro.startdate
                            end_date = discount_pro.enddate
                            if start_date <= today_date <= end_date:
                                discount = discount_pro.discount
                                pro_price = product_data.price
                                dis_price =((discount*pro_price)/100)
                                fprice = f"{pro_price - dis_price:.2f}"   
                                prod_discount = discount    

                        # Check the status conditions
                        if product_data.status == 1 and store_id_instance.status == 1:
                            storestatus = 1
                        elif product_data.status == 0 and store_id_instance.status == 1:
                            storestatus = 0
                        elif product_data.status == 1 and store_id_instance.status == 0:
                            storestatus = 0
                        elif product_data.status == 0 and store_id_instance.status == 0:
                            storestatus = 0
                        else:
                            storestatus = 1

                        product_id = order_item.product_id  # Get the product_id from order_item

                        # Check if the product_id has already been added to the set
                        if product_id in product_set:
                            continue  # Skip this product if it's a duplicate
                        else:
                            product_set.add(product_id)  # Add the product_id to the set
                            product = Product.objects.filter(id=product_id )
                            serializer = GetProductSerializer(product, many=True)
                            product_data_list = serializer.data

                            for product_data in product_data_list:
                                is_favourite = Wishlist.objects.filter(Product_id=product_id, user_id=request.user.id).exists()
                                in_cart = Cart.objects.filter(productId_id=product_id, user_id=request.user.id).exists()
                                cart_quantity = Cart.objects.filter(productId_id=product_id, user_id=request.user.id).first()
                                inventory_count = StoreInventory.objects.filter(product_id = product_id, status = 1 , store_id=store_id).first()
                                prorating = ProductRating.objects.filter(product_id=product_id).aggregate(Avg('rating'))['rating__avg']

                                if cart_quantity:
                                    quantity = cart_quantity.quantity
                                else:
                                    quantity = 0
                                product_data['product_name'] = product_data['product_name'].title()
                                product_data['is_favourite'] = is_favourite
                                product_data['in_cart'] = in_cart
                                product_data['pro_quantity'] = quantity
                                product_data['product_tags'] = 0
                                product_data['inventory'] = inventory_count.inventory if inventory_count else 0
                                product_data['rating'] = prorating if prorating else 4.5
                                product_data['status'] = storestatus
                                product_data['price'] = fprice
                                product_data['product_discount'] = prod_discount

                                if storestatus == 1:
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

            get_product_ids = Product.objects.filter(
                category_id=category_id,
                product_tags=6,
                id__in=product_ids_query
            ).exclude(price=0)
      else:
             get_product_ids = Product.objects.filter(
                product_tags=6,
                id__in=product_ids_query
            ).exclude(price=0)

      total_product = get_product_ids.count()
      items_per_page = 20  # You can adjust this value as needed
      page_number = request.data.get('page', 1)
      paginator = Paginator(get_product_ids, items_per_page)
      try:
                page = paginator.page(page_number)
      except EmptyPage:
                # If the requested page is out of range, return an empty list
                return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})
      page = paginator.get_page(page_number)

      newarival_productlist = []

      for store_pro in page:

        if not category_id:
          productlist = Product.objects.filter(product_tags = 6, id=store_pro.id)

        else:
          productlist = Product.objects.filter(category_id=category_id,product_tags = 6, id=store_pro.id)

        try:
                store_inventory_instance = StoreInventory.objects.get(product_id=store_pro.id, store_id=store_id, status=1)
                Product_id_instance = Product.objects.get(id=store_pro.id)
                today_date = date.today()
                fprice = str(Product_id_instance.price)
                prod_discount = 0
                discount_pro = ProductDiscount.objects.filter(product_id=Product_id_instance.id).first()
                if discount_pro:
                        start_date = discount_pro.startdate
                        end_date = discount_pro.enddate
                        if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = Product_id_instance.price
                            dis_price =((discount*pro_price)/100)
                            fprice = f"{pro_price - dis_price:.2f}"   
                            prod_discount = discount     


                if Product_id_instance is not None and store_inventory_instance is not None:
                    if Product_id_instance.status == 1 and store_inventory_instance.status == 1:
                        storestatus = 1
                    elif Product_id_instance.status == 0 and store_inventory_instance.status == 1:
                        storestatus = 0
                    elif Product_id_instance.status == 1 and store_inventory_instance.status == 0:
                        storestatus = 0
                    else:
                        storestatus = 1


                    is_favourite = Wishlist.objects.filter(Product_id=store_pro.id, user_id=request.user.id).exists()
                    in_cart = Cart.objects.filter(productId_id=store_pro.id, user_id=request.user.id).exists()
                    cart_quantity = Cart.objects.filter(productId_id=store_pro.id, user_id=request.user.id).first()
                    inventory_count = StoreInventory.objects.filter(product_id=store_pro.id, status=1 , store_id=store_id).first()
                    prorating = ProductRating.objects.filter(product_id=store_pro.id).aggregate(Avg('rating'))['rating__avg']


                    if cart_quantity:
                        quantity = cart_quantity.quantity
                    else:
                        quantity = 0


                    brand_product_serializer = NewArivalProductSerializer(productlist, many=True)
                    brandpro = brand_product_serializer.data


                    for item in brandpro:
                        item['product_name'] = item['product_name'].capitalize()
                        item['is_favourite'] = is_favourite
                        item['in_cart'] = in_cart
                        item['pro_quantity'] = quantity
                        item['product_tags'] = 0
                        item['inventory'] = inventory_count.inventory if inventory_count else 0
                        item['rating'] = prorating if prorating else 4.5
                        item['price'] = fprice
                        item['product_discount'] = prod_discount


                        if storestatus == 1 and store_pro.price != 0.00:
                            newarival_productlist.append(item)
        except StoreInventory.DoesNotExist:
                # Handle the case when StoreInventory does not exist
                pass

      if newarival_productlist:
          return Response({'status':True, 'msg':'Successfully','total_product':total_product, 'data':  newarival_productlist }, status=status.HTTP_200_OK)
      else:
            return Response({'status':False, 'msg':'Data not found', 'data': []}, status=status.HTTP_200_OK)

class TagProductList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      tag_id  = request.data.get('tag_id')
      store_id = request.data.get('store_id')

      product_ids_query = StoreInventory.objects.filter(store_id=store_id,status = 1).values('product_id')
      
      get_product_ids = Product.objects.filter(
            tags=tag_id,
            id__in=product_ids_query
            ).exclude(price=0)

      total_product = get_product_ids.count()
      items_per_page = 20  # You can adjust this value as needed
      page_number = request.data.get('page', 1)
      paginator = Paginator(get_product_ids, items_per_page)
      try:
                page = paginator.page(page_number)
      except EmptyPage:
                # If the requested page is out of range, return an empty list
                return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})
      page = paginator.get_page(page_number)

      tag_productlist = []

      for store_pro in page:
        
        productlist = Product.objects.filter(tags=tag_id, id=store_pro.id)

        try:
                store_inventory_instance = StoreInventory.objects.get(product_id=store_pro.id, store_id=store_id, status=1)
                Product_id_instance = Product.objects.get(id=store_pro.id)
                today_date = date.today()
                fprice = str(Product_id_instance.price)
                prod_discount = 0
                discount_pro = ProductDiscount.objects.filter(product_id=Product_id_instance.id).first()
                if discount_pro:
                        start_date = discount_pro.startdate
                        end_date = discount_pro.enddate
                        if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = Product_id_instance.price
                            dis_price =((discount*pro_price)/100)
                            fprice = f"{pro_price - dis_price:.2f}"   
                            prod_discount = discount 

                if Product_id_instance is not None and store_inventory_instance is not None:
                    if Product_id_instance.status == 1 and store_inventory_instance.status == 1:
                        storestatus = 1
                    elif Product_id_instance.status == 0 and store_inventory_instance.status == 1:
                        storestatus = 0
                    elif Product_id_instance.status == 1 and store_inventory_instance.status == 0:
                        storestatus = 0
                    else:
                        storestatus = 1


                    is_favourite = Wishlist.objects.filter(Product_id=store_pro.id, user_id=request.user.id).exists()
                    in_cart = Cart.objects.filter(productId_id=store_pro.id, user_id=request.user.id).exists()
                    cart_quantity = Cart.objects.filter(productId_id=store_pro.id, user_id=request.user.id).first()
                    inventory_count = StoreInventory.objects.filter(product_id=store_pro.id, status=1 , store_id=store_id).first()
                    prorating = ProductRating.objects.filter(product_id=store_pro.id).aggregate(Avg('rating'))['rating__avg']


                    if cart_quantity:
                        quantity = cart_quantity.quantity
                    else:
                        quantity = 0


                    brand_product_serializer = NewArivalProductSerializer(productlist, many=True)
                    brandpro = brand_product_serializer.data


                    for item in brandpro:
                        item['product_name'] = item['product_name'].title()
                        item['is_favourite'] = is_favourite
                        item['in_cart'] = in_cart
                        item['pro_quantity'] = quantity
                        item['product_tags'] = 0
                        item['inventory'] = inventory_count.inventory if inventory_count else 0
                        item['rating'] = prorating if prorating else 4.5
                        item['price'] = fprice
                        item['product_discount'] = prod_discount


                        if storestatus == 1 and store_pro.price != 0.00:
                            tag_productlist.append(item)
        except StoreInventory.DoesNotExist:
                # Handle the case when StoreInventory does not exist
                pass

      if tag_productlist:
          return Response({'status':True, 'msg':'Successfully','total_product':total_product, 'data':  tag_productlist }, status=status.HTTP_200_OK)
      else:
            return Response({'status':False, 'msg':'Data not found', 'data': []}, status=status.HTTP_200_OK)      
      
class BestSellerProductList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      category_id  = request.data.get('category_id')
      store_id = request.data.get('store_id')

      product_ids_query = StoreInventory.objects.filter(store_id=store_id,status = 1).values('product_id')


      if category_id is not None and category_id != '':

            get_product_ids = Product.objects.filter(
                category_id=category_id,
                product_tags=24,
                id__in=product_ids_query
            ).exclude(price=0)
      else:
             get_product_ids = Product.objects.filter(
                product_tags=24,
                id__in=product_ids_query
            ).exclude(price=0)

      total_product = get_product_ids.count()
      items_per_page = 20  # You can adjust this value as needed
      page_number = request.data.get('page', 1)
      paginator = Paginator(get_product_ids, items_per_page)
      try:
                page = paginator.page(page_number)
      except EmptyPage:
                # If the requested page is out of range, return an empty list
                return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})
      page = paginator.get_page(page_number)

      bestseller_productlist = []

      for store_pro in page:

        if not category_id:
          productlist = Product.objects.filter(product_tags = 24, id=store_pro.id)

        else:
          productlist = Product.objects.filter(category_id=category_id,product_tags = 24, id=store_pro.id)

        try:
                store_inventory_instance = StoreInventory.objects.get(product_id=store_pro.id, store_id=store_id, status=1)
                Product_id_instance = Product.objects.get(id=store_pro.id)
                today_date = date.today()
                fprice = str(Product_id_instance.price)
                prod_discount = 0
                discount_pro = ProductDiscount.objects.filter(product_id=Product_id_instance.id).first()
                if discount_pro:
                        start_date = discount_pro.startdate
                        end_date = discount_pro.enddate
                        if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = Product_id_instance.price
                            dis_price =((discount*pro_price)/100)
                            fprice = f"{pro_price - dis_price:.2f}"   
                            prod_discount = discount

                if Product_id_instance is not None and store_inventory_instance is not None:
                    if Product_id_instance.status == 1 and store_inventory_instance.status == 1:
                        storestatus = 1
                    elif Product_id_instance.status == 0 and store_inventory_instance.status == 1:
                        storestatus = 0
                    elif Product_id_instance.status == 1 and store_inventory_instance.status == 0:
                        storestatus = 0
                    else:
                        storestatus = 1


                    is_favourite = Wishlist.objects.filter(Product_id=store_pro.id, user_id=request.user.id).exists()
                    in_cart = Cart.objects.filter(productId_id=store_pro.id, user_id=request.user.id).exists()
                    cart_quantity = Cart.objects.filter(productId_id=store_pro.id, user_id=request.user.id).first()
                    inventory_count = StoreInventory.objects.filter(product_id=store_pro.id, status=1 , store_id=store_id).first()
                    prorating = ProductRating.objects.filter(product_id=store_pro.id).aggregate(Avg('rating'))['rating__avg']


                    if cart_quantity:
                        quantity = cart_quantity.quantity
                    else:
                        quantity = 0


                    brand_product_serializer = NewArivalProductSerializer(productlist, many=True)
                    brandpro = brand_product_serializer.data


                    for item in brandpro:
                        item['product_name'] = item['product_name'].title()
                        item['is_favourite'] = is_favourite
                        item['in_cart'] = in_cart
                        item['pro_quantity'] = quantity
                        item['product_tags'] = 0
                        item['inventory'] = inventory_count.inventory if inventory_count else 0
                        item['rating'] = prorating if prorating else 4.5
                        item['price'] = fprice
                        item['product_discount'] = prod_discount


                        if storestatus == 1 and store_pro.price != 0.00:
                            bestseller_productlist.append(item)
        except StoreInventory.DoesNotExist:
                # Handle the case when StoreInventory does not exist
                pass

      if bestseller_productlist:
          return Response({'status':True, 'msg':'Successfully','total_product':total_product, 'data':  bestseller_productlist }, status=status.HTTP_200_OK)
      else:
            return Response({'status':False, 'msg':'Data not found', 'data': []}, status=status.HTTP_200_OK)      

class PremiumProductList(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      category_id  = request.data.get('category_id')
      store_id = request.data.get('store_id')
      product_ids_query = StoreInventory.objects.filter(store_id=store_id,status = 1).values('product_id')

      if category_id is not None and category_id != '':
            get_product_ids = Product.objects.filter(
                product_tags=4,
                category_id=category_id,
                status=1,
                id__in=product_ids_query
            ).exclude(price=0)
      else:
            get_product_ids = Product.objects.filter(
                product_tags=4,
                status=1,
                id__in=product_ids_query
            ).exclude(price=0)

      total_product = get_product_ids.count()

      # get_store_product = StoreInventory.objects.filter(store_id=store_id)
      items_per_page = 20  # You can adjust this value as needed
      page_number = request.data.get('page', 1)
      paginator = Paginator(get_product_ids, items_per_page)
      try:
                page = paginator.page(page_number)
      except EmptyPage:
                # If the requested page is out of range, return an empty list
                return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})
      page = paginator.get_page(page_number)

      newarival_productlist = []
      for store_pro in page:
        if not category_id:
          productlist = Product.objects.filter(product_tags = 4, id=store_pro.id)

        else:
          productlist = Product.objects.filter(category_id=category_id,product_tags = 4, id=store_pro.id)


        try:
                store_inventory_instance = StoreInventory.objects.get(product_id=store_pro.id, store_id=store_id, status=1)
                Product_id_instance = Product.objects.get(id=store_pro.id)
                today_date = date.today()
                fprice = str(Product_id_instance.price)
                prod_discount = 0
                discount_pro = ProductDiscount.objects.filter(product_id=Product_id_instance.id).first()
                if discount_pro:
                        start_date = discount_pro.startdate
                        end_date = discount_pro.enddate
                        if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = Product_id_instance.price
                            dis_price =((discount*pro_price)/100)
                            fprice = f"{pro_price - dis_price:.2f}"   
                            prod_discount = discount    


                if Product_id_instance is not None and store_inventory_instance is not None:
                    if Product_id_instance.status == 1 and store_inventory_instance.status == 1:
                        storestatus = 1
                    elif Product_id_instance.status == 0 and store_inventory_instance.status == 1:
                        storestatus = 0
                    elif Product_id_instance.status == 1 and store_inventory_instance.status == 0:
                        storestatus = 0
                    else:
                        storestatus = 1

                    is_favourite = Wishlist.objects.filter(Product_id=store_pro.id, user_id=request.user.id).exists()
                    in_cart = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).exists()
                    cart_quantity = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).first()
                    inventory_count = StoreInventory.objects.filter(product_id = store_pro.id,status = 1 , store_id=store_id).first()
                    prorating = ProductRating.objects.filter(product_id=store_pro.id).aggregate(Avg('rating'))['rating__avg']

                    if cart_quantity:
                        quantity = cart_quantity.quantity
                    else:
                            quantity = 0

                    brand_product_serializer = NewArivalProductSerializer(productlist, many=True)
                    brandpro = brand_product_serializer.data
                    for item in brandpro:
                        item['product_name'] = item['product_name'].title()
                        item['is_favourite'] = is_favourite
                        item['in_cart'] = in_cart
                        item['pro_quantity'] = quantity
                        item['product_tags'] = 0
                        item['inventory'] = inventory_count.inventory if inventory_count else 0
                        item['rating'] = prorating if prorating else 4.5
                        item['status'] = storestatus
                        item['price'] = fprice
                        item['product_discount'] = prod_discount    
                        getcontext().prec = 10  # Adjust the precision as needed


                        tolerance = Decimal('0.0001')  # Adjust the tolerance based on your specific requirements

                        if storestatus == 1 and abs(store_pro.price - Decimal('0.00')) >= tolerance:

                            newarival_productlist.append(item)

        except StoreInventory.DoesNotExist:
                # Handle the case when StoreInventory does not exist
                pass


      if newarival_productlist:
          return Response({'status':True, 'msg':'Successfully','total_product':total_product, 'data': newarival_productlist}, status=status.HTTP_200_OK)
      else:
            return Response({'status':False, 'msg':'Data not found', 'data': []}, status=status.HTTP_200_OK)

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
            ).exclude(price=0).count()
            get_product_ids = Product.objects.filter(
                category_id=category_id,
                product_tags = 5,
                id__in=product_ids_query
            )
      else:
            total_product = Product.objects.filter(
                product_tags = 5,
                id__in=product_ids_query
            ).exclude(price=0).count()
            get_product_ids = Product.objects.filter(
                product_tags = 5,
                id__in=product_ids_query
            )

      get_store_product = StoreInventory.objects.filter(store_id=store_id,status = 1)
      items_per_page = 20  # You can adjust this value as needed
      page_number = request.data.get('page', 1)
      paginator = Paginator(get_product_ids, items_per_page)
      try:
                page = paginator.page(page_number)
      except EmptyPage:
                # If the requested page is out of range, return an empty list
                return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})
      page = paginator.get_page(page_number)

      newarival_productlist = []
      for store_pro in page:
        if not category_id:
          productlist = Product.objects.filter(product_tags = 5, id=store_pro.id)

        else:
          productlist = Product.objects.filter(category_id=category_id,product_tags = 5, id=store_pro.id)
          today_date = date.today()
          fprice = str(store_pro.price)
          prod_discount = 0
          discount_pro = ProductDiscount.objects.filter(product_id=store_pro.id).first()
          if discount_pro:
                        start_date = discount_pro.startdate
                        end_date = discount_pro.enddate
                        if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = store_pro.price
                            dis_price =((discount*pro_price)/100)
                            fprice = f"{pro_price - dis_price:.2f}"   
                            prod_discount = discount 

        is_favourite = Wishlist.objects.filter(Product_id=store_pro.id, user_id=request.user.id).exists()
        in_cart = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).exists()
        cart_quantity = Cart.objects.filter(productId_id = store_pro.id, user_id = request.user.id).first()
        inventory_count = StoreInventory.objects.filter(product_id = store_pro.id,status = 1, store_id=store_id).first()
        prorating = ProductRating.objects.filter(product_id=store_pro.id).aggregate(Avg('rating'))['rating__avg']

        if cart_quantity:
               quantity = cart_quantity.quantity
        else:
                quantity = 0

        brand_product_serializer = NewArivalProductSerializer(productlist, many=True)
        brandpro = brand_product_serializer.data
        for item in brandpro:
            item['product_name'] = item['product_name'].title()
            item['is_favourite'] = is_favourite
            item['in_cart'] = in_cart
            item['pro_quantity'] = quantity
            item['product_tags'] = 0
            item['inventory'] = inventory_count.inventory if inventory_count else 0
            item['rating'] = prorating if prorating else 4.5
            item['price'] = fprice
            item['product_discount'] = prod_discount

            newarival_productlist.append(item)

      if newarival_productlist:
          return Response({'status':True, 'msg':'Successfully', 'data': newarival_productlist}, status=status.HTTP_200_OK)
      else:
            return Response({'status':False, 'msg':'Data not found', 'data': []}, status=status.HTTP_200_OK)

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
         return Response({'status':True, 'msg':'Coupon applied successfully', 'data': {}}, status=status.HTTP_200_OK)

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
   def post(self, request, format=None):
      user_id =  request.user.id
      looking_for = request.data.get('looking_for')

      search_keyp = SerachProduct.objects.filter(user_id=user_id) \
                    .values('product_name') \
                    .annotate(max_id=Max('id')) \
                    .order_by('-max_id') \
                    [:5]
      search_key = SearchKeySerializer(search_keyp, many=True)
      return Response({'status': True, 'msg': 'Recent search', 'data': search_keyp}, status=status.HTTP_200_OK)


class ClearOrderHistory(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      user_id =  request.user.id
      order_id = request.data.get('order_id')
      looking_for = request.data.get('looking_for')
      if order_id is not None and order_id != '':
         delete_order = Order.objects.filter(user_id = user_id,order_id = order_id, order_status_id__in = [6,7,8],order_for=looking_for).update(is_delete=1)
         return Response({'status': True, 'msg': 'This order is deleted successfully', 'data': {}}, status=status.HTTP_200_OK)
      else:
         delete_order = Order.objects.filter(user_id = user_id,order_status_id__in = [6,7,8],order_for=looking_for).update(is_delete=1)
         return Response({'status': True, 'msg': 'All orders deleted successfully', 'data': {}}, status=status.HTTP_200_OK)

class CartQuantity(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def post(self, request, format=None):
      user_id = request.user.id
      looking_for = request.data['looking_for']
      if Cart.objects.filter(user_id = user_id,looking_for=looking_for).exists():
        cartiteam_quantity = Cart.objects.filter(user_id = user_id,plan_id = None,looking_for=looking_for).count()
        product_id = Cart.objects.filter(user_id = user_id,looking_for=looking_for).first()
        get_productimage =  Product.objects.filter(id=product_id.productId_id,product_for=looking_for).first()
        cartimg = CartImageSerializer(get_productimage).data
        subtotal_amount = Cart.objects.filter(user_id=user_id,looking_for=looking_for).aggregate(total=Sum('total_amount'))['total']
        cartdata = {
                'iteam_quantity': cartiteam_quantity,
                'total_amount': str(subtotal_amount),
                'image' : cartimg
            }
        return Response({'status': True, 'msg': 'Successfully', 'data': cartdata}, status=status.HTTP_200_OK)
      else:
         return Response({'status': False, 'msg': 'Your cart is empty', 'data': {}}, status=status.HTTP_200_OK)

class ProductDetail(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        from collections import defaultdict

        product_id = request.data.get('product_id')
        category_id = request.data.get('category_id')
        store_id = request.data.get('store_id')
        looking_for = request.data.get('looking_for')
        today_date = date.today()

        product = Product.objects.filter(id=product_id, price__gt=Decimal('0.00'), product_for=looking_for).select_related('subcategory').first()
        if not product:
            return Response({'status': False, 'data': [], 'msg': 'Product not found or has price 0.00'}, status=status.HTTP_200_OK)

        discount = ProductDiscount.objects.filter(product_id=product_id, startdate__lte=today_date, enddate__gte=today_date).first()
        price = product.price
        discount_percentage = discount.discount if discount else 0
        final_price = price - ((discount_percentage * price) / 100) if discount else price

        wishlist_exists = Wishlist.objects.filter(Product_id=product_id, user_id=request.user.id).exists()
        cart_item = Cart.objects.filter(productId_id=product_id, user_id=request.user.id).first()
        cart_qty = cart_item.quantity if cart_item else 0
        total_amount = float(final_price) * cart_qty if cart_qty else 0

        inventory = StoreInventory.objects.filter(product_id=product_id, store_id=store_id, status=1).first()
        rating = ProductRating.objects.filter(product_id=product_id).aggregate(Avg('rating'))['rating__avg'] or 4.5

        product_data = ProductDetilSerializer(product).data
        product_data.update({
            'product_name': product_data['product_name'].title(),
            'product_tags': 0,
            'is_favourite': wishlist_exists,
            'in_cart': bool(cart_item),
            'pro_quantity': cart_qty,
            'tota_amount': str(round(total_amount, 2)),
            'product_all_images': ProductImagesSerializer(Images.objects.filter(product_id=product_id), many=True).data,
            'inventory': inventory.inventory if inventory else 0,
            'rating': rating,
            'price': f"{final_price:.2f}",
            'product_discount': discount_percentage,
        })

        def fetch_related_products(queryset):
            result = []
            product_ids = [p.id for p in queryset]
            discounts = ProductDiscount.objects.filter(product_id__in=product_ids, startdate__lte=today_date, enddate__gte=today_date)
            discount_map = {d.product_id: d.discount for d in discounts}
            inventories = StoreInventory.objects.filter(product_id__in=product_ids, store_id=store_id, status=1)
            inventory_map = {inv.product_id: inv for inv in inventories}

            for product in queryset:
                if product.id not in inventory_map:
                    continue
                
                price = product.price
                discount = discount_map.get(product.id, 0)
                final_price = price - ((discount * price) / 100) if discount else price
                
                wishlist_exists = Wishlist.objects.filter(Product_id=product.id, user_id=request.user.id).exists()
                cart_item = Cart.objects.filter(productId_id=product.id, user_id=request.user.id).first()
                cart_qty = cart_item.quantity if cart_item else 0
                total_amount = float(final_price) * cart_qty if cart_qty else 0
                rating = ProductRating.objects.filter(product_id=product.id).aggregate(Avg('rating'))['rating__avg'] or 4.5

                item_data = ProductDetilSerializer(product).data
                item_data.update({
                    'product_name': item_data['product_name'].title(),
                    'product_tags': 0,
                    'is_favourite': wishlist_exists,
                    'in_cart': bool(cart_item),
                    'pro_quantity': cart_qty,
                    'tota_amount': str(round(total_amount, 2)),
                    'inventory': inventory_map[product.id].inventory,
                    'rating': rating,
                    'price': f"{final_price:.2f}",
                    'product_discount': discount,
                    'status': 1 if product.status == 1 else 0,
                })
                result.append(item_data)
            return result

        similar_queryset = Product.objects.filter(
            category_id=product.category_id if category_id in [None, '', '0'] else category_id,
            price__gt=Decimal('0.00'), product_for=looking_for
        ).exclude(id=product_id)[:15]

        must_like_queryset = Product.objects.filter(
            subcategory_id=product.subcategory_id, product_for=looking_for
        ).exclude(id=product_id)[:15]

        product_data['you_may_like'] = fetch_related_products(similar_queryset)
        product_data['similar_product'] = fetch_related_products(must_like_queryset)

        return Response({'status': True, 'msg': 'Successfully', 'data': product_data}, status=status.HTTP_200_OK)

class Notifications(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user_id = request.user.id
        looking_for = request.data.get('looking_for')
        if Notification.objects.filter(user_id = user_id).exists():
            notification_list = Notification.objects.filter(user_id = user_id,notification_for=looking_for).order_by('-timestamp')
            listnotification = NotificationListSerializer(notification_list,many =True).data
            return Response({'status':True, 'data': listnotification,'msg': 'Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False, 'data': [],'msg': 'Data not found'}, status=status.HTTP_200_OK)

class ReorderView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user_id = request.user.id
        order_id = request.data.get('order_id')
        store_id = request.data.get('store_id')
        looking_for = request.data.get('looking_for')
        if not order_id:
            return Response({'status':False, 'data': {},'msg': 'Order_id is required.'}, status=status.HTTP_200_OK)
        elif not store_id:
            return Response({'status':False, 'data': {},'msg': 'Store_id is required.'}, status=status.HTTP_200_OK)
        else:
            if Order.objects.filter(order_id = order_id,store_id=store_id,order_for=looking_for).exists():
              removecart = Cart.objects.filter(user_id=user_id).delete()
              getorder_id = Order.objects.filter(order_id = order_id,order_for=looking_for).first()
              order_iteam = OrderItem.objects.filter(order_id = getorder_id.id)

              for item in order_iteam:
                  priceinventory = StoreInventory.objects.filter(product_id = item.product_id, store_id= store_id).first()
                  getpro_detail = Product.objects.filter(id = item.product_id,product_for=looking_for).first()

                  if getpro_detail.status == 1 and priceinventory.status == 1:

                        storestatus = 1
                  else:

                        storestatus = 0
                  if storestatus == 1:

                    priamt = getpro_detail.price
                    quantity = int(item.item_quantity)
                    weight = getpro_detail.product_weight
                    amount = float(priamt)
                    total_amount = int(quantity*amount)
                    productId_id = item.product_id
                    user_id = user_id
                    store_id = item.store_id
                    addincart = Cart(quantity=quantity,weight=weight,amount=amount,total_amount=total_amount,productId_id=productId_id,user_id=user_id,store_id=store_id,looking_for=looking_for)
                    addincart.save()
                  else :
                        return Response({'status':False, 'data': {},'msg': '', 'storestatus': '0'}, status=status.HTTP_200_OK)

              return Response({'status':True, 'data': {},'msg': 'Success.'}, status=status.HTTP_200_OK)
            else:
              return Response({'status':False, 'data': {},'msg': 'Please change store.'}, status=status.HTTP_200_OK)


class AddOrderRatingView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user_id = request.user.id
        message = request.data.get('message')
        order_id = request.data.get('order_id')
        rating = request.data.get('rating')
        looking_for = request.data.get('looking_for')
        if not order_id:
            return Response({'status':False, 'data': {},'msg': 'Order_id is required.'}, status=status.HTTP_200_OK)
        elif not rating:
            return Response({'status':False, 'data': {},'msg': 'Rating is required.'}, status=status.HTTP_200_OK)
        else:
            if OrderRating.objects.filter(user_id_id=user_id,order_id=order_id,rating_for=looking_for).exists():
               return Response({'status':False, 'data': {},'msg': 'Already added.'}, status=status.HTTP_200_OK)
            else:
              getorderiteam = OrderItem.objects.filter(order_id = order_id)
              for orderiteam in getorderiteam:
                 addratingpro = ProductRating(rating = rating,product_id = orderiteam.product_id,rating_for=looking_for)
                 addratingpro.save()

              order_id = order_id
              user_id = user_id
              message = message
              rating = rating
              addincart = OrderRating(order_id=order_id,user_id_id=user_id,messages=message,rating=rating,rating_for=looking_for)
              addincart.save()
              return Response({'status':True, 'data': {},'msg': 'Success.'}, status=status.HTTP_200_OK)


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
        looking_for = request.data.get('looking_for')
        if not order_id:
            return Response({'status':False, 'data': {},'msg': 'Order_id is required.'}, status=status.HTTP_200_OK)
        elif not deliveryboy_id:
            return Response({'status':False, 'data': {},'msg': 'Delivery boy id is required.'}, status=status.HTTP_200_OK)
        else:
            if DeliveryBoyRating.objects.filter(user_id_id=user_id,order_id=order_id,rating_for=looking_for).exists():
               updaterating = Order.objects.filter(id = order_id).update(skip_rating = 1)
               return Response({'status':False, 'data': {},'msg': 'Already added.'}, status=status.HTTP_200_OK)
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
                    addincart = DeliveryBoyRating(order_id=order_id,user_id_id=user_id,messages=message,rating=rating,deliveryboy_id = deliveryboy_id,rating_for=looking_for)
                    addincart.save()

                    getorderiteam = OrderItem.objects.filter(order_id = order_id)
                    for orderiteam in getorderiteam:
                        addratingpro = ProductRating(rating = rating,product_id = orderiteam.product_id,rating_for=looking_for)
                        addratingpro.save()

                    order_id = order_id
                    user_id = user_id
                    order_message = order_message
                    order_rating = order_rating
                    addincart = OrderRating(order_id=order_id,user_id_id=user_id,messages=order_message,rating=order_rating,rating_for=looking_for)
                    addincart.save()
                    updaterating = Order.objects.filter(id = order_id).update(skip_rating = 1)

                    return Response({'status':True, 'data': {},'msg': 'Your rating has been submitted successfully.'}, status=status.HTTP_200_OK)

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
    
class Chkdistance(GenericAPIView):
    def get(self, request, format=None):
        coords_1 = (28.6060285, 77.4296325)
        coords_2 = (28.62730604780265, 77.37335586662124)
        distance = geodesic(coords_1, coords_2).kilometers
        time = 30
        km_time = distance/time
        totaltime = int(km_time*60)+8
        dtime = str(totaltime)+' mins'

        print(distance)
        print(dtime)
        return Response({'status':True, 'data': {},'msg': distance}, status=status.HTTP_200_OK)



class HomeBannerClickableList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
 
    def post(self, request, format=None):      
 
        store_id = int(request.data.get('store_id'))
        product_tags = int(request.data.get('product_tags', 0))
        banner_tags = int(request.data.get('banner_tags', 0))
        looking_for = int(request.data.get('looking_for'))
 
        product_ids_query = StoreInventory.objects.filter(
            store_id=store_id, status=1
        ).values_list('product_id', flat=True)
 
        base_filter = Q(id__in=product_ids_query, status=1, product_for=looking_for)
        if banner_tags:
            base_filter &= Q(product_tags=banner_tags)
        elif product_tags:
            base_filter &= Q(tags__id=product_tags)
 
        all_products = Product.objects.filter(base_filter).distinct()
 
        total_product = all_products.count()
 
        items_per_page = 20
        page_number = int(request.data.get('page', 1))
        paginator = Paginator(all_products, items_per_page)
        try:
            page = paginator.page(page_number)
        except EmptyPage:
            return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})
 
        page_products = list(page.object_list)
 
        product_ids = [p.id for p in page_products]
 
        # Prefetch related objects
        inventories = {
            inv.product_id: inv for inv in StoreInventory.objects.filter(
                product_id__in=product_ids, store_id=store_id, status=1
            )
        }
 
        discounts = {
            dis.product_id: dis for dis in ProductDiscount.objects.filter(
                product_id__in=product_ids, startdate__lte=date.today(), enddate__gte=date.today()
            )
        }
 
        ratings = ProductRating.objects.filter(product_id__in=product_ids).values('product_id').annotate(
            avg_rating=Avg('rating')
        )
        rating_map = {r['product_id']: r['avg_rating'] for r in ratings}
 
        wishlisted = set(Wishlist.objects.filter(Product_id__in=product_ids, user_id=request.user.id).values_list('Product_id', flat=True))
        cart_items = {
            c.productId_id: c for c in Cart.objects.filter(productId_id__in=product_ids, user_id=request.user.id)
        }
 
        serialized_products = NewArivalProductSerializer(page_products, many=True).data
 
        final_data = []
        for product, item in zip(page_products, serialized_products):
            product_id = product.id
 
            fprice = product.price
            prod_discount = 0
            discount_obj = discounts.get(product_id)
            if discount_obj:
                dis_price = (discount_obj.discount * product.price) / 100
                fprice = f"{product.price - dis_price:.2f}"
                prod_discount = discount_obj.discount
 
            inventory = inventories.get(product_id)
            if not inventory:
                continue
 
            storestatus = 1 if product.status == 1 and inventory.status == 1 else 0
            tolerance = Decimal('0.0001')
            if storestatus == 1 and abs(product.price - Decimal('0.00')) >= tolerance:
 
                item['product_name'] = item['product_name'].capitalize()
                item['is_favourite'] = product_id in wishlisted
                item['in_cart'] = product_id in cart_items
                item['pro_quantity'] = cart_items[product_id].quantity if product_id in cart_items else 0
                item['product_tags'] = product_tags if product_tags else 0
                item['inventory'] = inventory.inventory
                item['rating'] = round(rating_map.get(product_id, 4.5), 1)
                item['price'] = str(fprice)
                item['product_discount'] = prod_discount
 
                final_data.append(item)
 
        return Response({
            'status': bool(final_data),
            'msg': 'Successfully' if final_data else 'Data not found',
            'total_product': total_product,
            'data': final_data,
            'store_id': store_id,
            'product_tags': product_tags,
            'banner_tags': banner_tags,
            'looking_for': looking_for
        }, status=status.HTTP_200_OK)


class SortFilterCategorylist(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            # 🔽 Static sort options
            sort_options = [
                {"value": "A_to_Z", "label": "A to Z"},
                {"value": "Z_to_A", "label": "Z to A"},
                {"value": "low_to_high", "label": "Low to High"},
                {"value": "high_to_low", "label": "High to Low"},
                {"value": "most_popular_product", "label": "Most Popular"},
            ]

            # 🔽 Brand list
            brands = ProductBrand.objects.filter(status=1).values('id', 'name')
            brand_list = [{"id": brand["id"], "name": brand["name"]} for brand in brands]
         
            # 🔽 Tag list
            tags = ProductTag.objects.filter(status=1).values('id', 'name')
            tag_list = [{"id": tag["id"], "name": tag["name"]} for tag in tags]

            return Response({
                "status": True,
                "message": "Filter options fetched successfully.",
                "data": {
                    "sort_options": sort_options,
                    "brand_list": brand_list,
                    "tag_list": tag_list,
                }
               

            })

        except Exception as e:
            return Response({
                "status": False,
                "message": f"Something went wrong: {str(e)}",
                "data": {}
            }, status=500)


class SearchProductCategory(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SearchProductSerializer
    filter_backends = [SearchFilter]

    def post(self, request, format= None):
        search_fields = request.data.get('product_name')
        store_id = request.data.get('store_id')
        looking_for = request.data.get('looking_for')
        category_id =  request.data.get('category_id')
        subcategories_id  =request.data.get('subCategories_id')
        user_id = request.user.id
        searchproduct = SerachProduct(product_name=search_fields, user_id=user_id)
        searchproduct.save()
        # queryset = Product.objects.filter(product_name__icontains=search_fields)
        queryset_ids = Product.objects.filter(product_name__icontains=search_fields, price__gt=0.00,product_for=looking_for).values_list('id', flat=True)
        priduct_ids = StoreInventory.objects.filter(product_id__in=queryset_ids,store_id = store_id,status = 1).values_list('product_id', flat=True)
        filters = {
            'id__in': priduct_ids,
            'product_for': looking_for
        }

        if category_id:
            filters['category'] = category_id

        if subcategories_id:
            filters['subcategory'] = subcategories_id

        queryset = Product.objects.filter(**filters)

        # queryset = Product.objects.filter(id__in=priduct_ids,product_for=looking_for)
        id_list = list(queryset_ids)
        items_per_page = 20  # You can adjust this value as needed
        page_number = request.data.get('page', 1)
        paginator = Paginator(queryset, items_per_page)
        try:
            page = paginator.page(page_number)
        except EmptyPage:
            # If the requested page is out of range, return an empty list
            return Response({'status': True, 'total_product': 0, 'data': [], 'msg': 'No more data'})

        page = paginator.get_page(page_number)
        search_productlist =[]
        product_ids = []
        for new_pro in page:
            today_date = date.today()
            fprice = str(new_pro.price)
            prod_discount = 0
            discount_pro = ProductDiscount.objects.filter(product_id=new_pro.id).first()
            if discount_pro:
                    start_date = discount_pro.startdate
                    end_date = discount_pro.enddate
                    if start_date <= today_date <= end_date:
                            discount = discount_pro.discount
                            pro_price = new_pro.price
                            dis_price =((discount*pro_price)/100)
                            fprice = f"{pro_price - dis_price:.2f}"
                            prod_discount = discount
            if StoreInventory.objects.filter(product_id = new_pro.id,store_id = store_id,status = 1).exists():
              product_ids.append(new_pro.id)
              is_favourite = Wishlist.objects.filter(Product_id=new_pro.id, user_id=self.request.user.id).exists()
              in_cart = Cart.objects.filter(productId_id=new_pro.id, user_id=self.request.user.id).exists()
              cart_quantity = Cart.objects.filter(productId_id=new_pro.id, user_id=self.request.user.id).first()
              pro_inventry = StoreInventory.objects.filter(product_id = new_pro.id,status = 1, store_id = store_id).first()
              prorating = ProductRating.objects.filter(product_id=new_pro.id).aggregate(Avg('rating'))['rating__avg']


              if cart_quantity:
                  quantity = cart_quantity.quantity
              else:
                  quantity = 0
              if pro_inventry is not None and new_pro is not None:
                    if new_pro.status == 1 and pro_inventry.status == 1:
                        storestatus = 1
                    elif new_pro.status == 0 and pro_inventry.status == 1:
                        storestatus = 0
                    elif new_pro.status == 1 and pro_inventry.status == 0:
                        storestatus = 0
                    else:
                        storestatus = 1


                    search_serializer = GetProductSerializer(new_pro)
                    search_data = search_serializer.data
                    search_data['product_name'] = search_data['product_name'].title()
                    search_data['is_favourite'] = is_favourite
                    search_data['in_cart'] = in_cart
                    search_data['pro_quantity'] = quantity
                    search_data['product_tags'] = 0
                    search_data['inventory'] = pro_inventry.inventory if pro_inventry else 0
                    search_data['rating'] = prorating if prorating else 4.5
                    search_data['price'] = fprice
                    search_data['product_discount'] = prod_discount

                    if storestatus == 1:

                       search_productlist.append(search_data)

        count = StoreInventory.objects.filter(product_id__in=id_list,store_id = store_id,status = 1).count()

        return Response({'status': True, 'total_product':count, 'data': search_productlist[:items_per_page], 'msg': 'Product list'})
