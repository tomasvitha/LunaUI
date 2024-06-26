import time
import atexit
import luna_hardware
import luna_core
import logging
import netifaces as ni

# get hardware objects
lcd = luna_hardware.lcd
led = luna_hardware.led

# get logger
logger = logging.getLogger(__name__)
logger.addHandler(luna_core.file_handler)

# get services from core module
srv_chrony = luna_core.LinuxService('chrony')
srv_gpsd = luna_core.LinuxService('gpsd')
gps_stats = luna_core.GpsdServiceStatus(srv_gpsd)
ntp_stats = luna_core.ChronyServerStats(srv_chrony)

# clear the LCD and LED on exit
def exit():
    lcd.clear()
    led.value = False
atexit.register(exit)

# Print a message to the console
print('Luna UI for GPS disciplined NTP server')
print('v1.1\n4.10.2021 FakirCZ\n')
print('Press Ctrl+C to exit.')

# LED test and welcome screen
lcd.cursor_position(0,0)
lcd.message = '   GPS NTP SERVER'
lcd.cursor_position(0,1)
lcd.message = 'v2.1         10/2021'
led.value = True
time.sleep(3)
led.value = False

# Show hostname and IP address
ip_address = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
lcd.clear()
lcd.cursor_position(0,0)
lcd.message = 'luna.vitha.cz'
lcd.cursor_position(0,1)
lcd.message = ip_address
time.sleep(3)
lcd.clear()

while True:
    next_time = time.time() + 1

    # show current time
    lcd.cursor_position(12, 0)
    lcd.message = time.strftime("%H:%M:%S", time.localtime())

    # Refresh GPS status
    gps_stats.update()
    ntp_stats.update()

    # show GPS text + set LED value
    lcd.cursor_position(0, 0)
    lcd.message = gps_stats.gps_text
    led.value = gps_stats.led_status

    # show current NTP text
    lcd.cursor_position(0, 1)
    lcd.message = ntp_stats.ntp_text

    # sleep until next second (drifts a bit but who cares)
    time.sleep(max(0, next_time - time.time()))
