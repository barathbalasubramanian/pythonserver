from fastapi import APIRouter
from config import S3, BUCKET_NAME
import json
import numpy as np
import io
import face_recognition as fr
import tqdm
import botocore.exceptions
import boto3
import zipfile
router = APIRouter()
def ZipFolder(prefix, files):
    uniqueFile = list(set(files))
    count = 0
    zippath = prefix + '/Favourites/'
    if zip_folder_exists(zippath):
        return zippath

    existing_zip_files = get_existing_zip_files(zippath)
    
    for i in range(0, len(uniqueFile), 50):
        if "Photos_"+str(count-1)+'.zip' in existing_zip_files:
            count += 1
        else:
            zip_buffer = io.BytesIO()  # Create a new buffer for each batch
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, True) as zipper:
                batch_files = uniqueFile[i:i + 50]  # Get the next batch of files
                for file in batch_files:
                    file = file.split("/")[-2]+'/'+file.split("/")[-1];
                    object_key = prefix + '/photographers_images/' + file
                    try:
                        infile_object = S3.get_object(Bucket=BUCKET_NAME, Key=object_key)
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == 'NoSuchKey':
                            print(f"Skipping {object_key} as it does not exist.")
                            continue
                        else:
                            raise
                    infile_content = infile_object['Body'].read()
                    zipper.writestr(file, infile_content)
            S3.put_object(Bucket=BUCKET_NAME, Key=zippath + 'Photos_' + str(count) + '.zip', Body=zip_buffer.getvalue())
            count += 1

def zip_folder_exists(zippath):
    try:
        S3.head_object(Bucket=BUCKET_NAME, Key=zippath)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise

def get_existing_zip_files(zippath):
    # Get existing zip files in the zip folder
    try:
        response = S3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=zippath)
        existing_files = [obj['Key'].split('/')[-1] for obj in response.get('Contents', []) if obj['Key'].endswith('.zip')]
        return existing_files
    except botocore.exceptions.ClientError as e:
        raise


@router.get("/{eventName}")
async def face_match(
    eventName: str
):
    Photo_encoded_response = S3.get_object(Bucket=BUCKET_NAME, Key=f"{eventName}/Favorites.json")
    json_content = Photo_encoded_response['Body'].read().decode('utf-8')
    key = json.loads(json_content)
    ZipFolder(eventName,key)
    return True