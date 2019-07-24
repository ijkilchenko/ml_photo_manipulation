from PIL import Image, ExifTags
import os
import sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--in-path', help='Path to the original images')
parser.add_argument('--out-path', help='Path to the resized images')
parser.add_argument('--resize-factor', help='Multiplicative factor for the new height and new width')
args = parser.parse_args()

if not os.path.exists(args.out_path):
    os.makedirs(args.out_path)

def resize():
  for item in os.listdir(args.in_path):
    if os.path.isfile(os.path.join(args.in_path,item)):
      try:
        im = Image.open(os.path.join(args.in_path,item))
      except OSError:
        print('Could not open %s' % item)
        continue

      # Keep orientation
      if hasattr(im, '_getexif'):
        exif = im._getexif()
        if exif:
          for tag, label in ExifTags.TAGS.items():
            if label == 'Orientation':
              orientation = tag
              break
          if orientation in exif:
            if exif[orientation] == 3:
              im = im.rotate(180, expand=True)
            elif exif[orientation] == 6:
              im = im.rotate(270, expand=True)
            elif exif[orientation] == 8:
              im = im.rotate(90, expand=True)

      f, e = os.path.splitext(os.path.join(args.in_path,item))
      height, width = im.size
      imResize = im.resize((int(height*float(args.resize_factor)), int(width*float(args.resize_factor))), Image.ANTIALIAS)
      imResize.save(os.path.join(args.out_path, item), 'JPEG', quality=90)
      print('%s resized' % item)

resize()