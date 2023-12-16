# Code Version: 1
# Status: Ready to deploy, no issues.
# Preconditions: Ensure that your hardware setup is open to clear sky to get GPS signals. (use power bank to power your RPi)

# Importing required libraries
import RPi.GPIO as GPIO
import smbus2
import bme280
from datetime import datetime
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE
import subprocess
import requests

def gpioSetup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)  # Green LED
    GPIO.setup(27, GPIO.OUT)  # Red LED

# Controlling LED's based on sensor temperature.
def ledControls(temperature):
    # Turn off both LEDs initially
    GPIO.output(17, GPIO.LOW)
    GPIO.output(27, GPIO.LOW)
    if temperature < 30:
        # Turn on green LED if temperature is < 30
        GPIO.output(17, GPIO.HIGH)
    else:
        # Turn on red LED if temperature is > 30
        GPIO.output(27, GPIO.HIGH)

# Updating seriousness based on sensor temperature. 
def tempSeriousness(temperature):
    if temperature < 30:
        return 0
    elif 30 <= temperature < 40:
        return 1
    else:
        return 3

# Configuring the AWS IoT placeholders
def configureAwsIot():
    iot_port = 8883
    iot_endpoint = "xxxx"  # Replace with your AWS IoT endpoint
    iot_client_id = "xxxx"  # Replace with your MQTT client ID
    iot_topic = "icecreamTruckDataLogger/truckData"  # Set your topic structure
    
    # Device certificates
    iot_root_ca_path = "/home/pi/Projects/icecream-truck-solution/AmazonRootCA1.pem" # Replace with your RootCA1.pem path
    iot_private_key_path = "/home/pi/Projects/icecream-truck-solution/bc5b9c3470c652840e3570c6829c446a102add5224d53a796ff3954e15d35177-private.pem.key" # Replace with your private key path
    iot_cert_path = "/home/pi/Projects/icecream-truck-solution/bc5b9c3470c652840e3570c6829c446a102add5224d53a796ff3954e15d35177-certificate.pem.crt" # Replace with your private key path

    myAWSIoTMQTTClient = AWSIoTMQTTClient(iot_client_id)
    myAWSIoTMQTTClient.configureEndpoint(iot_endpoint, iot_port)
    myAWSIoTMQTTClient.configureCredentials(iot_root_ca_path, iot_private_key_path, iot_cert_path)
    return myAWSIoTMQTTClient, iot_topic

def readBme280Data(bus, address, calibration_params):
    bme280_sensor_data = bme280.sample(bus, address, calibration_params)
    return bme280_sensor_data

# Enabling gpsd service as subprocess
def enable_gpsd_service():
    try:
        # Enable and start the gpsd service
        subprocess.run(['sudo', 'systemctl', 'enable', 'gpsd'])
        subprocess.run(['sudo', 'systemctl', 'start', 'gpsd'])

        # Wait for a moment to allow the service to start
        time.sleep(2)

        # Check the service status (for trouble shooting the GPS data)
        #subprocess.run(['sudo', 'systemctl', 'status', 'gpsd'])
    except subprocess.CalledProcessError as e:
        print(f"Error enabling gpsd service: {e.stderr}")
    except Exception as e:
        print(f"An unknown error occurred: {e}")

# Reading latitude and longitude
def readLatLon():
    try:
        session = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)
        while True:
            report = session.next()
            if report['class'] == 'TPV':
                if hasattr(report, 'time'):
                    #print(f'Time: {report.time}')
                    if hasattr(report, 'lat') and hasattr(report, 'lon'):
                        #print(f'Latitude: {report.lat}, Longitude: {report.lon}')
                        return report.lat, report.lon
        return None, None
    except KeyboardInterrupt:
        print('Exiting...')
        return None, None
    finally:
        session.close()

# Reading weather data to understand the nearby weather station condition.
def readApiWeatherdata(apiKey, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apiKey}"
    response = requests.get(url)
    data = response.json()  
    if response.status_code == 200:
        apiTemp_C = round(data['main']['temp'] - 273.15, 2)
        apiHumidity_pc = data['main']['humidity']
        apiPressure_hPa = data['main']['pressure']
        return apiTemp_C, apiHumidity_pc, apiPressure_hPa, None
    else:
        weatherApiStatus = f"Error: {response.status_code}"
        return None, None, None, weatherApiStatus

def main():
    try:
        gpioSetup()
        session = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)

        # Including BME280 address on the I2C bus and creating a bus object
        address = 0x76
        port = 1
        bus = smbus2.SMBus(port)
        calibration_params = bme280.load_calibration_params(bus, address)

        # Including weather API info
        apiKey = "xxxx" # Replace with your API key
        
        # Connecting to AWS IoT
        myAWSIoTMQTTClient, iot_topic = configureAwsIot()
        myAWSIoTMQTTClient.connect()

        # Enabling GPSD services
        enable_gpsd_service()

        while True:

            # Reading the BME280 sensor data
            print("BME280 sensor data status:")
            data = readBme280Data(bus, address, calibration_params)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Round the values to two decimal places
            temperature = round(data.temperature, 2)
            humidity = round(data.humidity, 2)
            pressure = round(data.pressure, 2)
            if temperature is not None and humidity is not None and pressure is not None:
                print("--> Received BME280 sensor data")
            else:
                print("--> Failed to return BME280 sensor data")
            
            # Reading GPS module data
            print("GPS data status:")
            lat, lon = readLatLon()
            if lat is not None and lon is not None:
                print("--> Received GPS data")
            else:
                print("--> Failed to return GPS data")
            
            # Reading ambient data via weather API (https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key})
            print("Ambient conditions data status:")
            if lat is not None and lon is not None:
                apiTemp_C, apiHumidity_pc, apiPressure_kPa, weatherApiStatus = readApiWeatherdata(apiKey, lat, lon)
                if apiTemp_C is not None and apiHumidity_pc is not None and apiPressure_kPa is not None:
                    print("--> Received ambient conditions data from weather API")
                else:
                    print("--> Failed to return weather API data " + weatherApiStatus)
            else:
                print("--> No GPS data available, Skipping API request.")
            
            # Final payload
            payload = {
                "time_local": timestamp,
                "temp_C": temperature,
                "humidity_pc": humidity,
                "pressure_hPa": pressure,
                "ambTemp_C" : apiTemp_C,
                "ambHumidity_pc" : apiHumidity_pc,
                "ambPressure_hPa" : apiPressure_kPa,
                "seriousness": tempSeriousness(temperature),
                "truck_lat": lat,
                "truck_lon": lon
            }
            payload_json = json.dumps(payload)

            # Logging JSON data to terminal before sending to AWS IoT
            print("Final JSON data from Raspberry Pi:")
            print("--> " + payload_json)
            myAWSIoTMQTTClient.publish(iot_topic, payload_json, 1)
            # Logging the details after publishing to AWS IoT
            print(f"Above data published to AWS IoT topic:{iot_topic}")

            # Controlling LEDs based on temperature
            ledControls(temperature)

            # Wait for some time before the next reading
            print("---------------------------------------------------------------------------")
            time.sleep(60)  # Adjust as needed, current setting 60 sec

    #Exception Handling:
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Exiting gracefully.")
    except AWSIoTMQTTClientError:
        print("An error occurred with the AWS IoT client.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Exiting... Cleaning up GPIO settings.")
        GPIO.cleanup()
        myAWSIoTMQTTClient.disconnect()

if __name__ == "__main__":
    main()