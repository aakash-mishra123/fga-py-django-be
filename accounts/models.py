from django.db import models
from PIL import Image
# from product.models import Product
from django.utils.html import mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django import forms
from django.core.validators import RegexValidator
#from django.core.validators import MaxLengthValidator
from django.db import models
#from django.contrib.auth.signals import user_logged_in
#from django.dispatch import receiver
#from django.contrib.sessions.models import Session
from django.db.models.signals import pre_save
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from django.utils.html import strip_tags
from django.core.cache import cache
from accounts.cache_utils import invalidate_prefix, invalidate_cache_pattern
import logging

logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, mobile, password=None):
        """
        Creates and saves a User with the given email, password.
        """
        # if not email:
        #     raise ValueError("User must have an email address")
        if not password:
            raise ValueError(_("The password must be set"))


        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            mobile=mobile,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, mobile, password=None):
        """
        Creates and saves a superuser with the given email, password.
        """
        user = self.create_user(
            email,
            password=password,
            full_name=full_name,
            mobile=mobile,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

# Create your models here.
# models.py


class User(AbstractBaseUser, PermissionsMixin):
     # These fields tie to the roles!
    ADMIN = 1
    staff = 2
    EMPLOYEE = 3

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (staff , 'staff'),
        (EMPLOYEE, 'Employee')
    )

    email = models.EmailField(
        verbose_name="Email",
        max_length=40,
        unique=False,
        null=True,
        blank=True
    )
    is_locked = models.BooleanField(default=False)

    full_name = models.CharField(max_length=25)
    mobile = models.CharField(
        # min_length=6,  # Set the desired minimum length
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^(\+)?\d{9,12}$',
                message='Mobile number must contain only numeric digits.',
                code='invalid_mobile_number'
            ),
            MinLengthValidator(limit_value=6, message='Mobile number must be at least 6 characters long.')
        ]
    )
    alternate_mobile = models.CharField(
        # min_length=6,
        max_length=12,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d+$',
                message='Alternate mobile number must contain only numeric digits.',
                code='invalid_mobile_number'
            ),
            MinLengthValidator(limit_value=6, message='Mobile number must be at least 6 characters long.')
        ]
    )
    employee_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    device_id = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(null=True,
            blank=True,
            max_length=1,
            # validators=[
            #     MaxLengthValidator(limit_value=10, message="Ensure this value has at most 10 characters."),  # Custom validation for birth date
            # ]
        )
    profile_image=models.ImageField(
        upload_to="users/profile_images",
        max_length=254, blank=True, null=True
    )
    provider = models.CharField(max_length=500, blank=True, null=True)
    provider_id = models.CharField(max_length=500, blank=True, null=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    skip_prime = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_store_popup = models.BooleanField(default=False)
    is_prime = models.BooleanField(default=False)
    is_store_popup = models.BooleanField(default=False)
    country_code = models.CharField(blank=True, null=True,default=0,max_length =3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    old_mobile = models.CharField(max_length=12, blank=True, null=True)
    old_email = models.CharField(max_length=255, blank=True, null=True)
    vehicle_number = models.CharField(max_length=12, blank=True, null=True)
    vehicle_purchase_date = models.DateField(blank=True, null=True)
    vehicle_name = models.CharField(max_length=15, blank=True, null=True)
    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Unblock'),
        (0, 'Block'),
    )

    status = models.SmallIntegerField( choices=STATUS_CHOICES, default=1)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    objects = UserManager()
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = ["full_name","email"]

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def save(self, *args, **kwargs):
        # Strip HTML tags from string fields before saving
        for field in self._meta.fields:
            if isinstance(field, models.CharField):
                setattr(self, field.name, strip_tags(getattr(self, field.name, '')))
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Clear all user-related caches when user data is updated
        if not is_new:  # Only if updating an existing user to avoid cache ops on new users
            try:
                invalidate_prefix(f"user_{self.pk}")
                invalidate_cache_pattern(f"user_profile_{self.pk}")
                logger.debug(f"Invalidated cache for user {self.pk}")
            except Exception as e:
                logger.error(f"Error invalidating cache for user {self.pk}: {str(e)}")

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_admin


    class Meta:
        permissions = [
            ("can_do_something", "Can Do Something"),
            ("can_view_something", "Can View Something"),
            # Add more custom permissions as needed
        ]

class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    type = models.TextField(max_length=500, blank=True, null=True)
    otp = models.IntegerField(blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(default=0,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class FcmToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GustUser(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class LoginOtp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20)
    otp = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    productId = models.ForeignKey('product.Product', on_delete=models.CASCADE, blank=True, null=True)
    store =models.ForeignKey('stores.Stores', on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    weight = models.CharField(max_length=20,blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    plan_id = models.IntegerField(blank=True, null=True)
    add_tip = models.IntegerField(default=0,blank=True, null=True)
    looking_for = models.IntegerField(default=1,blank=True, null=True)
    delivery_instructions = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class State(models.Model):
    state_name = models.TextField(max_length=500, blank=True, null=True)
    country_id = models.IntegerField(blank=True, null=True)
    country_code = models.TextField(max_length=500, blank=True, null=True)
    country_name = models.TextField(max_length=500, blank=True, null=True)
    state_code = models.TextField(max_length=500, blank=True, null=True)
    latitude = models.TextField(max_length=500, blank=True, null=True)
    longitude = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.state_name

class Cities(models.Model):
    city_name = models.TextField(max_length=500, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    state_code = models.TextField(max_length=500, blank=True, null=True)
    state_name = models.TextField(max_length=500, blank=True, null=True)
    country_code = models.TextField(max_length=500, blank=True, null=True)
    latitude = models.TextField(max_length=500, blank=True, null=True)
    longitude = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city_name

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    house_no = models.TextField(max_length=500, blank=True, null=True)
    bulding_name = models.TextField(max_length=500, blank=True, null=True)
    street_address = models.TextField(max_length=500, blank=True, null=True)
    address = models.TextField(max_length=500, blank=True, null=True)
    address_info = models.TextField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=255,blank=True, null=True)
    contact_number = models.CharField(max_length=255,blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    deafult = models.BooleanField("default",default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def set_future_datetime(self):
        future_time = timezone.now() + timedelta(days=7)
        self.created_at = future_time
        self.save()

    def clean(self):
        if self.deafult:
            # Check if there's already another address set as default
            other_default_addresses = Address.objects.filter(user_id=self.user_id,deafult=True).exclude(pk=self.pk).count()
            if other_default_addresses > 1:
                raise ValidationError("Only one address can be set as default.")
        super(Address, self).clean()

    def save(self, *args, **kwargs):
        # If this address is set as default, unset others as default
        if self.deafult:
            Address.objects.filter(user_id=self.user_id, deafult=True).exclude(pk=self.pk).update(deafult=False)
        
        is_new = self.pk is None
        super(Address, self).save(*args, **kwargs)
        
        # Invalidate address caches when they change
        try:
            invalidate_prefix(f"user_{self.user_id}_addresses")
            invalidate_cache_pattern(f"user_profile_{self.user_id}")
            logger.debug(f"Invalidated address cache for user {self.user_id}")
        except Exception as e:
            logger.error(f"Error invalidating address cache: {str(e)}")

    def __str__(self):
        address= self.bulding_name
        return str(address)


    # def clean(self, *args, **kwargs):
    #     # Check if plan_amount is negative
    #     # Count the number of records with plan_recommanded = 1

    #     counter= self.deafult
    #     print(counter.count())
    #     count_default = Address.objects.filter(deafult=1,user_id=self.user_id).count()

    #     if count_default > 0:
    #         raise ValidationError("Multipile default address set")


class OrderAddress(models.Model):
    order_id = models.ForeignKey(User, on_delete=models.CASCADE ,related_name='order_addresses')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE , related_name='user_addresses')
    house_no = models.TextField(max_length=500, blank=True, null=True)
    bulding_name = models.TextField(max_length=500, blank=True, null=True)
    street_address = models.TextField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=255,blank=True, null=True)
    contact_number = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    deafult = models.BooleanField("default",default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)




    # def clean(self, *args, **kwargs):
    #     # Check if plan_amount is negative
    #     # Count the number of records with plan_recommanded = 1

    #     counter= self.deafult
    #     print(counter.count())
    #     count_default = Address.objects.filter(deafult=1,user_id=self.user_id).count()

    #     if count_default > 0:
    #         raise ValidationError("Multipile default address set")


class PrimeMemberPlan(models.Model):
    PLAN_CHOICES = [
        (0, '0'),
        (1, '1'),
    ]
    plan_amount = models.IntegerField(blank=False, null=True)
    plan_validity = models.CharField(max_length=20,blank=False, null=True)
    plan_text = models.CharField(max_length=255,blank=False, null=True)
    plan_recommanded = models.IntegerField(choices=PLAN_CHOICES,
        blank=False,
        null=True,
        default=0,
        validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ])
    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


    def clean(self, *args, **kwargs):
        # Check if plan_amount is negative
        if self.plan_amount is not None and self.plan_amount < 0:
            raise ValidationError("Plan amount cannot be negative.")
        if self.plan_recommanded is not None and self.plan_recommanded < 0:
            raise ValidationError("Plan plan recommanded cannot be negative.")


        # Count the number of records with plan_recommanded = 1
        count_recommended = PrimeMemberPlan.objects.filter(plan_recommanded=1).count()

        if self.plan_recommanded > 1 or self.plan_recommanded < 0:
            raise ValidationError("The value of plan_recommended should be between 0 and 1, inclusive.")
        if self.plan_recommanded == 1 and count_recommended > 0:
            raise ValidationError("There is already a record with Plan Recommended set to 1.")


    def save(self, *args, **kwargs):
        self.full_clean()  # Perform model validation before saving
        super(PrimeMemberPlan, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.plan_text)

class PlanBenefits(models.Model):
    plan = models.ForeignKey(PrimeMemberPlan, on_delete=models.CASCADE)
    plan_title = models.CharField(max_length=255,blank=False, null=True)
    plan_content = models.CharField(max_length=255,blank=False, null=True)
    prime_discount = models.CharField(max_length=255,blank=False, null=True)
    market_discount = models.CharField(max_length=255,blank=False, null=True)
    free_delivery_order = models.CharField(max_length=255,blank=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plan Benefits"
        verbose_name_plural = "Plan Benefits"

    def __str__(self):
        return str(self.id)

class UserSubscription(models.Model):
    order_id = models.CharField(max_length=255,blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(PrimeMemberPlan, on_delete=models.CASCADE)
    plan_amount = models.IntegerField(blank=True, null=True)
    plan_validity = models.CharField(max_length=255,blank=True, null=True)
    plan_expiredate = models.CharField(max_length=255,blank=True, null=True)

    payment_status = models.IntegerField(blank=True, null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    STATUS_CHOICES = (
        ('', 'select'),
        (1, 'Active'),
        (0, 'Inactive'),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)

class UserCardDeatils(models.Model):
    card_number = models.CharField(max_length=255,blank=True, null=True)
    card_name = models.CharField(max_length=255,blank=True, null=True)
    card_month_year = models.CharField(max_length=255,blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class CountryCode(models.Model):
    country_code = models.IntegerField(blank=True, null=True,default=0)
    country_name = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.country_code < 0:
            raise ValidationError("Country code cannot be a negative number.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Perform model validation before saving
        super(CountryCode, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)



# @receiver(user_logged_in)
# def user_logged_in_handler(sender, request, user, **kwargs):
#     # Invalidate all other sessions for this user
#     Session.objects.filter(usersessions__user=user).delete()

# @receiver(pre_save, sender=get_user_model())
# def user_pre_save_handler(sender, instance, **kwargs):
#     # This will ensure that each user has at most one session.
#     if instance.pk:
#         # Close existing sessions when the user logs in
#         Session.objects.filter(usersessions__user=instance).delete()



class DeviceVersion(models.Model):
    version = models.FloatField(default =0)
    min = models.FloatField(default =0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.id)


