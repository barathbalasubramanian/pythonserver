import boto3

BUCKET_NAME='selife-bucket'
SELFIE_PATH = "/home/ubuntu/selfies"
PHOTOS_PATH = "/home/ubuntu/photographers_images"
OUTPUT_PATH = "/home/ubuntu/output_images"

MIME_TYPE_MAPPING = {
    "image/jpeg": ".jpeg",
    "image/png": ".png",
    "image/jpg":".jpg",
    "image/gif":".gif",
    "image/bmp":".bmp"
}

S3 = boto3.client("s3", region_name='ap-south-1')


def get_dir_name(names : list, name : str):
    if name not in names:
        return name
    else:
        co = 1
        while name+str(co) in names:
            co += 1
        return name+str(co)