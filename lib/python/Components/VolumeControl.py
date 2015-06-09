# 2015.06.09 07:35:31 CET
#Embedded file name: /usr/lib/enigma2/python/Components/VolumeControl.py
from enigma import eDVBVolumecontrol, eTimer
from Tools.Profile import profile
from Screens.Volume import Volume
from Screens.Mute import Mute
from GlobalActions import globalActionMap
from config import config, ConfigSubsection, ConfigInteger
profile('VolumeControl')

class VolumeControl:
    instance = None

    def __init__(self, session):
        global globalActionMap
        globalActionMap.actions['volumeUp'] = self.volUp
        globalActionMap.actions['volumeDown'] = self.volDown
        globalActionMap.actions['volumeMute'] = self.volMute
        VolumeControl.instance = self
        config.audio = ConfigSubsection()
        config.audio.volume = ConfigInteger(default=50, limits=(0, 100))
        self.volumeDialog = session.instantiateDialog(Volume)
        self.volumeDialog.setAnimationMode(0)
        self.muteDialog = session.instantiateDialog(Mute)
        self.muteDialog.setAnimationMode(0)
        self.hideVolTimer = eTimer()
        self.hideVolTimer.callback.append(self.volHide)
        vol = config.audio.volume.value
        self.volumeDialog.setValue(vol)
        self.volctrl = eDVBVolumecontrol.getInstance()
        self.volctrl.setVolume(vol, vol)

    def volSave(self):
        if self.volctrl.isMuted():
            config.audio.volume.setValue(0)
        else:
            config.audio.volume.setValue(self.volctrl.getVolume())
        config.audio.volume.save()

    def volUp(self):
        vol = self.volctrl.getVolume()
        if vol < 3:
            vol += 1
        elif vol < 9:
            vol += 2
        elif vol < 18:
            vol += 3
        elif vol < 30:
            vol += 4
        else:
            vol += 5
        self.setVolume(vol)

    def volDown(self):
        vol = self.volctrl.getVolume()
        if vol <= 3:
            vol -= 1
        elif vol <= 9:
            vol -= 2
        elif vol <= 18:
            vol -= 3
        elif vol <= 30:
            vol -= 4
        else:
            vol -= 5
        self.setVolume(vol)

    def setVolume(self, newvol):
        self.volctrl.setVolume(newvol, newvol)
        is_muted = self.volctrl.isMuted()
        vol = self.volctrl.getVolume()
        self.volumeDialog.show()
        if is_muted:
            self.volMute()
        elif not vol:
            self.volMute(False, True)
        if self.volctrl.isMuted():
            self.volumeDialog.setValue(0)
        else:
            self.volumeDialog.setValue(self.volctrl.getVolume())
        self.volSave()
        self.hideVolTimer.start(3000, True)

    def volHide(self):
        self.volumeDialog.hide()

    def volMute(self, showMuteSymbol = True, force = False):
        vol = self.volctrl.getVolume()
        if vol or force:
            self.volctrl.volumeToggleMute()
            if self.volctrl.isMuted():
                if showMuteSymbol:
                    self.muteDialog.show()
                self.volumeDialog.setValue(0)
            else:
                self.muteDialog.hide()
                self.volumeDialog.setValue(vol)
