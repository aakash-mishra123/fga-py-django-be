from django import forms
from product.models import Product
from product.models import ProductTag  # Import only once, if needed
from django.contrib.admin.widgets import FilteredSelectMultiple

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV file')

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_tags_multipul'].queryset = ProductTag.objects.all()


