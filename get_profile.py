from fastapi import APIRouter, Form
from config import S3, BUCKET_NAME
router = APIRouter()
@router.post("/get-profile")
async def get_names(eventName: str = Form(...),name: str = Form(...)):
    actual_result = []
    response = S3.list_objects(Bucket=BUCKET_NAME, Prefix=f'{eventName}/selfie/{name}/')
    keys = [item["Key"] for item in response.get("Contents", []) if "Key" in item]
    for j in keys:
        if 'image' in j:
            signed_url = S3.generate_presigned_url(
                "get_object", Params={"Bucket": BUCKET_NAME, "Key":j}, ExpiresIn=3600
            )
            actual_result.append({
                'name':name,
                'url': signed_url
            })
    return {
        'sucess':actual_result
    }

