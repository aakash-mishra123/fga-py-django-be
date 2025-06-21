from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from .cache_utils import cache_result, invalidate_prefix

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @cache_result(timeout=300, key_prefix="model_queryset")
    def get_queryset(self):
        queryset = super().get_queryset()
        # Additional filtering
        return queryset

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Invalidate user-specific cache entries
        user_id = kwargs.get('pk')
        invalidate_prefix(f"user:{user_id}")
        return response