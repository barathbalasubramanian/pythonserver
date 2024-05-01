from fastapi import APIRouter, Form
from config import S3, BUCKET_NAME
import json
import os
from typing import Optional

router = APIRouter()


@router.post("/get-names")
async def get_names(eventName: str = Form(...)):
    response = S3.list_objects(Bucket=BUCKET_NAME, Prefix=f'{eventName}/', Delimiter='/')
    actual_result = []
    result = []
    for o in response.get('CommonPrefixes'):
        result.append(o['Prefix'].split('/')[-2])
    
    if "photographers_images" in result: result.remove('photographers_images')
    if "selfie" in result: result.remove("selfie")

    for i in result:
        response = S3.list_objects(Bucket=BUCKET_NAME, Prefix=f'{eventName}/selfie/{i}/')
        keys = [item["Key"] for item in response.get("Contents", []) if "Key" in item]
        for j in keys:
            if 'image' in j:
                signed_url = S3.generate_presigned_url(
                    "get_object", Params={"Bucket": BUCKET_NAME, "Key":j}, ExpiresIn=3600
                )
                actual_result.append({
                    'name':i,
                    'url':signed_url
                })
    return {
        'sucess':actual_result
    }

