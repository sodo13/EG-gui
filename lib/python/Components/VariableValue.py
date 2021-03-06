# 2015.06.09 07:34:11 CET
#Embedded file name: /usr/lib/enigma2/python/Components/VariableValue.py


class VariableValue(object):

    def __init__(self):
        self.__value = 0

    def setValue(self, value):
        self.__value = value
        if self.instance:
            try:
                self.instance.setValue(self.__value)
            except TypeError:
                self.instance.setValue(0)

    def getValue(self):
        return self.__value

    def postWidgetCreate(self, instance):
        print self
        print self.GUI_WIDGET
        self.instance.setValue(self.__value)

    value = property(getValue, setValue)
