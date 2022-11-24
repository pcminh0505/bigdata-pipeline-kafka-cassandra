"""Produce binance API content to 'binance' kafka topic."""
import asyncio
import configparser
import os
import time
import json
from collections import namedtuple
from kafka import KafkaProducer
from datetime import datetime
from binance import AsyncClient, BinanceSocketManager

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 60))

config = configparser.ConfigParser()
config.read('binance_service.cfg')
api_credential = config['binance_api_credential']
api_key = api_credential['api_key']
api_secret = api_credential['api_secret']

producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
)

def reformat_msg(res):
    # API Doc: https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams 
    now = time.localtime()
    eventTime = time.strftime("%Y-%m-%d %H:%M:%S", now)
    
    pair = res['s']
    data = res['k']
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

async def main():
    
    client = await AsyncClient.create(api_key, api_secret)
    bm = BinanceSocketManager(client, user_timeout=60)

    # API Document: https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams 
    # Start socket: https://python-binance.readthedocs.io/en/latest/websockets.html#id3

    # <symbol>@kline_<interval>
    streams = ['btcusdt@kline_1m', 'ethusdt@kline_1m']
    ms = bm.multiplex_socket(streams)

    iterator = 0

    # then start receiving messages
    async with ms as tscm:
        while True:
            res = await tscm.recv()
            producer.send(TOPIC_NAME, value=reformat_msg(res['data']))
            print("New data from stream",res['stream'], "sent!")
            producer.flush()
            iterator += 1
            if (iterator % 2 == 0): 
                print("Sleep for 1 minute...")
                time.sleep(SLEEP_TIME)
                print("Waking up.")

    await client.close_connection()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
