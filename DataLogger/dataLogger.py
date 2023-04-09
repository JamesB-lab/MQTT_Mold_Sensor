import paho.mqtt.client as mqtt
import pandas as pd
from datetime import datetime
import sqlalchemy
from Certs import passwords


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




def on_connect(client, userdata, flags, rc, dummy):
    print(f"Connected with result code {str(rc)}")
    

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("picow/+/TempHumidity")

def on_message(client, userdata, msg):
    
    rawString = msg.payload
    humidity = msg.payload[13:17]
    #print(humidity)
    temperature = msg.payload[34:38]
    #print(temperature)
    topic = msg.topic
    topicSplit = topic.split('/')
    print(topicSplit)
    room = topicSplit[1]
    print(room)

    myDict = {'LoggedTime': [datetime.now()], 'Humidity': humidity, 'Temperature': temperature, 'room': room }
    #print(myDict)

    df = pd.DataFrame(myDict)
    df['Humidity'] = df['Humidity'].astype(float)
    df['Temperature'] = df['Temperature'].astype(float)
    print(df)
    print(df.shape)
    print(df.dtypes)

    df.to_sql('MQTTRead', con, if_exists='append', index = False)


    



client = mqtt.Client(client_id='JamesMacBook', protocol=mqtt.MQTTv5)
client.tls_set(ca_certs= './Certs/AmazonRootCA1.pem',certfile='./Certs/certificate.pem.crt', keyfile='./Certs/private.pem.key', tls_version=2)
client.on_connect = on_connect
client.on_message = on_message

client.connect("a24kyzcmr4cd4k-ats.iot.eu-west-2.amazonaws.com", 8883, 60)




# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()




