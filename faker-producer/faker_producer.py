"""Produce faker API content to 'faker' kafka topic."""
import asyncio
import configparser
import os
import time
from collections import namedtuple
from kafka import KafkaProducer
from faker import Faker
import json

fake = Faker()

# Context: Registered User with his/her car
def get_registered_user():
    return {
        "username": fake.user_name(),               # String
        "name": fake.name(),                        # String
        "email": fake.ascii_free_email(),           # String
        "phone_number": fake.phone_number(),        # String
        "address": fake.address(),                  # String
        "company": fake.company(),                  # String
        "job": fake.job(),                          # String
        "license_plate": fake.license_plate(),      # String
        "year": fake.year(),                        # Int
        "safe_color_name": fake.safe_color_name()   # String
    }

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 5))

def run():
    iterator = 0
    print("Setting up Faker producer at {}".format(KAFKA_BROKER_URL))
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )

    while True:
        # adding prints for debugging in logs
        print("Sending new faker data iteration - {}".format(iterator))      
        registered_user = get_registered_user()
        producer.send(TOPIC_NAME, value=registered_user)
        print("New faker data sent")
        time.sleep(SLEEP_TIME)
        print("Waking up!")
        iterator += 1


if __name__ == "__main__":
    run()
