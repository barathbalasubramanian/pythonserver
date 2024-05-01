from fastapi import APIRouter, Form, UploadFile
from config import S3, BUCKET_NAME
import json
import os
from typing import Optional

router = APIRouter()


@router.post("/get-data")
async def get_images(
    eventName: str = Form(...),
    name: str = Form(...),
):
    response = S3.get_object(Bucket=BUCKET_NAME, Key=f"{eventName}/selfie/{name}/data.json")[
            "Body"
        ]

    return {"sucess": json.load(response)}