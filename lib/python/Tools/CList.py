# 2015.06.09 08:39:16 CET
#Embedded file name: /usr/lib/enigma2/python/Tools/CList.py


class CList(list):

    def __getattr__(self, attr):
        return CList([ getattr(a, attr) for a in self ])

    def __call__(self, *args, **kwargs):
        for x in self:
            x(*args, **kwargs)
