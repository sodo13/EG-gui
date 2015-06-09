# 2015.06.09 08:43:31 CET
#Embedded file name: /usr/lib/enigma2/python/Tools/LoadPixmap.py
from enigma import loadPNG, loadJPG

def LoadPixmap(path, desktop = None, cached = False):
    if path[-4:] == '.png':
        ptr = loadPNG(path)
    elif path[-4:] == '.jpg':
        ptr = loadJPG(path)
    elif path[-1:] == '.':
        alpha = loadPNG(path + 'a.png')
        ptr = loadJPG(path + 'rgb.jpg', alpha)
    else:
        raise Exception('neither .png nor .jpg, please fix file extension')
    if ptr and desktop:
        desktop.makeCompatiblePixmap(ptr)
    return ptr
