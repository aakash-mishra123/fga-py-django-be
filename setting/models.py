from django.db import models

# Create your models here.
class OrderStatus(models.Model):
    class Meta:
        verbose_name_plural = "Order Status"

    title = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Report(models.Model):
    class Meta:
        verbose_name_plural = "All Reports"

    title = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title