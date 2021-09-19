import time
import luna_hardware
import netifaces as ni

# get hardware objects
lcd = luna_hardware.lcd
led = luna_hardware.led

# LED test and welcome screen
lcd.clear()
lcd.message = ' GPS NTP server\n      v2.0'
led.value = True
time.sleep(3)
led.value = False

# Show hostname and IP address
ipAddress = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
lcd.clear()
lcd.message = 'luna.vitha.cz\n' + ipAddress
time.sleep(4)
lcd.clear()

# Check for gpsd
