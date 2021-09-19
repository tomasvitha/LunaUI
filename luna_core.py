# System checks for the status LCD

from pystemd.systemd1 import Unit

def getGpsdStatus():
    unit = Unit(b'gpsd.service')
    unit.load()
    return unit.Unit.ActiveState

def getChronyStatus():
    unit = Unit(b'chrony.service')
    unit.load()
    return unit.Unit.ActiveState
