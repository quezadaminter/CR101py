#!/bin/python3
import os
import sys
import soco
from Xlib import X, display
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Gdk
import zonesPage
from zonesPage import ZonesPage, Zones
from MusicPage import MusicPage
from MusicPlayingPage import MusicPlayingPage
from MusicAlbumArtPage import MusicAlbumArtPage
from QueuePage import QueuePage
from musicLibraryPage import MusicLibraryPage
from mediaListItemsPage import MediaListItemsPage
from mediaListArtistsPage import MediaListArtistsPage
from mediaListAlbumsPage import MediaListAlbumsPage
from systemSettingsPage import SystemSettingsPage
from Zone import Zone
from threading import Thread, Event
import time
from mediaListTracksPage import MediaListTracksPage
from zoneListener import ZoneListener
from I2C import I2CListener, CRi2c
import I2C
import imageManager
import CSS

def moduleExists(module_name):
   try:
      __import__(module_name)
   except ImportError:
      return False
   else:
      return True

volumeDialog = None

class VolumeDialog(Gtk.Dialog):
   def __init__(self, parent):
      Gtk.Dialog.__init__(self, "Volume", parent, 0,
            (Gtk.STOCK_NO, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_YES, Gtk.ResponseType.OK))

      self.set_default_size(80, 100)
      label = Gtk.Label("Zone")

      box = self.get_content_area()
      box.add(label)

      hbox = Gtk.HBox()

      self.volPos = 180

      i = Gtk.Image()
      i.set_from_pixbuf(imageManager.get_pixbuf("zone.connect"))
      hbox.pack_start(i, False, False, 2)
      self.volImage = Gtk.Image()
      self.volImage.set_from_pixbuf(imageManager.get_pixbuf("vol.180"))
      hbox.pack_start(self.volImage, False, False, 2)
      i = Gtk.Image()
      i.set_from_pixbuf(imageManager.get_pixbuf("speaker"))
      hbox.pack_start(i, False, False, 2)
      self.volumeProgressBar = Gtk.ProgressBar()
      hbox.pack_start(self.volumeProgressBar, False, False, 2)

      box.add(hbox)
      self.show_all()

   def Up(self, zone):
      self.volPos += 18
      if self.volPos >= 180:
         self.volPos = 180

      #self.volImage.set_from_pixbuf(imageManager.get_image("vol." + str(self.volPos)).Scale(32, 32))

      self.volumeProgressBar.set_fraction(self.volPos / 180)

   def Down(self, zone):
      self.volPos -= 18
      if self.volPos <= 0:
         self.volPos = 0
      self.volumeProgressBar.set_fraction(self.volPos / 180)

