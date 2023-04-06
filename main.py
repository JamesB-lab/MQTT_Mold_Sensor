from machine import I2C, Pin
from time import sleep
from DHT22 import DHT22
import utime
import time
import network
from umqtt.simple import MQTTClient


print("Starting Program")
led = Pin("LED", Pin.OUT)
for i in range(5):
    led.on()
    time.sleep_ms(100)
    led.off()
    time.sleep_ms(100)


####Configure WiFi SSID and password####

ssid = "SSID"  # Update as required for wifi devices
password = "Password"  # Update as required for wifi devices

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm=0xa11140)  # Disables Power Save Mode
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
max_wait -= 1
print('waiting for connection...')
utime.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('wifi connection failed')
else:
    print('connected')
    led.on()
status = wlan.ifconfig()
print('ip = ' + status[0])


####Connect to MQTT Broker#####

def connectMQTT():
    client = MQTTClient(client_id=b"living_room_raspberrypi_picow",  # Change for each new device
                        server=b"51b0b84080d54258ac9a54366aca2c4d.s2.eu.hivemq.cloud",  # Change depending on cloud host
                        port=0,  # Do not change
                        user=b"living_room_client",  # Change depending on cloud host
                        password=b"Password",  # Change depending on cloud host
                        keepalive=7200,  # Do not change
                        ssl=True,  # Do not change
                        ssl_params={'server_hostname': '51b0b84080d54258ac9a54366aca2c4d.s2.eu.hivemq.cloud'}  # Change depending on cloud host
                        )

    client.connect()
    return client


####MQTT Publish#####

def publish(client, topic, value):
    print(topic)
    print(value)
    client.publish(topic, str(value))
    print("publish Done")


client = connectMQTT()


####Sensor Programming####

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)  # Initialise pinout
dht22 = DHT22(Pin(15, Pin.IN, Pin.PULL_UP))  # Sensor connected GPIO 15 pin on Pico W


try:
    while True:
        T, H = dht22.read()
        print('Temperature: ', T, '°C', 'Humidity: ', H, '%RH')
        publish(client, 'picow/temperature', T)
        publish(client, 'picow/humidity', H)
        time.sleep_ms(500)
except:
    led.off()
