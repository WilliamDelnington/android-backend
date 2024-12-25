import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AndroidAPI.settings')
django.setup()

from api.models import *

def update_objects():
    obj_set = Video.objects.filter(fetchable_url=None)

    for obj in obj_set:
        try:
            videoUniqueId = obj.videoUniqueId
            obj.fetchable_url = f'https://drive.google.com/uc?export=download&id={videoUniqueId}'
            obj.save(update_fields=["fetchable_url"])
            print(f"Update successfully: {videoUniqueId}")
        except Exception as e:
            print(f"Update failed in {videoUniqueId}: {e}")

if __name__ == "__main__":
    update_objects()