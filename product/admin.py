from django.contrib import admin
from product.models import Product, CatalogCategory,CatalogSubCategory, Images, Seo, ProductBrand, ProductTag, ProductDiscountm,DeliveryBoyRating,OrderRating,Tag
from accounts.models import User
from tinymce.models import HTMLField
from django.template.defaultfilters import truncatechars
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.admin import StackedInline
from django.urls import path
from product.forms import CSVUploadForm
from django.contrib import messages
from django.http import HttpResponseRedirect
# from django_select2.forms import ModelSelect2MultipleWidget
from django.urls import reverse
from django import forms
from decimal import Decimal,InvalidOperation
from django.core.exceptions import ObjectDoesNotExist
import requests
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from django.core.files.storage import default_storage
from product.forms import ProductForm
from django.contrib.admin.widgets import FilteredSelectMultiple
import csv
from django.db import models
from django.contrib import admin
from django.forms import CheckboxSelectMultiple
# import chardet
import codecs
from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponse
import csv
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from permissions_utils import get_group_permissions
from django.contrib.admin import widgets
from django import forms



class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()



class ProductAdminInline(admin.TabularInline):
    model = Images
    extra = 3
    readonly_fields = ['product_image']

class ProductAdminInlineSeo(admin.StackedInline):
    model = Seo
    #extra = 1
    #extra = 0
    max_num=1

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

    #readonly_fields = ['product_image']

class BaseAdminMixin:
    """Mixin providing common permission checking for all admin classes"""
    def _has_permission(self, request, permission_codename):
        """Check if user has a specific permission via group."""
        user_group_permissions = get_group_permissions(request.user)
        return any(perm.codename == permission_codename for perm in user_group_permissions)
    
    def has_view_permission(self, request, obj=None):
        return self._has_permission(request, f'view_{self.opts.model_name}')
        
    def has_change_permission(self, request, obj=None):
        return self._has_permission(request, f'change_{self.opts.model_name}')
        
    def has_add_permission(self, request, obj=None):
        return self._has_permission(request, f'add_{self.opts.model_name}')
        
    def has_delete_permission(self, request, obj=None):
        return self._has_permission(request, f'delete_{self.opts.model_name}')
        
    def changelist_view(self, request, extra_context=None):
        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        extra_context = extra_context or {}
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]
        
        return super().changelist_view(request, extra_context=extra_context)

