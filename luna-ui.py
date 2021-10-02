import time
import atexit
import luna_hardware
import luna_core
import logging
import netifaces as ni

# get hardware objects
lcd = luna_hardware.lcd
led = luna_hardware.led

# get service objects
srvGpsd = luna_core.LinuxService('gpsd')
srvChrony = luna_core.LinuxService('chrony')
chrony_stats = luna_core.ChronyServerStats()

# get logger
logger = logging.getLogger(__name__)
logger.addHandler(luna_core.file_handler)

# clear the LCD and LED on exit
def clear_hw():
    lcd.clear()
    led.value = False
atexit.register(clear_hw)

# LED test and welcome screen
time.sleep(0.1)
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
def format_gps_status():
    if srvGpsd.IsRunning():
        fix_type = luna_core.getGpsdFixType()
        text = ''
        led_status = False
        if fix_type == 1:
            text = 'GPS NO FIX'
            led_status = False
        elif fix_type == 2:
            text = 'GPS 2D    '
            led_status = not led.value # blink at polling rate
        elif fix_type == 3:
            text = 'GPS 3D    '
            led_status = True
    else:
        text = 'NO GPS    '
        led_status = False

    return text, led_status

# Prepare NTP strings
count = 0
def format_ntp_status():
    global count
    if srvChrony.IsRunning():
        chrony_stats.get_stats()
        # we have multiple screens to show
        if count < 3: ntp_text = f'NTP pps: {chrony_stats.reqs_per_second}'.ljust(20)
        elif count < 6: ntp_text = f'NTP packets: {chrony_stats.ntp_packets}'.ljust(20)
        elif count < 9: ntp_text = f'NTP dropped: {chrony_stats.ntp_dropped}'.ljust(20)
        
        count += 1
        if count >= 9: count = 0
    else: 
        ntp_text = 'NTP offline'.ljust(20)

    return ntp_text


# show clock (temp)
while True:
  t = time.strftime("%H:%M:%S", time.localtime())
    
  lcd.cursor_position(0, 0)
  lcd.message = format_gps_status()[0]
  led.value = format_gps_status()[1]
  lcd.cursor_position(12, 0)
  lcd.message = t

  lcd.cursor_position(0, 1)
  lcd.message = format_ntp_status()
  time.sleep(1)
