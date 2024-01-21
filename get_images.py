from fastapi import APIRouter, Form, UploadFile
from config import S3, BUCKET_NAME
import json
import os
from typing import Optional

router = APIRouter()


@router.post("/get-image")
async def get_images(
    eventName: str = Form(...),
    name: str = Form(...),
):
    response = S3.list_objects(Bucket=BUCKET_NAME, Prefix=f"{eventName}/{name}")
    keys = [item["Key"] for item in response.get("Contents", []) if "Key" in item]
    urls = []
    for i in keys:
        signed_url = S3.generate_presigned_url(
            "get_object", Params={"Bucket": BUCKET_NAME, "Key": i}, ExpiresIn=3600
        )
        print("signed_url",signed_url)
        urls.append(signed_url)

    return {"sucess": urls}
