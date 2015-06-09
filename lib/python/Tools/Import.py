# 2015.06.09 08:41:54 CET
#Embedded file name: /usr/lib/enigma2/python/Tools/Import.py


def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)

    return mod
