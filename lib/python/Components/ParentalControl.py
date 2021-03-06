# 2015.06.09 07:07:29 CET
#Embedded file name: /usr/lib/enigma2/python/Components/ParentalControl.py
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigPIN, ConfigText, ConfigYesNo, ConfigSubList, ConfigInteger
from Components.ServiceList import refreshServiceList
from Screens.InputBox import PinInput
from Screens.MessageBox import MessageBox
from Tools.BoundFunction import boundFunction
from ServiceReference import ServiceReference
from Tools import Notifications
from Tools.Directories import resolveFilename, SCOPE_CONFIG
from Tools.Notifications import AddPopup
from enigma import eTimer, eServiceCenter, iServiceInformation, eServiceReference, eDVBDB
import time, os
TYPE_SERVICE = 'SERVICE'
TYPE_BOUQUETSERVICE = 'BOUQUETSERVICE'
TYPE_BOUQUET = 'BOUQUET'
LIST_BLACKLIST = 'blacklist'

def InitParentalControl():
    global parentalControl
    config.ParentalControl = ConfigSubsection()
    config.ParentalControl.storeservicepin = ConfigSelection(default='never', choices=[('never', _('never')),
     ('5', _('%d minutes') % 5),
     ('30', _('%d minutes') % 30),
     ('60', _('%d minutes') % 60),
     ('standby', _('until standby/restart'))])
    config.ParentalControl.configured = ConfigYesNo(default=False)
    config.ParentalControl.setuppinactive = ConfigYesNo(default=False)
    config.ParentalControl.retries = ConfigSubsection()
    config.ParentalControl.retries.servicepin = ConfigSubsection()
    config.ParentalControl.retries.servicepin.tries = ConfigInteger(default=3)
    config.ParentalControl.retries.servicepin.time = ConfigInteger(default=3)
    config.ParentalControl.servicepin = ConfigSubList()
    config.ParentalControl.servicepin.append(ConfigPIN(default=0))
    config.ParentalControl.age = ConfigSelection(default='18', choices=[('0', _('No age block'))] + list(((str(x), '%d+' % x) for x in range(3, 19))))
    config.ParentalControl.hideBlacklist = ConfigYesNo(default=False)
    config.ParentalControl.config_sections = ConfigSubsection()
    config.ParentalControl.config_sections.main_menu = ConfigYesNo(default=False)
    config.ParentalControl.config_sections.configuration = ConfigYesNo(default=False)
    config.ParentalControl.config_sections.timer_menu = ConfigYesNo(default=False)
    config.ParentalControl.config_sections.plugin_browser = ConfigYesNo(default=False)
    config.ParentalControl.config_sections.standby_menu = ConfigYesNo(default=False)
    config.ParentalControl.config_sections.software_update = ConfigYesNo(default=False)
    config.ParentalControl.config_sections.manufacturer_reset = ConfigYesNo(default=True)
    config.ParentalControl.config_sections.movie_list = ConfigYesNo(default=False)
    config.ParentalControl.config_sections.context_menus = ConfigYesNo(default=False)
    config.ParentalControl.config_sections.vixmenu = ConfigYesNo(default=False)
    config.ParentalControl.servicepinactive = config.ParentalControl.configured
    config.ParentalControl.setuppin = config.ParentalControl.servicepin[0]
    config.ParentalControl.retries.setuppin = config.ParentalControl.retries.servicepin
    config.ParentalControl.type = ConfigSelection(default='blacklist', choices=[(LIST_BLACKLIST, _('blacklist'))])
    parentalControl = ParentalControl()