class PyApp(Gtk.Window):

   class zoneListener(ZoneListener):
      def __init__(self, owner):
         super().__init__(owner)

      def on_selected_zone_changed(self):
         for key, value in self.owner.zoneListeners.items():
            value.on_selected_zone_changed()

      def on_zone_transport_change_event(self, event):
         for key, value in self.owner.zoneListeners.items():
            value.on_zone_transport_change_event(event)

      def on_zone_render_change_event(self, event):
         for key, value in self.owner.zoneListeners.items():
            value.on_zone_render_change_event(event)

      def on_zone_queue_update_begin(self):
         for key, value in self.owner.zoneListeners.items():
            value.on_zone_queue_update_begin()

      def on_zone_queue_update_end(self):
         for key, value in self.owner.zoneListeners.items():
            value.on_zone_queue_update_end()
   
      def on_current_track_update_state(self, trackInfo):
         for key, value in self.owner.zoneListeners.items():
            value.on_current_track_update_state(trackInfo)

   class i2cListenerInterface(I2CListener):
      def __init__(self, owner):
         self.owner = owner

      # We need this wrapper because the method
      # must return False in order to inform
      # the gui thread that it should be called only once.
      #def add_as_idle(self, function):
      #   function(None)
      #   return False
      def add_as_idle(self, function, *args):
         #print("ADD_AS_IDLE: ", id(function))
         function(args)
         return False

      def on_button_pressed_event(self, btn):
          if btn == I2C.SWITCH_VOL_UP:
             GLib.idle_add(self.add_as_idle, self.owner.on_zoneVolUpButton_Pressed)
          elif btn == I2C.SWITCH_VOL_DN:
             GLib.idle_add(self.add_as_idle, self.owner.on_zoneVolDownButton_Pressed)

      def on_button_released_event(self, btn):
          print("BUTTON: ", btn)
          print("release event: ", btn)
          if btn == I2C.SWITCH_MUTE:
             GLib.idle_add(self.add_as_idle, self.owner.on_zoneMuteButton_Clicked)
          elif btn == I2C.SWITCH_VOL_UP:
             GLib.idle_add(self.add_as_idle, self.owner.on_zoneVolUpButton_Released)
          elif btn == I2C.SWITCH_VOL_DN:
             GLib.idle_add(self.add_as_idle, self.owner.on_zoneVolDownButton_Released)
          elif btn == I2C.SWITCH_A:
             GLib.idle_add(self.add_as_idle, self.owner.on_Button_A_Clicked)
          elif btn == I2C.SWITCH_B:
             GLib.idle_add(self.add_as_idle, self.owner.on_Button_B_Clicked)
          elif btn == I2C.SWITCH_C:
             GLib.idle_add(self.add_as_idle, self.owner.on_Button_C_Clicked)
          elif btn == I2C.SWITCH_ZONE:
             GLib.idle_add(self.add_as_idle, self.owner.on_Zones_Button_Clicked)
          elif btn == I2C.SWITCH_BACK:
             GLib.idle_add(self.add_as_idle, self.owner.on_Return_Button_Clicked)
          elif btn == I2C.SWITCH_MUSIC:
             GLib.idle_add(self.add_as_idle, self.owner.on_Music_Button_Clicked)
          elif btn == I2C.SWITCH_ENTER:
             GLib.idle_add(self.add_as_idle, self.owner.on_Button_Ok_Clicked)
          elif btn == I2C.SWITCH_REWIND:
             GLib.idle_add(self.add_as_idle, self.owner.on_Previous_Button_Clicked)
          elif btn == I2C.SWITCH_PLAY_PAUSE:
             GLib.idle_add(self.add_as_idle, self.owner.on_Play_Button_Clicked)
          elif btn == I2C.SWITCH_FORWARD:
             GLib.idle_add(self.add_as_idle, self.owner.on_Next_Button_Clicked)

      def on_scroll_event(self, steps):
         if steps < 0:
            GLib.idle_add(self.add_as_idle, self.owner.on_Scroll_Up)
         elif steps > 0:
            GLib.idle_add(self.add_as_idle, self.owner.on_Scroll_Down)

      def on_battery_level_event(self, level):
         #GLib.idle_add(self.add_as_idle, self.owner.on_Battery_Level_Event, level)
         pass

      def on_charger_event(self):
         pass

      def on_system_event(self, events):
         if events & I2C.PI_EVENT_SLEEP_BIT:
            pass
         elif events & I2C.PI_EVENT_REBOOT_BIT:
            os.system("sudo reboot now")
         elif events & I2C.PI_EVENT_RESTART_APP_BIT:
            GLib.idle_add(self.add_as_idle, self.owner.on_destroy)
            python = sys.executable
            os.execl(python, python, *sys.argv)
         elif events & I2C.PI_EVENT_SHUTDOWN_BIT:
            GLib.idle_add(self.add_as_idle, self.owner.on_destroy)
            os.system("sudo shutdown now")

   def on_Zones_Button_Press(self, button, event):
       print("Zones press ", event)
       self.i2c.sendEvent(I2C.SWITCH_ZONE, True)
       return True

   def on_Zones_Button_Release(self, button, event):
       print("Zones Release", event)
       self.i2c.sendEvent(I2C.SWITCH_ZONE, False)
       return True

   def on_Zones_Button_Clicked(self, button):
      self.pageInView.on_zoneButton_Clicked()
      return True

   def on_Music_Button_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_MUSIC, True)
      return True

   def on_Music_Button_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_MUSIC, False)
      return True

   def on_Music_Button_Clicked(self, button):
      self.pageInView.on_musicButton_Clicked()
      return True

   def on_zoneMuteButton_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_MUTE, True)
      return True

   def on_zoneMuteButton_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_MUTE, False)
      return True

   def on_zoneMuteButton_Clicked(self, button):
      print("Mute")
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.mute(not zp.selectedZone.is_muted())

   def on_zoneVolUpButton_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_VOL_UP, True)
      return True

   def on_zoneVolUpButton_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_VOL_UP, False)
      return True

   def on_zoneVolUpButton_Pressed(self, button):
      print("Up")
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.volume('+')

      global volumeDialog
      if volumeDialog is None:
         volumeDialog = VolumeDialog(self.get_toplevel())
         volumeDialog.set_decorated(False)
         volumeDialog.run()
      return True

   def on_zoneVolUpButton_Released(self, button):
      print("Up")
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         pass

      if volumeDialog is not None:
         volumeDialog.Up(zp)
      return True

   def on_zoneVolDownButton_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_VOL_DN, True)
      return True

   def on_zoneVolDownButton_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_VOL_DN, False)
      return True

   def on_zoneVolDownButton_Pressed(self, button):
      print("Down")
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.volume('-')
      
      global volumeDialog
      if volumeDialog is None:
         volumeDialog = VolumeDialog(self.get_toplevel())
         volumeDialog.set_decorated(False)
         volumeDialog.run()
      return True
   
   def on_zoneVolDownButton_Released(self, button):
      print("Up")
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         pass

      if volumeDialog is not None:
         volumeDialog.Down(zp)
      return True


   def get_selected_zone(self):
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         return(zp.selectedZone)
      else:
         return(None)

   def get_page(self, page):
      return(self.pageDict[page])

   def show_page(self, page):

      if self.pageInView is self.pageDict["QueuePage"]:
         self.hide_queue_page()
      else:
         self.pageInView.hide()

      self.pageInView.on_Page_Exit_View()

      if isinstance(page, str) and page == "PastPage":
         page = self.pageDict["PastPage"]

      self.pageDict["PastPage"] = self.pageInView

      self.pageRevealer.remove(self.pageInView)

      if isinstance(page, str):
         self.pageInView = self.pageDict[page]
      else:
         self.pageInView = page

      self.pageRevealer.add(self.pageInView)
      self.pageInView.on_Page_Entered_View(self.pageDict["ZonesPage"].selectedZone)
      self.pageInView.show()

      # Consider moving this, it starts the event monitoring
      # thread on initial call
      if self.pageInView is self.pageDict["ZonesPage"]:
         print("on PAge Changed: ", zonesPage.Zones)
         if zonesPage.Zones is not None and len(zonesPage.Zones) > 0:
            if self.eventThread.is_alive() == False:
               print("Starting event thread.")
               self.eventThread.start()

   def on_Page_Changed(self, stack, gparamstring):
