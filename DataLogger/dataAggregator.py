#Project documentation for MQTT Mold Detector usign Raspbery Pi Pico W and DHT22 AM203 sensors
#Developed by J Booth April 2023
#This script connects to the MQTTRead table and returns summary statistics of the sensor data
#The summary statistics are passed into a second table 'TrendAnalysis' for use in a later project
#Using SQLAlchemy we then clean up our MQTTRead table which adds a new row approimately every 10 seconds
#We use DELETE FROM function to free up space in the MQTTRead table and prevent the table from growing infinitely


import pandas as pd
import sqlalchemy
import passwords
import time

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

####Create while loop####

while True:
    #Select data from MQTTRead within the past hour and create summary statistics, return a pandas dataframe
    data = pd.read_sql(""" 
                        SELECT MIN("LoggedTime") AS starttime, MAX("LoggedTime") AS endtime,
                        COUNT(*) AS measurements_count,
                        AVG("Temperature") AS avg_temp,
                        MIN("Temperature") AS min_temp,
                        MAX("Temperature") AS max_temp,
                        STDDEV("Temperature") AS std_dev_temp,

                        AVG("Humidity") AS avg_humidity,
                        MIN("Humidity") AS min_humidity,
                        MAX("Humidity") AS max_humidity,
                        STDDEV("Humidity") AS std_dev_humidity,

                        room 
                        FROM "MQTTRead"

                        WHERE "LoggedTime" >= (now() AT time ZONE 'utc') - INTERVAL '30 minutes'

                        GROUP BY room
                        ;
                        """, 
    con)

    print(data)

    df = pd.DataFrame(data)
    df.to_sql('TrendAnalysis', engine, if_exists='append', index = False) #Write to our SQL database
    

    #Remove data that is 1 day old from MQTT database
    with engine.connect() as con2:

        cleanUp = con2.execute(sqlalchemy.text("""DELETE FROM "MQTTRead" 
                                                    WHERE "LoggedTime" < (now() AT time ZONE 'utc') - INTERVAL '1 DAY' 
                                                    RETURNING *"""))
        
        con2.commit()

        #Returing * returns the to be deleted rows in our SQL statement 
        #con2.commit() needed to commit the change to database
    
    time.sleep(1800)
