import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import soco
from soco.events import event_listener
import socos.exceptions
from socos import mixer
from soco.exceptions import SoCoUPnPException#, SoCoIllegalSeekException
import queue

class Zone():

   def update_queue(self):
        """Show the current queue"""
        queue = self.sonos.get_queue()

        # pylint: disable=invalid-name
        ANSI_BOLD = '\033[1m'
        ANSI_RESET = '\033[0m'

        current = int(self.sonos.get_current_track_info()['playlist_position'])

        print("Current index = ", current)

        queue_length = len(queue)
        padding = len(str(queue_length))

        for idx, track in enumerate(queue, 1):
            if idx == current:
                color = ANSI_BOLD
            else:
                color = ANSI_RESET

#            idx = str(idx).rjust(padding)
            yield ( [idx, track, idx == current]
#                "%s%s: %s - %s. From album %s.%s" % (
#                "%s%s: %s - %s. From album Not implemented%s" % (
#                    color,
#                    idx,
#                    track.creator,
#                    track.title,
#                    track.album,
#                    ANSI_RESET,
#                )
            )
   def on_zone_selected(self):
      self.on_queue_remote_event()

   def on_queue_remote_event(self):
      self.parent.on_zone_queue_update_begin()
      result = self.update_queue()
      if result is None:
         pass
      elif not isinstance(result, str):
         try:
            self.qStore.clear()
            for line in result:
               x = None
               if line[2] == True:
                  x = Gtk.IconTheme.get_default().load_icon("media-optical", 16, 0)
                  #x = "*"
               self.qStore.append([x, line[1].title, None])

         except (KeyError, ValueError, TypeError, socos.exceptions.SocosException, socos.exceptions.SoCoIllegalSeekException) as ex:
#            err(ex)
            return None
      else:
         print(result)

      self.parent.on_zone_queue_update_end()

   def add_to_queue(self, item):
      self.sonos.add_to_queue(item)

   def get_queue_store(self):
      self.update_queue()
      return(self.qStore)

   def get_queue_length(self):
      return(self.qStore.size())

   def volume(self, *args):
        """Change or show the volume of a device"""
        if not args:
            return str(self.sonos.volume)

        operator = args[0]
        newvolume = mixer.adjust_volume(self.sonos, operator)
        return str(newvolume)

   def mute(self, t_or_f):
      self.sonos.mute = t_or_f

   def is_muted(self):
      return self.sonos.mute

   def state(self):
        """Get the current state of a device / group"""
        return self.sonos.get_current_transport_info()['current_transport_state']

   def play_mode(self, playMode):
      self.sonos.play_mode(playMode)

   def cross_fade(self, enabled):
      self.sonos.cross_fade(enabled)

   def get_current_transport_info(self):
      return self.sonos.get_current_transport_info()

   def get_current_track_info(self):
        """Show the current track"""
        track = self.sonos.get_current_track_info()
        print(track)
        return(track)