#       self.show_page(self.stack.get_visible_child())
      pass

   def on_Button_A_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_A, True)
      return True

   def on_Button_A_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_A, False)
      return True

   def on_Button_A_Clicked(self, button):
       self.pageInView.on_Button_A_Clicked()
       return True

   def on_Button_B_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_B, True)
      return True

   def on_Button_B_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_B, False)
      return True

   def on_Button_B_Clicked(self, button):
       self.pageInView.on_Button_B_Clicked()
       return True

   def on_Button_C_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_C, True)
      return True

   def on_Button_C_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_C, False)
      return True

   def on_Button_C_Clicked(self, button):
      self.pageInView.on_Button_C_Clicked()

   def on_Return_Button_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_BACK, True)
      return True

   def on_Return_Button_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_BACK, False)
      return True

   def on_Return_Button_Clicked(self, button):
      global volumeDialog
      if volumeDialog is not None:
         volumeDialog.destroy()
         volumeDialog = None
      else:
         self.pageInView.on_Return_Button_Clicked()
      return True

   def on_Scroll_Up(self, button):
       self.pageInView.on_Scroll_Up()

   def on_Button_Ok_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_ENTER, True)
      return True

   def on_Button_Ok_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_ENTER, False)
      return True

   def on_Button_Ok_Clicked(self, button):
       self.pageInView.on_Button_Ok_Clicked()
       return True

   def on_Scroll_Down(self, button):
       self.pageInView.on_Scroll_Down()

   def on_Previous_Button_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_REWIND, True)
      return True

   def on_Previous_Button_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_REWIND, False)
      return True

   def on_Previous_Button_Clicked(self, button):
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.previous()
      else :
         print(zp.selectedZone)
      return True

   def on_Play_Button_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_PLAY_PAUSE, True)
      return True

   def on_Play_Button_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_PLAY_PAUSE, False)
      return True

   def on_Play_Button_Clicked(self, button):
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.play()
      else :
         print(zp.selectedZone)
      return True

   def on_Next_Button_Press(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_FORWARD, True)
      return True

   def on_Next_Button_Release(self, button, event):
      self.i2c.sendEvent(I2C.SWITCH_FORWARD, False)
      return True

   def on_Next_Button_Clicked(self, button):
      zp = self.pageDict["ZonesPage"]
      if zp is not None and zp.selectedZone is not None:
         zp.selectedZone.next()
      else :
         print(zp.selectedZone)
      return True

   def eventThreadHandler(self):
      print("Running event thread handler: ", zonesPage.Zones)
      while self.RunEventThread:
         for zone in zonesPage.Zones:
            zone.update()
         if self.get_selected_zone() is not None:
            self.get_selected_zone().monitor()

         # Add timer here to enable and disable screen blanking manually.


         time.sleep(1.0)

   def hide_queue_page(self):
      self.queueRevealer.set_reveal_child(False)
      if self.pageDict["PastPage"] is not None:
         self.pageInView = self.pageDict["PastPage"]
      else:
         self.pageInView = self.pageDict["MusicPage"]

      self.queueRevealer.hide()
      self.pageRevealer.show()
