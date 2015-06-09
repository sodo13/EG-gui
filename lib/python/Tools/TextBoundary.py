# 2015.06.09 08:45:44 CET
#Embedded file name: /usr/lib/enigma2/python/Tools/TextBoundary.py
from enigma import eLabel

def getTextBoundarySize(instance, font, targetSize, text):
    dummy = eLabel(instance)
    dummy.setFont(font)
    dummy.resize(targetSize)
    dummy.setText(text)
    return dummy.calculateSize()
