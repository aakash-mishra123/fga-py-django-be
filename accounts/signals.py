# from django.contrib.auth import get_user_model
# from django.utils import timezone

# User = get_user_model()

# def handle_login_failed(mobile):
#     user = User.objects.filter(mobile=mobile).first()
#     print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiii")

#     if user:
#         # Increase the failed login attempts count
#         user.failed_login_attempts += 1
#         user.save()

#         # Check if the user has exceeded the allowed attempts
#         if user.failed_login_attempts >= 3:
#             # Lock the user account
#             user.is_locked = True
#             user.locked_at = timezone.now()
#             user.save()

