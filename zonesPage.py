import soco
import gi
import psutil
import socket
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from PageBase import PageBase
from Zone import Zone
from zoneListener import ZoneListener

Zones = []

class Dialog(Gtk.Dialog):
   def __init__(self, parent):
      Gtk.Dialog.__init__(self, "Pause All", parent, 0,
            (Gtk.STOCK_NO, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_YES, Gtk.ResponseType.OK))

      self.set_default_size(80, 100)
      label = Gtk.Label("Do you want to pause all devices?")

      box = self.get_content_area()
      box.add(label)
      self.show_all()

class ZonesPage(PageBase):

   def on_Page_Entered_View(self, SelectedZone):
      self.scanForZones()
      pass

   def on_Back_Button_Clicked(self):
       pass

   def on_Button_A_Clicked(self):
      pass

   def on_Button_B_Clicked(self):
       pass

   def on_Button_C_Clicked(self):
      dialog = Dialog(self.get_toplevel())
      response = dialog.run()

      if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
      elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

      dialog.destroy()

   def on_Return_Button_Clicked(self):
       pass

   # The scroll wheel
   def on_Scroll_Up(self):
      if self.selected_row_iter is not None:
         self.selected_row_iter = self.zoneStore.iter_previous(self.selected_row_iter)
         if self.selected_row_iter is None:
            self.selected_row_iter = self.zoneStore.get_iter_first()
         self.select.select_iter(self.selected_row_iter)

   def on_Scroll_Down(self):
      if self.selected_row_iter is not None:
         last = self.selected_row_iter
         self.selected_row_iter = self.zoneStore.iter_next(self.selected_row_iter)
         if self.selected_row_iter is None:
            self.selected_row_iter = last
         self.select.select_iter(self.selected_row_iter)

   def on_Button_Ok_Clicked(self):
#      if len(Zones) is > 0:
          model, treeiter = self.select.get_selected()
          if treeiter is not None:
            self.selectedZone = model.get_value(treeiter, 4)
            if self.selectedZone is not None:
               self.selectedZone.on_zone_selected()
               self.titleLabel.set_text("Rooms : " + model.get_value(treeiter, 1))

   def on_tree_selection_changed(self, selection):
       model, treeiter = selection.get_selected()
       if treeiter is not None: # and Zones is not None:
          print("Selected: ", model.get_value(treeiter, 1))

   def on_zone_transport_change_event(self, event):
      if self.zoneListener is not None:
         self.zoneListener.on_zone_transport_change_event(event)

#      mp = self.topLevel.get_page("MusicPlayingPage")
#      mp.on_zone_transport_change_event(event)

      for row in self.zoneStore:
         if row[1] == event.service.soco.player_name:
            row[3] = event.variables['transport_state']
            break

   def on_zone_render_change_event(self, event):
      if self.zoneListener is not None:
         self.zoneListener.on_zone_render_change_event(event)

      for row in self.zoneStore:
         if row[1] == event.service.soco.player_name:
            break

   def on_zone_queue_update_begin(self):
      if self.zoneListener is not None:
         self.zoneListener.on_zone_queue_update_begin()
#      qp = self.topLevel.get_page("QueuePage")
#      qp.on_zone_queue_update_begin()

   def on_zone_queue_update_end(self):
      if self.zoneListener is not None:
         self.zoneListener.on_zone_queue_update_end()
#      qp = self.topLevel.get_page("QueuePage")
#      qp.on_zone_queue_update_end()

   def on_current_track_update_state(self, trackInfo):
      if self.zoneListener is not None:
         self.zoneListener.on_current_track_update_state(trackInfo)
#      mp = self.topLevel.get_page("MusicPlayingPage")
#      mp.on_current_track_update_state(trackInfo)

   def title(self):
      self.titleLabel = Gtk.Label("Rooms")
      return(self.titleLabel)

   def scrolledWindow(self):
      self.testSymbol = Gtk.IconTheme.get_default().load_icon("media-optical", 16, 0)
      self.testSymbol2 = Gtk.IconTheme.get_default().load_icon("image-loading", 16, 0)
      self.zoneStore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, GdkPixbuf.Pixbuf, str, object)
      self.zoneListView = Gtk.TreeView(self.zoneStore)
      self.zoneListView.set_headers_visible(False)

      rend = Gtk.CellRendererPixbuf()
      rend.set_property('cell-background', 'white')
      col = Gtk.TreeViewColumn("I", rend, pixbuf = 0)
      col.set_resizable(False)
      col.set_expand(False)
      self.zoneListView.append_column(col)

      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("Name", rend, text=1)
      col.set_resizable(False)
      col.set_expand(False)
      self.zoneListView.append_column(col)

      rend = Gtk.CellRendererPixbuf()
      rend.set_property('cell-background', 'white')
      col = Gtk.TreeViewColumn("I", rend, pixbuf = 2)
      col.set_resizable(False)
      col.set_expand(False)
      self.zoneListView.append_column(col)

      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("State", rend, text=3)
      col.set_resizable(False)
      col.set_expand(False)
      self.zoneListView.append_column(col)

      self.select = self.zoneListView.get_selection()
      self.select.connect("changed", self.on_tree_selection_changed)

      self.selected_row_iter = self.zoneStore.get_iter_first()
      if self.selected_row_iter is not None:
         self.select.select_iter(self.selected_row_iter)

      sw = Gtk.ScrolledWindow()
      sw.set_policy(1, 1)
#      Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
      sw.add(self.zoneListView)
      return(sw)

   def status(self):
      return Gtk.Label("Status goes here.")

   def footer(self):

      grid = Gtk.Grid()
      l = Gtk.Label("Link Zone")
      l.set_hexpand(True)
      l.set_size_request(100, -1)
      grid.add(l)

      l = Gtk.Label("Drop Zone")
      l.set_hexpand(True)
      l.set_size_request(100, -1)
      grid.attach(l, 1, 0, 1, 1)

      l = Gtk.Label("Pause All")
      l.set_hexpand(True)
      l.set_size_request(100, -1)
      grid.attach(l, 2, 0, 1, 1)

      return grid

   def set_listener(self, listener):
      self.zoneListener = listener

   def __init__(self, topLevel):
      super().__init__(topLevel)
      self.zoneListener = None

   def scanForZones(self):
      print("SCAN!")
      global Zones

      addressDict = psutil.net_if_addrs()
      ipList = []
      for key in addressDict:
         intf = addressDict[key]
         for l in intf:
            if l.family == socket.AddressFamily.AF_INET and l.address.startswith('192.168.'):
               ipList.append(l.address)
      #zones = soco.discover(interface_addr='192.168.1.86')
      for ip in ipList:
         zones = soco.discover(timeout=1, interface_addr=ip)
         if zones is not None and len(Zones) != len(zones):
            self.zoneStore.clear()
            if len(zones) > 0:
               self.titleLabel.set_label("Rooms (" + str(len(zones)) + ")")
               for zone in zones:
                  z = Zone(zone, self)
                  Zones.append(z)
                  self.zoneStore.append([self.testSymbol, zone.player_name, self.testSymbol2, zone.get_current_transport_info()["current_transport_state"], z])
#                  print(zone.get_current_transport_info())
               self.selected_row_iter = self.zoneStore.get_iter_first()
               self.select.select_iter(self.selected_row_iter)
               break
         elif zones is None:
            print("No zones found at " + ip)
         else:
            print("CACHED!")

      if zones is None:
         self.titleLabel.set_label("No Zones Found")
      self.show_all()

