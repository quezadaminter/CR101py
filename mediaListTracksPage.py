import soco
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from PageBase import PageBase
from Zone import Zone
from socos.music_lib import MusicLibrary
from mediaListItemsPage import MediaListItemsPage

class TrackDialog(Gtk.Dialog):
   def on_tree_selection_changed(self, selection):
       model, treeiter = selection.get_selected()
       if treeiter is not None:
         print("Selected: ", model.get_value(treeiter, 1))

         option = model.get_value(treeiter, 0)
         self.selection = option

# The scroll wheel
   def on_Scroll_Up(self):
      if self.selected_row_iter is not None:
         self.selected_row_iter = self.listStore.iter_previous(self.selected_row_iter)
         if self.selected_row_iter is None:
            self.selected_row_iter = self.listStore.get_iter_first()
         self.select.select_iter(self.selected_row_iter)

   def on_Scroll_Down(self):
      if self.selected_row_iter is not None:
         last = self.selected_row_iter
         self.selected_row_iter = self.listStore.iter_next(self.selected_row_iter)
         if self.selected_row_iter is None:
            self.selected_row_iter = last
         self.select.select_iter(self.selected_row_iter)

   def get_response(self):
      return self.selection

   def __init__(self, parent):
      Gtk.Dialog.__init__(self, "", parent, 0)#,

      self.selection = None

      self.listStore = Gtk.ListStore(str, int)
      self.listView = Gtk.TreeView(self.listStore)
      self.listView.set_headers_visible(False)
      
      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("Type", rend, text=0)
      col.set_resizable(False)
      col.set_expand(False)
      self.listView.append_column(col)
      
      self.listStore.append(["Play Now", 0])
      self.listStore.append(["Play Next", 1])
      self.listStore.append(["Add to End of Queue", 2])
      self.listStore.append(["Play Now and Replace Queue", 3])

      self.select = self.listView.get_selection()
      self.select.connect("changed", self.on_tree_selection_changed)
      
      self.selected_row_iter = self.listStore.get_iter_first()
      if self.selected_row_iter is not None:
         self.select.select_iter(self.selected_row_iter)

      box = self.get_content_area()
      box.add(self.listView)
      self.show_all()

class MediaListTracksPage(MediaListItemsPage):

   def closeDialog(self):
      self.trackDialog.destroy()
      self.trackDialog = None

   def on_zoneButton_Clicked(self):
      if self.trackDialog is not None:
         self.closeDialog()

      super().on_zoneButton_Clicked()

   def on_musicButton_Clicked(self):
      if self.trackDialog is None:
         super().on_musicButton_Clicked()
      else:
         self.closeDialog()

   def on_tree_selection_changed(self, selection):
       model, treeiter = selection.get_selected()
       if treeiter is not None:
          print("Selected: ", model.get_value(treeiter, 1))

   def on_Button_B_Clicked(self):
      model, treeiter = self.select.get_selected()
      if treeiter is not None:
         if self.selectedZone is not None:
            val1 = model.get_value(treeiter, 2)
            didl = model.get_value(treeiter, 3)
            if didl is None and val1 == True:
               # Add all tracks
               for row in self.libStore:
                  if row[1] != "All Tracks":
                     self.topLevel.get_selected_zone().add_to_queue(row[3])
            elif didl is not None:
               # play or queue the track
               self.selectedZone.add_to_queue(didl)

   def on_Return_Button_Clicked(self):
      if self.trackDialog is None:
         super().on_Return_Button_Clicked()
      else:
         self.closeDialog()

   def on_Scroll_Up(self):
      if self.trackDialog is None:
         super().on_Scroll_Up()
      else:
         self.trackDialog.on_Scroll_Up()

   def on_Scroll_Down(self):
      if self.trackDialog is None:
         super().on_Scroll_Down()
      else:
         self.trackDialog.on_Scroll_Down()

   def on_Button_Ok_Clicked(self):
      model, treeiter = self.select.get_selected()
      if treeiter is not None:
         if self.selectedZone is not None:
            if self.trackDialog is None:
               # Enter selected item's function
                     # Pop-up dialog:
                     # Plae Now, Play Next, Add to End of Queue, Play Now and Replace Queue
                     # In any case, item is adde to the queue.
                     self.trackDialog = TrackDialog(self.get_toplevel())
                     self.trackDialog.set_decorated(False)
                     self.trackDialog.show_all()
            else:
               response = self.trackDialog.get_response()
               self.closeDialog()
               if self.topLevel.get_selected_zone() is not None:
                  val1 = model.get_value(treeiter, 2)
                  didl = model.get_value(treeiter, 3)
                  if val1 is True and didl is None:
                     # Add all tracks
                     # TODO: Implement the other queueing modes as listed below.
                     for row in self.libStore:
                        if row[1] != "All Tracks":
                           self.topLevel.get_selected_zone().add_to_queue(row[3])
                  elif didl is not None:
                     if response == 0:
                        self.topLevel.get_selected_zone().play_now(model.get_value(treeiter, 3))
                     elif response == 1:
                        self.topLevel.get_selected_zone().play_next(model.get_value(treeiter, 3))
                     elif response == 2:
                        self.topLevel.get_selected_zone().add_to_queue(model.get_value(treeiter, 3))
                     elif response == 3:
                        self.topLevel.get_selected_zone().play_now_and_replace_queue(model.get_value(treeiter, 3))

   def title(self):
      self.titleLabel = Gtk.Label("Media Tracks List")
      return(self.titleLabel)

   def scrolledWindow(self):
      self.arrowMore = Gtk.IconTheme.get_default().load_icon("image-loading", 16, 0)
      self.libStore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, bool, object)
      self.libListView = Gtk.TreeView(self.libStore)
      self.libListView.set_headers_visible(False)

      rend = Gtk.CellRendererPixbuf()
      rend.set_property('cell-background', 'white')
      col = Gtk.TreeViewColumn("I", rend, pixbuf = 0)
      col.set_resizable(False)
      col.set_expand(False)
      self.libListView.append_column(col)

      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("Type", rend, text=1)
      col.set_resizable(False)
      col.set_expand(False)
      self.libListView.append_column(col)
      
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

   def prependRow(self):
      # I need a better/cleaner way of doing this...
      self.libStore.prepend([self.arrowMore, "All Tracks", True, None])

   def appendRow(self, item_dict, data_type, DidlItem):
      if item_dict is not None:
         self.libStore.append([self.arrowMore, self.printPatterns(data_type).format(**item_dict), True, DidlItem])
      else:
         self.libStore.append([self.arrowMore, "No Tracks Found", False, None])

   def __init__(self, topLevel):
      super().__init__(topLevel)
      self.trackDialog = None
