from fastapi import APIRouter
from config import S3, BUCKET_NAME
import json
import numpy as np
import io
import face_recognition as fr
import tqdm
import botocore.exceptions
import zipfile
router = APIRouter()

def load_image_from_s3(bucket_name, key):
    response = S3.get_object(Bucket=bucket_name, Key=key)
    image_content = response['Body'].read()
    image = fr.load_image_file(io.BytesIO(image_content))
    return image
def list_objects_in_folder(bucket_name, folder_prefix):
    paginator = S3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=folder_prefix)
    all_objects = []
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                all_objects.append(obj['Key'])
    return all_objects
def ZipFolder(prefix, files, name):
    uniqueFile = list(set(files))
    count = 0
    zippath = prefix + '/Output/' + name + '/Zip/'
    for i in range(0, len(uniqueFile), 50):
        zip_buffer = io.BytesIO()  # Create a new buffer for each batch
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, True) as zipper:
            batch_files = uniqueFile[i:i + 50]  # Get the next batch of files
            for file in batch_files:
                object_key = prefix + '/photographers_images/' + file
                print(object_key)
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
    test_images_encodings = {}
    test_selfie_encodings = {}
    Object = {}

    Photo_encoded_response = S3.get_object(Bucket=BUCKET_NAME, Key=f"{eventName}/Photograph_Encoded.json")
    json_content = Photo_encoded_response['Body'].read().decode('utf-8')
    test_images_encodings = json.loads(json_content)
    prefix = f"{eventName}/COMPRESS_IMAGES"
    # response = S3.list_objects(Bucket=BUCKET_NAME, Prefix=prefix)
    img_keys = list_objects_in_folder(BUCKET_NAME,prefix)
    # img_keys = [item["Key"] for item in response.get("Contents", []) if "Key" in item]
    for img_key in tqdm.tqdm(img_keys):
        img_name = img_key.split('/')[-2]+'/'+img_key.split('/')[-1]
        if not img_name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            continue
        img = load_image_from_s3(BUCKET_NAME, img_key)
        if img_name not in test_images_encodings:
            face_locations = fr.face_locations(img)
            face_encodings = [fr.face_encodings(img, [face_location])[0] for face_location in face_locations]
            test_images_encodings[img_name] = [enc.tolist() for enc in face_encodings]
    json_content = json.dumps(test_images_encodings)
    S3.put_object(Body=json_content, Bucket=BUCKET_NAME, Key=f"{eventName}/Photograph_Encoded.json")


    selfie_encoded_response = S3.get_object(Bucket=BUCKET_NAME, Key=f"{eventName}/Selfie_Encoded.json")
    selfie_json_content = selfie_encoded_response['Body'].read().decode('utf-8')
    test_selfie_encodings = json.loads(selfie_json_content)

    prefix = f"{eventName}/selfie"
    selfie_img_keys = list_objects_in_folder(BUCKET_NAME,prefix)
    # selfie_img_keys = [item["Key"] for item in selfie_response.get("Contents", []) if "Key" in item]
    for img_key in tqdm.tqdm(selfie_img_keys):
        img_name = img_key.split('/')[-1]
        if not img_name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            continue
        img = load_image_from_s3(BUCKET_NAME, img_key)
        nameoffolder = img_key.split('/')[2]
        if nameoffolder not in test_selfie_encodings:
            face_locations = fr.face_locations(img)
            face_encodings = [fr.face_encodings(img, [face_location])[0] for face_location in face_locations]
            test_selfie_encodings[nameoffolder] = [enc.tolist() for enc in face_encodings]

    selfie_json_content = json.dumps(test_selfie_encodings)
    S3.put_object(Body=selfie_json_content, Bucket=BUCKET_NAME, Key=f"{eventName}/Selfie_Encoded.json")
    for target_img_name, encodings in test_images_encodings.items():
        for target_face_encoding in encodings:
            for selfie_img_name, selfie_face_encodings in test_selfie_encodings.items():
                for selfie_face_encoding in selfie_face_encodings:
                    target_face_encoding_np = np.array(target_face_encoding)
                    selfie_face_encoding_np = np.array(selfie_face_encoding)
                    if fr.compare_faces([target_face_encoding_np], selfie_face_encoding_np, tolerance=0.45)[0]:
                        key = selfie_img_name
                        if key not in Object:
                            Object[key] = [target_img_name]
                        else:
                            Object[key].append(target_img_name)  
    for key, value in Object.items():
        selfie_json = json.dumps(value)
        ZipFolder(eventName,value,key)
        S3.put_object(Body=selfie_json, Bucket=BUCKET_NAME, Key=f"{eventName}/Output/{key}/Data.json")
    return True