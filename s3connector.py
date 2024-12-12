import os
import boto3
from dotenv import load_dotenv


def uploadFileToS3(filename):

    load_dotenv()

    s3 = boto3.resource(
            service_name='s3',
            region_name='eu-west-3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    s3.Bucket(os.getenv("BUCKET_NAME")).upload_file(Filename=f"results/{filename}", Key=f"scrapping-input/{filename}")

