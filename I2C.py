import os
import time
import pigpio
import threading
from PipeW import PipeW
from enum import Enum
from contextlib import redirect_stdout
from Xlib import X, display

# GPIO 19 (SCL)
# GPIO 18 (SDA)

PI_I2C_ADDRESS = 0x01

SWITCH_MUTE = 0
SWITCH_VOL_UP =  1
SWITCH_VOL_DN = 2
SWITCH_A = 3
SWITCH_B = 4
SWITCH_C = 5
SWITCH_ZONE = 6
SWITCH_BACK = 7
SWITCH_MUSIC = 8
SWITCH_ENTER = 9
SWITCH_REWIND = 10
SWITCH_PLAY_PAUSE = 11
SWITCH_FORWARD = 12
SWITCH_SCROLL_EVENT = 13
SWITCH_LIST_END = 14

SWITCH_MUTEbm = (1 << SWITCH_MUTE)
SWITCH_VOL_UPbm = (1 <<  SWITCH_VOL_UP)
SWITCH_VOL_DNbm = (1 << SWITCH_VOL_DN)
SWITCH_Abm = (1 << SWITCH_A)
SWITCH_Bbm = (1 << SWITCH_B)
SWITCH_Cbm = (1 << SWITCH_C)
SWITCH_ZONEbm = (1 << SWITCH_ZONE)
SWITCH_BACKbm = (1 << SWITCH_BACK)
SWITCH_MUSICbm = (1 << SWITCH_MUSIC)
SWITCH_ENTERbm = (1 << SWITCH_ENTER)
SWITCH_REWINDbm = (1 << SWITCH_REWIND)
SWITCH_PLAY_PAUSEbm = (1 << SWITCH_PLAY_PAUSE)
SWITCH_FORWARDbm = (1 << SWITCH_FORWARD)
SWITCH_SCROLL_EVENTbm = (1 << SWITCH_SCROLL_EVENT)

PI_EVENT_REGISTER = 0x01
PI_EVENT_SLEEP_BIT = (1 << 0)
PI_EVENT_SHUTDOWN_BIT = (1 << 1)
PI_EVENT_REBOOT_BIT = (1 << 2)
PI_EVENT_CHARGING_BIT_A = (1 << 3)
PI_EVENT_CHARGING_BIT_B = (1 << 4)
PI_EVENT_RESTART_APP_BIT = (1 << 5)

PI_BATTERY_LEVEL_REGISTER = 0x02
PI_INPUT_REGISTER_H = 0x03
PI_INPUT_REGISTER_L = 0x04
PI_SCROLL_CLICKS_REGISTER = 0x05
PI_DEBUG_BYTE_REGISTER = 0x06
PI_DEBUG_WORD_REGISTER_H = 0x07
PI_DEBUG_WORD_REGISTER_L = 0x08
PI_FREE_TEXT_REGISTER = 0x09
PI_END_REGISTER = 0x0A

PI_REGISTERS = [0] * PI_END_REGISTER

from abc import ABCMeta, abstractmethod

# I/O pipes
I2C_OUT = '/tmp/cr101.i2c.out'

class I2CListener(object):
   __metaclass__=ABCMeta

   def __init__(self):
      pass
   
   @abstractmethod
   def on_button_pressed_event(self, btn):
      pass

   @abstractmethod
   def on_button_released_event(self, btn):
      pass

   @abstractmethod
   def on_scroll_event(self, steps):
      pass

   @abstractmethod
   def on_battery_level_event(self, level):
      pass

   @abstractmethod
   def on_charger_event(self):
      pass

   @abstractmethod
   def on_system_event(self, event):
      pass


class CRi2c():

   def Log(self, s, both = False):
      if self.pipe is not None:
         self.pipe.Send(s + '\n')
         if both == True:
            print(s)
      else:
         print(s)

   def updateListeners(self, event):
       pass
