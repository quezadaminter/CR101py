import os
import time
import io
import threading
import queue
from threading import Thread, Lock

class PipeW:
   def __init__(self, fifoPath, msgQMax):
      self.path = fifoPath
      self.pipe = None
      self.blocking = False
      self.msgQ = queue.Queue()
      self.msgQMax = msgQMax
      self.pipeThread = Thread(target = self.PipeThreadHandler)

   def OpenPipe(self):
   
      try:
         os.mkfifo(self.path)
         print("Created pipe on filesystem: " . self.path)
      except Exception as e:
         print("MKFIFO: " + repr(e))

      try:
         print("Waiting for listener.")
         self.blocking = True
         fd = os.open(self.path, os.O_WRONLY)# blocking
         self.blocking = False
         print("OPENED File")
         out = os.fdopen(fd, 'w') #also non-blocking
         print("OPENED File descriptor")
         print(io.DEFAULT_BUFFER_SIZE)
      except Exception as e:
         out = None
         print("OPEN: " . e)
   
      return out
   
   def ClosePipe(self):
      try:
         if self.blocking == False:
            self.pipe.flush()
            self.pipe.close()
         else:
            self.pipeThreadRunning = False
      except BrokenPipeError:
         print("Pipe was already closed.")
      self.pipe = None
      try:
         os.unlink(self.path)
      except FileNotFoundError:
         pass

   def PipeThreadHandler(self):
      self.pipeThreadRunning = True
      self.pipe = self.OpenPipe()
      while self.pipeThreadRunning:
         try:
            msg = self.msgQ.get(block = True, timeout = 2)
            self.msgQ.task_done()
            self.pipe.write(msg)
            self.pipe.flush()
         except queue.Empty:
            pass
         except BrokenPipeError:
            print("Disconnected!")
            self.ClosePipe()
            self.pipe = self.OpenPipe()
   
      self.ClosePipe()

   def Send(self, message):
      if self.msgQ.qsize() < self.msgQMax:
         self.msgQ.put(message)
      else:
         self.msgQ.get(block = False)
         self.msgQ.task_done()
         self.msgQ.put(message)

   def Start(self):
      if self.pipeThread.is_alive() == False:
         print("Starting pipe thread.")
         self.pipeThread.start()

   def Stop(self):
      if self.pipeThread.is_alive() == True:
         self.pipeThreadRunning = False
         if self.blocking == True:
            fifo = os.open(self.path, os.O_RDONLY)
            os.close(fifo)
      else:
         self.ClosePipe()