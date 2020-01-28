import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import Pango
from gi.repository import Gio
from PageBase import PageBase
from threading import Lock
from enum import Enum
import requests

mutex = Lock()

class PlayModeDialog(Gtk.Dialog):

   class Choice(Enum):
      PLAY_NORMAL = 0
      PLAY_SHUFFLE = 1
      PLAY_REPEAT = 2
      PLAY_SHUFFLE_REPEAT = 3
      CROSSFADE = 4

   def on_tree_selection_changed(self, selection):
       model, treeiter = selection.get_selected()
       if treeiter is not None:
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
      Gtk.Dialog.__init__(self, "", parent.topLevel, 0)

      self.selection = None

      self.listStore = Gtk.ListStore(str, object)
      self.listView = Gtk.TreeView(self.listStore)
      self.listView.set_headers_visible(False)
      
      rend = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn("Type", rend, text=0)
      col.set_resizable(False)
      col.set_expand(False)
      self.listView.append_column(col)
      
      xfade = "Turn Crossfade " + ("On" if parent.crossFadeMode == '0' else "Off")
      self.listStore.append(["Normal", self.Choice.NORMAL])
      self.listStore.append(["Shuffle", self.Choice.SHUFFLE])
      self.listStore.append(["Repeat", self.Choice.REPEAT])
      self.listStore.append(["Shuffle-Repeat", self.Choice.SHUFFLE_REPEAT])
      self.listStore.append([xfade, self.Choice.CROSSFADE])

      self.select = self.listView.get_selection()
      self.select.connect("changed", self.on_tree_selection_changed)
      
      self.selected_row_iter = self.listStore.get_iter_first()
      if self.selected_row_iter is not None:
         self.select.select_iter(self.selected_row_iter)

      box = self.get_content_area()
      box.add(self.listView)
      self.show_all()

