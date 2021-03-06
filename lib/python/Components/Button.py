# 2015.06.09 06:49:03 CET
#Embedded file name: /usr/lib/enigma2/python/Components/Button.py
from HTMLComponent import HTMLComponent
from GUIComponent import GUIComponent
from VariableText import VariableText
from enigma import eButton

class Button(VariableText, HTMLComponent, GUIComponent):

    def __init__(self, text = '', onClick = None):
        if not onClick:
            onClick = []
        GUIComponent.__init__(self)
        VariableText.__init__(self)
        self.setText(text)
        self.onClick = onClick

    def push(self):
        for x in self.onClick:
            x()

        return 0

    def disable(self):
        pass

    def enable(self):
        pass

    def connectDownstream(self, downstream):
        pass

    def checkSuspend(self):
        pass

    def disconnectDownstream(self, downstream):
        pass

    def produceHTML(self):
        return '<input type="submit" text="' + self.getText() + '">\n'

    GUI_WIDGET = eButton

    def postWidgetCreate(self, instance):
        instance.setText(self.text)
        try:
            instance.selected.get().append(self.push)
        except:
            print '[COMPONENT] Button crash'

    def preWidgetRemove(self, instance):
        try:
            instance.selected.get().remove(self.push)
        except:
            print '[COMPONENT] Button crash'
