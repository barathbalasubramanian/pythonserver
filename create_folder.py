from fastapi import APIRouter, Form
from config import S3, BUCKET_NAME
router = APIRouter()
@router.post("/create_folder")
async def get_images(
    folderName: str = Form(...),
):
    S3.put_object(Bucket=BUCKET_NAME, Key=f"{folderName}/photographers_images/")
    return {"sucess": True}
