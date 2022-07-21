__version__ = '1.0.0b9'
__all__ = ['SpeedDBClient', 'SpeedDBServer', 'RunUDPServer']

from .SpeedDB import SpeedDBClient, SpeedDBServer
from .utils.server import RunUDPServer