#      self.pageInView.show()
   
   def show_queue_page(self):
      self.pageRevealer.hide()
      self.pageDict["PastPage"] = self.pageInView
      self.pageInView = self.pageDict["QueuePage"]
      self.pageInView.on_Page_Entered_View(self.pageDict["ZonesPage"].selectedZone)
      self.queueRevealer.show_all()
      self.queueRevealer.set_reveal_child(True)
#      self.pageInView.show()

   def add_zone_listener(self, id, listener):
      self.zoneListeners[id] = listener

   def remove_zone_listener(self, id):
      if id in self.zoneListeners:
         self.zoneListeners.pop(id)

   def on_destroy(self, widget):
      self.RunEventThread = False
      self.i2c.Close()
      time.sleep(1.0)
      Gtk.main_quit()

###############################################################################
###############################################################################
###############################################################################

   def __init__(self, hideUI, hideDecorations):
      super(PyApp, self).__init__()

      self.zoneListeners = {}

      imageManager.add_image("./images/AlbumArtEmpty.jpg", 'emptyArt')
      imageManager.add_image("./images/CrossFade.png", 'crossFade')
      imageManager.add_image("./images/Mute.png", 'mute')
      imageManager.add_image("./images/NoAlbumArt.jpg", 'noArt')
      imageManager.add_image("./images/Pause.png", 'pause')
      imageManager.add_image("./images/Play.png", 'play')
      imageManager.add_image("./images/Queue.png", 'queue')
      imageManager.add_image("./images/Repeat.png", 'repeat')
      imageManager.add_image("./images/separator.png", 'separator')
      imageManager.add_image("./images/Shuffle.png", 'shuffle')
      imageManager.add_image("./images/Stop.png", 'stop')
      imageManager.add_image("./images/Shrug.png", 'shrug')
      imageManager.add_image("./images/Transition.png", 'transition')
      imageManager.add_image("./images/RightArrow.png", 'more')
      imageManager.add_image("./images/Connect.png", 'zone.connect')
      imageManager.add_image("./images/Volume_180.png", 'vol.180')
      imageManager.add_image("./images/Volume_00.svg", 'vol.0')
      imageManager.add_image("./images/Speaker.png", 'speaker')

      self.pageDict = {
         "ZonesPage" : ZonesPage(self),
         "MusicPage" : MusicPage(self),
         "MusicPlayingPage" : MusicPlayingPage(self),
         "MusicAlbumArtPage" : MusicAlbumArtPage(self),
         "QueuePage" : QueuePage(self),
         "MusicLibraryPage" : MusicLibraryPage(self),
         "MediaListArtistsPage" : MediaListArtistsPage(self),
         "MediaListAlbumsPage" : MediaListAlbumsPage(self),
         "MediaListTracksPage" : MediaListTracksPage(self),
         "SystemSettingsPage" : SystemSettingsPage(self),
         "PastPage" : None
         }

      self.zlistener = self.zoneListener(self)
      self.i2cListener = self.i2cListenerInterface(self)
      self.i2c = CRi2c()
      self.i2c.setListener(self.__class__.__name__, self.i2cListener)

      self.pageInView = self.pageDict["ZonesPage"]
      self.pageInView.set_listener(self.zlistener)

      self.RunEventThread = True
      self.eventThread = Thread(target = self.eventThreadHandler)

      #self.set_default_size(480, 320)

      #self.set_default_size(620, 320)

