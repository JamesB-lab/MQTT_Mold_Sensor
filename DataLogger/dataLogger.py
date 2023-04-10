#Project documentation for MQTT Mold Detector usign Raspbery Pi Pico W and DHT22 AM203 sensors
#Developed by J Booth April 2023
#This script connects to an AWS hosted database running PostgreSQL
#After connecting to the databse, using paho mqtt we subcrcibe to our MQTT broker to collect JSON data packets
#We then parse the JSON string to create unique variables for humidity, temperature and room and pass into a dictionary
#We use pandas to convert the dictionary to a dataframe and log this data to our SQL server 'MQTTRead'
#The code loops continously, adding new data to the database as it is recieved.


import paho.mqtt.client as mqtt
import pandas as pd
from datetime import datetime
import sqlalchemy
import passwords

####Connect to AWS PostgreSQL database####

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


####Subscribe to AWS IoT Core MQTT Broker####

def on_connect(client, userdata, flags, rc, dummy):
    print(f"Connected with result code {str(rc)}")
    
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("picow/+/TempHumidity")

def on_message(client, userdata, msg):
    
    rawString = msg.payload
    humidity = msg.payload[13:17] #Split the incoming string to return a string numeric of the humidity value
    temperature = msg.payload[34:38] #Split the incoming string to return a string numeric of the temperature value
    topic = msg.topic
    topicSplit = topic.split('/') #Split the incoming string to return the room the sensor is in
    room = topicSplit[1]

    myDict = {'LoggedTime': [datetime.now()], 'Humidity': humidity, 'Temperature': temperature, 'room': room }

    df = pd.DataFrame(myDict)
    df['Humidity'] = df['Humidity'].astype(float) #Cast the string numberic to float64
    df['Temperature'] = df['Temperature'].astype(float) #Cast the string numberic to float64
    print(df) #Print for debugging

    df.to_sql('MQTTRead', con, if_exists='append', index = False) #Write to our SQL database


    



client = mqtt.Client(client_id='JamesMacBook', protocol=mqtt.MQTTv5) #Specifiy client and protocol
client.tls_set(ca_certs= './Certs/AmazonRootCA1.pem',certfile='./Certs/certificate.pem.crt', keyfile='./Certs/private.pem.key', tls_version=2)
#Configure TLS credentials for AWS security
client.on_connect = on_connect
client.on_message = on_message

client.connect("a24kyzcmr4cd4k-ats.iot.eu-west-2.amazonaws.com", 8883, 60) #Connect to client

#Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
#Other loop*() functions are available that give a threaded interface and a manual interface.
client.loop_forever()




