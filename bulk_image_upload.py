from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from config import S3, BUCKET_NAME, MIME_TYPE_MAPPING
from botocore.exceptions import NoCredentialsError
from typing import Optional,List
router = APIRouter()
def upload_to_s3(file, bucket_name, object_name):
    try:
        S3.upload_fileobj(file.file, bucket_name, object_name)
        return True
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Something went wrong...")


@router.post("/{EventName}")
async def bulk_image_upload(
    EventName: str,
    Image_Files: list[UploadFile]
    # Image_Files: List = Form(...),
):
    S3.put_object(Bucket=BUCKET_NAME, Key=f"{EventName}/photographers_images/")
    print(Image_Files)
    for Files in Image_Files:
        s3_object_name = f"{EventName}/photographers_images/{Files.filename}"
        if not upload_to_s3(Files, BUCKET_NAME, s3_object_name):
            raise HTTPException(status_code=500, detail="Failed to upload one or more files")
    return {"sucess": True}
