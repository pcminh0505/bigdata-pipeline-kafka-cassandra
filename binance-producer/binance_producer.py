"""Produce binance API content to 'binance' kafka topic."""
import asyncio
import configparser
import os
import time
import json
from collections import namedtuple
from kafka import KafkaProducer
from datetime import datetime
from binance.websocket.spot.websocket_client import SpotWebsocketClient as Client


KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 60))


producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
)

lastUpdate = {"BTCUSDT": 0, "ETHUSDT": 0}

def reformat_msg(res):
    # API Doc: https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams 
    pair = res['s']
    data = res['k']

    startTime = data['t']
    eventTime = datetime.fromtimestamp(startTime / 1e3).timetuple()
    eventTime = time.strftime("%Y-%m-%d %H:%M:%S", eventTime)
    return {
        "datetime": eventTime,
        "pair": pair,
        "open_price": data['o'],
        "close_price": data['c'],
        "high_price": data['h'],
        "low_price": data['l'],
        "volume": data['v'],
        "trades": data['n']
}

def message_handler(message):
    data = message['data']
    stream = message['stream']

    pair = data['s']
    detail = data['k']
    startTime = detail['t']

    if (lastUpdate[str(pair)] < startTime):
        producer.send(TOPIC_NAME, value=reformat_msg(data))
        print("New data from stream", stream, "at", startTime, "was sent!")
        lastUpdate[str(pair)] = startTime
        producer.flush()

my_client = Client()
my_client.start()

my_client.instant_subscribe(
    stream=["btcusdt@kline_1m", "ethusdt@kline_1m"], 
    callback=message_handler,
)
