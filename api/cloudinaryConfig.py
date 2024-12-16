import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config( 
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"), # Click 'View API Keys' above to copy your API secret
    secure=True
)

def upload_video_to_cloudinary(input_url):
    res = cloudinary.uploader.upload_large(input_url, resource_type='video')
    video_secure_url = res["secure_url"]
    return video_secure_url

print(upload_video_to_cloudinary("Videos/videotest.mp4"))