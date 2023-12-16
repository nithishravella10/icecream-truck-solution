
# Ice Cream Truck Solution

This project is developed to monitor and analyze environmental conditions in an ice cream truck during transportation to understand the root cause of ice cream spoilage. It utilizes a Raspberry Pi equipped with sensors, including the BME280 for measuring temperature, humidity, and pressure, and a NEO-6M GPS module for location tracking. Additionally, ambient weather information is obtained from the OpenWeatherMap API. The collected data is seamlessly transmitted to AWS IoT for in-depth analysis, using AWS Lambda, DynamoDB, SNS, and IoT Analytics services. The integration of IoT rules enhanced the project's capability to provide real-time insights and timely alerts, ensuring optimal conditions for ice cream storage during transit.

## Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation and Usage](#installation-and-usage)
- [Issues and Path for Rev2](#Issues-and-Path-for-Rev2)
- [Conclusion](#conclusion)

## Introduction

**Problem:**  
  The ice cream company faces a recurring problem with product spoilage during the daily transportation of its goods using a distribution truck. The issue might be because of several reasons but the company wants to know the root cause to mitigate the spoilage.

**Solution:**  
Implemented a system that deploys sensors for monitoring indoor and outdoor conditions (leveraging open APIs). In case of unforeseen events, such as issues with ice cream storage, the system will generate alerts directed to the driver or manager. Concurrently, the system will enable real-time truck tracking and archive all sensor readings for in-depth analysis aimed at understanding the root cause and further analytical processes.

**Note:** Intermediate knowledge of AWS IoT, Raspberry Pi (RPi), sensors, and electronics is required for this project, as the details of each component are not covered in-depth.

**Architecture:**  
![](https://github.com/nithishravella10/icecream-truck-solution/blob/main/iceCreamTruckArchRev1.png)

## Prerequisites
### Hardware Requirements
- Raspberry Pi. (any model with GPIO pins (non zero), I have used Raspberry Pi Model 3)
- BME280 Sensor.
- u-blox NEO-6M GPS Module.
- 2 LEDs. (Red and green)
- 2 Resistors. (200 ohms each)
- Breadboard and the required number of jumper wires.
- Power Supply. (I have used a power bank for testing)
### Software Requirements
- Latest Raspbian OS installed on your Raspberry Pi. I'll help you to run this project without any additional accessories for Raspberry Pi.
- Ensure you have the AWS Python SDK installed on your Raspberry Pi. Full installation is discussed in [Installation and Usage](#installation-and-usage) section.

## Hardware Setup

#### 1. Raspberry Pi
- **OS:** Install the latest Raspbian OS. Follow this [Install using Imager](https://www.raspberrypi.com/documentation/computers/getting-started.html#raspberry-pi-imager) and use "OS customization" option, enable SSH & VNC in case you want to preconfigure your Raspberry Pi.
- **Power Supply:** Ensure a recommended power supply. Refer to [Raspberry Pi Power Supply Requirements](https://www.raspberrypi.com/documentation/computers/getting-started.html#power-supply).
- **Enable I2C Communication:** In the Raspberry Pi Configuration tool (`sudo raspi-config`), select option 3 and enable I2C.

#### 2. BME280 Sensor
- **GPIO Connections:**
  - VCC to 3.3V
  - GND to Common GND
  - SDA to GPIO2 (Board pin 3) [for I2C]
  - SCL to GPIO3 (Board pin 5) [for I2C]
- **Power Supply:** 3.3V/3.4μA. For more information, refer to [BME280 Datasheet](https://www.bosch-sensortec.com/products/environmental-sensors/pressure-sensors/bmp280/).

#### 3. u-blox NEO-6M GPS Module

- **GPIO Connections:**
  - VCC to 5V
  - GND to Common GND
  - RX to TX pin (GPIO14/ Board pin 8)
  - TX to RX pin (GPIO15/ Board pin 10)
- **Power Supply:** 5V. For detailed specifications, visit [u-blox NEO-6 Series](https://www.u-blox.com/en/product/neo-6-series) and [Neo6M GPS Arduino Tutorial](https://lastminuteengineers.com/neo6m-gps-arduino-tutorial/).

#### 4. LEDs and Resistors
- **Green LED:**  
  - High pin to GPIO17 (Board pin 11)
  - GND to Common GND
  - High pin to GPIO17 (Board pin 11)
  - Other end to a 100-ohm resistor connected to common GND
- **Red LED:**
  - High pin to GPIO27 (Board pin 13)
  - Other end to a 100-ohm resistor connected to common GND
- **Ground Connections:**
   - Connect all GND pins of sensors to a common GND using a breadboard.
#### 5. Ensure proper connections
   - Double-check your wiring to ensure all connections are tight and correct.
   - Confirm that the GPIO pins match the ones specified in the code.
#### My Hardware setup:
![](https://github.com/nithishravella10/icecream-truck-solution/blob/main/iceCreamTruckHardwareSetup.jpg)
## Installation and Usage

1. **Update Packages:**
   Once you complete the hardware setup and connect to the Raspberry Pi, update the packages using `sudo apt update && sudo apt upgrade -y` command to ensure they are at the latest version.

2. **Installing Required Libraries:**  
   - Install [smbus2](https://pypi.org/project/smbus2/) library for I2C communication. (`sudo pip install smbus2`)
   - Install [RPi.bme280](https://pypi.org/project/RPi.bme280/) library for interfacing Bosch BME280 digital sensor module. (`pip install RPi.bme280`)
   - After the above two steps, check with `i2cdetect -y 1` and observe whether you are returned with an address, mostly it is 76, if not modify the script accordingly.

3. **Wether API Setup:**  
   - You are required to create an account at [openweathermap.org](https://home.openweathermap.org/users/sign_up) to generate an API key.
   - Once you generate an API key, wait for some time to receive an activation mail.
   - Now make note of the API key, you are required to insert this in the script.

4. **AWS Account Setup:**
   - Make sure you have a working AWS account. If not, create a free-tier account.
   - Log in with a user account and select a region (use the same region consistently throughout the project; I used Sydney - ap-southeast-2). Ensure the chosen region has all AWS services available.

5. **Install AWS IoT Device SDK (Python):**  
   An essential step is to install the Python SDK on the Raspberry Pi and test if it is running correctly.
   - Go to `AWS IoT > Connect > Connect one device`
   - Complete the mentioned 5 steps to make sure that your device has SDK and can talk with AWS IoT Core. (Tip: use VNC for file transfer)
   - Provide appropriate permissions while creating the thing. This will conclude SDK installation and now you can observe a thing created in `AWS IoT > Manage > Things`.
   - The device name used in this project is "icecreamTruckDataLogger".
   - Once the SDK is set up, proceed to the next step, else troubleshoot.

6. **Create AWS IoT Rules & Resources:**
   - Create a standard table in DynamoDB, and use this in the lambda function to insert an item. (Partition key: `time_local` (String)) 
   - Rule for triggering the Lambda service (ruleForLambda):
      - Choose the AWS action as a Lambda function.
      - Provide a description and assign policies appropriately.
      - Message topic: "icecreamTruckDataLogger/truckData".
      - Basic ingest topic: "$aws/rules/ruleForLambda".
      - In the SQL statement, use `SELECT * FROM 'icecreamTruckDataLogger/truckData'`.
      - Create a Lambda function named "FunctionToStoreTruckData" with the runtime set to Python.
      - The code for the Lambda function is available in `lambdaFunRev1.py` file.
   - Rule for sending data to IoT Analytics services:
      - Follow similar steps as the previous one but choose the IoT Analytics action.
      - Create an IoT Analytics channel and IAM role for this.
   - Create an SNS topic (topicForTemperatureThd):
      - Create a topic and then a subscription in that topic, use email as the protocol, and verify the email to receive mail alerts.

7. **Clone and Run the Project:**
   Open the terminal, and move to a desired directory on your Raspberry Pi to clone this repository:  
   `git clone https://github.com/nithishravella10/icecream-truck-solution`
8. Take some time and review the code and replace the API keys and ARN's of your resources correctly.
9. **Run the Script:** `python3 icecreamTruckRev1.py`
   - Sensor status & JSON data logging in the Raspberry Pi terminal.(used for troubleshooting)  
    ![](https://github.com/nithishravella10/icecream-truck-solution/blob/main/iceCreamTruckTerminalRev1.png)
   - JSON data inserted into DynamoDB.  
    ![](https://github.com/nithishravella10/icecream-truck-solution/blob/main/iceCreamTruckDBRev1.png)
   - Email alert sent via SNS service.  
    ![](https://github.com/nithishravella10/icecream-truck-solution/blob/main/iceCreamTruckMailRev1.png)
11. **Troubleshooting Tips**
   - **Procedure:** Hardware setup > MQTT Broker > Lambda/ IoT Analytics > SNS/ DynamoBD.  
   - **Issue:** Monitor the Raspberry Pi's terminal for error messages or warnings generated by the script.  
     **Solution:** Review the terminal output for any error messages and address them accordingly to resolve script issues.

   - **Issue:** If the script is not running, double-check the connections of sensors, LEDs, and other components.  
     **Solution:** Ensure all components are correctly connected as per the hardware setup. Inspect wires and connections for any faults.

   - **Issue:** API keys and ARNs for AWS services are not correctly replaced in the script.  
     **Solution:** Review the script and replace placeholders with accurate API keys and ARNs obtained from the respective services. Additionally, check if the API can make a request.

   - **Issue:** Required Python libraries (smbus2, RPi.bme280) are not installed, or the I2C address is misconfigured.  
     **Solution:** Install the necessary libraries using the provided commands and verify the correct I2C address (usually 76).
     
   - **Issue:** Other libraries issues.  
     **Solution:** Make sure you have all libraries mentioned in the script.

   - **Issue:** AWS IoT Thing configuration and permissions are incorrect, leading to communication issues.  
     **Solution:** Verify the AWS IoT Thing settings, ensuring proper permissions and policies are assigned.

   - **Issue:** AWS IoT Rules and Resources are misconfigured, affecting topics, actions, or Lambda functions.  
     **Solution:** Review and adjust AWS IoT Rules and Resources setup, ensuring accurate topic names, actions, and Lambda functions.

   - **Issue:** DynamoDB table configuration or Lambda function code may be incorrect, affecting data storage.  
     **Solution:** Review DynamoDB table settings and Lambda function code, ensuring compatibility and correct data handling.

   - **Issue:** AWS IoT Analytics channel or IAM role setup might be misconfigured for data forwarding.
     **Solution:** Inspect and adjust the settings for AWS IoT Analytics channel and IAM role to facilitate accurate data forwarding.

   - **Issue:** Email alerts are not received through SNS topics.
     **Solution:** Check the SNS topic subscription and email verification process. Ensure the recipient's email is correctly verified.

## Issues and Features for Rev2
### Current Features
1. The Raspberry Pi executes the code line by line, taking inputs from the sensors and APIs. Once the inputs are ready, the data is sent to IoT Core in JSON format via the MQTT protocol.
2. When the temperature is normal (<30), the green LED glows. If the temperature is greater than 30, the red LED glows, indicating abnormal temperature.
3. After data is published to IoT Core, the data is sent to DynamoDB. If the data has abnormal values (temperature greater than 35), an email (SNS service) is delivered to the recipient, indicating abnormal temperature.
4. Similarly, a message is sent to IoT Analytics.

### Features for Rev2
1. Implementation of a feature to automatically start the Python script upon powering up the Raspberry Pi.
2. Implementation of a pre-conditioning feature for the sensors. (Research optimal threshold values for all operational sensors.)
3. Implementation of a slave device feature to gather data for the master (RPi). (integration of Zigbee/ Wifi/ Bluetooth protocols to enable short-range wireless communication between sensors and the main controller.
4. Implementation of a feature for logging errors to a text file with timestamps. Ensure the log includes the state data when the vehicle was started and its subsequent behavior.
5. Adding a logic to print in the terminal whether valid data has been received from the sensors or not.
6. Organize the DynamoDB table using a dynamic approach to efficiently store data in the database. Leverage the advantages of NoSQL to optimize data storage and retrieval processes.
7. Addressing the issue where the Lambda function is not invoked if GPS data is invalid. For example, in the current code, if a sensor fails to retrieve a value, it becomes stuck in an infinite loop and does not progress to the next line of code.
8. Performance improvements to enhance the response rate. Currently, it is 4-5 seconds.

## Conclusion
This Ice Cream Truck Solution project presents a foundational solution for monitoring transportation conditions. While the current features may not directly solve the ice cream truck problem, further calibration and the addition of other sensors in the upcoming Rev2 can potentially transform this project into a comprehensive solution offering real-time insights to address the root causes effectively.

If you are interested in collaborating, feel free to fork the repository or create issues to express your interest. Your contributions and ideas are welcome as we work together to enhance and optimize this project.