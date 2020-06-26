import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from PageBase import PageBase
from enum import Enum
from zoneListener import ZoneListener



class EditQueueDialog(Gtk.Dialog):

   class Choice(Enum):
      SAVE_QUEUE = 0
      REMOVE_TRACK = 1
      MOVE_TRACK = 2

   def on_tree_selection_changed(self, selection):
       model, treeiter = selection.get_selected()
       if treeiter is not None:
         self.listView.scroll_to_cell(model.get_path(treeiter), column=None, use_align=False, row_align=0.0, col_align=0.0)
         print("Selected: ", model.get_value(treeiter, 0))

         option = model.get_value(treeiter, 1)
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
      Gtk.Dialog.__init__(self, "", parent, 0)

      self.selection = None

      self.listStore = Gtk.ListStore(str, object)
      self.listView = Gtk.TreeView(self.listStore)
      self.listView.set_headers_visible(False)
      
      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("Type", rend, text=0)
      col.set_resizable(False)
      col.set_expand(False)
      self.listView.append_column(col)
      
      #self.listStore.append(["Save Queue", self.Choice.SAVE_QUEUE])
      self.listStore.append(["Remove Track", self.Choice.REMOVE_TRACK])
      #self.listStore.append(["Move Track", self.Choice.MOVE_TRACK])

      self.select = self.listView.get_selection()
      self.select.connect("changed", self.on_tree_selection_changed)
      
      self.selected_row_iter = self.listStore.get_iter_first()
      if self.selected_row_iter is not None:
         self.select.select_iter(self.selected_row_iter)

      box = self.get_content_area()
      box.add(self.listView)
      self.show_all()

class ClearDialog(Gtk.Dialog):
   def __init__(self, parent):
      Gtk.Dialog.__init__(self, "Clear Queue", parent, 0,
            (Gtk.STOCK_NO, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_YES, Gtk.ResponseType.OK))

      self.set_default_size(80, 100)
      label = Gtk.Label("Are you sure you want to remove all\nitems from the queue?")

      box = self.get_content_area()
      box.add(label)
      self.show_all()

class QueuePage(PageBase):

   class State(Enum):
      LIST = 1
      EDIT = 2
      MOVE = 3
      SAVE = 4

   class zoneListener(ZoneListener):
      def __init__(self, owner):
         super().__init__(owner)

      def on_selected_zone_changed(self):
         #Consider refreshing the queue
         #although this should not happen
         #to the controller from the QueuePage.
         pass

      def on_zone_transport_change_event(self, event):
         #Update the icon on the list that shows
         #the current track playback state
         pass

      def on_zone_render_change_event(self, event):
         pass

      def on_zone_queue_update_begin(self):
         self.owner.on_zone_queue_update_begin()

      def on_zone_queue_update_end(self):
         self.owner.on_zone_queue_update_end()

      def on_current_track_update_state(self, trackInfo):
         pass
   
   def closeEditDialog(self):
      self.editQueueDialog.destroy()
      self.editQueueDialog = None

   def closeSaveQueueDialog(self):
      self.saveQueueDialog.destroy()
      self.saveQueueDialog = None

   def handleEditResponse(self):
      response = self.editQueueDialog.get_response()
      self.closeEditDialog()
      if response == EditQueueDialog.Choice.SAVE_QUEUE:
         # Open save queue dialog.
         # Set state to SAVE
         pass
      elif response == EditQueueDialog.Choice.REMOVE_TRACK:
         self.state = self.State.LIST
         if self.topLevel.get_selected_zone() is not None:
            position = self.get_selected_item_index()
            if position is not None:
               self.topLevel.get_selected_zone().remove_track_from_queue(position)
      elif response == EditQueueDialog.Choice.MOVE_TRACK:
         self.bButtonLabel.set_text("Place Track")
         self.state = self.State.MOVE
         # copy queueStore to moveStore
         # swap model in view

   def get_selected_item_index(self):
      position = None
      model, treeiter = self.select.get_selected()
      if treeiter is not None:
         if self.topLevel.get_selected_zone() is not None:
            position = self.zoneListView.get_selection().get_selected_rows()[1][0][0]
      return position

   def place_track(self, position):
      self.state = self.State.LIST
      self.bButtonLabel.set_text("Clear Queue")
      #swap back model in view to queueStore
      self.moveStore.clear()
      self.moveStore = None
      if position is not None:
         pass
         #place track in new position

   def on_zoneButton_Clicked(self, button):
      #Close any open dialogs and
      # reset the state to LIST
      # before closing.
       print("Zone Button clicked")

   def on_Page_Entered_View(self, zone):
      super().on_Page_Entered_View(zone)
      if zone is not None:
         print("Queue in view")
         self.queueStore = zone.get_queue_store()
         self.zoneListView.set_model(self.queueStore)
         self.selected_row_iter = self.queueStore.get_iter_first()
         if self.selected_row_iter is not None:
            self.select.select_iter(self.selected_row_iter)

   def on_Button_A_Clicked(self):
      if self.state == self.State.LIST:
         self.editQueueDialog = EditQueueDialog(self.get_toplevel())
         self.editQueueDialog.set_decorated(False)
         self.state = self.State.EDIT
      elif self.state == self.State.EDIT:
         self.handleEditResponse()
         # Works as the OK/Select/Enter function

   def on_Button_B_Clicked(self):
      if self.state == self.State.LIST:
         dialog = ClearDialog(self.get_toplevel())
         response = dialog.run()

         if response == Gtk.ResponseType.OK:
            self.queueStore.clear()
            if self.selectedZone is not None:
               self.selectedZone.sonos.clear_queue()

         elif response == Gtk.ResponseType.CANCEL:
               print("The Cancel button was clicked")

         dialog.destroy()
      elif self.state == self.State.MOVE:
         self.place_track(self.get_selected_item_index())

   def on_Button_C_Clicked(self):
      if self.state == self.State.LIST:
         self.topLevel.hide_queue_page()

   def on_Return_Button_Clicked(self):
      if self.state == self.State.LIST:
         self.topLevel.hide_queue_page()
      else:
         if self.editQueueDialog is not None:
            self.closeEditDialog()
         elif self.saveQueueDialog is not None:
            self.closeSaveQueueDialog()
         self.state = self.State.LIST

   # The scroll wheel
   def on_Scroll_Up(self):
      if self.state == self.State.LIST:
         if self.selected_row_iter is not None:
            self.selected_row_iter = self.queueStore.iter_previous(self.selected_row_iter)
            if self.selected_row_iter is None:
               self.selected_row_iter = self.queueStore.get_iter_first()
            self.select.select_iter(self.selected_row_iter)
      elif self.state == self.State.MOVE:
         #Same but for the moveStore
         pass

   def on_Scroll_Down(self):
      if self.state == self.State.LIST:
         if self.selected_row_iter is not None:
            last = self.selected_row_iter
            self.selected_row_iter = self.queueStore.iter_next(self.selected_row_iter)
            if self.selected_row_iter is None:
               self.selected_row_iter = last
            self.select.select_iter(self.selected_row_iter)
      elif self.state == self.State.MOVE:
         #same but for the moveStore
         pass

   def on_Button_Ok_Clicked(self):
      position = self.get_selected_item_index()
      if position is not None:
         if self.state == self.State.LIST:
            if self.topLevel.get_selected_zone() is not None:
               self.topLevel.get_selected_zone().play_track_at_position(position + 1)
         elif self.state == self.State.EDIT:
            self.handleEditResponse()
         elif self.state == self.State.MOVE:
            self.place_track(position)

   def on_zone_queue_update_begin(self):
      # Capture reference object
      # so we can re-select it after
      # the queue is edited.
      pass

   def on_zone_queue_update_end(self):
      # Recapture any selected objects.
      pass

   def on_tree_selection_changed(self, selection):
      model, treeiter = selection.get_selected()
      if treeiter is not None:
         self.zoneListView.scroll_to_cell(model.get_path(treeiter), column=None, use_align=False, row_align=0.0, col_align=0.0)
