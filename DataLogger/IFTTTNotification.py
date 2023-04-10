#Project documentation for MQTT Mold Detector usign Raspbery Pi Pico W and DHT22 AM203 sensors
#Developed by J Booth April 2023
#This script reads data from our AWS hosted database an returns the average temperature and humidity within the past hour
#These values are passed to if/else logic to determine if conditions are met to trigger a mold growth warning
#If true to script runs a curl command to send a push notification via IFTTT app 
#https://maker.ifttt.com/trigger/Notify/json/with/key/dVGiOllK5fPN-mo5A_6K7J


import pandas as pd
import sqlalchemy
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



####Create while loop####
####SQLAlchemy returns data from the DB within the past hour and groups by room
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

    for index, row in data.iterrows(): #We use a for loop to itterate over the dataframes rows to give us values for each room
        print(row['avg_temp'], row['avg_hum'], row['room'])
        temp = row['avg_temp']
        humidity = row['avg_hum']
        room = row['room']



        if temp >= 15.5 and temp <18.3 and humidity >= 72:
            os.system('curl -X POST -H "Content-Type: application/json" -d \'{"value1":"'+room+'"}\' https://maker.ifttt.com/trigger/Notify/with/key/dVGiOllK5fPN-mo5A_6K7J')

        elif temp >= 18.3 and temp <21.1 and humidity >= 70:
            os.system('curl -X POST -H "Content-Type: application/json" -d \'{"value1":"'+room+'"}\' https://maker.ifttt.com/trigger/Notify/with/key/dVGiOllK5fPN-mo5A_6K7J')

        elif temp >= 21.1 and temp <23.9 and humidity >= 66:
            os.system('curl -X POST -H "Content-Type: application/json" -d \'{"value1":"'+room+'"}\' https://maker.ifttt.com/trigger/Notify/with/key/dVGiOllK5fPN-mo5A_6K7J')

        elif temp >= 23.9 and temp <26.7 and humidity >= 65:
            os.system('curl -X POST -H "Content-Type: application/json" -d \'{"value1":"'+room+'"}\' https://maker.ifttt.com/trigger/Notify/with/key/dVGiOllK5fPN-mo5A_6K7J')

        elif temp >= 26.7 and temp <29.4 and humidity >= 65:
            os.system('curl -X POST -H "Content-Type: application/json" -d \'{"value1":"'+room+'"}\' https://maker.ifttt.com/trigger/Notify/with/key/dVGiOllK5fPN-mo5A_6K7J')

        elif humidity >= 80:
            os.system('curl -X POST -H "Content-Type: application/json" -d \'{"value1":"'+room+'"}\' https://maker.ifttt.com/trigger/Notify/with/key/dVGiOllK5fPN-mo5A_6K7J')
            
    
    time.sleep(3600) #Delay for 1 hour to prevent spamming of push notifications and allow sensor values to reset
