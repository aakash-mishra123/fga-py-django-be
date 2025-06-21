from django.db import models
from tinymce.models import HTMLField
from product.models import ProductTag
from autoslug import AutoSlugField
from PIL import Image
from django.utils.html import mark_safe
from accounts.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.html import strip_tags


class HomeBanner(models.Model):
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='title', unique=True, null=True,default=None)
    banner = models.ImageField(upload_to='HomeBanner',max_length=255,null=True,default=None)
    product_tags    =   models.ManyToManyField(ProductTag, blank=True)  # Many-to-many relationship with ProductTag
    default = models.IntegerField(default=None)
    priority = models.IntegerField(default=None)
    content = HTMLField(null=True,default=None,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)

    BANNER_CHOICES = (
        ('', 'select'),
        (1, 'Grocery'),
        (2, 'Restaurant'),
    )
    banner_for = models.SmallIntegerField(choices=BANNER_CHOICES, default=1)

    def clean(self):
        # Check if priority is not negative
        if self.priority < 0:
            raise ValidationError("Priority should not be negative.")

        # Check if default is not negative
        if self.default and self.default < 0:
            raise ValidationError("Default value should not be negative.")

        count_recommended = HomeBanner.objects.filter(default=1).count()

        if self.default > 1 or self.default < 0:
            raise ValidationError("The value of default should be between 0 and 1, inclusive.")
        if self.default == 1 and count_recommended > 0:
            raise ValidationError("There is already a record with  default set to 1.")

    def save(self, *args, **kwargs):
            fields_to_strip = ['title']
            for field_name in fields_to_strip:
                value = getattr(self, field_name, '')
                if isinstance(value, str):  # Check if the value is a string
                    setattr(self, field_name, strip_tags(value))

            self.full_clean()  # Perform model validation before saving
            super().save(*args, **kwargs)



    class Meta:
        verbose_name_plural = "Home Banner"


    def __str__(self):
        return self.title

    def image_preview(self): #new
        return mark_safe(f'<img src = "{self.banner.url}" width = "100"/>')

class OfferBanners(models.Model):
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='title', unique=True, null=True,default=None)
    banner = models.ImageField(upload_to='offerbanners',max_length=255,null=True,default=None)
    product_tags    =   models.ManyToManyField(ProductTag, blank=True)  # Many-to-many relationship with ProductTag

    content = HTMLField(null=True,default=None,blank=True)
    default = models.IntegerField(default=None)
    priority = models.IntegerField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)

    BANNER_CHOICES = (
        ('', 'select'),
        (1, 'Grocery'),
        (2, 'Restaurant'),
    )
    banner_for = models.SmallIntegerField(choices=BANNER_CHOICES, default=1)

    def clean(self):
        if self.status < 0:
            raise ValidationError("Status should not be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run the clean method to validate the status field
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Offers Banner"

    def __str__(self):
        return self.title

    def image_preview(self): #new
        return mark_safe(f'<img src = "{self.banner.url}" width = "100"/>')

    def save(self, *args, **kwargs):
            fields_to_strip = ['title']
            for field_name in fields_to_strip:
                value = getattr(self, field_name, '')
                if isinstance(value, str):  # Check if the value is a string
                    setattr(self, field_name, strip_tags(value))

            self.full_clean()  # Perform model validation before saving
            super().save(*args, **kwargs)


class PrivacyPolicy(models.Model):
    class Meta:
        verbose_name = "Privacy Policy"
        verbose_name_plural = "Privacy Policy"
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='title', unique=True, null=True, default=None)
    content = HTMLField()


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        fields_to_strip = ['title']
        for field_name in fields_to_strip:
            value = getattr(self, field_name, '')
            if isinstance(value, str):  # Check if the value is a string
                setattr(self, field_name, strip_tags(value))

        self.full_clean()  # Perform model validation before saving
        super().save(*args, **kwargs)

class TermsConditions(models.Model):
    class Meta:
        verbose_name = "Terms & Conditions"
        verbose_name_plural = "Terms & Conditions"
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='title', unique=True, null=True, default=None)
    content = HTMLField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        fields_to_strip = ['title']
        for field_name in fields_to_strip:
            value = getattr(self, field_name, '')
            if isinstance(value, str):  # Check if the value is a string
                setattr(self, field_name, strip_tags(value))

        self.full_clean()  # Perform model validation before saving
        super().save(*args, **kwargs)

class FAQ(models.Model):
    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='title', unique=True, null=True, default=None)
    content = HTMLField()

    class Meta:
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        fields_to_strip = ['title']
        for field_name in fields_to_strip:
            value = getattr(self, field_name, '')
            if isinstance(value, str):  # Check if the value is a string
                setattr(self, field_name, strip_tags(value))

        self.full_clean()  # Perform model validation before saving
        super().save(*args, **kwargs)


class Issues(models.Model):
    title = models.TextField(max_length=500)
    issuetype = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)


    class Meta:
        verbose_name_plural = "Issues"

    def __str__(self):
        return self.title    
    
class DeliveryHelps(models.Model):    
    additional_note = models.TextField(max_length=500)   
    issuetype = models.ForeignKey(Issues, on_delete=models.CASCADE)
    type = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('', ''), 
        ('0', 'Pending'),       
        ('1', 'Resolved'),
        
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='0')

    class Meta:
        verbose_name_plural = "Delivery Boy Issues"

    def __str__(self):
        return self.additional_note   
     
    
class Supports(models.Model):
    support_number = models.CharField(max_length=20)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "Support Number"

    def __str__(self):
        return self.support_number


class Notification(models.Model):
    class Meta:
        verbose_name = "Notifications"
        verbose_name_plural = "Notifications"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    order_id = models.CharField(max_length=200,null=True, default=None)
    message = models.TextField()
    order_status = models.IntegerField(default=0)
    notification_for = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    users_group = models.CharField(  # Add the users_group field
        max_length=10,
        choices=(
            ('1', 'Customer'),
            ('2', 'Prime'),
            ('3', 'Non Prime'),
        ),
        default='1',  # Set the default choice if needed
    )

    def __str__(self):
        return self.title

class ContactUs(models.Model):
    class Meta:
        verbose_name_plural = "Contact Us"

    name = models.CharField(max_length=200)
    phone = models.BigIntegerField(
        unique=True,
        blank=False,
        null=False,
        help_text="Phone number"
    )
    another_phone = models.BigIntegerField(
        unique=True,
        blank=False,
        null=False,
        help_text="Another Phone number"
    )
    whatsapp_number = models.BigIntegerField(
        unique=True,
        blank=False,
        null=False,
        help_text="Whatsapp Phone number"
    )
    email= models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        fields_to_strip = ['name']
        for field_name in fields_to_strip:
            value = getattr(self, field_name, '')
            if isinstance(value, str):  # Check if the value is a string
                setattr(self, field_name, strip_tags(value))

        self.full_clean()  # Perform model validation before saving
        super().save(*args, **kwargs)
