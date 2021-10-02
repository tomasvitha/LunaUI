# System checks for the status LCD

import gpsd
import logging
import subprocess
from pystemd.systemd1 import Unit

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('luna-ui.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Wrapper for gpsd object
def getGpsdFixType():
  try:
    gpsd.connect()
    return gpsd.get_current().mode
  except:
    logger.warn('Connection to gpsd failed, retrying...')

# Chrony server statistics
class ChronyServerStats:
  def __init__(self) -> None:
    self.ntp_packets_last = 0
    self.ntp_packets = 0
    self.ntp_dropped = 0
    self.reqs_per_second = 0
  
  def get_stats(self):
    raw_result = subprocess.run(['sudo', 'chronyc', '-c', 'serverstats'], stdout = subprocess.PIPE) 
    stats = raw_result.stdout.decode('utf8').split(',')
    self.ntp_packets = int(stats[0])
    self.ntp_dropped = int(stats[1])
    self.reqs_per_second = int(self.ntp_packets) - int(self.ntp_packets_last)

# Wrapper class for pystemd
class LinuxService:
  def __init__(self, name) -> None:
    serviceName = name + '.service'
    self.service = Unit(bytes(serviceName,'utf8'))
    self.service.load()
    logger.info('LinuxService has loaded service %s', self.service)

  def IsRunning(self):
    return self.service.Unit.ActiveState.decode() == 'active'

