import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
from gi.repository import Gio
from gi.repository import Pango
from PageBase import PageBase
from threading import Lock
from zoneListener import ZoneListener
from image import Image
from scrollLabel import ScrollLabel

import imageManager
import requests

mutex = Lock()

class MusicAlbumArtPage(PageBase):

   class zoneListener(ZoneListener):
      def __init__(self, owner):
         super().__init__(owner)

      def on_selected_zone_changed(self):
         if self.owner.pageInView == True:
            self.owner.on_Page_Entered_View(None)

      def on_zone_transport_change_event(self, event):
         if self.owner.pageInView == True:
            self.owner.on_zone_transport_change_event(event)

      def on_zone_render_change_event(self, event):
         pass

      def on_zone_queue_update_begin(self):
         pass

      def on_zone_queue_update_end(self):
         pass
      
      def on_current_track_update_state(self, trackInfo):
         pass

   def on_Page_Entered_View(self, SelectedZone):
      super().on_Page_Entered_View(SelectedZone)
      if self.selectedZone is not None:
         self.on_zone_transport_change_event(self.selectedZone.get_current_transport_info())
         self.on_current_track_update_state(self.selectedZone.get_current_track_info())
      print("Album art in view")

   def on_current_track_update_state(self, trackInfo):
      mutex.acquire()

      try:
         if isinstance(trackInfo, dict):
            self.set_album_art(trackInfo)
            
            if trackInfo['artist'] == "" or trackInfo["title"] == "":
               self.musicLabel.set_markup("[no music]")
               #self.musicLabel.set_markup("<span size=\"12000\"><b>[no music]</b></span>")
            else:
               #music = GLib.markup_escape_text(trackInfo['title'] + " - " + trackInfo['artist'])
               #self.musicLabel.set_markup("<span size=\"12000\"><b>" + music + "</b></span>")
               music = (trackInfo['title'] + " - " + trackInfo['artist'])
               self.musicLabel.set_markup(music)
            

      finally:
         mutex.release()

   def set_album_art(self, data):
      artUri = ""
      if 'album_art_uri' in data:
         artUri = data['album_art_uri']
      elif 'album_art' in data:
         artUri = data['album_art']

      if artUri != "":
         self.albumArtUri = self.topLevel.get_selected_zone().sonos.music_library.build_album_art_full_uri(artUri)
         response = requests.get(self.albumArtUri)
         if response.status_code == 200:
            im = Image(None)
            im.SetFromStream(response.content)
            self.albumArtImage.set_from_pixbuf(im.Scale(250, 250))
      else:
         self.albumArtImage.set_from_pixbuf(imageManager.get_image('noArt').Scale(250, 250))

   def on_zone_transport_change_event(self, event):
      mutex.acquire()

      try:
         if hasattr(event, 'variables'):
            varDict = event.variables
         else:
            varDict = event

         if 'current_track_meta_data' in varDict:
            currentTrackMetaData = varDict['current_track_meta_data']
            if currentTrackMetaData is not '':
               currentTrackMetaData = currentTrackMetaData.to_dict()
               #music = GLib.markup_escape_text(currentTrackMetaData['title'] + " - " + currentTrackMetaData['creator'])
               #self.musicLabel.set_markup("<span size=\"12000\"><b>" + music + "</b></span>")
               music = (currentTrackMetaData['title'] + " - " + currentTrackMetaData['creator'])
               self.musicLabel.set_markup(music)

               #if self.topLevel.get_selected_zone() is not None and 'album_art_uri' in currentTrackMetaData:
               if self.topLevel.get_selected_zone() is not None:
                  self.set_album_art(currentTrackMetaData)
               else:
                  #self.albumArtImage.set_from_file('./images/NoAlbumArt.jpg')
                  self.albumArtImage.set_from_file('./images/AlbumArtEmpty.jpg')
                  pixbuf = self.albumArtImage.get_pixbuf().scale_simple(250, 250, GdkPixbuf.InterpType.BILINEAR)
                  self.albumArtImage.set_from_pixbuf(pixbuf)
            else:
               #self.musicLabel.set_markup("<span size=\"12000\"><b>[no music]</b></span>")
               self.musicLabel.set_markup("[no music]")
               self.albumArtImage.set_from_file('./images/AlbumArtEmpty.jpg')
               pixbuf = self.albumArtImage.get_pixbuf().scale_simple(250, 250, GdkPixbuf.InterpType.BILINEAR)
               self.albumArtImage.set_from_pixbuf(pixbuf)
      finally:
         mutex.release()

   def on_Button_A_Clicked(self):
      pass

   def on_Button_B_Clicked(self):
      pass

   def on_Button_C_Clicked(self):
      pass

   def on_Return_Button_Clicked(self):
      self.topLevel.show_page("MusicPlayingPage")

   # The scroll wheel
   def on_Scroll_Up(self):
      pass

   def on_Scroll_Down(self):
      pass

   def on_Button_Ok_Clicked(self):
      self.topLevel.show_page("MusicPlayingPage")

   def title(self):
      #self.titleLabel = Gtk.Label("Now Playing (Album Art)")
      return(Gtk.VBox())

   def scrolledWindow(self):
      vbox = Gtk.VBox()

      self.albumArtImage = Gtk.Image()
      self.albumArtImage.set_from_file('./images/AlbumArtEmpty.jpg')
      pixbuf = self.albumArtImage.get_pixbuf().scale_simple(250, 250, GdkPixbuf.InterpType.BILINEAR)
      self.albumArtImage.set_from_pixbuf(pixbuf)
      self.albumArtImage.show()
      vbox.pack_start(self.albumArtImage, True, True, 5)

      self.musicLabel = ScrollLabel(1)#Gtk.Label()
      music = "[no music]"
      #self.musicLabel.set_markup("<span size=\"12000\"><b>" + music + "</b></span>")
      self.musicLabel.assign_markup("<span size=\"12000\"><b> {0} </b></span>")
      self.musicLabel.set_markup(music)
      self.musicLabel.set_max_width_chars(25)
      self.musicLabel.set_ellipsize(Pango.EllipsizeMode.END)
      vbox.pack_start(self.musicLabel, False, False, 0)

      return(vbox)

   def status(self):
      pass

   def footer(self):
      return Gtk.VBox()

   def __init__(self, topLevel):
      super().__init__(topLevel)
      self.zlistener = self.zoneListener(self)
      self.topLevel.add_zone_listener(self.__class__.__name__, self.zlistener)