#      self.set_resizable(False)
      self.set_title("CR101!")

#      if moduleExists("RPi.GPIO"):
#         # connect to the hardware IO
#         import RPi.GPIO as GPIO

      topHBox = Gtk.HBox()

      vBoxVol = Gtk.VButtonBox()
      b = Gtk.Button(label="MUTE")
      #b.connect("clicked", self.on_zoneMuteButton_Clicked)
      b.connect("button-press-event", self.on_zoneMuteButton_Press)
      b.connect("button-release-event", self.on_zoneMuteButton_Release)
      vBoxVol.pack_start(b, False, False, 1)
      b = Gtk.Button(label="VOL")
      b.set_sensitive(False)
      vBoxVol.pack_start(b, False, False, 1)
      b = Gtk.Button(label="UP")
      #b.connect("clicked", self.on_zoneVolUpButton_Clicked)
      b.connect("button-press-event", self.on_zoneVolUpButton_Press)
      b.connect("button-release-event", self.on_zoneVolUpButton_Release)
      vBoxVol.pack_start(b, False, False, 1)
      b = Gtk.Button(label="DN")
      #b.connect("clicked", self.on_zoneVolDownButton_Clicked)
      b.connect("button-press-event", self.on_zoneVolDownButton_Press)
      b.connect("button-release-event", self.on_zoneVolDownButton_Release)
      vBoxVol.pack_start(b, False, False, 1)

      topHBox.pack_start(vBoxVol, False, False, 1)

      self.vbox = Gtk.VBox()
#      self.stack = Gtk.Stack()
#      self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
#      self.stack.set_transition_duration(500)
#      self.stack.set_homogeneous(True)
#      self.stack.connect("notify::visible-child", self.on_Page_Changed)

#      self.stack.add_titled(pageDict["ZonesPage"], "ZonesPage", "Zones!!")
#      self.stack.add_titled(pageDict["MusicPage"], "MusicPage", "Music!!")

#      stack_switcher = Gtk.StackSwitcher()
#      stack_switcher.set_stack(self.stack)

      self.pageRevealer = Gtk.Revealer()
      self.pageRevealer.set_transition_duration(0.5)
      self.pageRevealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
      self.pageRevealer.add(self.pageDict["ZonesPage"])
      self.pageRevealer.set_reveal_child(True)
      self.vbox.pack_start(self.pageRevealer, True, True, 0)

#      self.vbox.pack_start(self.stack, True, True, 0)

      self.queueRevealer = Gtk.Revealer()
      self.queueRevealer.set_transition_duration(0.5)
      self.queueRevealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
      self.queueRevealer.add(self.pageDict["QueuePage"])
      self.queueRevealer.set_reveal_child(False)
      self.vbox.pack_start(self.queueRevealer, True, True, 0)

      buttonBoxABC = Gtk.HButtonBox()
      buttonBoxABC.set_layout(Gtk.ButtonBoxStyle.SPREAD)
      b = Gtk.Button(label="A")
      #b.connect("clicked", self.on_Button_A_Clicked)
      b.connect("button-press-event", self.on_Button_A_Press)
      b.connect("button-release-event", self.on_Button_A_Release)
      buttonBoxABC.pack_start(b, True, True, 1)

      b = Gtk.Button(label="B")
      #b.connect("clicked", self.on_Button_B_Clicked)
      b.connect("button-press-event", self.on_Button_B_Press)
      b.connect("button-release-event", self.on_Button_B_Release)
      buttonBoxABC.pack_start(b, True, True, 1)

      b = Gtk.Button(label="C")
      #b.connect("clicked", self.on_Button_C_Clicked)
      b.connect("button-press-event", self.on_Button_C_Press)
      b.connect("button-release-event", self.on_Button_C_Release)
      buttonBoxABC.pack_start(b, True, True, 1)

      self.vbox.pack_start(buttonBoxABC, False, False, 0)

      topHBox.pack_start(self.vbox, True, True, 1)


      cmdVBox = Gtk.VBox()
#
      buttonBox = Gtk.HButtonBox()
#      cmdVBox.pack_start(stack_switcher, False, False, 1)
      
      b = Gtk.Button(label="Zones")
      #b.connect("clicked", self.on_Zones_Button_Clicked)
      b.connect("button-press-event", self.on_Zones_Button_Press)
      b.connect("button-release-event", self.on_Zones_Button_Release)
      buttonBox.pack_start(b, True, False, 1)
      
      b = Gtk.Button(label="Ret")
      #b.connect("clicked", self.on_Return_Button_Clicked)
      b.connect("button-press-event", self.on_Return_Button_Press)
      b.connect("button-release-event", self.on_Return_Button_Release)
      buttonBox.pack_start(b, True, False, 1)
