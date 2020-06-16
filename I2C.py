import time
import pigpio
from enum import Enum

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

PI_BATTERY_LEVEL_REGISTER = 0x02
PI_INPUT_REGISTER_H = 0x03
PI_INPUT_REGISTER_L = 0x04
PI_DEBUG_BYTE_REGISTER = 0x05
PI_DEBUG_WORD_REGISTER_H = 0x06
PI_DEBUG_WORD_REGISTER_L = 0x07
PI_FREE_TEXT_REGISTER = 0x08
PI_END_REGISTER = 0x09

PI_REGISTERS = [0] * PI_END_REGISTER

from abc import ABCMeta, abstractmethod

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
   def on_system_event(self):
      pass


class CRi2c():

   I2C_ADDR=0x01

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
      print(s)

   def processMessage(self, data, rem):
       #print("REM: {}".format(rem))
       #print(len(data))

       reg = data[0]
       n = 2

       if reg == PI_EVENT_REGISTER:
           print("Got EVENT register: {}, data: {}".format(reg, data[1]))
           print("Byte value: {}". format(data[1]))
           ch = 0 if (data[1] & PI_EVENT_CHARGING_BIT_A == False and data[1] & PI_EVENT_CHARGING_BIT_B == False) else \
                1 if data[1] & PI_EVENT_CHARGING_BIT_A else \
                2 if data[1] & PI_EVENT_CHARGING_BIT_B else \
                3
           print("Sleep: {}, Shutdown: {}, Reboot: {}, Charger: {}".
               format(data[1] & PI_EVENT_SLEEP_BIT, data[1] & PI_EVENT_SHUTDOWN_BIT, data[1] & PI_EVENT_REBOOT_BIT,
                   "Disconnected" if ch == 0 else "EOC" if ch == 1 else "Charging" if ch == 2 else "UNK"))
           self.printByte(data[1], 1)

       elif reg == PI_BATTERY_LEVEL_REGISTER:
           print("Got BATT LEVEL register: {}, Level: {}%". format(reg, data[1]))
           self.printByte(data[1], 1)
           PI_REGISTERS[PI_BATTERY_LEVEL_REGISTERS] = data[1]
           if self.I2CListeners is not None and len(self.I2CListeners) > 0:
              for key in self.I2CListeners:
                 self.I2CListeners[key].on_battery_level_event(PI_REGISTERS[PI_BATTERY_LEVEL_REGISTER])

       elif reg == PI_INPUT_REGISTER_H:
           print("Got SWITCH register: {}, data: {} {}".format(reg, data[1], data[2]))
           n = 3
           #print("sent={} FR={} received={} [{}]".format(s>>16, s&0xfff, b, data))

           #print("Got byte: {}".format(data[1]))
           #print("Got byte: {}".format(data[2]))
           if len(data) > 2:
              s = ""
              w = (data[1] << 8) | data[2]
              print("Word value: {}".format(w))
              self.printByte(w, 2)
              print("Current reg")
              self.printByte(PI_REGISTERS[PI_INPUT_REGISTER_H], 2)

              oldW = (PI_REGISTERS[PI_INPUT_REGISTER_H] << 8) | PI_REGISTERS[PI_INPUT_REGISTER_L]
              if self.I2CListeners is not None and len(self.I2CListeners) > 0:
                 change = w ^ oldW
                 if change != 0:
                    print("CHANGE: ")
                    self.printByte(change, 2)
                    i = 0
                    while i < SWITCH_LIST_END:
                        if change & (1 << i):
                           for key in self.I2CListeners:
                               if i == SWITCH_SCROLL_EVENT:
                                   self.I2CListeners[key].on_scroll_event(w >> SWITCH_SCROLL_EVENT) # NEEDS DIRECTION!!
                                   pass
                               else:
                                   if w & (1 << i):
                                      self.I2CListeners[key].on_button_pressed_event(i)
                                   else:
                                      self.I2CListeners[key].on_button_released_event(i)
                        i = i + 1

                    PI_REGISTERS[PI_INPUT_REGISTER_H] = data[1]
                    PI_REGISTERS[PI_INPUT_REGISTER_L] = data[2]


       elif reg == PI_DEBUG_BYTE_REGISTER:
           print("Got BYTE DEBUG register: {}, data: {}". format(reg, data[1]))
           self.printByte(data[1], 1)

       elif reg == PI_DEBUG_WORD_REGISTER_H:
           print("Got WORD DEBUG register: {}, data: {} {}".format(reg, data[1], data[2]))
           n = 3
           i = 0
           #print("sent={} FR={} received={} [{}]".format(s>>16, s&0xfff, b, data))

           #print("Got byte: {}".format(data[1]))
           #print("Got byte: {}".format(data[2]))
           if len(data) > 2:
              s = ""
              w = (data[1] << 8) | data[2]
              print("Word value: {}".format(w))
              self.printByte(w, 2)


       elif reg == PI_FREE_TEXT_REGISTER:
           print("Got TEXT register: {}, rem: {}, len: {}, LEN: {}". format(reg, rem, data[1], len(data[2:])))
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
               print(i)
               print(l)
               print(e)

       return n

   def i2c(self, id, tick):

       s, b, d = self.pi.bsc_i2c(PI_I2C_ADDRESS)
       if b:
           print("-----------------Got {} bytes! Status {}--------------".format(b, s))
           j = 0
           rem = b
           while j < b:
               reg = d[j]
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
        print("Loading I2C interface.")
        self.I2CListeners = {}

        self.pi = pigpio.pi()

        if not self.pi.connected:
           exit()

        # handle slave activity
        self.e = self.pi.event_callback(pigpio.EVENT_BSC, self.i2c)

        self.pi.bsc_i2c(PI_I2C_ADDRESS) # configures the BSC as I2C slave

      except:
          self.Close()

      print("I2C running!")

   def Close(self):
     print("I2C Done!")

     self.e.cancel()

     self.pi.bsc_i2c(0) # disable peripherial

     self.pi.stop()
