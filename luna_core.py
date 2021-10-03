# Core module for the status LCD
import gpsd
import logging
import subprocess
from pystemd.systemd1 import Unit

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create file handler for logger
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('luna-ui.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Wrapper class for pystemd
class LinuxService:
  def __init__(self, name) -> None:
    serviceName = name + '.service'
    self.service = Unit(bytes(serviceName,'utf8'))
    self.service.load()
    logger.info('LinuxService has loaded service %s', self.service.Unit.Names)

  def is_running(self):
    return self.service.Unit.ActiveState.decode() == 'active'

# Prepare GPS strings
class GpsdServiceStatus:
  def __init__(self, gpsd_service) -> None:
    self._gpsd_service = gpsd_service
    self.led_status = False
    self.gps_text = ''
    self.fix_mode = 0

  # Wrapper for gpsd "static" object
  def get_gps_fix_mode(self):
    try:
      gpsd.connect()
      self.fix_mode = gpsd.get_current().mode
    except:
      logger.warn('Connection to gpsd failed, retrying...')

  def update(self):
    if self._gpsd_service.is_running():
        self.get_gps_fix_mode() 
        if self.fix_mode == 1:
            self.gps_text = 'GPS NO FIX'.ljust(11)
            self.led_status = False
        elif self.fix_mode == 2:
            self.gps_text = 'GPS 2D'.ljust(11)
            self.led_status = not self.led_status # blink at polling rate
        elif self.fix_mode == 3:
            self.gps_text = 'GPS 3D'.ljust(11)
            self.led_status = True
    else:
        self.gps_text = 'NO GPS'.ljust(11)
        self.led_status = False

# Chrony server statistics class
class ChronyServerStats:
  def __init__(self,chrony_service) -> None:
    self._chrony_service = chrony_service
    self._display_count = 0
    self.ntp_packets_last = 0
    self.ntp_packets = 0
    self.ntp_dropped = 0
    self.reqs_per_second = 0
    self.ntp_text = ''
  
  def _get_raw_stats(self):
    raw_result = subprocess.run(['sudo', 'chronyc', '-c', 'serverstats'], stdout = subprocess.PIPE) 
    stats = raw_result.stdout.decode('utf8').split(',')
    self.ntp_packets = int(stats[0])
    self.ntp_dropped = int(stats[1])

    # calculate packets per second
    self.reqs_per_second = int(self.ntp_packets) - int(self.ntp_packets_last)
    self.ntp_packets_last = self.ntp_packets

  def update(self):
    logger.debug('format_ntp_status called from thread')
    if self._chrony_service.is_running():
        self._get_raw_stats()
        # we have multiple screens to show
        if self._display_count < 3: self.ntp_text = f'NTP pps: {self.reqs_per_second}'.ljust(20)
        elif self._display_count < 6: self.ntp_text = f'NTP packets: {self.ntp_packets}'.ljust(20)
        elif self._display_count < 9: self.ntp_text = f'NTP dropped: {self.ntp_dropped}'.ljust(20)
        
        self._display_count += 1
        if self._display_count >= 9: self._display_count = 0 # reset counter
    else: 
        self.ntp_text = 'NTP IS OFFLINE !!'.ljust(20)


