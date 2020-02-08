import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
from gi.repository import Gio

class Image():
   def __init__(self, fileName):
      super().__init__()

      if fileName is not None:
         self.pixbuf = GdkPixbuf.Pixbuf().new_from_file(fileName)
      else:
         self.pixbuf = None

   def GetPixbuf(self):
      return(self.pixbuf)

   def SetFromStream(self, stream):
      if self.pixbuf is None:
         self.pixbuf = GdkPixbuf.Pixbuf()

      input_stream = Gio.MemoryInputStream.new_from_data(stream, None) 
      self.pixbuf = self.pixbuf.new_from_stream(input_stream, None)
      return self

   def Scale(self, w, h):
      if self.pixbuf is not None:
         return self.pixbuf.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR)
      else:
         return self.pixbuf