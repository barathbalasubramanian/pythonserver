from fastapi import APIRouter, Form, UploadFile
from config import SELFIE_PATH, MIME_TYPE_MAPPING, S3, BUCKET_NAME, get_dir_name
import json
import os
from typing import Optional

router = APIRouter()


@router.post("/save-selfie")
async def save_selfie(
    selfie: UploadFile,
    eventName: str = Form(...),
    email: Optional[str] = Form(None),
    phno: str = Form(...),
    name: str = Form(...),
):
    extension = MIME_TYPE_MAPPING.get(selfie.content_type, None)
    if not extension:
        return {"error": "Unsupported file type"}

    # check for duplicate names
    response = S3.list_objects(Bucket=BUCKET_NAME, Prefix=f"{eventName}/selfie/")
    keys = [
        item["Key"].split("/")[-2]
        for item in response.get("Contents", [])
        if "Key" in item
    ]
    dir_name = get_dir_name(keys, name)

    image_data = await selfie.read()
    key = f"{eventName}/selfie/{dir_name}"

    S3.put_object(
        Body=image_data,
        Bucket=BUCKET_NAME,
        Key=f"{key}/image{extension}",
        ContentType=selfie.content_type,
    )

    data = {"email": email, "phno": phno, "name": name}

    S3.put_object(
        Body=json.dumps(data),
        Bucket=BUCKET_NAME,
        Key=f"{key}/data.json",
        ContentType=selfie.content_type,
    )
    return {"sucess": "selfie updated"}
