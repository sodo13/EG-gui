# 2015.06.09 07:12:23 CET
#Embedded file name: /usr/lib/enigma2/python/Components/SelectionList.py
from MenuList import MenuList
from Tools.Directories import resolveFilename, SCOPE_ACTIVE_SKIN
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER
from Tools.LoadPixmap import LoadPixmap
import skin
selectiononpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_on.png'))
selectionoffpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_off.png'))

def SelectionEntryComponent(description, value, index, selected):
    dx, dy, dw, dh = skin.parameters.get('SelectionListDescr', (25, 3, 650, 30))
    res = [(description,
      value,
      index,
      selected), (eListboxPythonMultiContent.TYPE_TEXT,
      dx,
      dy,
      dw,
      dh,
      0,
      RT_HALIGN_LEFT,
      description)]
    if selected:
        ix, iy, iw, ih = skin.parameters.get('SelectionListLock', (0, 2, 25, 24))
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         ix,
         iy,
         iw,
         ih,
         selectiononpng))
    else:
        ix, iy, iw, ih = skin.parameters.get('SelectionListLockOff', (0, 2, 25, 24))
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         ix,
         iy,
         iw,
         ih,
         selectionoffpng))
    return res


class SelectionList(MenuList):

    def __init__(self, list = None, enableWrapAround = False):
        MenuList.__init__(self, list or [], enableWrapAround, content=eListboxPythonMultiContent)
        font = skin.fonts.get('SelectionList', ('Regular', 20, 30))
        self.l.setFont(0, gFont(font[0], font[1]))
        self.l.setItemHeight(font[2])

    def addSelection(self, description, value, index, selected = True):
        self.list.append(SelectionEntryComponent(description, value, index, selected))
        self.setList(self.list)

    def toggleSelection(self):
        if len(self.list) > 0:
            idx = self.getSelectedIndex()
            item = self.list[idx][0]
            self.list[idx] = SelectionEntryComponent(item[0], item[1], item[2], not item[3])
            self.setList(self.list)

    def getSelectionsList(self):
        return [ (item[0][0], item[0][1], item[0][2]) for item in self.list if item[0][3] ]

    def toggleAllSelection(self):
        for idx, item in enumerate(self.list):
            item = self.list[idx][0]
            self.list[idx] = SelectionEntryComponent(item[0], item[1], item[2], not item[3])

        self.setList(self.list)

    def sort(self, sortType = False, flag = False):
        self.list.sort(key=lambda x: x[0][sortType], reverse=flag)
        self.setList(self.list)
