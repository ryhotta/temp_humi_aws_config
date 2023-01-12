from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import RPi.GPIO as GPIO
import dht11
import time
import datetime
from datetime import datetime
from zoneinfo import ZoneInfo

myMQTTClient = AWSIoTMQTTClient("raspi-zero")

myMQTTClient.configureEndpoint("aws-endpoint.region.amazonaws.com", 443)
myMQTTClient.configureCredentials("../../../cert/AmazonRootCA1.pem", "../../../cert/XXXXXXXX-private.pem.key", "../../../cert/XXXXXXX-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)

myMQTTClient.connect()
print ("Connected to AWS IoT")

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BOARD)

# read data using pin 7
instance = dht11.DHT11(pin=7)

# datetime
def expireEncoda(object):
    if isinstance(object, datetime):
        return object.isoformat()

try:
        while True:
            result = instance.read()
            if result.is_valid() and result.temperature >= 5.0:

                print("Temperature: %-3.1f C" % result.temperature)
                print("Humidity: %-3.1f %%" % result.humidity)
                print("=====================")

                now = datetime.now(ZoneInfo("Asia/Tokyo"))

                dict = {"timestamp": now , "clientid":"raspi001" , "Temperature":(result.temperature) , "Humiditumidity":(result.humidity)}

                myMQTTClient.publish("topic/temp" , json.dumps(dict , default=expireEncoda) , 0)

            elif result.is_valid() and result.temperature < 5.0:

                print("低温注意")
                print("Temperature: %-3.1f C" % result.temperature)
                print("Humidity: %-3.1f %%" % result.humidity)
                print("=====================")

                now = datetime.now(ZoneInfo("Asia/Tokyo"))

                dict2 = {"timestamp": now , "clientid":"raspi001" , "Temperature":(result.temperature) , "Humiditumidity":(result.humidity)}

                myMQTTClient.publish("topic/temp/alert" , json.dumps(dict2 , default=expireEncoda) , 0)

            time.sleep(1800)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()