#      cmdVBox.pack_start(b, False, False, 1)
      b = Gtk.Button(label="Music")
      #b.connect("clicked", self.on_Music_Button_Clicked)
      b.connect("button-press-event", self.on_Music_Button_Press)
      b.connect("button-release-event", self.on_Music_Button_Release)
      buttonBox.pack_start(b, True, False, 1)
      
      cmdVBox.pack_start(buttonBox, False, False, 1)

      buttonBox = Gtk.HButtonBox()
#      buttonBox.set_layout(Gtk.BUTTONBOX_START)
      b = Gtk.Button(label="B")
      b.connect("clicked", self.on_Scroll_Up)
      buttonBox.pack_start(b, True, False, 1)
      b = Gtk.Button(label="OK")
      #b.connect("clicked", self.on_Button_Ok_Clicked)
      b.connect("button-press-event", self.on_Button_Ok_Press)
      b.connect("button-release-event", self.on_Button_Ok_Release)
      buttonBox.pack_start(b, True, False, 1)
      b = Gtk.Button(label="F")
      b.connect("clicked", self.on_Scroll_Down)
      buttonBox.pack_start(b, True, False, 1)

      cmdVBox.pack_start(buttonBox, True, False, 1)

      buttonBox = Gtk.HButtonBox()
#      buttonBox.set_layout(Gtk.BUTTONBOX_START)
      b = Gtk.Button(label="Prev")
      #b.connect("clicked", self.on_Previous_Button_Clicked)
      b.connect("button-press-event", self.on_Previous_Button_Press)
      b.connect("button-release-event", self.on_Previous_Button_Release)
      buttonBox.pack_start(b, True, False, 1)
      b = Gtk.Button(stock = Gtk.STOCK_MEDIA_PLAY)
      #b.connect("clicked", self.on_Play_Button_Clicked)
      b.connect("button-press-event", self.on_Play_Button_Press)
      b.connect("button-release-event", self.on_Play_Button_Release)
      buttonBox.pack_start(b, True, False, 1)
      b = Gtk.Button(label="Next")
      #b.connect("clicked", self.on_Next_Button_Clicked)
      b.connect("button-press-event", self.on_Next_Button_Press)
      b.connect("button-release-event", self.on_Next_Button_Release)
      buttonBox.pack_start(b, True, False, 1)

      cmdVBox.pack_start(buttonBox, False, False, 1)

      topHBox.pack_start(cmdVBox, False, False, 1)

      self.add(topHBox)

      self.connect("destroy", self.on_destroy)

      self.show_all()

      self.queueRevealer.hide()
      
      self.pageInView.on_Page_Entered_View(None)

      if hideUI == True:
         cmdVBox.hide()
         buttonBoxABC.hide()
         vBoxVol.hide()
         d = display.Display()
         s = d.screen()
         root = s.root
         root.warp_pointer(481, 321)
         d.sync()
         ss = d.get_screen_saver()
         print("Screen saver timeout was: ", ss.timeout)
         ss.timeout = 60
         d.set_screen_saver(ss.timeout, ss.interval, ss.prefer_blanking, ss.allow_exposures)
         d.sync()
         ss = d.get_screen_saver()
         print("Screen saver timeout now is: ", ss.timeout)

      if hideDecorations == True:
         self.get_window().set_decorations(Gdk.WMDecoration.BORDER)

      self.get_window().fullscreen()

   def __del__(self):
      self.RunEventThread = False
#      if self.eventThread.is_alive():
#         self.eventThread.join()


try:
   print("CWD: ", os.getcwd())
   # Need a better way to inform
   # the CR101 code on the path
   # of its resources, such as
   # images...
   os.chdir('/home/pi/CR101py/')
   print("Argv: ", len(sys.argv))

   hideUI = False
   hideDecorations = False

   for a in sys.argv:
      if a == "-hui":
         hideUI = True
      elif a == "-hdec":
         hideDecorations = True

   CSS.mainStyle()
   app = PyApp(hideUI, hideDecorations)
   Gtk.main()
except KeyboardInterrupt:
   app.i2c.Close()
