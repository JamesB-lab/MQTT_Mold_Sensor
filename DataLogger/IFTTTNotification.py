#https://maker.ifttt.com/trigger/Notify/json/with/key/dVGiOllK5fPN-mo5A_6K7J

import paho.mqtt.client as mqtt
import pandas as pd
from datetime import datetime
import sqlalchemy
import requests
import passwords
import os
import time



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
    data = pd.read_sql(""" 
                        SELECT AVG("Temperature") AS avg_temp, AVG("Humidity") AS avg_hum, room 
                        FROM "MQTTRead"
                        WHERE "LoggedTime" >= (now() AT time ZONE 'utc') - INTERVAL '1 hour'
                        GROUP BY "room" 
                        ORDER BY "room" 
                        ;
                        """, 
    con)

    print(data)

    for index, row in data.iterrows():
        print(row['avg_temp'], row['avg_hum'], row['room'])
        temp = row['avg_temp']
        humidity = row['avg_hum']
        room = row['room']



        if temp >= 20 and humidity >= 45:
            os.system('curl -X POST -H "Content-Type: application/json" -d \'{"value1":"'+room+'"}\' https://maker.ifttt.com/trigger/Notify/with/key/dVGiOllK5fPN-mo5A_6K7J')
            #requests.post("https://maker.ifttt.com/trigger/Notify/json/with/key/dVGiOllK5fPN-mo5A_6K7J", data)
    
    time.sleep(3600) #Delay for 1 hour






    # temp = data.loc[:, 'Temperature'].mean()
    # print(f'Average Temperature: {temp}')
    # humidity = data['Humidity'].mean()
    # print(f'Average Humidity {humidity}')
    # #print(data)
    # room = data.iloc[0]['room']
    # # print (f'Room: {room}')