#      if len(I2CListeners) gt 0:
#          for key in I2CListeners:

   def printByte(self, data, size):
      i = size * 8
      s = ""
      while i > 0:
          if data & (1 << (i - 1)):
             s += "1"
          else:
             s += "0"
          i = i - 1
          if i % 4 == 0:
              s += " "
      self.Log(s)

   def sendEvent(self, btn, pressed):
      data = []
      data.append(PI_INPUT_REGISTER_H)
      if btn < SWITCH_MUSIC:
         data.append(0)
         data.append((1 << btn) if pressed == True else 0)
      else:
         data.append((1 << (btn - 8)) if pressed == True else 0)
         data.append(0)
      #self.Log(data)
      self.processMessage(data, 3)


   def processMessage(self, data, rem):
       #print("REM: {}".format(rem))
       #print(len(data))

       with self.mutex:
           reg = data[0]
           n = 2

           if reg == PI_EVENT_REGISTER:
               self.Log("Got EVENT register: {}, data: {}".format(reg, data[1]))
               self.Log("Byte value: {}". format(data[1]))
               ch = 0 if (data[1] & PI_EVENT_CHARGING_BIT_A == False and data[1] & PI_EVENT_CHARGING_BIT_B == False) else \
                    1 if data[1] & PI_EVENT_CHARGING_BIT_A else \
                    2 if data[1] & PI_EVENT_CHARGING_BIT_B else \
                    3
               self.Log("Sleep: {}, Shutdown: {}, Reboot: {}, Charger: {}".
                   format(data[1] & PI_EVENT_SLEEP_BIT, data[1] & PI_EVENT_SHUTDOWN_BIT, data[1] & PI_EVENT_REBOOT_BIT,
                       "Disconnected" if ch == 0 else "EOC" if ch == 1 else "Charging" if ch == 2 else "UNK"))
               self.printByte(data[1], 1)

               oldR = PI_REGISTERS[PI_EVENT_REGISTER]
               change = data[1] ^ oldR
               PI_REGISTERS[PI_EVENT_REGISTER] = data[1]
               if change != 0:
                  if self.I2CListeners is not None and len(self.I2CListeners) > 0:
                     if reg & PI_EVENT_SHUTDOWN_BIT:
                        self.Log("SOFT SHUTDOWN RECEIVED!")
                     elif reg & PI_EVENT_RESTART_APP_BIT:
                        self.Log("RESTART APP RECEIVED!")
                     elif reg & PI_EVENT_REBOOT_BIT:
                        self.Log("REBOOT OS RECEIVED!")
                     elif change & PI_EVENT_SLEEP_BIT:
                         if data[1] & PI_EVENT_SLEEP_BIT:
                            self.pi.write(22, 0)
                            self.Log("Go to sleep LCD.")
                         else:
                            self.pi.write(22, 1)
                            self.Log("Wake up LCD.")

                     for key in self.I2CListeners:
                        self.I2CListeners[key].on_system_event(PI_REGISTERS[PI_EVENT_REGISTER])

           elif reg == PI_BATTERY_LEVEL_REGISTER:
               self.Log("Got BATT LEVEL register: {}, Level: {}%". format(reg, data[1]))
               self.printByte(data[1], 1)
               PI_REGISTERS[PI_BATTERY_LEVEL_REGISTER] = data[1]
               if self.I2CListeners is not None and len(self.I2CListeners) > 0:
                  for key in self.I2CListeners:
                     self.I2CListeners[key].on_battery_level_event(PI_REGISTERS[PI_BATTERY_LEVEL_REGISTER])

           elif reg == PI_INPUT_REGISTER_H:
               # If it is a sleep, wake up the display on button/scroll events.
               d = display.Display()
               s = d.screen()
               root = s.root
               root.warp_pointer(0, 0)
               d.sync()
               root.warp_pointer(481, 321)
               d.sync()
               self.pi.write(22, 1)

               self.Log("Got SWITCH register: {}, data: {} {}".format(reg, data[1], data[2]))
               n = 3
               #print("sent={} FR={} received={} [{}]".format(s>>16, s&0xfff, b, data))

               #print("Got byte: {}".format(data[1]))
               #print("Got byte: {}".format(data[2]))
               if len(data) > 2:
                  s = ""
                  w = (data[1] << 8) | data[2]
                  self.Log("Word value: {}".format(w))
                  self.printByte(w, 2)
                  self.Log("Current reg")
                  self.printByte(PI_REGISTERS[PI_INPUT_REGISTER_H], 2)

                  oldW = (PI_REGISTERS[PI_INPUT_REGISTER_H] << 8) | PI_REGISTERS[PI_INPUT_REGISTER_L]
                  if self.I2CListeners is not None and len(self.I2CListeners) > 0:
                     change = w ^ oldW
                     if change != 0:
                        self.Log("CHANGE: ")
                        self.printByte(change, 2)
                        i = 0
                        while i < SWITCH_LIST_END:
                            if change & (1 << i):
                               for key in self.I2CListeners:
                                   if i == SWITCH_SCROLL_EVENT:
                                      pass
                                       #self.Log("SCROLL!! {}".format(w))
                                       #self.I2CListeners[key].on_scroll_event(w >> SWITCH_SCROLL_EVENT) # NEEDS DIRECTION!!

                                   else:
                                       if w & (1 << i):
                                          self.I2CListeners[key].on_button_pressed_event(i)
                                       else:
                                          self.I2CListeners[key].on_button_released_event(i)
                            i = i + 1

                        PI_REGISTERS[PI_INPUT_REGISTER_H] = data[1]
                        PI_REGISTERS[PI_INPUT_REGISTER_L] = data[2]


           elif reg == PI_SCROLL_CLICKS_REGISTER:
              clicks = data[1] - 128 # convert unsigned to signed count.
              self.Log("Got SRCOLL BYTE register: {}, data: {}, clicks: {}". format(reg, data[1], clicks))
              self.printByte(data[1], 1)
              if self.I2CListeners is not None and len(self.I2CListeners) > 0:
                 for key in self.I2CListeners:
                    self.I2CListeners[key].on_scroll_event(clicks)

           elif reg == PI_DEBUG_BYTE_REGISTER:
               self.Log("Got BYTE DEBUG register: {}, data: {}". format(reg, data[1]))
               self.printByte(data[1], 1)

           elif reg == PI_DEBUG_WORD_REGISTER_H:
               self.Log("Got WORD DEBUG register: {}, data: {} {}".format(reg, data[1], data[2]))
               n = 3
               i = 0
               #print("sent={} FR={} received={} [{}]".format(s>>16, s&0xfff, b, data))

               #print("Got byte: {}".format(data[1]))
               #print("Got byte: {}".format(data[2]))
               if len(data) > 2:
                  s = ""
                  w = (data[1] << 8) | data[2]
                  self.Log("Word value: {}".format(w))
                  self.printByte(w, 2)


           elif reg == PI_FREE_TEXT_REGISTER:
               self.Log("Got TEXT register: {}, rem: {}, len: {}, LEN: {}". format(reg, rem, data[1], len(data[2:])))
               i = 0
               l = data[1]
               data = data[2:]
               s = ""
               try:
                   while i < l:# and data[i] is not 0:
                       #print(i)
                       #s += chr(data[i]);
                       s += str(data[i]) + ", "
                       self.printByte(data[i], 1)
                       i = i + 1
                   n = l + 2
                   print("Message: {}".format(s))
               except IndexError as e:
                   self.Log(str(i))
                   self.Log(l)
                   self.Log(e)

           return n

   def i2c(self, id, tick):
       self.Log("Receuved I2C data")
       s, b, d = self.pi.bsc_i2c(PI_I2C_ADDRESS)
       if b:
           self.Log("-----------------Got {} bytes! Status {} d[0] {}--------------".format(b, s, d[0]))
           j = 0
           rem = b
           while j < b:
               #reg = d[j]
               n = self.processMessage(d[j:], rem)
               j = j + n
               rem = rem - n

   def setListener(self, id, listener):
       self.I2CListeners[id] = listener

   def remove_i2c_listener(self, id):
      if id in self.I2CListeners:
         self.I2CListeners.pop(id)

   def __init__(self):
      try:
         try:
            self.pipe = PipeW(I2C_OUT, 100)
            self.pipe.Start()
         except:
            self.pipe = None

         self.Log("Loading I2C interface.", True)
         self.mutex = threading.Lock()
         
         self.I2CListeners = {}

         self.pi = pigpio.pi()

         if not self.pi.connected:
            self.Log("Running without PIGPIO!", True)
         else:
            # Enable the LCD backlight.
            self.pi.set_mode(22, pigpio.OUTPUT)
            self.pi.write(22, 1)
            # handle slave activity
            self.e = self.pi.event_callback(pigpio.EVENT_BSC, self.i2c)

            self.pi.bsc_i2c(PI_I2C_ADDRESS) # configures the BSC as I2C slave

      except:
         self.Close()

      self.Log("I2C running!", True)

   def Close(self):
     self.Log("I2C Done!", True)

     if self.pi is not None and self.pi.connected:
         self.e.cancel()

         self.pi.bsc_i2c(0) # disable peripherial

         self.pi.stop()

         if self.pipe is not None:
            self.pipe.Stop()