class ProductBrandAdmin(BaseAdminMixin, admin.ModelAdmin):
    def get_availability_status_display(self, obj):
        toggle_html = (
            f'<label class="switch" data-url="{reverse("customer:productbrand", args=[obj.pk])}"'
            f' data-status="{obj.status}">'
            f'<input type="checkbox" {"checked" if obj.status == 1 else ""}>'
            f'<span class="slider round"></span>'
            f'</label>'
        )

        return format_html(toggle_html)

    get_availability_status_display.short_description = 'Status'

    list_display = ('image_preview','name','slug','get_availability_status_display','edit_item')

    product_count = ProductBrand.objects.count()
    list_per_page = 50
    search_fields = ['name']

         # Define a custom method for the delete icon

    def edit_item(self, obj):
        url = reverse("admin:product_productbrand_change", args=[obj.id])
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', url)

    def delete_item(self, obj):

        url = reverse("admin:product_productbrand_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', url)

    # Delete icon method description
    delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')
    edit_item.short_description = format_html('<span class="edit-action-description">Action</span>')



    def product_brand_picture(self,obj):
        return format_html('<img src="{0}" width="100" />'.format(obj.image.url))

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv, name='product_productbrand_upload_csv'),]
        return new_urls + urls

    def changelist_view(self, request, extra_context=None):

        mutable_get = request.GET.copy()

        # Remove the 'p' parameter from the mutable copy
        # if 'p' in mutable_get:
        #     del mutable_get['p']

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]
        request.GET = mutable_get

        return super().changelist_view(request, extra_context=extra_context)

    def upload_csv(self, request):
        # if request.method == "POST":
        #     csv_file = request.FILES["csv_upload"]

        #     if not csv_file.name.endswith('.csv'):
        #         messages.warning(request, 'The wrong file type was uploaded')
        #         return HttpResponseRedirect(request.path_info)

        #     file_data = csv_file.read().decode("utf-8")
        #     csv_data = file_data.split("\n")

        #     for x in csv_data:
        #         fields = x.split(",")

        #         if len(fields) >= 5:  # Adjust the index based on your data
        #             name = fields[0]
        #             slug = fields[1].strip()
        #             image = fields[2].strip()
        #             content = fields[3].strip()
        #             status_value = fields[4].strip()

        #             if status_value.isdigit():  # Check if it's a valid integer
        #                 status = int(status_value)

        #                 ProductBrand_instance, created = ProductBrand.objects.update_or_create(
        #                     name=name,
        #                     defaults={'name': name,
        #                                 'slug': slug if slug else '',
        #                                 'content': content if content else '',
        #                                 'status': status,
        #                                 }
        #                 )



        #                 if not image:
        #                     default_image_url = 'https://demo2.1hour.in/media/users/no-image.png'
        #                     default_image_response = requests.get(default_image_url)

        #                     if default_image_response.status_code == 200:
        #                         default_image_content = ContentFile(default_image_response.content)
        #                         ProductBrand_instance.image.save('no-image.png', default_image_content)
        #                     else:
        #                         print(f"Failed to download default image from URL: {default_image_url}")

        #                 else:
        #                     # Download and save the image
        #                     image_response = requests.get(image)
        #                     if image_response.status_code == 200:
        #                         image_filename = image.split('/')[-1]
        #                         image_content = ContentFile(image_response.content)
        #                         ProductBrand_instance.image.save(image_filename, image_content)
        #                     else:
        #                         print(f"Failed to download image from URL: {image}")

        #                 # # Print the image URL before using it
        #                 # print("Image URL:", image)

        #                 # # Download and save the image
        #                 # image_response = requests.get(image)
        #                 # print("Image Response:", image_response)
        #                 # if image_response.status_code == 200:
        #                 #     image_filename = image.split('/')[-1]  # Get the filename from the URL
        #                 #     image_content = ContentFile(image_response.content)
        #                 #     ProductBrand_instance.image.save(image_filename, image_content)
        #                 # else:
        #                 #     print(f"Failed to download image from URL: {image}")
        #             else:
        #                 print("Incomplete data:", fields)

        #     url = reverse('admin:product_productbrand_changelist')
        #     return HttpResponseRedirect(url)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/brand_csv_upload.html", data)

    actions = ['export_as_csv']  # Add this line to enable the export action

    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_brands.csv"'

        writer = csv.writer(response)
        writer.writerow(['image','name', 'slug', 'status'])  # Add more fields as needed

        for product_brand in queryset:
            image_url = product_brand.image.url if product_brand.image else ""
            writer.writerow([
                image_url, 
                product_brand.name, 
                product_brand.slug, 
                product_brand.status
            ])

        return response

    export_as_csv.short_description = "Export selected products as CSV"

    actions = ['export_as_csv', 'disassociate_products']

    def disassociate_products(modeladmin, request, queryset):
        for product_brand in queryset:
            associated_products = Product.objects.filter(Brand=product_brand)
            if associated_products.exists():
                messages.error(
                    request,
                    f"Cannot delete '{product_brand.name}' because it's associated with products. "
                    f"Please update those products first."
                )
            else:
                product_brand.delete()
        return HttpResponseRedirect(request.get_full_path())

    disassociate_products.short_description = "Disassociate products and delete product brands"


class DeliveryBoyRatingAdmin(admin.ModelAdmin): 
    def has_delete_permission(self, request, obj=None):        
        return False 
    def has_add_permission(self, request, obj=None):        
            return False 
    def has_change_permission(self, request, obj=None):        
            return False 

    
    def custom_info_new(self, obj):
        return obj.user_id
    custom_info_new.short_description = 'Customer Name'

    def custom_info_newn(self, obj):
        if obj.deliveryboy_id:
            try:
                user = User.objects.get(id=obj.deliveryboy_id)
                return user.full_name
            except User.DoesNotExist:
                return "No matching user found"
        return "No Delivery Boy ID"

    custom_info_newn.short_description = 'Delivery Boy Name'

    list_display = ('order','custom_info_newn','rating', 'messages','custom_info_new')
    
      

    product_count = DeliveryBoyRating.objects.count()
    list_per_page = 50
    search_fields = ['name']

class OrderRatingAdmin(admin.ModelAdmin): 
    def has_delete_permission(self, request, obj=None):        
        return False 
    def has_add_permission(self, request, obj=None):        
            return False 
    def has_change_permission(self, request, obj=None):        
            return False 

    
    def custom_info_new(self, obj):
        return obj.user_id
    custom_info_new.short_description = 'Customer Name'   

    list_display = ('order','rating', 'messages','custom_info_new')  
      

    product_count = OrderRating.objects.count()
    list_per_page = 50
    search_fields = ['name']    


