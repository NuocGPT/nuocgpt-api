import os
import boto3
from core.constants import AWSConstants

class AWSService:
    def __init__(self) -> None:
        # Set your AWS credentials and region
        self.aws_access_key = AWSConstants.AWS_ACCESS_KEY
        self.aws_secret_key = AWSConstants.AWS_SECRET_ACCESS_KEY
        self.region_name = AWSConstants.REGION_NAME

        # Initialize the S3 client
        self.s3 = boto3.client('s3', aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key, region_name=self.region_name)

    def upload_to_s3(self, local_folder):
        s3_bucket = AWSConstants.S3_BUCKET

        # Iterate through the local files and upload them to S3
        for root, dirs, files in os.walk(local_folder):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_key = os.path.relpath(local_file_path, local_folder).replace('\\', '/')
                self.s3.upload_file(local_file_path, s3_bucket, s3_key)
                print(f'Uploaded {local_file_path} to s3://{s3_bucket}/{s3_key}')

    def download_from_s3(self, local_folder):
        s3_bucket = AWSConstants.S3_BUCKET
        objects = self.s3.list_objects_v2(Bucket=s3_bucket)
        for obj in objects.get('Contents', []):
            s3_key = obj['Key']
            local_file_path = os.path.join(local_folder, os.path.relpath(s3_key))
            
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            self.s3.download_file(s3_bucket, s3_key, local_file_path)
            print(f'Downloaded s3://{s3_bucket}/{s3_key} to {local_file_path}')