class ParentalControl:

    def __init__(self):
        self.filesOpened = False
        self.PinDlg = None
        self.sessionPinTimer = eTimer()
        self.sessionPinTimer.callback.append(self.resetSessionPin)
        self.getConfigValues()

    def serviceMethodWrapper(self, service, method, *args):
        if 'FROM BOUQUET' in service:
            method(service, TYPE_BOUQUET, *args)
            servicelist = self.readServicesFromBouquet(service, 'C')
            for ref in servicelist:
                sRef = str(ref[0])
                method(sRef, TYPE_BOUQUETSERVICE, *args)

        else:
            ref = ServiceReference(service)
            sRef = str(ref)
            method(sRef, TYPE_SERVICE, *args)

    def isProtected(self, ref):
        if not config.ParentalControl.servicepinactive.value or not ref:
            return False
        if self.storeServicePin != config.ParentalControl.storeservicepin.value:
            self.getConfigValues()
        service = ref.toCompareString()
        path = ref.getPath()
        info = eServiceCenter.getInstance().info(ref)
        age = 0
        if path.startswith('/'):
            if service.startswith('1:'):
                refstr = info and info.getInfoString(ref, iServiceInformation.sServiceref)
                service = refstr and eServiceReference(refstr).toCompareString()
            if [ x for x in path[1:].split('/') if x.startswith('.') if not x == '.Trash' ]:
                age = 18
        elif int(config.ParentalControl.age.value):
            event = info and info.getEvent(ref)
            rating = event and event.getParentalData()
            age = rating and rating.getRating()
            age = age and age <= 15 and age + 3 or 0
        return age and age >= int(config.ParentalControl.age.value) or service and self.blacklist.has_key(service)

    def isServicePlayable(self, ref, callback, session = None):
        self.session = session
        if self.isProtected(ref):
            if self.sessionPinCached:
                return True
            self.callback = callback
            service = ref.toCompareString()
            title = 'FROM BOUQUET "userbouquet.' in service and _('this bouquet is protected by a parental control pin') or _('this service is protected by a parental control pin')
            if session:
                Notifications.RemovePopup('Parental control')
                if self.PinDlg:
                    self.PinDlg.close()
                self.PinDlg = session.openWithCallback(boundFunction(self.servicePinEntered, ref), PinInput, triesEntry=config.ParentalControl.retries.servicepin, pinList=self.getPinList(), service=ServiceReference(ref).getServiceName(), title=title, windowTitle=_('Parental control'), simple=False)
            else:
                Notifications.AddNotificationParentalControl(boundFunction(self.servicePinEntered, ref), PinInput, triesEntry=config.ParentalControl.retries.servicepin, pinList=self.getPinList(), service=ServiceReference(ref).getServiceName(), title=title, windowTitle=_('Parental control'))
            return False
        else:
            return True

    def protectService(self, service):
        if not self.blacklist.has_key(service):
            self.serviceMethodWrapper(service, self.addServiceToList, self.blacklist)
            if config.ParentalControl.hideBlacklist.value and not self.sessionPinCached:
                eDVBDB.getInstance().addFlag(eServiceReference(service), 2)

    def unProtectService(self, service):
        if self.blacklist.has_key(service):
            self.serviceMethodWrapper(service, self.removeServiceFromList, self.blacklist)

    def getProtectionLevel(self, service):
        return not self.blacklist.has_key(service) and -1 or 0

    def getConfigValues(self):
        self.checkPinInterval = False
        self.checkPinIntervalCancel = False
        self.checkSessionPin = False
        self.sessionPinCached = False
        self.pinIntervalSeconds = 0
        self.pinIntervalSecondsCancel = 0
        self.storeServicePin = config.ParentalControl.storeservicepin.value
        if self.storeServicePin == 'never':
            pass
        elif self.storeServicePin == 'standby':
            self.checkSessionPin = True
        else:
            self.checkPinInterval = True
            iMinutes = float(self.storeServicePin)
            iSeconds = int(iMinutes * 60)
            self.pinIntervalSeconds = iSeconds

    def standbyCounterCallback(self, configElement):
        self.resetSessionPin()

    def resetSessionPin(self):
        self.sessionPinCached = False
        self.hideBlacklist()

    def getCurrentTimeStamp(self):
        return time.time()

    def getPinList(self):
        return [ x.value for x in config.ParentalControl.servicepin ]

    def setSessionPinCached(self):
        if self.checkSessionPin == True:
            self.sessionPinCached = True
        if self.checkPinInterval == True:
            self.sessionPinCached = True
            self.sessionPinTimer.startLongTimer(self.pinIntervalSeconds)

    def servicePinEntered(self, service, result = None):
        if result:
            self.setSessionPinCached()
            self.hideBlacklist()
            self.callback(ref=service)
        elif result == False:
            messageText = _('The pin code you entered is wrong.')
            if self.session:
                self.session.open(MessageBox, messageText, MessageBox.TYPE_INFO, timeout=3)
            else:
                AddPopup(messageText, MessageBox.TYPE_ERROR, timeout=3)

    def saveListToFile(self, sWhichList, vList):
        file = open(resolveFilename(SCOPE_CONFIG, sWhichList), 'w')
        for sService, sType in vList.iteritems():
            if TYPE_SERVICE in sType or TYPE_BOUQUET in sType:
                file.write(str(sService) + '\n')

        file.close()

    def openListFromFile(self, sWhichList):
        result = {}
        try:
            file = open(resolveFilename(SCOPE_CONFIG, sWhichList), 'r')
            for x in file:
                sPlain = x.strip()
                self.serviceMethodWrapper(sPlain, self.addServiceToList, result)

            file.close()
        except:
            pass

        return result

    def addServiceToList(self, service, type, vList):
        if vList.has_key(service):
            if type not in vList[service]:
                vList[service].append(type)
        else:
            vList[service] = [type]

    def removeServiceFromList(self, service, type, vList):
        if vList.has_key(service):
            if type in vList[service]:
                vList[service].remove(type)
            if not vList[service]:
                del vList[service]

    def readServicesFromBouquet(self, sBouquetSelection, formatstring):
        from enigma import eServiceCenter, eServiceReference
        serviceHandler = eServiceCenter.getInstance()
        refstr = sBouquetSelection
        root = eServiceReference(refstr)
        list = serviceHandler.list(root)
        if list is not None:
            services = list.getContent('CN', True)
            return services

    def save(self):
        self.saveListToFile(LIST_BLACKLIST, self.blacklist)

    def open(self):
        self.blacklist = self.openListFromFile(LIST_BLACKLIST)
        self.hideBlacklist()
        if not self.filesOpened:
            config.misc.standbyCounter.addNotifier(self.standbyCounterCallback, initial_call=False)
            self.filesOpened = True

    def __getattr__(self, name):
        if name in ('blacklist', 'whitelist'):
            if not self.filesOpened:
                self.open()
                return getattr(self, name)
        raise AttributeError, name

    def hideBlacklist(self):
        if self.blacklist:
            if config.ParentalControl.servicepinactive.value and config.ParentalControl.storeservicepin.value != 'never' and config.ParentalControl.hideBlacklist.value and not self.sessionPinCached:
                for ref in self.blacklist:
                    if TYPE_BOUQUET not in ref:
                        eDVBDB.getInstance().addFlag(eServiceReference(ref), 2)

            else:
                for ref in self.blacklist:
                    if TYPE_BOUQUET not in ref:
                        eDVBDB.getInstance().removeFlag(eServiceReference(ref), 2)

            refreshServiceList()
