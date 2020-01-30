import soco
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from PageBase import PageBase
from Zone import Zone
from socos.music_lib import MusicLibrary
from mediaListItemsPage import MediaListItemsPage

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

class UpdateMusicIndex():
   def __init__(self):
      pass

   def run(self, zone):
      if zone is not None:
         if(zone.sonos.music_library.library_updating == False):
            print("Updating music Index!")
            zone.sonos.music_library.start_library_update()
         else:
            print("Index update is currently in process.")


class SystemSettingsPage(PageBase):

   def on_zoneButton_Clicked(self, button):
       print("System Settings Page")

   def on_Page_Entered_View(self, SelectedZone):
      self.selectedZone = SelectedZone

   def on_Button_A_Clicked(self):
      pass

   def on_Button_B_Clicked(self):
      #Add to queue only if selected row item (2) is True
      pass

   def on_Button_C_Clicked(self):
#       self.topLevel.show_queue_page()
      pass

   def on_Return_Button_Clicked(self):
      self.topLevel.show_page("MusicPage")

   # The scroll wheel
   def on_Scroll_Up(self):
      if self.selected_row_iter is not None:
         self.selected_row_iter = self.libStore.iter_previous(self.selected_row_iter)
         if self.selected_row_iter is None:
            self.selected_row_iter = self.libStore.get_iter_first()
         self.select.select_iter(self.selected_row_iter)

   def on_Scroll_Down(self):
      if self.selected_row_iter is not None:
         last = self.selected_row_iter
         self.selected_row_iter = self.libStore.iter_next(self.selected_row_iter)
         if self.selected_row_iter is None:
            self.selected_row_iter = last
         self.select.select_iter(self.selected_row_iter)

   def on_Button_Ok_Clicked(self):
      # Enter selected item's function
      model, treeiter = self.select.get_selected()
      if treeiter is not None:
         print(model.get_value(treeiter, 0))
         if self.selectedZone is not None:
            ui = model.get_value(treeiter, 2)
            ui.run(self.selectedZone)

   def on_tree_selection_changed(self, selection):
      # if row item (2) is false hide B button label, else show it
       model, treeiter = selection.get_selected()
       if treeiter is not None: # and Zones is not None:
          print("Selected: ", model.get_value(treeiter, 0))

   def on_zone_transport_change_event(self, event):
      pass

   def on_zone_render_change_event(self, event):
      pass

   def title(self):
      self.titleLabel = Gtk.Label("System Settings")
      return(self.titleLabel)

   def scrolledWindow(self):
      self.arrowMore = Gtk.IconTheme.get_default().load_icon("image-loading", 16, 0)
      self.libStore = Gtk.ListStore(str, bool, object)
      self.libListView = Gtk.TreeView(self.libStore)
      self.libListView.set_headers_visible(False)

      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("Type", rend, text=0)
      col.set_resizable(False)
      col.set_expand(False)
      self.libListView.append_column(col)
      
#      rend = Gtk.CellRendererPixbuf()
#      rend.set_property('cell-background', 'white')
#      col = Gtk.TreeViewColumn("I", rend, pixbuf = 1)
#      col.set_resizable(False)
#      col.set_expand(False)
#      self.libListView.append_column(col)

      # Possible browsing items
      self.updateIndex = UpdateMusicIndex()
      self.libStore.append(["Update Music Index", True, self.updateIndex])

      self.select = self.libListView.get_selection()
      self.select.connect("changed", self.on_tree_selection_changed)
      
      self.selected_row_iter = self.libStore.get_iter_first()
      if self.selected_row_iter is not None:
         self.select.select_iter(self.selected_row_iter)

      sw = Gtk.ScrolledWindow()
      sw.set_policy(1, 1)
#      Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
      sw.add(self.libListView)
      return(sw)

   def status(self):
      return Gtk.Label("Status goes here.")

   def footer(self):

      grid = Gtk.Grid()
      l = Gtk.Label(" ")
      l.set_size_request(100, -1)
      grid.add(l)

      l = Gtk.Label("Add to Queue")
      l.set_size_request(100, -1)
      grid.attach(l, 1, 0, 1, 1)

      l = Gtk.Label("View Queue")
      l.set_size_request(100, -1)
      grid.attach(l, 2, 0, 1, 1)

      return grid

   def __init__(self, topLevel):
      super().__init__(topLevel)
