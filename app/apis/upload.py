import boto3
from flask_restx import Namespace, Resource, fields, Api
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from data.db_secrets import DATABASE_URL
from services.db_service import add_picture, modify_description

S3_BUCKET="iapbucket"
AWS_REGION="us-east-1"

api=Namespace("upload", path="/api/v1/upload", description="Operations to upload pictures and description of the restaurant")

s3_client = boto3.client('s3', region_name=AWS_REGION)

upload_picture_model = api.model('Upload', {
    'file': fields.String(required=True, description="The name of the file to upload", example="Your picture in the format .jpg, .png, etc.")
})

upload_description_model = api.model('Upload', {
    'description': fields.String(required=True, description="The description", example="This is a description")
})

@api.route('/upload_picture')
class ImageUpload(Resource):
    @api.expect(upload_picture_model)
    def post(self):
        """Upload a picture to S3"""
        if 'file' not in request.files:
            return {"message": "No file found in the request"}, 400
        
        
        file = request.files['file']
        restaurant_id = request.form.get('restaurant_id')

        if not restaurant_id:
            return {"message": "No restaurant ID given"}, 400

        if file.filename == '':
            return {"message": "Invalid file name"}, 400
        
        filename = secure_filename(file.filename)

        try:
            # Upload de l'image à S3
            s3_client.upload_fileobj(
                file,
                S3_BUCKET,
                filename,
                ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
            )

            file_url = f"https://{S3_BUCKET}.s3.{S3_BUCKET}.amazonaws.com/{filename}"

            #Fill in the DB with the new image
            add_picture(file_url, restaurant_id)

            return {"message": "File successfully uploaded", "file_url": file_url, "restaurant_id": restaurant_id}, 200

        except (NoCredentialsError, PartialCredentialsError):
            return {"message": "Missing credentials"}, 500
        except Exception as e:
            return {"message": str(e)}, 500


@api.route('/upload_description')
class DescriptionUpload(Resource):
    @api.expect(upload_description_model)
    def post(self):
        description = request.form.get('description')
        restaurant_id = request.form.get('restaurant_id')

        if not restaurant_id:
            return {"message": "No restaurant ID given"}, 400
        if not description : 
            return {"message": "No description given"}, 400
        try:
            #Modify the DB with the new description
            modify_description(description, restaurant_id)
            return {"message": "Description successfully modified", "description":description, "restaurant_id": restaurant_id}, 200
        except Exception as e:
            return {"message": str(e)}, 500
