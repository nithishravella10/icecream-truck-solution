# This piece of code is to troubleshoot GPS module
# This code gives the output by running gpsd command manually

from gps import gps, WATCH_ENABLE, WATCH_NEWSTYLE

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
