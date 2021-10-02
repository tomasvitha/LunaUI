from threading import Timer
import time
import atexit
import luna_hardware
import luna_core
import netifaces as ni

# get hardware objects
lcd = luna_hardware.lcd
led = luna_hardware.led

# get service objects
srvGpsd = luna_core.LinuxService('gpsd')
srvChrony = luna_core.LinuxService('chrony')

# clear the LCD and LED on exit
def clearHardware():
    lcd.clear()
    led.value = False
atexit.register(clearHardware)

# LED test and welcome screen
time.sleep(0.1)
lcd.home()
lcd.message = '12345678901234567890\n********************'
led.value = True
time.sleep(3)
led.value = False

# Show hostname and IP address
ipAddress = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
lcd.clear()
lcd.message = 'luna.vitha.cz\n' + ipAddress
time.sleep(4)
lcd.clear()

# Prepare GPS strings



# show clock (temp)
while True:
    t = time.localtime()
    strTime = time.strftime("%H:%M:%S", t)
    
    if srvGpsd.IsRunning():
        gpsStatus = luna_core.getGpsdFixType()
    else:
        gpsStatus = '   '

    if srvChrony.IsRunning():
        ntpStatus = 'NTP'
    else:
        ntpStatus = '   '

    lcd.cursor_position(0, 0)
    lcd.message = gpsStatus
    lcd.cursor_position(12, 0)
    lcd.message = strTime
    lcd.cursor_position(0, 1)
    lcd.message = ntpStatus
    time.sleep(1)
