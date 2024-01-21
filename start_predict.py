from fastapi import APIRouter, Form, UploadFile
from config import SELFIE_PATH, PHOTOS_PATH, S3, BUCKET_NAME, OUTPUT_PATH
import os
from face_recognition_process import face_recognition_process
router = APIRouter()

@router.post("/start-predict")
async def start_predict(
    eventName: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
):
    # Check for valid username and password
    valid_credentials = (
        name.lower() == "farzin"
        and password == "JAyCbmLmxwjjExvxNnofLBLUCdD4apH3ADsWQswXz7cGq3xuxFWGAn7TM4kTcJN"
    )
    
    if not valid_credentials:
        return {"failure": "Invalid username/password"}

    # Create selfie and photos folders
    selfie_folder_path = f"{SELFIE_PATH}/{eventName}/"
    os.makedirs(selfie_folder_path, exist_ok=True)
    
    photos_path = f"{PHOTOS_PATH}/{eventName}"
    os.makedirs(photos_path, exist_ok=True)

    # Download selfie images from S3
    download_s3_images(BUCKET_NAME, f"{eventName}/selfie/", selfie_folder_path)

    # Download photographer images from S3
    download_s3_images(BUCKET_NAME, f"{eventName}/photographers_images/", photos_path)

    # # Create output folder
    output_path = f"{OUTPUT_PATH}/{eventName}"
    os.makedirs(output_path, exist_ok=True)
    print(output_path)
    # Run face recognition process
    face_recognition_process(selfie_folder_path, photos_path, output_path)

    # Upload results back to S3
    upload_s3_results(BUCKET_NAME, output_path, eventName)

    return {"success": "prediction done"}


def download_s3_images(bucket, prefix, local_path):
    response = S3.list_objects(Bucket=bucket, Prefix=prefix)
    keys = [item["Key"] for item in response.get("Contents", []) if "Key" in item]
    print(keys)
    print(local_path)

    for key in keys:
        if key.endswith('.json'): continue
        try:
            if key.find('selfie') != -1:
                img_name = key.split('/')[-1]
                name = key.split('/')[-2]
                image_ext = img_name.split('.')[-1]
                S3.download_file(bucket, key, f"{local_path}/{name}.{image_ext}")
            else:
                img_name = key.split('/')[-1]
                S3.download_file(bucket, key, f"{local_path}/{img_name}")
        except:
            continue



def upload_s3_results(bucket, output_path, event_name):
    dirs = os.listdir(output_path)
    for dir_name in dirs:
        for image in os.listdir(os.path.join(output_path, dir_name)):
            local_file_path = os.path.join(output_path, dir_name, image)
            s3_key = f"{event_name}/{dir_name}/{image}"
            with open(local_file_path, "rb") as f:
                S3.upload_fileobj(f, BUCKET_NAME, s3_key)