class ProductDiscountAdmin(admin.ModelAdmin):    

    def get_availability_status_display(self, obj):
        toggle_html = (
            f'<label class="switch" data-url="{reverse("customer:productbrand", args=[obj.pk])}"'
            f' data-status="{obj.status}">'
            f'<input type="checkbox" {"checked" if obj.status == 1 else ""}>'
            f'<span class="slider round"></span>'
            f'</label>'
        )

        return format_html(toggle_html)

    get_availability_status_display.short_description = 'Status'

    list_display = ('discount','startdate', 'enddate','get_availability_status_display')
    formfield_overrides = {
        models.DateField: {'widget': widgets.AdminDateWidget},
    }
    formfield_overrides = {
        models.DateField: {'widget': widgets.AdminDateWidget},
    }
      

    product_count = ProductDiscountm.objects.count()
    list_per_page = 50
    search_fields = ['name']

         # Define a custom method for the delete icon

    def edit_item(self, obj):
        url = reverse("admin:product_productbrand_change", args=[obj.id])
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', url)

    def delete_item(self, obj):

        url = reverse("admin:product_productbrand_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', url)

    # Delete icon method description
    delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')
    edit_item.short_description = format_html('<span class="edit-action-description">Action</span>')



    def product_brand_picture(self,obj):
        return format_html('<img src="{0}" width="100" />'.format(obj.image.url))

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv, name='product_productbrand_upload_csv'),]
        return new_urls + urls

    def changelist_view(self, request, extra_context=None):

        mutable_get = request.GET.copy()

        # Remove the 'p' parameter from the mutable copy
        # if 'p' in mutable_get:
        #     del mutable_get['p']

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]
        request.GET = mutable_get

        return super().changelist_view(request, extra_context=extra_context)

    def upload_csv(self, request):
    

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/brand_csv_upload.html", data)

    actions = ['export_as_csv']  # Add this line to enable the export action

    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_brands.csv"'

        writer = csv.writer(response)
        writer.writerow(['image','name', 'slug', 'status'])  # Add more fields as needed

        for product_brand in queryset:
            image_url = product_brand.image.url if product_brand.image else ""
            writer.writerow([
                image_url, 
                product_brand.name, 
                product_brand.slug, 
                product_brand.status
            ])

        return response

    export_as_csv.short_description = "Export selected products as CSV"

    actions = ['export_as_csv', 'disassociate_products']

    def disassociate_products(modeladmin, request, queryset):
        for product_brand in queryset:
            associated_products = Product.objects.filter(Brand=product_brand)
            if associated_products.exists():
                messages.error(
                    request,
                    f"Cannot delete '{product_brand.name}' because it's associated with products. "
                    f"Please update those products first."
                )
            else:
                product_brand.delete()
        return HttpResponseRedirect(request.get_full_path())

    disassociate_products.short_description = "Disassociate products and delete product brands"    



