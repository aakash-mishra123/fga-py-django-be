from django.db import models
from ckeditor.fields import RichTextField
from autoslug import AutoSlugField
from PIL import Image
from django.utils.html import mark_safe
from accounts.models import User
from django.contrib.postgres.fields import ArrayField
from setting.models import OrderStatus
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.urls import path
# from product.forms import CSVUploadForm
from django import forms
from django.contrib import messages
from decimal import Decimal,InvalidOperation
from django.core.exceptions import ObjectDoesNotExist
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import csv
from django.shortcuts import render
#from taggit.managers import TaggableManager

class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


class CatalogCategory(models.Model):
    class Meta:
        verbose_name = "Categories"
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name',unique=True,null=True,default=None)
    banner = models.ImageField(upload_to="productsCategory",max_length=255,null=True,default=None)
    description = RichTextField(null=True,default=None,blank=True)
    short_description = RichTextField(null=True,default=None,blank=True)
    # status = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    CAT_CHOICES = (
        ('', 'select'),
        (1, 'Grocery'),
        (2, 'Restaurants'),
    )
    cat_for = models.SmallIntegerField(choices=CAT_CHOICES, default=1)

    STATUS_CHOICES = (
        ('', 'select'),
         (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    extra_eta = models.IntegerField(default=0)
    def __str__(self):
        return self.name

    def image_preview(self): #new
        return mark_safe(f'<img src = "{self.banner.url}" width = "100"/>')

class Tag(models.Model):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tag"

    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name',unique=True,null=True,default=None)
    banner = models.ImageField(upload_to="productsCategory",max_length=255,null=True,default=None)
    description = RichTextField(null=True,default=None,blank=True)
    short_description = RichTextField(null=True,default=None,blank=True)
    # status = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = (
        ('', 'select'),
         (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    TAG_FOR_CHOICES = (
       ('', 'select'),
        (1, 'Grocery'),
        (2, 'Restaurants'),
    )
    tag_for = models.SmallIntegerField(choices=TAG_FOR_CHOICES, default=1)

    def __str__(self):  
        return self.name

    def image_preview(self): #new
        return mark_safe(f'<img src = "{self.banner.url}" width = "100"/>')

class CatalogSubCategory(models.Model):
    class Meta:
        verbose_name = "Sub Categories"
        verbose_name_plural = "Sub Categories"
    category = models.ForeignKey(CatalogCategory,null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name',unique=True,null=True,default=None)
    banner = models.ImageField(upload_to="productsSubCategory",max_length=255,null=True,default=None)
    description = RichTextField(null=True,default=None,blank=True)
    short_description = RichTextField(null=True,default=None,blank=True)
    extra_eta = models.IntegerField(default=0)
    # status = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)

    SUBCAT_FOR_CHOICES = (
        ('', 'select'),
        (1, 'Grocery'),
        (2, 'Restaurants'),
    )
    subcat_for = models.SmallIntegerField(choices=SUBCAT_FOR_CHOICES, default=1)


    def __str__(self):
        return self.name

    def image_preview(self): #new
        return mark_safe(f'<img src = "{self.banner.url}" width = "100"/>')

class ProductBrand(models.Model):
    class Meta:
        verbose_name = "Product Brand"
        verbose_name_plural = "Product Brand"
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name",unique=True,null=True,default=None,blank=True)
    image = models.ImageField(upload_to="brands",max_length=255,null=True,default=None)
    content = RichTextField(null=True,default=None,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # status = models.SmallIntegerField(default=1)

    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    BRAND_FOR_CHOICES = (
        ('', 'select'),
        (1, 'Grocery'),
        (2, 'Restaurants'),
    )
    brand_for = models.SmallIntegerField(choices=BRAND_FOR_CHOICES, default=1)

    def __str__(self):
        return self.name

    def image_preview(self): #new
        return mark_safe(f'<img src = "{self.image.url}" width = "100"/>')

class ProductTag(models.Model):
    class Meta:
        verbose_name = "Product Tags"
        verbose_name_plural = "Product Tags"
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name",unique=True,null=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # status = models.SmallIntegerField(default=1)

    STATUS_CHOICES = (
         ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)






    def __str__(self):
        return self.name

class Product(models.Model):
    product_name    =   models.CharField(max_length=255)
    name_slug       =   AutoSlugField(populate_from="product_name",null=True,default=None)
    category        =   models.ForeignKey(CatalogCategory,null=True, on_delete=models.CASCADE)
    subcategory     =   models.ForeignKey(CatalogSubCategory,null=True, on_delete=models.CASCADE)
    Brand           =   models.ForeignKey(ProductBrand,null=True, blank=True, on_delete=models.CASCADE)
    sku             =   models.CharField(max_length=255,unique=True)
    price           =   models.DecimalField(max_digits=10, decimal_places=2)
    # price           =   models.CharField(max_length=255)
    #product_tags   =   models.ForeignKey(ProductTag,null=True, blank=True, on_delete=models.CASCADE)
    product_tags    =   models.ManyToManyField(ProductTag, blank=True)  # Many-to-many relationship with ProductTag
    tags    =   models.ManyToManyField(Tag, blank=True)  # Many-to-many relationship with Tag
    product_description =   RichTextField( null=True,default=None,blank=True)
    product_short_description   =   RichTextField(null=True,default=None,blank=True)
    quantity=models.IntegerField(null=True)
    product_weight=models.CharField(max_length=255,blank=True,default=1)
    product_image=models.ImageField(upload_to="products",max_length=255,null=True,default=None,blank=True)
    product_url=models.CharField(max_length=500,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    # status = models.SmallIntegerField(default=1)

    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField( choices=STATUS_CHOICES, default=1)

    PRODUCT_TYPE_CHOICES = (
        ('', 'select'),
        (1, 'Grocery'),
        (2, 'Restaurants'),
    )
    product_for = models.SmallIntegerField( choices=PRODUCT_TYPE_CHOICES, default=1)

    def set_product_tags(self, tag_ids):
        self.product_tags = ",".join(str(id) for id in tag_ids)

    def get_product_tags(self):
        return [tag.name for tag in self.product_tags.all()]

    def __str__(self):
        return self.product_name

    def image_preview(self):
        if self.product_image:
            return mark_safe(f'<img src="{self.product_image.url}" width="100"/>')
        else:
            return "No image available"

class Images(models.Model):
    product = models.ForeignKey(Product, null=True,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="products",max_length=255,null=True,default=None)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    # status = models.SmallIntegerField(default=1)

    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)

    class Meta:
        verbose_name_plural = "Product Images"

    def __str__(self):
        return self.title

    def product_image(self): #new
        return mark_safe(f'<img src = "{self.image.url}" width = "100"/>')

class Seo(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    url_key = models.CharField(max_length=255,null=True,default=None)
    meta_title = models.CharField(max_length=255, null=True,default=None)
    meta_keywords = RichTextField()
    meta_description = RichTextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(default=1)

    class Meta:
        verbose_name_plural = "SEO Fields"

    def __str__(self):
        return self.meta_title

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store_id = models.CharField(max_length=255, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(default=1)
    looking_for = models.CharField(default=1,max_length=255, blank=True, null=True)

class ProductDiscountm(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount = models.IntegerField(default=0)
    startdate = models.DateField(max_length=255, blank=True, null=True)
    enddate = models.DateField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=255, blank=True, null=True)
    subtotal = models.CharField(max_length=255, blank=True, null=True)
    total = models.CharField(max_length=255, blank=True, null=True)
    order_quantity = models.IntegerField(null=True)
    coupon_code = models.CharField(max_length=255, blank=True,null=True)
    coupon_discount = models.CharField(max_length=255, blank=True, null=True)
    prime_discount = models.CharField(max_length=20, default=0,blank=True, null=True)
    coupon_discount_amount = models.CharField(max_length=255, blank=True, null=True)
    user_address_id = models.ForeignKey('accounts.Address', null=True, on_delete=models.SET_NULL)
    store = models.ForeignKey('stores.Stores', null=True, on_delete=models.CASCADE)
    tip_amount = models.IntegerField(null=True)
    tip_status = models.IntegerField(null=True)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, null=True)
    delivery_signature = models.ImageField(upload_to='signatures/', max_length=255,null=True,default=None)
    is_delete = models.IntegerField(default=0)
    cancel_reason = models.CharField(max_length=255, blank=True, null=True)
    cancel_remark = models.CharField(max_length=255, blank=True, null=True)
    tip = models.CharField(max_length=255, blank=True, null=True)
    delivery_instructions = models.CharField(max_length=255, blank=True, null=True)
    delivery_instruction_name = models.CharField(max_length=255, blank=True, null=True)
    is_delete = models.IntegerField(default=0)
    delivery_boy_id = models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    order_status_merchant = models.CharField(max_length=255, blank=True, null=True)
    plan_id = models.IntegerField(default=0,null=True)
    delivery_time = models.CharField(default=0,max_length=255, blank=True, null=True)
    payment_mode = models.CharField(default=0,max_length=255, blank=True, null=True)
    payment_status = models.CharField(default=0,max_length=255, blank=True, null=True)
    reached = models.CharField(default=0,max_length=20, blank=True, null=True)
    skip_rating = models.IntegerField(default=0)
    delivery_charges = models.IntegerField(default=0, null=True)
    address = models.CharField(default=0,max_length=255, blank=True, null=True)
    order_for = models.CharField(default=1,max_length=255, blank=True, null=True)
    iteam_unavailable = models.CharField(max_length=255, blank=True, null=True)


    class Meta:
        permissions = [
            ("can_view_order", "Can view orders"),
            ("can_change_order", "Can change orders"),
            ("can_add_order", "Can add orders"),
            ("can_delete_order", "Can delete orders"),
        ]

    def __str__(self):
        return self.order_id

    def image_preview(self): #new
        return mark_safe(f'<img src = "{self.delivery_signature.url}" width = "100"/>')

class OrderItem(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE)
    store = models.ForeignKey('stores.Stores', null=True, on_delete=models.CASCADE)
    item_quantity = models.IntegerField(null=True)
    order_status = models.CharField(max_length=255, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    price =   models.DecimalField(max_digits=10, decimal_places=2 ,default=0)
    discount_offer = models.IntegerField(default=0)
    updated_at=models.DateTimeField(auto_now=True)
    removeItem = models.SmallIntegerField(default=0)

class OrderRating(models.Model):
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True)
    messages = models.CharField(max_length=255, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    rating_for = models.IntegerField(default=1)

class ProductRating(models.Model):
    rating = models.IntegerField(null=True)
    product_id = models.IntegerField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    rating_for = models.IntegerField(default=1)

class DeliveryBoyRating(models.Model):
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    deliveryboy_id = models.IntegerField(null=True)
    rating = models.IntegerField(null=True)
    messages = models.CharField(max_length=255, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    rating_for = models.IntegerField(default=1)

class ApplyCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=255, blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


class SerachProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
