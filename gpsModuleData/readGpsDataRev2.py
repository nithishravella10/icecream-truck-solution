# This piece of code is to troubleshoot GPS module
# Rev2- Added a feature for enabling and starting the gpsd in the code itself 
# Prints time, lat, long and reports of gpsd

from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE
import time
import subprocess

def enable_gpsd_service():
    try:
        # Enable and start the gpsd service
        subprocess.run(['sudo', 'systemctl', 'enable', 'gpsd'])
        subprocess.run(['sudo', 'systemctl', 'start', 'gpsd'])

        # Wait for a moment to allow the service to start
        time.sleep(2)

        # Check the service status
        subprocess.run(['sudo', 'systemctl', 'status', 'gpsd'])
    except subprocess.CalledProcessError as e:
        print(f"Error enabling gpsd service: {e.stderr}")
    except Exception as e:
        print(f"An unknown error occurred: {e}")

def read_gps_data():
    session = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)
    try:
        while True:
            report = session.next()
            if report['class'] == 'TPV':
                if hasattr(report, 'time'):
                    print(f'Time: {report.time}')
                    if hasattr(report, 'lat') and hasattr(report, 'lon'):
                        print(f'Latitude: {report.lat}, Longitude: {report.lon}')
    except KeyboardInterrupt:
        print('Exiting...')
    finally:
        session.close()

if __name__ == "__main__":
    enable_gpsd_service()
    read_gps_data()