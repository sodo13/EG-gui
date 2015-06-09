# 2015.06.09 07:35:11 CET
#Embedded file name: /usr/lib/enigma2/python/Components/VolumeBar.py
from HTMLComponent import HTMLComponent
from GUIComponent import GUIComponent
from VariableValue import VariableValue
from enigma import eSlider

class VolumeBar(VariableValue, HTMLComponent, GUIComponent):

    def __init__(self):
        VariableValue.__init__(self)
        GUIComponent.__init__(self)

    GUI_WIDGET = eSlider

    def postWidgetCreate(self, instance):
        instance.setRange(0, 100)