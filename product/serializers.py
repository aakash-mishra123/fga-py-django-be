
from rest_framework import serializers
from product.models import Product,OrderRating, Tag, CatalogCategory,Images, DeliveryBoyRating, CatalogSubCategory, ProductBrand, Wishlist,Order,OrderItem, SerachProduct
from accounts.models import Cart,Address,User,PlanBenefits,OrderAddress
from coupon_management.validations import validate_coupon
from coupon_management.models import Coupon
from banner.models import HomeBanner,OfferBanners,Notification
from stores.models import Stores,StoreInventory, AssignStoreBoy

class GetProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ViewCartlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_name','name_slug','quantity','price','product_image','id','category_id','subcategory_id']

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogCategory
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'        

class SubCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogSubCategory
        fields = '__all__'

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class AddCartSerializer(serializers.ModelSerializer):
     class Meta:
        model = Cart
        fields = ['productId', 'quantity', 'amount', 'weight', 'user_id', 'store','looking_for']

     def validate(self, data):

      if not data['productId']:
        raise serializers.ValidationError({'error':'productId should not be empty !'})
      if not data['quantity']:
        raise serializers.ValidationError({'error':'quantity should not be empty !'})
      if not data['amount']:
        raise serializers.ValidationError({'error':'amount should not be empty !'})
      if not data['store']:
         raise serializers.ValidationError({'error':'store should not be empty !'})
      if not data['looking_for']:
         raise serializers.ValidationError({'error':'looking_for should not be empty !'})

      return data

     def create(self, validated_data):        
        quantity = validated_data.pop('quantity')
        looking_for = validated_data.pop('looking_for')
        amount = validated_data.pop('amount')
        totalamount = quantity*amount
        user = self.context['request'].user

        addcart = Cart.objects.create(**validated_data,total_amount = totalamount,quantity= quantity,amount = amount,user=user,looking_for=looking_for)
        addcart.save()
        return addcart

class UpdateCartQuantitySerializer(serializers.Serializer):

    productId = serializers.IntegerField()
    update_quantity = serializers.IntegerField()
    looking_for = serializers.IntegerField()

class BrandProductlistSerializer(serializers.Serializer):

    brand_id = serializers.IntegerField()

class CouponCodeApplySerializer(serializers.Serializer):

    coupon_code = serializers.CharField()

class AddToWishSerializer(serializers.ModelSerializer):
     class Meta:
        model = Wishlist
        fields = '__all__'

class UserDefaultAddressSerializer(serializers.ModelSerializer):
     class Meta:
        model = Address
        fields = '__all__'

class UserorderAddressSerializer(serializers.ModelSerializer):
     class Meta:
        model = OrderAddress
        fields = '__all__'

class ViewCartSerializer(serializers.ModelSerializer):
    productId = ViewCartlistSerializer()
    class Meta:
        model = Cart
        fields = '__all__'

class DeleteCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class CouponListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id','code']

class CoupondiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class DashboardSerializer(serializers.ModelSerializer):

    product_tags = serializers.SerializerMethodField()


    class Meta:
        model = HomeBanner
        fields = ['id','product_tags','title','banner','content','status','created_at','update_at','priority','slug']

    def get_product_tags(self, instance):
        # Check if there are any product tags
        product_tags = instance.product_tags.all()
        if product_tags:
            # Return the first product tag ID
            return product_tags[0].id
        return None

class OfferSerializer(serializers.ModelSerializer):
    product_tags = serializers.SerializerMethodField()
    class Meta:
        model = OfferBanners
        fields = ['id','product_tags','title','banner','content','status','created_at','update_at','priority']

    def get_product_tags(self, instance):
        # Check if there are any product tags
        product_tags = instance.product_tags.all()
        if product_tags:
            # Return the first product tag ID
            return product_tags[0].id
        return None

class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrand
        fields = '__all__'


class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogCategory
        fields = ('name',)


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'product_name')


class ProductDetailSerializer(serializers.ModelSerializer):
    category_id = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['product_name','name_slug','quantity','price','id','category_id','payment_mode']

class CetegoryDetailSerializer(serializers.ModelSerializer):
    id = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CatalogCategory
        fields = ['id','name','slug','banner','description']


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogCategory
        fields = ('id', 'name')

class UserdetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'full_name', 'mobile', 'email' ,'skip_prime')

class OrderRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRating
        fields = '__all__'

class DeliveryRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoyRating
        fields = '__all__'


class SearchProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class StroreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stores
        fields = '__all__'

class BrandProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class SearchKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = SerachProduct
        fields = '__all__'

class DeliveryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','full_name','email','mobile','profile_image']

class CartImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_image']

class ProductDetilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['image']

class NotificationListSerializer(serializers.ModelSerializer):
   class Meta:
       model = Notification
       fields = '__all__'

class NewArivalProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  # Serialize all fields in the Product model

class PlanBenefitsSerializer(serializers.ModelSerializer):
  class Meta:
    model = PlanBenefits
    fields = '__all__'
