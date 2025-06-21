# product/utils.py

from django.http import JsonResponse
from .models import ProductBrand
import requests
from django.core.files.base import ContentFile

def process_csv_data(csv_data):
    total_rows = len(csv_data)
    processed_rows = 0

    for x in csv_data:
        fields = x.split(",")

        if len(fields) >= 5:  # Adjust the index based on your data
            name = fields[0]
            slug = fields[1].strip()
            image = fields[2].strip()
            content = fields[3].strip()
            status_value = fields[4].strip()

            if status_value.isdigit():  # Check if it's a valid integer
                status = int(status_value)

                ProductBrand_instance, created = ProductBrand.objects.update_or_create(
                    name=name,
                    defaults={'name': name,
                              'slug': slug if slug else '',
                              'content': content if content else '',
                              'status': status,
                              }
                )

                if not image:
                    default_image_url = 'https://demo2.1hour.in/media/users/no-image.png'
                    default_image_response = requests.get(default_image_url)

                    if default_image_response.status_code == 200:
                        default_image_content = ContentFile(default_image_response.content)
                        ProductBrand_instance.image.save('no-image.png', default_image_content)
                    else:
                        print(f"Failed to download default image from URL: {default_image_url}")

                else:
                    # Download and save the image
                    image_response = requests.get(image)
                    if image_response.status_code == 200:
                        image_filename = image.split('/')[-1]
                        image_content = ContentFile(image_response.content)
                        ProductBrand_instance.image.save(image_filename, image_content)
                    else:
                        print(f"Failed to download image from URL: {image}")

            else:
                print("Incomplete data:", fields)

            # Update the progress for each processed row
            processed_rows += 1
            progress_percentage = (processed_rows / total_rows) * 100

    # Return the progress to the caller after processing is complete
    return progress_percentage
