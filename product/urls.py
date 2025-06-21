from django.urls import path, include
from product.views import GetProductView
from product.views import HomeBannerClickableList,AddtoCart,SearchProductCategory, SearchProduct,ReorderView,OrderDetails,DeliveryInstAdd,RemoveDeliveryInst,RemovePrimeInCart,OrderPlaceNew,CartQuantity,AddPrimeInCart,ProductDetail, UpdateCartQuantity, UserWishList, DeleteWishList, ProductDetailAPIView,ProductListAPIView,CategoryListAPIView,CategoryDetailAPIView, Categories, SubCategories, ViewCart, DeleteCart, CouponList, CheckDiscount, OrderPlace, UserDashboard, PreviousOrder, RecentOrder, UserOrderList, AddToWishProduct, DownloadProductImage
from . import views
from product.views import SortFilterCategorylist,GetProductView,Chkdistance,TagProductList,AddTipIncart,BestSellerProductList, ClearCart, AddOrderRatingView, AddDelivryboyRatingView,RemoveTipIncart,AddtoCart,OrderAgain,Notifications,RemoveAllwishList,RecentSearch,ClearOrderHistory,RemoveApplyCoupn,ApplyCoupn,NewArivalProductList,SummerProductList,PremiumProductList,ProductBrandList,BrandProductList,SearchProduct,OrderDetails, UpdateCartQuantity, UserWishList, DeleteWishList, ProductDetailAPIView,ProductListAPIView,CategoryListAPIView,CategoryDetailAPIView, Categories, SubCategories, ViewCart, DeleteCart, CouponList, CheckDiscount, OrderPlace, UserDashboard, PreviousOrder, RecentOrder, UserOrderList, AddToWishProduct



urlpatterns = [
    path('get-products/', GetProductView.as_view(), name="get-products"),
    path('product_detail/', ProductDetail.as_view(), name="product_detail"),
    path('add-to-cart/', AddtoCart.as_view(), name="add-to-cart"),
    path('clear_cart/', ClearCart.as_view(), name="clear_cart"),
    path('update_cart_quantity/', UpdateCartQuantity.as_view(), name="update_cart_quantity"),
    path('add_tip/', AddTipIncart.as_view(), name="add_tip"),
    path('remove_tip/', RemoveTipIncart.as_view(), name="remove_tip"),
    path('delivery_instructions/', DeliveryInstAdd.as_view(), name="delivery_instructions"),
    path('remove_delivery_instructions/', RemoveDeliveryInst.as_view(), name="remove_delivery_instructions"),
    path('categories/', Categories.as_view(), name="categories"),
    path('sub_categories/', SubCategories.as_view(), name="sub_categories"),
    path('view_cart/', ViewCart.as_view(), name="view_cart"),
    path('delete_cart/', DeleteCart.as_view(), name="delete_cart"),
    path('coupon_list/', CouponList.as_view(), name="coupon_list"),
    path('chk_coupon_discount/', CheckDiscount.as_view(), name="chk_coupon_discount"),
    path('order_place/', OrderPlace.as_view(), name="order_place"),
    path('order_place_new/', OrderPlaceNew.as_view(), name="order_place_new"),
    path('user-dashboard/', UserDashboard.as_view(), name="user-dashboard"),
    path('categories/',CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<int:pk>/',CategoryDetailAPIView.as_view(), name='category-detail'),
    path('productslist/',ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/',ProductDetailAPIView.as_view(), name='product-detail'),
    path('user_previous_order/', PreviousOrder.as_view(), name="user_previous_order"),
    path('recent_order/', RecentOrder.as_view(), name="recent_order"),
    path('user_order_list/', UserOrderList.as_view(), name="user_order_list"),
    path('add_to_wish/', AddToWishProduct.as_view(), name="add_to_wish"),
    path('search-product/', SearchProduct.as_view(), name="search-product"),
    path('user_wishlist/', UserWishList.as_view(), name="user_wishlist"),
    path('delete_wishlist_product/', DeleteWishList.as_view(), name="delete_wishlist_product"),
    path('order_details/', OrderDetails.as_view(), name="order_details"),
    path('product_brand_list/', ProductBrandList.as_view(), name="product_brand_list"),
    path('brand_product_list/', BrandProductList.as_view(), name="brand_product_list"),
    path('new_arival_product_list/', NewArivalProductList.as_view(), name="new_arival_product_list"),
    path('tag_product_list/', TagProductList.as_view(), name="tag_product_list"),
    path('best_seller_product_list/', BestSellerProductList.as_view(), name="best_seller_product_list"),
    path('premium_product_list/', PremiumProductList.as_view(), name="premium_product_list"),
    path('summer_product_list/', SummerProductList.as_view(), name="summer_product_list"),
    path('apply_coupon/', ApplyCoupn.as_view(), name="apply_coupon"),
    path('remove_apply_coupon/', RemoveApplyCoupn.as_view(), name="remove_apply_coupon"),
    path('recent_search/', RecentSearch.as_view(), name="recent_search"),
    path('clear_order_history/', ClearOrderHistory.as_view(), name="clear_order_history"),
    path('remove_allwish_list/', RemoveAllwishList.as_view(), name="remove_allwish_list"),
    path('cart_quantity/', CartQuantity.as_view(), name="cart_quantity"),
    path('order_again/', OrderAgain.as_view(), name="order_again"),
    path('notifications/', Notifications.as_view(), name="notifications"),
    path('add_prime_incart/', AddPrimeInCart.as_view(), name="add_prime_incart"),
    path('remove_prime_incart/', RemovePrimeInCart.as_view(), name="remove_prime_incart"),
    path('reorder/', ReorderView.as_view(), name="reorder"),
    path('add_order_rating/', AddOrderRatingView.as_view(), name="add_order_rating"),
    path('add_deliveryboy_rating/', AddDelivryboyRatingView.as_view(), name="add_deliveryboy_rating"),
    path('download_product_image/', DownloadProductImage.as_view(), name="download_product_image"),
    path('home_banner_clickable_list/', HomeBannerClickableList.as_view(), name="home_banner_clickable_list"),
    path('chk_dis/', Chkdistance.as_view(), name="chk_dis"),
    path('sort_filter_category_list/', SortFilterCategorylist.as_view(), name="sort_filter_category_list"),
    path('search_product_category/', SearchProductCategory.as_view(), name="search_product_category"),




]
