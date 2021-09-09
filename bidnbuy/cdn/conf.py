import os

AWS_ACCESS_KEY_ID=os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME="bidder-django"
AWS_S3_ENDPOINT_URL="https://fra1.digitaloceanspaces.com"

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

AWS_LOCATION="https://bidder-django.fra1.cdn.digitaloceanspaces.com"

DEFAULT_FILE_STORAGE="bidnbuy.cdn.backends.MediaRootS3Boto3Storage"
STATICFILES_STORAGE="bidnbuy.cdn.backends.StaticRootS3Boto3Storage"