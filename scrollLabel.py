import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GObject
from gi.repository import Pango

class ScrollLabel(Gtk.Label):

   def __init__(self, dire = 0):
      super().__init__(self)
      self.text = ""
      self.set_direction(dire)
      self.cx = 0
      self.len = 0
      self.timeout_id = None
      self.markup_format = ""
      super().set_max_width_chars(15)

   def set_direction(self, dire):
      self.direction = 1 if dire > 0 else (-1 if dire < 0 else 0)

   def __rotateBy(self, q, l):
      cl = l
      txt = list(self.text)
#      txt.append(' ')
      i = q
      j = 0
      while cl > 0:
         txt[j] = self.text[i]
         i = (i + 1) % l
         j = j + 1
         cl = cl - 1

      return "".join(txt)

   def __scroll(self):
      if self.direction > 0:
         self.cx = (self.cx + 1) % len(self.text)
      elif self.direction < 0:
         self.cx = (self.cx + len(self.text) - 1) % len(self.text)

      text = self.__rotateBy(self.cx, len(self.text))
      if self.markup_format:
         text = self.markup_format.format(text)
         super().set_markup(text)
      else:
         super().set_text(text)
      return True

   def start(self):
      if self.len > super().get_max_width_chars() and self.direction != 0 and self.timeout_id is None:
         self.timeout_id = GObject.timeout_add(250, self.__scroll)

   def stop(self):
      if self.timeout_id is not None:
         if GObject.source_remove(self.timeout_id) == False:
            print("Failed to remove timeout!!")
         self.timeout_id = None
      self.cx = 0
      text = self.__rotateBy(0, len(self.text))
      if self.markup_format:
         text = self.markup_format.format(text)
         super().set_markup(text)
      else:
         super().set_text(text)

   def set_text(self, txt):
      self.len = len(self.text)
      if not txt:
         super().set_text(txt)
      else:
         self.text = GLib.markup_escape_text(txt)
         if self.len > super().get_max_width_chars():
            self.text = self.text + "      "
         super().set_text(self.text)
         
         self.stop()
         self.start()

   def set_markup(self, txt):
      self.len = len(txt)
      if not txt:
         super().set_text(txt)
      else:
         self.text = GLib.markup_escape_text(txt)
         if self.len > super().get_max_width_chars():
            self.text = self.text + "      "

         txt = self.text
         if self.markup_format:
            txt = self.markup_format.format(self.text)
         super().set_markup(txt)

         self.stop()
         self.start()

   def assign_markup(self, fmt):
      self.markup_format = fmt