import soco
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from PageBase import PageBase
from Zone import Zone
from socos.music_lib import MusicLibrary
from abc import ABCMeta, abstractmethod

class MediaListItemsPage(PageBase):
   __metaclass__=ABCMeta
   
   def on_Page_Entered_View(self, SelectedZone):
      self.selectedZone = SelectedZone

   def on_zoneButton_Clicked(self):
      super().on_zoneButton_Clicked()

   def on_musicButton_Clicked(self):
      super().on_musicButton_Clicked()

   def on_Button_A_Clicked(self):
      pass

   def on_Button_B_Clicked(self):
      #add currently selected item to queue
      pass

   def on_Button_C_Clicked(self):
       self.topLevel.show_queue_page()

   def on_Return_Button_Clicked(self):
      self.topLevel.show_page(self.fromPage)

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
         # Show "Add to queue dialog"
         print(model.get_value(treeiter, 0))

   def on_tree_selection_changed(self, selection):
       model, treeiter = selection.get_selected()
       if treeiter is not None:
          print("Selected: ", model.get_value(treeiter, 0))

   def on_zone_transport_change_event(self, event):
      pass

   def on_zone_render_change_event(self, event):
      pass

   def title(self):
      pass

   def scrolledWindow(self):
      pass

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

   @abstractmethod
   def appendRow(self, item_dict, data_type, DidlItem):
      pass

   def clear(self):
      self.libStore.clear()

   def printPatterns(self, data_type):
      print_patterns = {
            'tracks': '{title} on {album} by {creator}',
            'albums': '{title} by {creator}',
            'artists': '{title}',
            'composers': '{title}',
            'genres': '{title}',
            'playlists': '{title}',
            'sonos_playlists': '{title}'
        }
      return(print_patterns[data_type])

   def set_items(self, data_type, results, fromPage):
      self.fromPage = fromPage

      if results is not None:
         #index_length = len(str(len(results)))
         for index, item in enumerate(results):
            item_dict = item.to_dict()
            for key, value in item_dict.items():
               if hasattr(value, 'decode'):
                  item_dict[key] = value.encode('utf-8')
            self.appendRow(item_dict, data_type, item)
      else:
         self.appendRow(None, data_type, item)

      self.selected_row_iter = self.libStore.get_iter_first()
      if self.selected_row_iter is not None:
         self.select.select_iter(self.selected_row_iter)
#         number = '({{: >{}}}) '.format(index_length).format(index + 1)
#         yield number + print_patterns[data_type].format(**item_dict)

   def __init__(self):
      # These member variables must be called before the super() constructor
      # because they will be used by the child via abstract methods.
      self.libStore = None
      self.select = None
      super().__init__()