class CatalogCategoryAdmin(BaseAdminMixin, admin.ModelAdmin):
    def get_availability_status_display(self, obj):
        toggle_html = (
            f'<label class="switch" data-url="{reverse("customer:productCategoryStatusUpdate", args=[obj.pk])}"'
            f' data-status="{obj.status}">'
            f'<input type="checkbox" {"checked" if obj.status == 1 else ""}>'
            f'<span class="slider round"></span>'
            f'</label>'
        )

        return format_html(toggle_html)

    get_availability_status_display.short_description = 'Status'


    list_display = ('image_preview','name', 'get_availability_status_display','edit_item')
    product_count = CatalogCategory.objects.count()
    list_per_page = 50
    search_fields = ['name']

    def changelist_view(self, request, extra_context=None):

        mutable_get = request.GET.copy()

        # Remove the 'p' parameter from the mutable copy
        # if 'p' in mutable_get:
        #     del mutable_get['p']

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]
        request.GET = mutable_get

        return super().changelist_view(request, extra_context=extra_context)

           # Define a custom method for the delete icon


    def edit_item(self, obj):
        url = reverse("admin:product_catalogcategory_change", args=[obj.id])
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', url)

    def delete_item(self, obj):
        url = reverse("admin:product_catalogcategory_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', url)

    # Delete icon method description
    delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')

    def product_category_picture(self,obj):
        return format_html('<img src="{0}" width="100" />'.format(obj.banner.url))


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls


    def upload_csv(self, request):
        #  if request.method == "POST":
        #     csv_file = request.FILES["csv_upload"]

        #     if not csv_file.name.endswith('.csv'):
        #         messages.warning(request, 'The wrong file type was uploaded')
        #         return HttpResponseRedirect(request.path_info)
        #     # print(csv_file)
        #     csv_data = csv_file.read().decode("utf-8")
        #     csv_reader = csv.reader(csv_data.splitlines())
        #     # csv_data = file_data.split("\n")

        #      # Skip the first element (header)
        #     next(csv_reader, None)
        #     # csv_data = csv_data[1:]

        #     for fields in csv_reader:
        #         # fields = x.split(",")
        #         if len(fields) >= 6:
        #             name = fields[0].strip()
        #             slug = fields[1].strip()
        #             banner = fields[2].strip()
        #             description = fields[3].strip()
        #             short_description = fields[4].strip()
        #             status_value = fields[5].strip()

        #             # Default value for status
        #             # status = 0

        #             # if status_value.isdigit():  # Check if it's a valid integer
        #             #    status = int(status_value)

        #             print("Banner URL:", name)

        #             CatalogCategory_instance, created = CatalogCategory.objects.update_or_create(
        #                 name=name,
        #                 defaults={'name': name,
        #                             'slug': slug if slug else " ",
        #                             'description': description if description else " ",
        #                             'short_description': short_description if description else " ",
        #                             'status': status_value if status_value else 0,
        #                             }

        #             )

        #             if not banner:
        #                     default_image_url = 'https://demo2.1hour.in/media/users/no-image.png'
        #                     default_image_response = requests.get(default_image_url)

        #                     if default_image_response.status_code == 200:
        #                         default_image_content = ContentFile(default_image_response.content)
        #                         CatalogCategory_instance.banner.save('no-image.png', default_image_content)
        #                     else:
        #                         print(f"Failed to download default image from URL: {default_image_url}")

        #             else:
        #                     # Download and save the image
        #                     image_response = requests.get(banner)
        #                     if image_response.status_code == 200:
        #                         image_filename = banner.split('/')[-1]
        #                         image_content = ContentFile(image_response.content)
        #                         CatalogCategory_instance.banner.save(image_filename, image_content)
        #                     else:
        #                         print(f"Failed to download image from URL: {banner}")

        #             # print("monika:", name)
        #             # # Download and save the image
        #             # image_response = requests.get(banner)
        #             # print(image_response)
        #             # if image_response.status_code == 200:
        #             #     image_filename = banner.split('/')[-1]  # Get the filename from the URL
        #             #     image_content = ContentFile(image_response.content)
        #             #     CatalogCategory_instance.banner.save(image_filename, image_content)
        #             # else:
        #             #  print(f"Failed to download image from URL: {banner}")
        #         else:
        #              print("Incomplete data:", fields)

        #     url = reverse('admin:product_catalogcategory_changelist')
        #     return HttpResponseRedirect(url)

         form = CsvImportForm()
         data = {"form": form}
         return render(request, "admin/csv_upload_catalogcategory.html", data)


    actions = ['export_as_csv']  # Add this line to enable the export action

    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="catalog_categories.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Slug', 'Status', 'Image'])  # Add more fields as needed

        for catalog_category in queryset:
            image_url = catalog_category.banner.url if catalog_category.banner else ""
            writer.writerow([catalog_category.name, catalog_category.slug, catalog_category.status, image_url])  # Add more fields

        return response

    export_as_csv.short_description = "Export selected catalog categories as CSV"  # Set the action description


class CatalogSubCategoryAdmin(BaseAdminMixin, admin.ModelAdmin):
    def get_availability_status_display(self, obj):
        toggle_html = (
            f'<label class="switch" data-url="{reverse("customer:productSubCategoryStatusUpdate", args=[obj.pk])}"'
            f' data-status="{obj.status}">'
            f'<input type="checkbox" {"checked" if obj.status == 1 else ""}>'
            f'<span class="slider round"></span>'
            f'</label>'
        )

        return format_html(toggle_html)

    get_availability_status_display.short_description = 'Status'

    list_display = ('image_preview','name', 'category', 'get_availability_status_display','edit_item')

    product_count = CatalogSubCategory.objects.count()
    list_per_page = 50
    search_fields = ['name','category__name']


    def edit_item(self, obj):
        url = reverse("admin:product_catalogsubcategory_change", args=[obj.id])
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>',url)

               # Define a custom method for the delete icon
    def delete_item(self, obj):
        url = reverse("admin:product_catalogsubcategory_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', url)

    # Delete icon method description
    delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')
    edit_item.short_description = format_html('<span class="edit-action-description">Action</span>')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv, name='product_productbrand_upload_csv'),]
        return new_urls + urls



    def upload_csv(self, request):
        # if request.method == "POST":
        #     csv_file = request.FILES["csv_upload"]

        #     if not csv_file.name.endswith('.csv'):
        #         messages.warning(request, 'The wrong file type was uploaded')
        #         return HttpResponseRedirect(request.path_info)

        #     csv_data = csv_file.read().decode('utf-8')
        #     csv_reader = csv.reader(csv_data.splitlines())


        #     next(csv_reader, None)
        #     # csv_data = csv_data[1:]
        #     for fields in csv_reader:
        #         # fields = x.split(",")
        #         # print(len(fields), '7890')
        #         if len(fields) >= 7:
        #             category_name = fields[0]
        #             name = fields[1].strip()
        #             slug = fields[2].strip()
        #             banner = fields[3].strip()
        #             description = fields[4].strip()
        #             short_description = fields[5].strip()
        #             status = fields[6].strip()

        #             Category_instance = None

        #             try:
        #                 CatalogCategory_instance = CatalogCategory.objects.get(name=category_name)

        #                 # All filters have exactly one match, proceed with creating the product
        #                 Category_instance, created = CatalogSubCategory.objects.update_or_create(
        #                     name=name,
        #                     defaults={ 'category': CatalogCategory_instance ,
        #                                 'name': name,
        #                                 'slug': slug if slug  else " ",
        #                                 'description': description if description  else " ",
        #                                 'short_description': short_description if description  else " ",
        #                                 'status': status,
        #                             }

        #                 )
        #                 if not banner:
        #                     default_image_url = 'https://demo2.1hour.in/media/users/no-image.png'
        #                     default_image_response = requests.get(default_image_url)

        #                     if default_image_response.status_code == 200:
        #                         default_image_content = ContentFile(default_image_response.content)
        #                         Category_instance.banner.save('no-image.png', default_image_content)
        #                     else:
        #                         print(f"Failed to download default image from URL: {default_image_url}")

        #                 else:
        #                     # Download and save the image
        #                     image_response = requests.get(banner)
        #                     if image_response.status_code == 200:
        #                         image_filename = banner.split('/')[-1]
        #                         image_content = ContentFile(image_response.content)
        #                         Category_instance.banner.save(image_filename, image_content)
        #                     else:
        #                         print(f"Failed to download image from URL: {banner}")

                        # Download and save the image
                        # image_response = requests.get(banner)
                        # if image_response.status_code == 200:
                        #     image_filename = banner.split('/')[-1]
                        #     image_content = ContentFile(image_response.content)
                        #     Category_instance.banner.save(image_filename, image_content)
                        # else:
                        #     print(f"Failed to download image from URL: {banner}")

            #         except ObjectDoesNotExist:
            #             print(f"Address '{category_name}' does not exist.")
            #             print(f"Address '{name}' does not exist.")
            #             print(f"Address '{slug}' does not exist.")
            #             print(f"Address '{short_description}' does not exist.")
            #             print(f"Address '{description}' does not exist.")
            #             continue

            # url = reverse('admin:product_catalogsubcategory_changelist')
            # return HttpResponseRedirect(url)
        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload_subcategory.html", data)

    actions = ['export_as_csv']  # Add this line to enable the export action

    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="catalog_subcategories.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Category', 'Slug', 'Status', 'Image'])  # Add more fields as needed

        for catalog_subcategory in queryset:
            image_url = catalog_subcategory.banner.url if catalog_subcategory.banner else ""
            writer.writerow([catalog_subcategory.name, catalog_subcategory.category.name, catalog_subcategory.slug, catalog_subcategory.status, image_url])  # Add more fields

        return response

    export_as_csv.short_description = "Export selected catalog subcategories as CSV"  # Set the action description

    def changelist_view(self, request, extra_context=None):

        mutable_get = request.GET.copy()

        # Remove the 'p' parameter from the mutable copy
        # if 'p' in mutable_get:
        #     del mutable_get['p']

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]
        request.GET = mutable_get

        return super().changelist_view(request, extra_context=extra_context)
