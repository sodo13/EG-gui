# 2015.06.09 07:09:34 CET
#Embedded file name: /usr/lib/enigma2/python/Components/ProgressBar.py
from HTMLComponent import HTMLComponent
from GUIComponent import GUIComponent
from VariableValue import VariableValue
from enigma import eSlider

class ProgressBar(VariableValue, HTMLComponent, GUIComponent, object):

    def __init__(self):
        GUIComponent.__init__(self)
        VariableValue.__init__(self)
        self.__start = 0
        self.__end = 100

    GUI_WIDGET = eSlider

    def postWidgetCreate(self, instance):
        instance.setRange(self.__start, self.__end)

    def setRange(self, range):
        __start, __end = range
        if self.instance is not None:
            self.instance.setRange(__start, __end)

    def getRange(self):
        return (self.__start, self.__end)

    range = property(getRange, setRange)
