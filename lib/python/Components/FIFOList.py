# 2015.06.09 06:56:01 CET
#Embedded file name: /usr/lib/enigma2/python/Components/FIFOList.py
from Components.MenuList import MenuList

class FIFOList(MenuList):

    def __init__(self, menulist = None, length = 10):
        if not menulist:
            menulist = []
        self.list = menulist
        self.len = length
        MenuList.__init__(self, self.list)

    def addItem(self, item):
        self.list.append(item)
        self.l.setList(self.list[-self.len:])

    def clear(self):
        del self.list[:]
        self.l.setList(self.list)

    def getCurrentSelection(self):
        return self.list and self.getCurrent() or None

    def listAll(self):
        self.l.setList(self.list)
        self.selectionEnabled(True)
