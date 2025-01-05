import os
import django
from yt_dlp import YoutubeDL
from django.conf import settings
from api.utils import upload_file, delete_specific_file
import traceback
from PIL import Image
import threading

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

def setup_url_images(url, videoId):
    video = Video.objects.filter(id=videoId)
    if video.exists():
        if url.startswith('https://www.youtube.com'):
            ydl_opts = {
                'skip_download': True,
                'quiet': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                thumbnail_url = info_dict.get("thumbnail")

            file_path = os.path.join(settings.BASE_DIR, 'Images')
            file_name = f'thumbnail-for-{videoId}.jpg'

            old_full_path = os.path.join(file_path, file_name)

            thumbnail_opts = {
                'writethumbnail': True,
                'outtmpl': os.path.join(file_path, file_name),
            }

            with YoutubeDL(thumbnail_opts) as thydl:
                thydl.download([url])
                print(f"download complete: {thumbnail_url}")

            webp_file = Image.open(os.path.join(file_path, f'thumbnail-for-{videoId}.jpg.webp'))
            if os.path.exists(old_full_path):
                os.remove(old_full_path)
            webp_file.save(os.path.join(file_path, file_name), 'JPEG')

            print(os.path.join(file_path, file_name))

            try:
                image_id = upload_file(os.path.join(file_path, file_name), file_name, 'image/jpeg')
                for vid in video:
                    vid.thumbnailImageUrl = f'https://drive.google.com/file/d/{image_id}/view'
                    vid.thumbnailImageFetchableUrl = f'https://drive.google.com/uc?export=download?id={image_id}'
                    vid.save(update_fields=['thumbnailImageUrl', 'thumbnailImageFetchableUrl'])

                os.remove(os.path.join(file_path, file_name))
                os.remove(os.path.join(file_path, f'thumbnail-for-{videoId}.jpg.webp'))
                print("Upload and save successfully")

            except:
                print(f"An error occured in {videoId}: {traceback.format_exc()}")
            
    else:
        print("No object returned")

def setup_fetchable_urls():
    try:
        videos = Video.objects.all()
        for video in videos:
            id = video.videoUniqueId
            thumbnailImageFetchableUrl = video.thumbnailImageFetchableUrl
            imageId = thumbnailImageFetchableUrl.split("=")[-1].split("/")[-1]
            video.thumbnailImageFetchableUrl = f'fetch/{imageId}'
            video.fetchable_url = f'fetch/{id}'
            video.thumbnailImageId = imageId
            video.save(update_fields=["fetchable_url", "thumbnailImageFetchableUrl", "thumbnailImageId"])
            print(f"Update {id} successfully.")

        print("Update successfully.")
    except Exception as e:
        print(e)

def fixup_damaging_files(i):
    def fixing_object(id):
        try:
            video = Video.objects.get(id=id)
            thumbnailImageId = video.thumbnailImageId

            file_path = os.path.join(settings.BASE_DIR, 'Images')
            file_name = f"thumbnail_image_{id}.png"
            if not os.path.exists(os.path.join(file_path, file_name)):
                file_name = f"thumbnail_image_{id}.jpg"
            if not os.path.exists(os.path.join(file_path, file_name)):
                print(f"Path does not exist: {file_name}")
            
            delete_specific_file(thumbnailImageId)
            imageId = upload_file(os.path.join(file_path, file_name), f"thumbnail_image_{id}.jpg", "image/jpeg")
            video.thumbnailImageUrl = f"https://drive.google.com/file/d/{imageId}/view"
            video.thumbnailImageFetchableUrl = f"fetch/{imageId}"
            video.thumbnailImageId = imageId
            video.save(update_fields=["thumbnailImageId", "thumbnailImageUrl", "thumbnailImageFetchableUrl"])

            print(f"Successfully update object {id}, visit the site https://android-backend-tech-c52e01da23ae.herokuapp.com/videos/{id} to see the changes")
        except Exception as e:
            print(f"Error in id {id}: {traceback.print_exc()}")

    fixing_object(i)

if __name__ == "__main__":
    fixup_damaging_files(36)