#       model, treeiter = selection.get_selected()
#       if treeiter is not None and Zones is not None:
#          print("Selected: ", model.get_value(treeiter, 1))

   def title(self):
      self.titleLabel = Gtk.Label("Queue")
      return(self.titleLabel)

   def scrolledWindow(self):
      self.queueStore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, object)
      self.zoneListView = Gtk.TreeView(self.queueStore)
      self.zoneListView.set_headers_visible(False)

      rend = Gtk.CellRendererPixbuf()
      rend.set_property('cell-background', 'white')
      col = Gtk.TreeViewColumn("I", rend, pixbuf = 0)
      col.set_resizable(False)
      col.set_expand(False)
      self.zoneListView.append_column(col)

      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("Track", rend, text=1)
      col.set_resizable(False)
      col.set_expand(False)
      self.zoneListView.append_column(col)

      self.select = self.zoneListView.get_selection()
      self.select.connect("changed", self.on_tree_selection_changed)

      self.selected_row_iter = self.queueStore.get_iter_first()
      if self.selected_row_iter is not None:
         self.select.select_iter(self.selected_row_iter)

      sw = Gtk.ScrolledWindow()
      sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
      sw.add(self.zoneListView)
      return(sw)

   def status(self):
      return Gtk.Label("Status goes here.")

   def footer(self):
      grid = Gtk.Grid()
      l = Gtk.Label("Edit Queue")
      l.set_hexpand(True)
      l.set_size_request(100, -1)
      grid.add(l)

      self.bButtonLabel = Gtk.Label("Clear Queue")
      self.bButtonLabel.set_hexpand(True)
      self.bButtonLabel.set_size_request(100, -1)
      grid.attach(self.bButtonLabel, 1, 0, 1, 1)

      l = Gtk.Label("Close Queue")
      l.set_hexpand(True)
      l.set_size_request(100, -1)
      grid.attach(l, 2, 0, 1, 1)

      return grid

   def __init__(self, topLevel):
      super().__init__(topLevel)
      self.editQueueDialog = None
      self.saveQueueDialog = None
      self.bButtonLabel = None
      self.moveStore = None
      self.state = self.State.LIST
      self.zlistener = self.zoneListener(self)
      self.topLevel.add_zone_listener(self.__class__.__name__, self.zlistener)
