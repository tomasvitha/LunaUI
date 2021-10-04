# Core module for the status LCD
import gpsd
import logging
import subprocess
from pystemd.systemd1 import Unit

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler for logger
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('luna-ui.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Wrapper class for pystemd
class LinuxService:
  def __init__(self, name) -> None:
    serviceName = name + '.service'
    self.service = Unit(bytes(serviceName,'utf8')).load()
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
    logger.debug('Updating gpsd info')
    if self._gpsd_service.is_running():
        self.get_gps_fix_mode() 
        if self.fix_mode == 1:
            self.gps_text = 'GPS No Fix'.ljust(11)
            self.led_status = False
        elif self.fix_mode == 2:
            self.gps_text = 'GPS 2D Fix'.ljust(11)
            self.led_status = not self.led_status # blink at polling rate
        elif self.fix_mode == 3:
            self.gps_text = 'GPS 3D Fix'.ljust(11)
            self.led_status = True
    else:
        self.gps_text = 'NO GPSD'.ljust(11)
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
    self.stratum = 10
    self.ref_clock = ''
    self.ntp_text = ''
  
  def _get_raw_stats(self):
    # get data from 'sudo chronyc -c sourcestats'
    stats_result = subprocess.run(['sudo', 'chronyc', '-c', 'serverstats'], stdout = subprocess.PIPE) 
    stats = stats_result.stdout.decode('utf8').split(',')
    self.ntp_packets = int(stats[0])
    self.ntp_dropped = int(stats[1])

    # get current stratum and reference clock from 'chronyc -c tracking'
    tracking_result = subprocess.run(['chronyc', '-c', 'tracking'], stdout = subprocess.PIPE)
    tracking = tracking_result.stdout.decode('utf8').split(',')
    self.stratum = int(tracking[2])

    # if we are Stratum 1 then get the real ref_clock source, otherwise say 'NTP'
    if self.stratum == 1: self.ref_clock = tracking[1] 
    else: self.ref_clock = 'NTP'

    # calculate packets per second
    self.reqs_per_second = int(self.ntp_packets) - int(self.ntp_packets_last)
    self.ntp_packets_last = self.ntp_packets

  def update(self):
    logger.debug('Updating chrony info')
    if self._chrony_service.is_running():
        self._get_raw_stats()
        # we have multiple screens to show
        if self._display_count < 4: self.ntp_text = f'NTP rps: {self.reqs_per_second}'.ljust(20)
        elif self._display_count < 8: self.ntp_text = f'NTP pkts: {self.ntp_packets}'.ljust(20)
        elif self._display_count < 12: self.ntp_text = f'NTP drops: {self.ntp_dropped}'.ljust(20)
        elif self._display_count < 16: self.ntp_text = f'Stratum {self.stratum}  ref: {self.ref_clock}'.ljust(20)
        
        self._display_count += 1
        if self._display_count >= 16: self._display_count = 0 # reset counter
    else: 
        self.ntp_text = ' NTP IS OFFLINE !!'.ljust(20)
