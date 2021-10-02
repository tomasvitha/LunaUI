import time
import atexit
import luna_hardware
import luna_core
import netifaces as ni

# get hardware objects
lcd = luna_hardware.lcd
led = luna_hardware.led

# clear the LCD and LED on exit
def clearHardware():
    lcd.clear()
    led.value = False
atexit.register(clearHardware)

# LED test and welcome screen
lcd.clear()
lcd.message = '12345678901234567890'
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


# show clock (temp)
while True:
    t = time.localtime()
    strTime = time.strftime("%H:%M:%S", t)
    if luna_core.getGpsdStatus() == 'active':
        gpsdStatus = 'GPS'
    else:
        gpsdStatus = '   '

    if luna_core.getChronyStatus() == 'active':
        chronyStatus = 'NTP'
    else:
        chronyStatus = '   '

    lcdText = f'      {strTime}\n{gpsdStatus}              {chronyStatus}'
    lcd.message = lcdText

    time.sleep(1)

