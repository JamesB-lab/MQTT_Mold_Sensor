from machine import I2C, Pin
from time import sleep
from DHT22 import DHT22
import utime
import time
import network
from umqtt.simple import MQTTClient
import passwords


print("Starting Program")
led = Pin("LED", Pin.OUT)
for i in range(5):
    led.on()
    time.sleep_ms(100)
    led.off()
    time.sleep_ms(100)
    

####Configure WiFi SSID and password####

ssid = passwords.wifiSSID #Update as required for wifi devices
password = passwords.wifiPassword #Update as required for wifi devices

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm = 0xa11140) #Disables Power Save Mode
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
max_wait -= 1
print('waiting for connection...')
utime.sleep(1)

####Handle connection error####

if wlan.status() != 3:
    raise RuntimeError('wifi connection failed')
else:
    print('connected')
    led.on()
status = wlan.ifconfig()
print('ip = ' + status[0])

####AWS Get SSL Parameters####

def get_ssl_params():
    """ Get ssl parameters for MQTT"""
    # These keys must be in der format the keys
    # downloaded from AWS website is in pem format
    keyfile = '/certs/private.der'
    with open(keyfile, 'rb') as f:
        key = f.read()
    certfile = "/certs/certificate.der"
    with open(certfile, 'rb') as f:
        cert = f.read()    
    ssl_params = {'key': key,'cert': cert, 'server_side': False}
    return ssl_params



####Connect to MQTT Broker#####

def connectMQTT():
    client = MQTTClient(client_id=b"Living_Room_Pico", #Change for each new device
    server=b"a24kyzcmr4cd4k-ats.iot.eu-west-2.amazonaws.com", #Change depending on cloud host
    port=8883, #Do not change
    #user=b"living_room_client", #Change depending on cloud host
    #password=b"COmpL3XPa!SSwuRD#", #Change depending on cloud host
    keepalive=10000, #Do not change
    ssl=True, #Do not change
    #ssl_params={'server_hostname':'a24kyzcmr4cd4k-ats.iot.eu-west-2.amazonaws.com'} #Change depending on cloud host
    ssl_params = get_ssl_params()
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

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000) #Initialise pinout
dht22=DHT22(Pin(15,Pin.IN,Pin.PULL_UP)) #Sensor connected GPIO 15 pin on Pico W



try:
    while True:
        T, H = dht22.read()
        measurements = {'Temperature': T, 'Humidity': H}
        print('Temperature: ',T,'°C','Humidity: ',H,'%RH')
        publish(client,'picow/LivingRoom/TempHumidity', measurements) #Change Room for each new device
        time.sleep_ms(10000)
except:
    led.off()
    






