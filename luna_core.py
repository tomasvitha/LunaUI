# System checks for the status LCD

import gpsd
import logging
from pystemd.systemd1 import Unit

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('luna-ui.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def getGpsdFixType():
  try:
    gpsd.connect()
    return gpsd.get_current().mode
  except:
    logger.warn('Connection to gpsd failed, retrying...')
  
  
# Wrapper class for pystemd
class LinuxService:
  def __init__(self, name):
    serviceName = name + '.service'
    self.service = Unit(bytes(serviceName,'utf8'))
    self.service.load()
    logger.info('LinuxService has loaded service %s', self.service)

  def IsRunning(self):
    return self.service.Unit.ActiveState.decode() == 'active'
