# 2015.06.09 08:42:33 CET
#Embedded file name: /usr/lib/enigma2/python/Tools/IO.py
from os import fchmod, fsync, path, rename, unlink
from tempfile import NamedTemporaryFile

def saveFile(filename, data, mode = 420):
    tmpFilename = None
    try:
        f = NamedTemporaryFile(prefix='.%s.' % path.basename(filename), dir=path.dirname(filename), delete=False)
        tmpFilename = f.name
        if isinstance(data, list):
            for x in data:
                f.write(x)

        else:
            f.write(data)
        f.flush()
        fsync(f.fileno())
        fchmod(f.fileno(), mode)
        f.close()
        rename(tmpFilename, filename)
    except Exception as e:
        print 'saveFile: failed to write to %s: %s' % (filename, e)
        if tmpFilename and path.exists(tmpFilename):
            unlink(tmpFilename)
        return False

    return True