class BrandFilter(admin.SimpleListFilter):


    title = 'Brand'
    parameter_name = 'brand'  # This should match your search field name

    def lookups(self, request, model_admin):
        # Define the filter options
        unique_Brand = ProductBrand.objects.values('name','id').distinct()
        # unique_categories = CatalogCategory.objects.values('name','id').distinct()

        # Create a list of tuples with (category_id, category_name)
        Brand_choices = [
            (brand['id'], brand['name']) for brand in unique_Brand
        ]

        return Brand_choices

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        selected_option = self.value()
        if selected_option:
            return queryset.filter(Brand=selected_option)
        return queryset

class SubCategoriesFilter(admin.SimpleListFilter):
    title = 'Sub Category'
    parameter_name = 'subcategory'  # This should match your search field name

    def lookups(self, request, model_admin):
        # Define the filter options
        unique_categories = CatalogSubCategory.objects.values('name','id').distinct()
        # unique_categories = CatalogCategory.objects.values('name','id').distinct()

        # Create a list of tuples with (category_id, category_name)
        category_choices = [
            (category['id'], category['name']) for category in unique_categories
        ]
        # return (

        #     ('storeboy', _('Store Boy')),
        #     ('deliveryboy', _('Delivery Boy')),
        #     ('fulfillmentmanager', _('Fullfillment Manager')),
        #     ('storemanager', _('Store Manager')),

        # )

        return category_choices

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        selected_option = self.value()
        if selected_option:
            return queryset.filter(subcategory_id=selected_option)
        return queryset