#        return (
#            "Current track: %s - %s. From album %s. This is track number"
#            " %s in the playlist. It is %s minutes long." % (
#                track['artist'],
#                track['title'],
#                track['album'],
#                track['playlist_position'],
#                track['duration'],
#            )
#        )

   def remove_track_from_queue(self, position):
      p = self.sonos.get_current_track_info()['playlist_position']
      if int(p) - 1 == position and self.state() == 'PLAYING':
         self.sonos.stop()
      self.sonos.remove_from_queue(position)

   def play_now(self, DidlItem):
      # Add to end of Queue and play
      self.stop()
      self.add_to_queue(DidlItem)
      q = self.sonos.get_queue()
      self.sonos.play_from_queue(len(q) - 1)

   def play_next(self, DidlItem):
      #Find current track and insert item after it.
      q = self.sonos.get_queue()
      if len(q) > 0:
         p = self.sonos.get_current_track_info()['playlist_position']
         self.sonos.add_to_queue(DidlItem, position = int(p) + 1)
      else:
         self.sonos.add_to_queue(DidlItem)

   def add_to_end_of_queue(self, DidlItem):
      #Just do what the method says.
      self.add_to_queue(DidlItem)

   def play_now_and_replace_queue(self, DidlItem):
      #Again, just do what the method says
      self.stop()
      self.sonos.clear_queue()
      self.add_to_queue(DidlItem)
      self.sonos.play_from_queue(0)

   def play(self):
      if self.sonos is not None:
         if self.state() == 'PLAYING':
            self.sonos.pause()
            print("PAUSE")
         else:
            self.sonos.play()
            print("PLAY")

   def play_track_at_position(self, position):
      # This method is meant for the QueuePage
      # Pressing the OK button will play
      # the selcted item, but will not
      # toggle to pause if the track was
      # already playing.
      p = self.sonos.get_current_track_info()['playlist_position']
      if int(p) != position:
         self.sonos.stop()
         self.sonos.play_from_queue(position - 1)
      elif self.state() != 'PLAYING':
         self.sonos.play_from_queue(position - 1)

   def stop(self):
      """Stop"""
      states = ['PLAYING', 'PAUSED_PLAYBACK']

      if self.state() in states:
         self.sonos.stop()
      return self.get_current_track_info()

   def next(self):
      """Play the next track"""
      try:
         self.sonos.next()
      except SoCoUPnPException:
         print("No Such track!")
         #raise SoCoIllegalSeekException('No such track')
      return self.get_current_track_info()

   def previous(self):
       """Play the previous track"""
       try:
           self.sonos.previous()
       except SoCoUPnPException:
          print("No Such track!")
          #raise SoCoIllegalSeekException('No such track')
       return self.get_current_track_info()

   def on_auto_renewal_failure(self, exception):
      #This function is called from the subscription thread
      # so thread safety needs to be maintained here.
      msg = 'Error received on autorenew: {}'.format(str(exception))
      print(msg)

   def subscribe_to_events(self):
      # subscribe to both av and render events for each sonos device
#      self.eventSubs.append(self.sonos.avTransport.subscribe(auto_renew = True))
#      self.eventSubs.append(self.sonos.renderingControl.subscribe(auto_renew = True))
#      self.eventSubs.append(self.sonos.musicServices.subscribe(auto_renew = True))
#      self.eventSubs.append(self.sonos.contentDirectory.subscribe(auto_renew = True))
#      self.eventSubs.append(self.sonos.groupManagement.subscribe(auto_renew = True))

      service = soco.services.Queue(self.sonos)
      self.eventSubs.append(service.subscribe(auto_renew = True))

      service = soco.services.AVTransport(self.sonos)
      self.eventSubs.append(service.subscribe(auto_renew=True))

      service = soco.services.RenderingControl(self.sonos)
      self.eventSubs.append(service.subscribe(auto_renew=True))

      for sub in self.eventSubs:
         sub.auto_renew_fail = self.on_auto_renewal_failure

   def monitor(self):
      # Used to track the state of the
      # active or group master
      # zone.
      if self.state() == 'PLAYING':
         self.parent.on_current_track_update_state(self.sonos.get_current_track_info())

   def update(self):
      # Tracks the state of the events for
      # any instant of a Zone object.
      for sub in self.eventSubs:
         try:
            event = sub.events.get(timeout = 0.1)
#            print(event)
#            print(event.sid)
#            print(event.seq)
            print('event_type: {:20}  from: {}'.format(
                event.service.service_type,
                event.service.soco.player_name))
            print(event.variables)

            if event.service.service_type is "AVTransport":
               self.parent.on_zone_transport_change_event(event)
               # update view of the queue
               self.on_queue_remote_event()

            elif event.service.service_type is "RenderingControl":
               self.parent.on_zone_render_change_event(event)

            elif event.service.service_type is "Queue":
               self.on_queue_remote_event()

         except queue.Empty:
            pass

   def __init__(self, sonos, parent):
      self.sonos = sonos
      self.parent = parent

      self.qStore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, object)
#      self.qStore = Gtk.ListStore(str, str, object)
#      self.sonos.switch_to_line_in()

      self.eventSubs = []
      self.subscribe_to_events()

   def __del__(self):
      for sub in self.eventSubs:
         sub.unsubscribe()
      event_listener.stop()