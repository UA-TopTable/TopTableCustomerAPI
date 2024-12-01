import os
import boto3


def send_confirmation_request(reservation,sqs=boto3.client('sqs',region_name='us-east-1'),queue_url=os.getenv("SQS_RESERVATION_RESQUESTS_QUEUE_URL")):
    try:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=str({"reservation":reservation}) #aff as dict if add_reservation() ever stops returning a dict
        )
        return True
    except Exception:
        return False