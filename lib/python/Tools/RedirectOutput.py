# 2015.06.09 08:45:07 CET
#Embedded file name: /usr/lib/enigma2/python/Tools/RedirectOutput.py
import sys
from enigma import ePythonOutput

class EnigmaOutput:

    def __init__(self):
        pass

    def write(self, data):
        if isinstance(data, unicode):
            data = data.encode('UTF-8')
        ePythonOutput(data)

    def flush(self):
        pass

    def isatty(self):
        return True

    def isatty(self):
        return True


sys.stdout = sys.stderr = EnigmaOutput()
