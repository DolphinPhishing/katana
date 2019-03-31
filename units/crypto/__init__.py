from pwn import *
from unit import BaseUnit
import socket
import re

class CryptoUnit(BaseUnit):

    @classmethod
    def prepare_parser(cls, config, parser):
        try:
            # Add potential argument parsers in here.
            # parser.add_argument('--proxy', default=None, help='proxy (host:port) to use for web connections')
            pass
        except:
            # These arguments will be inherited by the Units...
            # So it may repeatedly conflict. We'll just have to ignore these
            pass

    def __init__(self, config):
        super(CryptoUnit, self).__init__(config)

    # The sub-class should define this...
    def check(self, target):

        return True

    # The sub-class should define this...
    #  def evaluate(self, target):
    #     pass  
    #
    # If you do not include this function, the main unit.py
    # will properly display its name.