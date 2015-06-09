##
## Permanent Clock
## by AliAbdul
##
from Components.ActionMap import ActionMap
from Components.config import config, ConfigInteger, ConfigSubsection, ConfigYesNo
from Components.MenuList import MenuList
from enigma import ePoint, eTimer, getDesktop
from os import environ
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from EGAMI.EGAMI_skins import EGPermanentClock_Skin

##############################################################################

config.plugins.PermanentClock = ConfigSubsection()
config.plugins.PermanentClock.enabled = ConfigYesNo(default=False)
config.plugins.PermanentClock.position_x = ConfigInteger(default=590)
config.plugins.PermanentClock.position_y = ConfigInteger(default=35)


##############################################################################

class PermanentClockScreen(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin = EGPermanentClock_Skin
		self.onShow.append(self.movePosition)

	def movePosition(self):
		if self.instance:
			self.instance.move(ePoint(config.plugins.PermanentClock.position_x.value, config.plugins.PermanentClock.position_y.value))

##############################################################################

class PermanentClock():
	def __init__(self):
		self.dialog = None

	def gotSession(self, session):
		self.dialog = session.instantiateDialog(PermanentClockScreen)
		self.showHide()

	def changeVisibility(self):
		if config.plugins.PermanentClock.enabled.value:
			config.plugins.PermanentClock.enabled.value = False
		else:
			config.plugins.PermanentClock.enabled.value = True
		config.plugins.PermanentClock.enabled.save()
		self.showHide()

	def showHide(self):
		if config.plugins.PermanentClock.enabled.value:
			self.dialog.show()
		else:
			self.dialog.hide()

pClock = PermanentClock()

##############################################################################

class PermanentClockPositioner(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin = EGPermanentClock_Skin
		
		self["actions"] = ActionMap(["WizardActions"],
		{
			"left": self.left,
			"up": self.up,
			"right": self.right,
			"down": self.down,
			"ok": self.ok,
			"back": self.exit
		}, -1)
		
		desktop = getDesktop(0)
		self.desktopWidth = desktop.size().width()
		self.desktopHeight = desktop.size().height()
		
		self.moveTimer = eTimer()
		self.moveTimer.callback.append(self.movePosition)
		self.moveTimer.start(100, 1)

	def movePosition(self):
		self.instance.move(ePoint(config.plugins.PermanentClock.position_x.value, config.plugins.PermanentClock.position_y.value))
		self.moveTimer.start(100, 1)

	def left(self):
		value = config.plugins.PermanentClock.position_x.value
		value -= 10
		if value < 0:
			value = 0
		config.plugins.PermanentClock.position_x.value = value

	def up(self):
		value = config.plugins.PermanentClock.position_y.value
		value -= 10
		if value < 0:
			value = 0
		config.plugins.PermanentClock.position_y.value = value

	def right(self):
		value = config.plugins.PermanentClock.position_x.value
		value += 10
		if value > self.desktopWidth:
			value = self.desktopWidth
		config.plugins.PermanentClock.position_x.value = value

	def down(self):
		value = config.plugins.PermanentClock.position_y.value
		value += 10
		if value > self.desktopHeight:
			value = self.desktopHeight
		config.plugins.PermanentClock.position_y.value = value

	def ok(self):
		config.plugins.PermanentClock.position_x.save()
		config.plugins.PermanentClock.position_y.save()
		self.close()

	def exit(self):
		config.plugins.PermanentClock.position_x.cancel()
		config.plugins.PermanentClock.position_y.cancel()
		self.close()

##############################################################################

class PermanentClockMenu(Screen):
	skin = """
		<screen position="center,center" size="420,105" title="%s">
			<widget name="list" position="10,10" size="400,85" />
		</screen>""" % _("Permanent Clock")

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self["list"] = MenuList([])
		self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
		self.onLayoutFinish.append(self.showMenu)

	def showMenu(self):
		list = []
		if config.plugins.PermanentClock.enabled.value:
			list.append(_("Deactivate permanent clock"))
		else:
			list.append(_("Activate permanent clock"))
		list.append(_("Change permanent clock position"))
		self["list"].setList(list)

	def okClicked(self):
		sel = self["list"].getCurrent()
		if pClock.dialog is None:
			pClock.gotSession(self.session)
		if sel == _("Deactivate permanent clock") or sel == _("Activate permanent clock"):
			pClock.changeVisibility()
			self.showMenu()
		else:
			pClock.dialog.hide()
			self.session.openWithCallback(self.positionerCallback, PermanentClockPositioner)

	def positionerCallback(self, callback=None):
		pClock.showHide()

##############################################################################

def sessionstart(reason, **kwargs):
	if reason == 0:
		pClock.gotSession(kwargs["session"])

def Plugins(**kwargs):
	return [
		PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart)]
