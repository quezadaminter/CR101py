from image import Image

ImageManager = {}

def add_image(fileName, id):
   ImageManager[id] = Image(fileName)
   return ImageManager[id]

def get_image(id):
   return ImageManager[id]

def get_pixbuf(id):
   return ImageManager[id].GetPixbuf()