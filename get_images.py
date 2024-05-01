from fastapi import APIRouter, Form, UploadFile
from config import S3, BUCKET_NAME
import json
import os
from typing import Optional

router = APIRouter()
@router.post("/get-image")
async def get_images(
    eventName: str = Form(...),
    name: Optional[str] = Form(None),
):
    prefix = f"{eventName}/"
    if name:
        prefix += f"{name}"
    response = S3.list_objects(Bucket=BUCKET_NAME, Prefix=prefix)
    # keys = [item["Key"] for item in response.get("Contents", []) if "Key" in item]
    print(response)
    urls = []
    # for i in keys:
    #     for j in ['.png','.jpeg' , '.bmp','.gif','.jpg']:
    #         if j in i:
    #             signed_url = S3.generate_presigned_url(
    #                     "get_object", Params={"Bucket": BUCKET_NAME, "Key":i}, ExpiresIn=3600
    #                 )
    #             urls.append([signed_url,i])

    return {"sucess": urls}
