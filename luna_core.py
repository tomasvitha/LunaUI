# System checks for the status LCD

from typing import Text
from pystemd.systemd1 import Unit
import gpsd

gpsd.connect()

def getGpsdFixType():
  try:
    return gpsd.get_current().mode
  except:
    print('Exception - GPSD not running?')
  
# Wrapper class for pystemd
class LinuxService:
  def __init__(self, name):
    serviceName = name + '.service'
    self.service = Unit(bytes(serviceName,'utf8'))
    self.service.load()

  def IsRunning(self):
    return self.service.Unit.ActiveState.decode() == 'active'
