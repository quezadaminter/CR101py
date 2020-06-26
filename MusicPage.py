import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from PageBase import PageBase

class MusicPage(PageBase):

   def on_Button_A_Clicked(self):
      pass

   def on_Button_B_Clicked(self):
       pass

   def on_Button_C_Clicked(self):
       self.topLevel.show_queue_page()

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
      model, treeiter = self.select.get_selected()
      if treeiter is not None:
         self.topLevel.show_page(model.get_value(treeiter, 2))

   def on_tree_selection_changed(self, selection):
       model, treeiter = selection.get_selected()
       if treeiter is not None and Zones is not None:
          self.zoneListView.scroll_to_cell(model.get_path(treeiter), column=None, use_align=False, row_align=0.0, col_align=0.0)
#          print("Selected: ", model.get_value(treeiter, 1))

   def title(self):
      self.titleLabel = Gtk.Label("Music")
      return(self.titleLabel)

   def scrolledWindow(self):
      self.arrowMore = Gtk.IconTheme.get_default().load_icon("image-loading", 16, 0)

      self.zoneStore = Gtk.ListStore(str, GdkPixbuf.Pixbuf, str, object)
      self.zoneListView = Gtk.TreeView(self.zoneStore)
      self.zoneListView.set_headers_visible(False)

      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("Service", rend, text=0)
      col.set_resizable(False)
      col.set_expand(False)
      self.zoneListView.append_column(col)

      rend = Gtk.CellRendererPixbuf()
      rend.set_property('cell-background', 'white')
      col = Gtk.TreeViewColumn("I", rend, pixbuf = 1)
      col.set_resizable(False)
      col.set_expand(False)
      self.zoneListView.append_column(col)

      # How do we get the list of services??
      self.zoneStore.append(["Music Library", self.arrowMore, "MusicLibraryPage", None])
      self.zoneStore.append(["Amazon Music", self.arrowMore, "AmazonMusicPage", None])
      self.zoneStore.append(["Line In", self.arrowMore, "LineInPage", None])
      self.zoneStore.append(["Clock and Alarms", self.arrowMore, "ClockAndAlarmsPage", None])
      self.zoneStore.append(["System Settings", self.arrowMore, "SystemSettingsPage", None])

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
      l = Gtk.Label("View Clock")
      l.set_hexpand(True)
      l.set_size_request(100, -1)
      grid.add(l)
      l = Gtk.Label(" ")
      l.set_hexpand(True)
      l.set_size_request(100, -1)
      grid.attach(l, 1, 0, 1, 1)
      l = Gtk.Label("View Queue")
      l.set_hexpand(True)
      l.set_size_request(100, -1)
      grid.attach(l, 2, 0, 1, 1)
      return grid

   def __init__(self, topLevel):
      super().__init__(topLevel)
