# 2015.06.09 06:59:15 CET
#Embedded file name: /usr/lib/enigma2/python/Components/HTMLSkin.py


class HTMLSkin:
    order = ()

    def __init__(self, order):
        self.order = order

    def produceHTML(self):
        res = '<html>\n'
        for name in self.order:
            res += self[name].produceHTML()

        res += '</html>\n'
        return res
