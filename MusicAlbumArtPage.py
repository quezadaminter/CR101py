import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from PageBase import PageBase

class MusicAlbumArtPage(PageBase):

   def on_zoneButton_Clicked(self, button):
       print("Zone Button clicked")

   def on_Page_Entered_View(self, SelectedZone):
      print("Album art in view")

   def on_Button_A_Clicked(self):
      pass

   def on_Button_B_Clicked(self):
       pass

   def on_Button_C_Clicked(self):
       self.topLevel.show_queue_page()

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
      self.titleLabel = Gtk.Label("Now Playing (Album Art)")
      return(self.titleLabel)

   def scrolledWindow(self):
      sw = Gtk.ScrolledWindow()
      sw.set_policy(1, 1)
#      Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
#      sw.add(self.zoneListView)
      return(sw)

   def status(self):
      pass

   def footer(self):
      grid = Gtk.Grid()
      l = Gtk.Label("View Clock")
      l.set_size_request(100, -1)
      grid.add(l)
      l = Gtk.Label(" ")
      l.set_size_request(100, -1)
      grid.attach(l, 1, 0, 1, 1)
      l = Gtk.Label("View Queue")
      l.set_size_request(100, -1)
      grid.attach(l, 2, 0, 1, 1)
      return grid

   def __init__(self):
      super().__init__()
