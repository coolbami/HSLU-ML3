''
  @file  read_gas_concentration.py
  @brief Obtain gas concentration corresponding to the current environment, output as concentration value
  @n Experimental mode: connect sensor communication pin to the main controller and burn
  @n Experimental phenomenon: view the gas concentration corresponding to the current environment through serial port printing
  @n Communication mode select, DIP switch SEL: 0: I2C, 1: UART
  @n Group serial number         Address in the set
  A0 A1 DIP level    00    01    10    11
  @n 1            0x60  0x61  0x62  0x63
  @n 2            0x64  0x65  0x66  0x67
  @n 3            0x68  0x69  0x6A  0x6B
  @n 4            0x6C  0x6D  0x6E  0x6F
  @n 5            0x70  0x71  0x72  0x73
  @n 6 (Default address group) 0x74  0x75  0x76  0x77 (Default address)
  @n 7            0x78  0x79  0x7A  0x7B
  @n 8            0x7C  0x7D  0x7E  0x7F
  @n I2C address select, default to 0x77, A1 and A0 are grouped into 4 I2C addresses.
  @n             | A0 | A1 |
  @n             | 0  | 0  |    0x74
  @n             | 0  | 1  |    0x75
  @n             | 1  | 0  |    0x76
  @n             | 1  | 1  |    0x77   default i2c address
  @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license     The MIT License (MIT)
  @author      PengKaixing(kaixing.peng@dfrobot.com)
  @version     V2.0
  @date        2021-03-28
  @url         https://github.com/DFRobot/DFRobot_MultiGasSensor
'''
import sys
import os
import time
import json
import paho.mqtt.client as mqtt

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from DFRobot_MultiGasSensor import *

# MQTT Broker (Replace with your broker's IP address or hostname)
MQTT_BROKER = "192.168.1.107"
# MQTT Topic to publish gas concentration readings
MQTT_TOPIC = "zurich/CO"

'''
  ctype=1:UART
  ctype=0:IIC
'''
ctype = 0

if ctype == 0:
    I2C_1 = 0x01  # I2C_1 Use i2c1 interface (or i2c0 with configuring Raspberry Pi) to drive sensor
    I2C_ADDRESS = 0x77  # I2C Device address, which can be changed by changing A1 and A0,
                        # the default address on the terminal board as shipped is 0x74
    gas = DFRobot_MultiGasSensor_I2C(I2C_1, I2C_ADDRESS)
else:
    gas = DFRobot_MultiGasSensor_UART(9600)

def setup():
    # Mode of obtaining data: the main controller needs to request the sensor for data
    while (False == gas.change_acquire_mode(gas.PASSIVITY)):
        print("wait acquire mode change!")
        time.sleep(1)
    print("change acquire mode success!")
    gas.set_temp_compensation(gas.ON)
    time.sleep(1)

def loop():
    try:
        # Gastype is set while reading the gas level. Must first perform a read before
        # attempting to use it.
        con = gas.read_gas_concentration()
        temp = gas.temp
        print(f"Ambient {gas.gastype} concentration: {con:.2f} {gas.gasunits} temp: {temp:.1f}C")
        # Publish gas concentration reading to MQTT broker
        publish_mqtt(con, temp)
    except Exception as e:
        print(f"An error occurred: {e}")

    time.sleep(1)

def publish_mqtt(concentration, temperature):
    # Create a JSON object
    data = {
        "gas_concentration": concentration,
        "temperature": temperature
    }
    json_data = json.dumps(data)

    # Connect to MQTT Broker
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER, 1883, 60)
    # Publish gas concentration to MQTT topic
    client.publish(MQTT_TOPIC, json_data)
    # Disconnect from MQTT Broker
    client.disconnect()

if __name__ == "__main__":
    setup()
    while True:
        loop()