class MusicPlayingPage(PageBase):

   def close_play_mode_dialog(self):
      self.playModeDialog.destroy()
      self.playModeDialog = None

   def handlePlayModeResponse(self):
      response = self.playModeDialog.get_response()
      self.close_play_mode_dialog()
      if response == PlayModeDialog.Choice.PLAY_NORMAL:
         pass
      elif response == PlayModeDialog.Choice.PLAY_SHUFFLE:
         pass
      elif response == PlayModeDialog.Choice.PLAY_REPEAT:
         pass
      elif response == PlayModeDialog.Choice.PLAY_SHUFFLE_REPEAT:
         pass
      elif response == PlayModeDialog.Choice.CROSSFADE:
         pass

   def on_zoneButton_Clicked(self):
      # Close all open dialogs.
      if self.playModeDialog is not None:
         self.close_play_mode_dialog()
      super().on_zoneButton_Clicked()

   def on_Page_Entered_View(self, SelectedZone):
      # Update the page when it shows up with
      # the latest information.
      zone = self.topLevel.get_selected_zone()
      if zone is not None:
         self.on_zone_transport_change_event(zone.get_current_transport_info())
         self.on_current_track_update_state(zone.get_current_track_info())
      print("Music playing view")

   def on_Button_A_Clicked(self):
      if self.playModeDialog is None:
         self.playModeDialog = PlayModeDialog(self)
         self.playModeDialog.set_decorated(False)
      else:
         self.handlePlayModeResponse()

   def on_Button_B_Clicked(self):
       pass

   def on_Button_C_Clicked(self):
      if self.playModeDialog is not None:
         self.close_play_mode_dialog()
      self.topLevel.show_queue_page()

   def on_Return_Button_Clicked(self):
      if self.playModeDialog is None:
         self.topLevel.show_page("MusicPage")
      else:
         self.close_play_mode_dialog()

   # The scroll wheel
   def on_Scroll_Up(self):
      if self.playModeDialog is not None:
         self.playModeDialog.on_Scroll_Up()

   def on_Scroll_Down(self):
      if self.playModeDialog is not None:
         self.playModeDialog.on_Scroll_Down()

   def on_Button_Ok_Clicked(self):
      if self.playModeDialog is None:
         self.topLevel.show_page("MusicAlbumArtPage")
      else:
         self.handlePlayModeResponse()

   def set_text_size(self, textSize):
      #PangoAttrList *attrlist = pango_attr_list_new();
      #PangoAttribute *attr = pango_attr_size_new_absolute(20);
      #pango_attr_list_insert(attrlist, attr);
      #gtk_label_set_attributes(GTK_LABEL(label), attrlist);
      #attrList = pango.AttrList()
      #attr = pango.AttrSize(textSize * 1000, 0, -1)
      #attrList.insert(attr)
      #return attrList
      pass

   def on_zone_transport_change_event(self, event):
      mutex.acquire()

      try:
         currentPlayMode = event.variables['current_play_mode']
         if currentPlayMode == 'SHUFFLE_NOREPEAT':
            self.playModeRepeatImage.clear()
            self.playModeShuffleImage.set_from_icon_name(Gtk.STOCK_FIND, Gtk.IconSize.SMALL_TOOLBAR)
         elif currentPlayMode == 'REPEAT_ALL':
            self.playModeRepeatImage.set_from_icon_name(Gtk.STOCK_REFRESH, Gtk.IconSize.SMALL_TOOLBAR)
            self.playModeShuffleImage.clear()
         elif currentPlayMode == 'NORMAL':
            self.playModeRepeatImage.clear()
            self.playModeShuffleImage.clear()
         elif currentPlayMode == 'SHUFFLE': # shuffle and repeat
            self.playModeRepeatImage.set_from_icon_name(Gtk.STOCK_REFRESH, Gtk.IconSize.SMALL_TOOLBAR)
            self.playModeShuffleImage.set_from_icon_name(Gtk.STOCK_FIND, Gtk.IconSize.SMALL_TOOLBAR)

         xportState = event.variables['transport_state']
         if xportState == 'PAUSED_PLAYBACK':
            self.xportStateImage.set_from_icon_name(Gtk.STOCK_MEDIA_PAUSE, Gtk.IconSize.SMALL_TOOLBAR)
         elif xportState == 'TRANSITIONING':
            self.xportStateImage.set_from_icon_name(Gtk.STOCK_INFO, Gtk.IconSize.SMALL_TOOLBAR)
         elif xportState == 'PLAYING':
            self.xportStateImage.set_from_icon_name(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.SMALL_TOOLBAR)
         elif xportState == 'STOPPED':
            self.xportStateImage.set_from_icon_name(Gtk.STOCK_MEDIA_STOP, Gtk.IconSize.SMALL_TOOLBAR)
            self.trackProgressBar.set_fraction(0.0)
            self.trackProgressTimeLabel.set_text("--:--/--:--")
         else:
            self.xportStateImage.set_from_icon_name(Gtk.STOCK_DIALOG_QUESTION, Gtk.IconSize.SMALL_TOOLBAR)

         self.crossFadeMode = event.variables['current_crossfade_mode']
         if self.crossFadeMode == '1':
            self.crossFadeImage.set_from_icon_name(Gtk.STOCK_NETWORK, Gtk.IconSize.SMALL_TOOLBAR)
         else:
            self.crossFadeImage.clear()

         nextTrackMetaData = event.variables['next_track_meta_data']
         if nextTrackMetaData is not '':
            nextTrackMetaData = nextTrackMetaData.to_dict()
            nextTrackTitle = nextTrackMetaData['title']
            nextTrackArtist = nextTrackMetaData['creator']
            string = "<b>{0} - {1}</b>"
            self.nextTrackNameLabel.set_markup(string.format(nextTrackTitle, nextTrackArtist))
         else:
            self.nextTrackNameLabel.set_text("")

         currentTrack = event.variables['current_track']
         numberOfTracks = event.variables['number_of_tracks']
         string = "Track [{0}/{1}]"
         self.trackNumberLabel.set_text(string.format(currentTrack, numberOfTracks))

         string = "<b>{0}</b>"
         self.inQueueCountLabel.set_markup(string.format(numberOfTracks))

         currentTrackMetaData = event.variables['current_track_meta_data']
         if currentTrackMetaData is not '':
            currentTrackMetaData = currentTrackMetaData.to_dict()
            self.trackNameLabel.set_markup("<b>" + currentTrackMetaData['title'] + "</b>")
            self.artistsNameLabel.set_markup("<b>" + currentTrackMetaData['creator'] + "</b>")
            self.albumNameLabel.set_markup("<b>" + currentTrackMetaData['album'] + "</b>")
            self.trackProgressBar.show()
            self.trackProgressTimeLabel.show()

            if self.topLevel.get_selected_zone() is not None:
               self.albumArtUri = self.topLevel.get_selected_zone().sonos.music_library.build_album_art_full_uri(currentTrackMetaData['album_art_uri'])
               response = requests.get(self.albumArtUri)
               if response.status_code == 200:
                  input_stream = Gio.MemoryInputStream.new_from_data(response.content, None) 
                  pixbuf = GdkPixbuf.Pixbuf()
                  pixbuf = pixbuf.new_from_stream(input_stream, None).scale_simple(128, 128, GdkPixbuf.InterpType.BILINEAR)
                  self.albumArtImage.set_from_pixbuf(pixbuf)
         else:
            self.trackNameLabel.set_markup("<b>[no music]</b>")
            self.artistsNameLabel.set_text("")
            self.albumNameLabel.set_text("")
            self.albumArtImage.set_from_icon_name(Gtk.STOCK_CDROM, Gtk.IconSize.DIALOG)
            self.trackProgressBar.hide()
            self.trackProgressTimeLabel.hide()
      finally:
         mutex.release()

   def on_current_track_update_state(self, trackInfo):
      mutex.acquire()
      try:
         # grab the values from the current track
         # state and update the gui
         trackPos = trackInfo['position'].split(':')
         trackLen = trackInfo['duration'].split(':')
         tpH = int(trackPos[0])
         tpM = int(trackPos[1])
         tpS = int(trackPos[2])

         tlH = int(trackLen[0])
         tlM = int(trackLen[1])
         tlS = int(trackLen[2])

         trackProg = float((tpH * 24) + (tpM * 60) + tpS)
         trackDur  = float((tlH * 24) + (tlM * 60) + tlS)

         tpos = ((trackPos[0] + ":") if tpH > 0 else "") + trackPos[1] + ":" + trackPos[2]
         tdur = ((trackLen[0] + ":") if tlH > 0 else "") + trackLen[1] + ":" + trackLen[2]
      
         self.trackProgressBar.set_fraction(trackProg / trackDur)
         self.trackProgressTimeLabel.set_text(tpos + "/" + tdur)
      finally:
         mutex.release()


   def title(self):
      self.titleLabel = Gtk.Label("Now Playing")
      #self.titleLabel.set_markup("<span size=20000>Now Playing</span>")
      #self.titleLabel.set_attributes(self.set_text_size(20))
      return(self.titleLabel)

   def scrolledWindow(self):
      topVbox = Gtk.VBox()

      stateHBox = Gtk.HBox()
      self.xportStateImage = Gtk.Image()
      self.xportStateImage.set_from_icon_name(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.SMALL_TOOLBAR)
      stateHBox.pack_start(self.xportStateImage, False, False, 5)
      xportStateLabel = Gtk.Label()#"Now Playing")
      xportStateLabel.set_markup("<span size=\"15000\">Now Playing</span>")
      xportStateLabel.set_alignment(0.0, 0.5)
      stateHBox.pack_start(xportStateLabel, True, True, 5)
      self.crossFadeImage = Gtk.Image()
      self.crossFadeImage.set_from_icon_name(Gtk.STOCK_NETWORK, Gtk.IconSize.SMALL_TOOLBAR)
      stateHBox.pack_start(self.crossFadeImage, False, False, 5)
      self.playModeShuffleImage = Gtk.Image()
      self.playModeShuffleImage.set_from_icon_name(Gtk.STOCK_FIND, Gtk.IconSize.SMALL_TOOLBAR)
      stateHBox.pack_start(self.playModeShuffleImage, False, False, 5)
      self.playModeRepeatImage = Gtk.Image()
      self.playModeRepeatImage.set_from_icon_name(Gtk.STOCK_REFRESH, Gtk.IconSize.SMALL_TOOLBAR)
      stateHBox.pack_start(self.playModeRepeatImage, False, False, 5)
      topVbox.pack_start(stateHBox, False, False, 0)

      detailHBox = Gtk.HBox()
      self.albumArtImage = Gtk.Image()
      self.albumArtImage.set_from_icon_name(Gtk.STOCK_CDROM, Gtk.IconSize.DIALOG)
      self.albumArtImage.show()
      detailHBox.pack_start(self.albumArtImage, False, False, 5)

      detailVBox = Gtk.VBox()

      self.trackNumberLabel = Gtk.Label("Track [x/y]")
      self.trackNumberLabel.set_alignment(0.0, 0.5)
      detailVBox.pack_start(self.trackNumberLabel, True, False, 0)

      self.trackNameLabel = Gtk.Label()
      #self.trackNameLabel.set_markup("<b>Track Name Goes Here In Bold</b>")
      self.trackNameLabel.set_markup("<span weight=\"bold\">Track Name Goes Here In Bold</span>")
      self.trackNameLabel.set_ellipsize(Pango.EllipsizeMode.END)
      self.trackNameLabel.set_alignment(0.0, 0.5)
      detailVBox.pack_start(self.trackNameLabel, True, False, 0)

      self.trackProgressBar = Gtk.ProgressBar()
      detailVBox.pack_start(self.trackProgressBar, True, False, 0)

      self.trackProgressTimeLabel = Gtk.Label("--:--/--:--")
      self.trackProgressTimeLabel.set_alignment(1.0, 0.5)
      detailVBox.pack_start(self.trackProgressTimeLabel, True, False, 0)

      artistsLabel = Gtk.Label("Artists")
      artistsLabel.set_alignment(0.0, 0.5)
      detailVBox.pack_start(artistsLabel, True, False, 0)

      self.artistsNameLabel = Gtk.Label()
      self.artistsNameLabel.set_markup("<b>Artist Name Goes Here</b>")
      self.artistsNameLabel.set_ellipsize(Pango.EllipsizeMode.END)
      self.artistsNameLabel.set_alignment(0.0, 0.5)
      detailVBox.pack_start(self.artistsNameLabel, True, False, 0)

      separatorLine = Gtk.Image()
      separatorLine.set_from_file("./separator.png")
      detailVBox.pack_start(separatorLine, True, False, 0)

      albumsLabel = Gtk.Label("Albums")
      albumsLabel.set_alignment(0.0, 0.5)
      detailVBox.pack_start(albumsLabel, True, False, 0)

      self.albumNameLabel = Gtk.Label()
      self.albumNameLabel.set_markup("<b>Album Name Goes Here</b>")
      self.albumNameLabel.set_ellipsize(Pango.EllipsizeMode.END)
      self.albumNameLabel.set_alignment(0.0, 0.5)
      detailVBox.pack_start(self.albumNameLabel, True, False, 0)

      detailHBox.pack_start(detailVBox, True, True, 5)

      topVbox.pack_start(detailHBox, True, True, 2)

      return(topVbox)

   def status(self):
      bottomHBox = Gtk.HBox()

      nextTrackLabel = Gtk.Label("Next: ")
      bottomHBox.pack_start(nextTrackLabel, False, False, 0)

      self.nextTrackNameLabel = Gtk.Label()
      self.nextTrackNameLabel.set_markup("<b>Track Name - Artist Name</b>")
      self.nextTrackNameLabel.set_ellipsize(Pango.EllipsizeMode.END)
      bottomHBox.pack_start(self.nextTrackNameLabel, True, True, 0)

      queueImage = Gtk.Image()
      queueImage.set_from_icon_name(Gtk.STOCK_JUSTIFY_FILL, Gtk.IconSize.SMALL_TOOLBAR)
      bottomHBox.pack_start(queueImage, False, False, 2)

      inQueueLabel = Gtk.Label("In Queue: ")
      bottomHBox.pack_start(inQueueLabel, False, False, 0)

      self.inQueueCountLabel = Gtk.Label()
      self.inQueueCountLabel.set_markup("<b>##</b>")
      self.inQueueCountLabel.set_ellipsize(Pango.EllipsizeMode.END)
      bottomHBox.pack_start(self.inQueueCountLabel, False, False, 0)
      
      return bottomHBox

   def footer(self):
      grid = Gtk.Grid()
      l = Gtk.Label("Play Mode")
      l.set_size_request(100, -1)
      grid.add(l)
      l = Gtk.Label(" ")
      l.set_size_request(100, -1)
      grid.attach(l, 1, 0, 1, 1)
      l = Gtk.Label("View Queue")
      l.set_size_request(100, -1)
      grid.attach(l, 2, 0, 1, 1)
      return grid

   def __init__(self):
      super().__init__()
      self.crossFadeMode = '0'
      self.playModeDialog = None