class CategoriesFilter(admin.SimpleListFilter):
    title = 'Category'
    parameter_name = 'Category'  # This should match your search field name

    def lookups(self, request, model_admin):
        # Define the filter options
        unique_categories = CatalogCategory.objects.values('name','id').distinct()
        # unique_categories = CatalogCategory.objects.values('name','id').distinct()

        # Create a list of tuples with (category_id, category_name)
        category_choices = [
            (category['id'], category['name']) for category in unique_categories
        ]
        # return (

        #     ('storeboy', _('Store Boy')),
        #     ('deliveryboy', _('Delivery Boy')),
        #     ('fulfillmentmanager', _('Fullfillment Manager')),
        #     ('storemanager', _('Store Manager')),

        # )

        return category_choices

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        selected_option = self.value()
        if selected_option:
            return queryset.filter(category_id=selected_option)
        return queryset
from django.db.models import F
from django.forms import Textarea

def convert_line_breaks_to_html(self, text):
        # Convert newline characters to HTML line breaks
        return '<br>'.join(line for line in text.splitlines())
class ProductAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_per_page = 50
    product_count = Product.objects.count()
    search_fields =['product_name','category__name','subcategory__name','Brand__name','sku','price']

    list_display = ('id','image_preview','product_name', 'category','subcategory','Brand', 'sku','price','status','edit_item')
    readonly_fields = ['image_preview']

    inlines = [ProductAdminInline, ProductAdminInlineSeo]

    fieldsets = [
        (None, {"fields": ['product_name', 'category','subcategory','Brand', 'sku','product_tags','tags', 'price','product_description','product_short_description','product_weight','product_image','image_preview','status','product_for']}),
        ]

    list_filter = (CategoriesFilter,SubCategoriesFilter,BrandFilter,)

    def edit_item(self, obj):
        url = reverse("admin:product_product_change", args=[obj.id])
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', url)

               # Define a custom method for the delete icon
    def delete_item(self, obj):
        url = reverse("admin:product_product_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', url)

    # Delete icon method description
    delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')

    # def tag_list(self, obj):
    #     return u", ".join(o.name for o in obj.product_tags.all())
    def display_product_tags(self, obj):
        return ', '.join(obj.get_product_tags())  # Use get_product_tags() method
    display_product_tags.short_description = 'Product Tags'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('product_tags')
    def product_des(self):
        return truncatechars(self.product_description,20)
    def product_picture(self,obj):
        return format_html('<img src="{0}" width="100" />'.format(obj.product_image.url))

    change_list_template = 'admin/product_change_list.html'

    def changelist_view(self, request, extra_context=None):
        mutable_get = request.GET.copy()

        # Remove the 'p' parameter from the mutable copy
        # if 'p' in mutable_get:
        #     del mutable_get['p']

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]
        request.GET = mutable_get

        # Call the superclass method with the modified request
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls

    def upload_csv(self, request):

        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]

            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)

            # Decode the CSV file using UTF-8 encoding
            csv_data = csv_file.read().decode('windows-1252')
            csv_reader = csv.reader(csv_data.splitlines())

            next(csv_reader, None)
            # csv_data = csv_data[1:]
            for fields in csv_reader:

                # fields = x.split(",")
                # print(len(fields), '7890')
                if len(fields) >= 14:
                    product_tags_names = [tag.strip('""') for tag in fields[7].strip().split(',')]
                    product_name = fields[0]
                    name_slug = fields[1].strip()
                    category_name = fields[2].strip()
                    subcategory_name = fields[3].strip()
                    Brand_name = fields[4].strip()
                    sku = fields[5].strip()
                    price = fields[6].strip()
                    product_description = fields[8]
                    product_short_description = fields[9]
                    quantity = fields[10].strip()
                    product_weight = fields[11].strip()
                    product_image = fields[12].strip()
                    status = fields[13].strip()
                    # product_tags_names = [tag.strip() for tag in product_tags_names.split(',')]
                    product_tags_instances = []
                    for tag_name in product_tags_names:
                        product_tag_instance, created = ProductTag.objects.get_or_create(name=tag_name)
                        product_tags_instances.append(product_tag_instance)

                    Product_instance = None
                    try:
                        CatalogCategory_instance = CatalogCategory.objects.get(name=category_name)
                        CatalogSubCategory_instance = CatalogSubCategory.objects.get(name=subcategory_name)
                        ProductBrand_instance = ProductBrand.objects.get(name=Brand_name)

                        short_description = product_short_description.replace('\\n', '\n')
                        short_description_with_tags = "<p>" + "</p><p>".join(short_description.split('\n')) + "</p>"
                        # print(description_with_tags)

                        description = product_description.replace('\\n', '\n')
                        description_with_tags = "<p>" + "</p><p>".join(description.split('\n')) + "</p>"
                        
                        # All filters have exactly one match, proceed with creating the product
                        Product_instance,created= Product.objects.update_or_create(
                            sku=sku,
                            defaults={'product_name': product_name,
                                        'category': CatalogCategory_instance,
                                        'subcategory': CatalogSubCategory_instance,
                                        'Brand': ProductBrand_instance,
                                        'name_slug': name_slug,
                                        'sku': sku,
                                        'price': price if price else 0,
                                        'product_description': description_with_tags,
                                        'product_short_description': short_description_with_tags,
                                        'quantity': quantity if quantity else 0,
                                        'product_weight': product_weight if product_weight else 1,
                                        'status': status,
                                        }

                        )

                        # Product_instance.save()

                        # Add the product_tags_instances to the many-to-many field
                        Product_instance.product_tags.set(product_tags_instances)

                        # Download and save the image
                        # print(image_response)
                        if not product_image:
                            default_image_url = 'https://demo2.1hour.in/media/users/no-image.png'
                            default_image_response = requests.get(default_image_url)

                            if default_image_response.status_code == 200:
                                default_image_content = ContentFile(default_image_response.content)
                                Product_instance.product_image.save('no-image.png', default_image_content)
                            else:
                                print(f"Failed to download default image from URL: {default_image_url}")

                        else:
                            # Download and save the image
                            image_response = requests.get(product_image)
                            if image_response.status_code == 200:
                                image_filename = product_image.split('/')[-1]
                                image_content = ContentFile(image_response.content)
                                Product_instance.product_image.save(image_filename, image_content)
                            else:
                                print(f"Failed to download image from URL: {product_image}")
                    except ObjectDoesNotExist:
                        print(f"Address '{category_name}' categories does not exist.")
                        print(f"Address '{subcategory_name}' Sub categories does not exist.")
                        print(f"Address '{product_name}' product does not exist.")
                        continue


            url = reverse('admin:product_product_changelist')
            return HttpResponseRedirect(url)
        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/product_csv_upload.html", data)

    actions = ['export_as_csv']  # Add this line to enable the export action

    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product Name', 'Category', 'SKU', 'Price', 'Quantity', 'Product Short Description', 'Image'])  # Add more fields as needed

        for product in queryset:
            image_url = product.product_image.url if product.product_image else ""
            writer.writerow([product.product_name, product.category.name, product.sku, product.price, product.quantity, product.product_short_description, image_url])  # Add more fields

        return response

    export_as_csv.short_description = "Export selected products as CSV"  # Set the action description

class ProductTagAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'status','view_all_products','edit_item')


    def view_all_products(self, obj):
        products = Product.objects.filter(product_tags=obj)
        product_count = products.count()
        if product_count > 0:
            url = reverse("admin:product_product_changelist") + f'?product_tags__id__exact={obj.id}'
            return format_html('<a href="{}"> View Products ({})</a>', url, product_count)
        else:
            return "No Products"

    view_all_products.short_description = "All Products"

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if response.status_code == 302 and obj.id:  # Ensure object is saved and has an ID (existing object)
            # Remove the _changelist_filters parameter from the URL
            url = reverse("admin:product_product_changelist")
            return HttpResponseRedirect(url)
        return response

    product_count = ProductTag.objects.count()
    list_per_page = 50
    search_fields =['name']

               # Define a custom method for the delete icon
    def edit_item(self, obj):
        url = reverse("admin:product_producttag_change", args=[obj.id])
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', url)

    def delete_item(self, obj):
        url = reverse("admin:product_producttag_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button" href="{}">Delete</a>', url)

    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv_product_tag, name='product_producttag_upload_csv'),]
        return new_urls + urls

    def changelist_view(self, request, extra_context=None):

        mutable_get = request.GET.copy()
        # Remove the 'p' parameter from the mutable copy
        # if 'p' in mutable_get:
        #     del mutable_get['p']

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]
        request.GET = mutable_get

        return super().changelist_view(request, extra_context=extra_context)

    def upload_csv_product_tag(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]

            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)

            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")

            for x in csv_data:
                fields = x.split(",")
                if len(fields) >= 3:  # Adjust the index based on your data
                    name = fields[0]
                    slug = fields[1].strip()
                    status_value = fields[2].strip()

                    if status_value.isdigit():  # Check if it's a valid integer
                        status = int(status_value)

                        created = ProductTag.objects.update_or_create(
                            name=name,
                            slug=slug,
                            status=status,
                        )


                    else:
                        print("Incomplete data:", fields)

            url = reverse('admin:product_producttag_changelist')
            return HttpResponseRedirect(url)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)

    actions = ['export_as_csv']  # Add this line to enable the export action

    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_tags.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Slug', 'Status'])  # Add more fields as needed

        for product_tag in queryset:
            writer.writerow([product_tag.name, product_tag.slug, product_tag.status])  # Add more fields

        return response

    export_as_csv.short_description = "Export selected product tags as CSV"  # Set the action description

class ImagesAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_images'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_images'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False


    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_images'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False


    def has_delete_permission(self, request, obj=None):
        # user_group_permissions = get_group_permissions(request.user)
        # desired_permission_codename = 'delete_images'
        # if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
        #     return True
        # else:
            return False


    list_display = ('product_image', 'title', 'product','edit_item')

    product_count = Images.objects.count()
    list_per_page = product_count
               # Define a custom method for the delete icon
    def edit_item(self, obj):
        url = reverse("admin:product_images_change", args=[obj.id])
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', url)

    def delete_item(self, obj):
        url = reverse("admin:product_images_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button" href="{}">Delete</a>', url)

    # Delete icon method description
    delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')

class TagAdmin(admin.ModelAdmin):

    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_tag'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False
 
    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_tag'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False
 
    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_tag'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False
 
 
    def has_delete_permission(self, request, obj=None):
        # user_group_permissions = get_group_permissions(request.user)
        # desired_permission_codename = 'delete_producttag'
        # if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
        #     return True
        # else:
            return False
 
 
    list_display = ('name', 'slug', 'status','view_all_products','edit_item')
 
 
    def view_all_products(self, obj):
        products = Product.objects.filter(tags=obj)
        product_count = products.count()
        if product_count > 0:
            url = reverse("admin:product_product_changelist") + f'?tags__id__exact={obj.id}'
            return format_html('<a href="{}"> View Products ({})</a>', url, product_count)
        else:
            return "No Products"
 
    view_all_products.short_description = "All Products"
 
    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if response.status_code == 302 and obj.id:  # Ensure object is saved and has an ID (existing object)
            # Remove the _changelist_filters parameter from the URL
            url = reverse("admin:product_product_changelist")
            return HttpResponseRedirect(url)
        return response
 
    product_count = Tag.objects.count()
    list_per_page = 50
    search_fields =['name']
 
               # Define a custom method for the delete icon
    def edit_item(self, obj):
        url = reverse("admin:product_tag_change", args=[obj.id])
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', url)
 
    def delete_item(self, obj):
        url = reverse("admin:product_tag_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button" href="{}">Delete</a>', url)
 
    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')
 
 
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv_tag, name='product_tag_upload_csv'),]
        return new_urls + urls
 
    def changelist_view(self, request, extra_context=None):
 
        mutable_get = request.GET.copy()
        # Remove the 'p' parameter from the mutable copy
        # if 'p' in mutable_get:
        #     del mutable_get['p']
 
        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page
 
        if extra_context is None:
            extra_context = {}
 
        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]
        request.GET = mutable_get
 
        return super().changelist_view(request, extra_context=extra_context)
 
    def upload_csv_tag(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
 
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
 
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")
 
            for x in csv_data:
                fields = x.split(",")
                if len(fields) >= 3:  # Adjust the index based on your data
                    name = fields[0]
                    slug = fields[1].strip()
                    status_value = fields[2].strip()
 
                    if status_value.isdigit():  # Check if it's a valid integer
                        status = int(status_value)
 
                        created = Tag.objects.update_or_create(
                            name=name,
                            slug=slug,
                            status=status,
                        )
 
 
                    else:
                        print("Incomplete data:", fields)
 
            url = reverse('admin:product_tag_changelist')
            return HttpResponseRedirect(url)
 
        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)
 
    actions = ['export_as_csv']  # Add this line to enable the export action
 
    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_tags.csv"'
 
        writer = csv.writer(response)
        writer.writerow(['Name', 'Slug', 'Status'])  # Add more fields as needed
 
        for product_tag in queryset:
            writer.writerow([product_tag.name, product_tag.slug, product_tag.status])  # Add more fields
 
        return response
 
    export_as_csv.short_description = "Export selected product tags as CSV"  # Set the action description

admin.site.register(CatalogCategory,CatalogCategoryAdmin)
admin.site.register(CatalogSubCategory,CatalogSubCategoryAdmin)
admin.site.register(ProductBrand,ProductBrandAdmin)
admin.site.register(ProductTag,ProductTagAdmin)
admin.site.register(ProductDiscountm,ProductDiscountAdmin)
admin.site.register(DeliveryBoyRating,DeliveryBoyRatingAdmin)
admin.site.register(OrderRating,OrderRatingAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Images,ImagesAdmin)
admin.site.register(Tag,TagAdmin)

# Register your models here.
