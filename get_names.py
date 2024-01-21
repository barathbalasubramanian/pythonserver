from fastapi import APIRouter, Form
from config import S3, BUCKET_NAME
import json
import os
from typing import Optional

router = APIRouter()


@router.post("/get-names")
async def get_names(eventName: str = Form(...)):
    response = S3.list_objects(Bucket=BUCKET_NAME, Prefix=f'{eventName}/', Delimiter='/')
    result = []
    print(response)
    for o in response.get('CommonPrefixes'):
        result.append(o['Prefix'].split('/')[-2])
    
    if "photographers_images" in result: result.remove('photographers_images')
    if "selfie" in result: result.remove("selfie")
    return {
        'sucess':result
    }

