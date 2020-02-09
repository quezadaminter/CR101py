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
      Gtk.Dialog.__init__(self, "Add To Queue", parent, 0,
            (Gtk.STOCK_NO, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_YES, Gtk.ResponseType.OK))

      self.set_default_size(80, 100)
      label = Gtk.Label("Do you want to add item to queue?")

      box = self.get_content_area()
      box.add(label)
      self.show_all()

class MediaListAlbumsPage(MediaListItemsPage):

   def on_Button_Ok_Clicked(self):
      # Enter selected item's function
      model, treeiter = self.select.get_selected()
      if treeiter is not None:
         print(model.get_value(treeiter, 0))
         if self.selectedZone is not None:
            page = self.topLevel.get_page("MediaListTracksPage")
            search_type = "artists"

            if page is not None:
               page.clear()
               artist = model.get_value(treeiter, 2)
               album = model.get_value(treeiter, 0)
               if album == "All":
                  results = self.selectedZone.sonos.music_library.get_music_library_information(search_type=search_type, subcategories=[artist, ''], complete_result=True)
               else:
                  results = self.selectedZone.sonos.music_library.get_music_library_information(search_type=search_type, subcategories=[artist, album], complete_result=True)
               page.set_items(search_type, results, self)
               self.topLevel.show_page(page)

   def title(self):
      self.titleLabel = Gtk.Label("Media Albums List")
      return(self.titleLabel)

   def scrolledWindow(self):
      self.arrowMore = Gtk.IconTheme.get_default().load_icon("image-loading", 16, 0)
      self.libStore = Gtk.ListStore(str, GdkPixbuf.Pixbuf, str, bool, object)
      self.libListView = Gtk.TreeView(self.libStore)
      self.libListView.set_headers_visible(False)

      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("Type", rend, text=0)
      col.set_resizable(False)
      col.set_expand(False)
      self.libListView.append_column(col)
      
      rend = Gtk.CellRendererPixbuf()
      rend.set_property('cell-background', 'white')
      col = Gtk.TreeViewColumn("I", rend, pixbuf = 1)
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
      pass

   def appendRow(self, item_dict, data_type, DidlItem):
      if item_dict is not None:
         if 'creator' in item_dict:
            creator = item_dict['creator']
         else:
            creator = item_dict['parent_id'].rsplit('/', 1)[-1]
         self.libStore.append([self.printPatterns(data_type).format(**item_dict), self.arrowMore, creator, True, DidlItem])
      else:
         self.libStore.append(["No Albums Found", self.arrowMore, "None", True, None])

   def __init__(self, topLevel):
      super().__init__(topLevel)
