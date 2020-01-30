
from abc import ABCMeta, abstractmethod

class ZoneListener(object):
   __metaclass__=ABCMeta

   def __init__(self, owner):
      self.owner = owner

   @abstractmethod
   def on_selected_zone_changed(self):
      pass

   @abstractmethod
   def on_zone_transport_change_event(self, event):
      pass

   @abstractmethod
   def on_zone_render_change_event(self, event):
      pass

   @abstractmethod
   def on_zone_queue_update_begin(self):
      pass

   @abstractmethod
   def on_zone_queue_update_end(self):
      pass

   @abstractmethod
   def on_current_track_update_state(self, trackInfo):
      pass