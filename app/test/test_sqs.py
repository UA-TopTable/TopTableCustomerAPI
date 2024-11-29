from datetime import datetime, timedelta
from random import choice
from string import ascii_letters
import boto3
from moto import mock_aws
import pytest
from services.queue_service import send_confirmation_request
from data.models.Reservation import Reservation

example_reservation=[]

def generate_unique_string(size=10):
    my_list = [choice(ascii_letters) for _ in range(size)] 
    my_str = ''.join(my_list) 
    return my_str 

@pytest.fixture(scope="session",autouse=True)
def setup():
    global example_reservation
    example_reservation=Reservation(user_id=1,restaurant_id=123,dining_table_id=123,reservation_start_time=datetime.now()-timedelta(minutes=30),reservation_end_time=datetime.now()+timedelta(minutes=30),number_of_people=2,status="pending",special_requests="none",reservation_code=generate_unique_string(size=10),created_date=datetime.now(),updated_date=datetime.now())
    yield


@mock_aws
def test_sending_confirmation_request():
    global example_reservation

    sqs = boto3.client('sqs', region_name='us-east-1')
    queue=sqs.create_queue(QueueName='test_queue')
    queue_url=queue['QueueUrl']

    assert send_confirmation_request(example_reservation,sqs,queue_url)