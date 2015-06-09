# 2015.06.09 08:44:11 CET
#Embedded file name: /usr/lib/enigma2/python/Tools/Notifications.py
notifications = []
notificationAdded = []
current_notifications = []

def __AddNotification(fnc, screen, id, *args, **kwargs):
    if ".MessageBox'>" in `screen`:
        kwargs['simple'] = True
    notifications.append((fnc,
     screen,
     args,
     kwargs,
     id))
    for x in notificationAdded:
        x()


def AddNotification(screen, *args, **kwargs):
    AddNotificationWithCallback(None, screen, *args, **kwargs)


def AddNotificationWithCallback(fnc, screen, *args, **kwargs):
    __AddNotification(fnc, screen, None, *args, **kwargs)


def AddNotificationParentalControl(fnc, screen, *args, **kwargs):
    RemovePopup('Parental control')
    __AddNotification(fnc, screen, 'Parental control', *args, **kwargs)


def AddNotificationWithID(id, screen, *args, **kwargs):
    __AddNotification(None, screen, id, *args, **kwargs)


def AddNotificationWithIDCallback(fnc, id, screen, *args, **kwargs):
    __AddNotification(fnc, screen, id, *args, **kwargs)


def RemovePopup(id):
    print 'RemovePopup, id =', id
    for x in notifications:
        if x[4] and x[4] == id:
            print '(found in notifications)'
            notifications.remove(x)

    for x in current_notifications:
        if x[0] == id:
            print '(found in current notifications)'
            x[1].close()


from Screens.MessageBox import MessageBox

def AddPopup(text, type, timeout, id = None):
    if id is not None:
        RemovePopup(id)
    print 'AddPopup, id =', id
    AddNotificationWithID(id, MessageBox, text=text, type=type, timeout=timeout, close_on_any_key=True)


def AddPopupWithCallback(fnc, text, type, timeout, id = None):
    if id is not None:
        RemovePopup(id)
    print 'AddPopup, id =', id
    AddNotificationWithIDCallback(fnc, id, MessageBox, text=text, type=type, timeout=timeout, close_on_any_key=False)
