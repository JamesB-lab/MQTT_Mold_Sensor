#https://maker.ifttt.com/trigger/Notify/json/with/key/dVGiOllK5fPN-mo5A_6K7J

import paho.mqtt.client as mqtt
import pandas as pd
from datetime import datetime
import sqlalchemy
import requests
from Certs import passwords



####Connect to DB####

def init_connection_engine():
    engine = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername='postgresql+pg8000',
            username=passwords.postgresUN,
            password=passwords.postgresPW,
            database='mqtt_read',
            host='mqttread.chur0am9fav5.eu-west-2.rds.amazonaws.com',
        ),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800,
    )
    return engine

engine = init_connection_engine()

con = engine.connect()

while True:
    data = pd.read_sql("""SELECT * FROM public."MQTTRead" m ORDER BY "LoggedTime" DESC LIMIT 2;""", con)

    # print(data)

    temp = data.loc[:, 'Temperature'].mean()
    print(f'Average Temperature: {temp}')
    humidity = data['Humidity'].mean()
    print(f'Average Humidity {humidity}')
    # room = data['room']
    # print (f'Room: {room}')

    if temp >= 20 and humidity >= 50:
        requests.post("https://maker.ifttt.com/trigger/Notify/json/with/key/dVGiOllK5fPN-mo5A_6K7J")
        break






